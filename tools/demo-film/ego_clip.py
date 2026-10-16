# Egocentric demonstration panel: pre-action scan -> removal -> post-action scan, with step labels.
import subprocess, sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Usage: ego_clip.py CLIPS_DIR OUT.mp4 deleaf|harvest
src_dir, out_path, task = sys.argv[1:4]
FFMPEG = "C:/Users/USER/miniconda3/Library/bin/ffmpeg.exe"
W, FPS = 720, 30
ACC = (70, 209, 139)
font = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 31)
PARTS = {
    "deleaf": [("pre_deleaf.mov", 2.0, "Pre-action views"), ("dur_deleaf.mov", 1.5, "Removal"), ("post_deleaf.mov", 2.0, "Post-action views")],
    "harvest": [("dur_harvest.mov", 1.5, "Removal"), ("post_harvest.mov", 2.0, "Post-action views")],
}[task]


def frames(path, speed):
    cmd = [FFMPEG, "-v", "error", "-i", path, "-vf", f"setpts=PTS/{speed},fps={FPS},scale={W}:{W}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * W * 3)
        if len(b) < W * W * 3: break
        yield np.frombuffer(b, np.uint8).reshape(W, W, 3)


def label(arr, text, step, alpha):
    im = Image.fromarray(arr).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    tw = d.textlength(text, font=font)
    d.rounded_rectangle((22, 22, 22 + tw + 40, 76), radius=27, fill=(12, 14, 18, int(190 * alpha)))
    d.text((42, 29), text, font=font, fill=(255, 255, 255, int(255 * alpha)))
    return np.asarray(Image.alpha_composite(im, ov).convert("RGB"))


out = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{W}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
for step, (name, speed, text) in enumerate(PARTS, 1):
    fs = list(frames(f"{src_dir}/{name}", speed))
    n = len(fs)
    for i, f in enumerate(fs):
        a = min(1.0, i / 8, (n - 1 - i) / 8)  # quick fade at each cut
        lab = label(f, text, step, max(0.0, min(1.0, i / 6)))
        out.stdin.write((lab.astype(np.float32) * (0.35 + 0.65 * max(0.0, a))).astype(np.uint8).tobytes())
out.stdin.close(); out.wait()
print("wrote", out_path)
