# Illustrative "EgoDelta pipeline" film built from two aligned egocentric frames (no real 2DGS):
# splats converge into the pre-action scene, the removed branch dissolves (post-action), splats recolour by a
# removal score, a target pin appears at the attachment point, and a robot trajectory reaches it and pulls the branch.
import math, subprocess, sys

import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

d_dir, out_path, still_dir = sys.argv[1:4]
FFMPEG = "C:/Users/USER/miniconda3/Library/bin/ffmpeg.exe"
dev = "cuda"
W, FPS = 720, 30
S0 = W / 1408
ACCENT = np.array([70, 209, 139]) / 255
rng = np.random.default_rng(7)


def load(name):
    im = cv2.imread(f"{d_dir}/{name}")[:, :, ::-1]
    return cv2.resize(im, (W, W), interpolation=cv2.INTER_AREA).astype(np.float32) / 255


pre, post = load("dl_pre.png"), load("dl_postclean.png")
mask = cv2.resize(np.load(f"{d_dir}/dl_mask.npy"), (W, W), interpolation=cv2.INTER_AREA)
diff = cv2.resize(np.load(f"{d_dir}/dl_diff.npy"), (W, W), interpolation=cv2.INTER_AREA)
yy, xx = np.mgrid[:W, :W]
circle = ((xx - W / 2) ** 2 + (yy - W / 2) ** 2) < (0.47 * W) ** 2
TARGET = np.array([500 * S0, 678 * S0], np.float32)
INFERNO = cv2.applyColorMap(np.arange(256, dtype=np.uint8)[:, None], cv2.COLORMAP_INFERNO)[:, 0, ::-1] / 255.0


def sample(img, p):
    xi = np.clip(p[:, 0], 0, W - 1.001); yi = np.clip(p[:, 1], 0, W - 1.001)
    x0, y0 = xi.astype(int), yi.astype(int); fx, fy = (xi - x0)[:, None], (yi - y0)[:, None]
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    if a.ndim == 1: fx, fy = fx[:, 0], fy[:, 0]
    return a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy


def splats_from(img, region, n_detail, base_step, seed):
    r = np.random.default_rng(seed)
    g = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
    gx, gy = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3), cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    jxx, jyy, jxy = (cv2.GaussianBlur(v, (0, 0), 1.5) for v in (gx * gx, gy * gy, gx * gy))
    mag = np.sqrt(cv2.GaussianBlur(gx * gx + gy * gy, (0, 0), 1.0))
    mag_n = np.clip(mag / np.percentile(mag[circle], 98), 0, 1)
    valid = circle & region
    ys, xs = np.mgrid[base_step / 2:W:base_step, base_step / 2:W:base_step]
    bp = np.stack([xs.ravel(), ys.ravel()], 1) + r.uniform(-base_step / 2, base_step / 2, (xs.size, 2))
    bp = bp[valid[np.clip(bp[:, 1].astype(int), 0, W - 1), np.clip(bp[:, 0].astype(int), 0, W - 1)]]
    prob = (mag_n ** 0.9 + 0.02) * valid
    idx = r.choice(W * W, n_detail, p=(prob / prob.sum()).ravel())
    dp = np.stack([idx % W, idx // W], 1).astype(np.float32) + r.uniform(0, 1, (n_detail, 2))
    blur = cv2.GaussianBlur(img, (0, 0), 0.8)
    out = []
    for p, base in ((bp.astype(np.float32), True), (dp, False)):
        a, b, c = sample(jxx, p), sample(jyy, p), sample(jxy, p)
        disc = np.sqrt((a - b) ** 2 + 4 * c * c)
        coh = disc / (a + b + 1e-6)
        theta = 0.5 * np.arctan2(2 * c, a - b) + np.pi / 2  # long axis along the edge
        m = sample(mag_n, p)
        if base:
            sig = r.uniform(3.2, 5.0, len(p)); sa, sb, op = sig * (1 + 0.5 * coh), sig, np.full(len(p), 0.45)
        else:
            sig = np.clip(2.4 - 1.5 * m, 0.85, 2.4); sa, sb, op = sig * (1 + 1.6 * coh), sig * (1 - 0.25 * coh), np.full(len(p), 0.95)
        out.append(dict(p=p, sa=sa, sb=sb, th=theta, col=sample(blur, p), op=op, base=np.full(len(p), base), m=m))
    return {k: np.concatenate([o[k] for o in out]) for k in out[0]}


pre_s = splats_from(pre, np.ones_like(circle), 62000, 7, 1)
fill_region = cv2.dilate((mask > 0.05).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
fill_s = splats_from(post, fill_region, 9000, 6, 2)

# Removal score per pre-action splat: high on the removed branch, faint responses elsewhere.
in_mask = sample(mask, pre_s["p"])
dn = np.clip(sample(diff, pre_s["p"]) / 30, 0, 1)
score = np.clip(in_mask * (0.55 + 0.45 * dn) + 0.13 * dn * (1 - in_mask) + rng.uniform(0, 0.03, len(dn)), 0, 1)
removed = in_mask > 0.35
lum = pre_s["col"] @ np.array([0.3, 0.55, 0.15])
heat = INFERNO[np.clip(np.maximum(score, 0.36 * lum) * 255, 0, 255).astype(int)]

# Build-up timing: coarse base splats first, detailed ones later.
N = len(pre_s["p"])
start = np.where(pre_s["base"], rng.uniform(0.0, 0.9, N), rng.uniform(0.5, 1.9, N) + 0.35 * pre_s["m"])
jitter = rng.normal(0, 46, (N, 2)).astype(np.float32)
fly = (rng.normal(0, 1, (N, 2)) * [26, 18] + [0, -70]).astype(np.float32)  # dissolve drift (upward)
delay = rng.uniform(0, 0.45, N)
depth = 0.35 + 0.65 * cv2.GaussianBlur(mask, (0, 0), 20) / max(1e-6, cv2.GaussianBlur(mask, (0, 0), 20).max()) + 0.25 * yy / W
pz = sample(depth.astype(np.float32), pre_s["p"]); fz = sample(depth.astype(np.float32), fill_s["p"])

T = torch.tensor
def gpu(x): return T(np.asarray(x, np.float32), device=dev)


def render(p, sa, sb, th, col, op):
    p, sa, sb, th, col, op = map(gpu, (p, sa, sb, th, col, op))
    keep = op > 1e-3
    p, sa, sb, th, col, op = p[keep], sa[keep], sb[keep], th[keep], col[keep], op[keep]
    c, s = torch.cos(th), torch.sin(th)
    a11 = c * c / sa ** 2 + s * s / sb ** 2; a22 = s * s / sa ** 2 + c * c / sb ** 2; a12 = c * s * (1 / sa ** 2 - 1 / sb ** 2)
    rad = torch.ceil(3 * torch.maximum(sa, sb)).clamp(1, 22)
    acc_w = torch.zeros(W * W, device=dev); acc_c = torch.zeros(W * W, 3, device=dev)
    lo = 0
    for rb in (2, 3, 5, 8, 12, 16, 22):
        sel = (rad > lo) & (rad <= rb); lo = rb
        if not sel.any(): continue
        g = torch.arange(-rb, rb + 1, device=dev, dtype=torch.float32)
        oy, ox = torch.meshgrid(g, g, indexing="ij")
        px = torch.floor(p[sel, 0])[:, None] + ox.reshape(1, -1); py = torch.floor(p[sel, 1])[:, None] + oy.reshape(1, -1)
        dx, dy = px + 0.5 - p[sel, 0:1], py + 0.5 - p[sel, 1:2]
        q = a11[sel, None] * dx * dx + 2 * a12[sel, None] * dx * dy + a22[sel, None] * dy * dy
        w = op[sel, None] * torch.exp(-0.5 * q)
        ok = (px >= 0) & (px < W) & (py >= 0) & (py < W) & (q < 12)
        idx = (py * W + px).long()[ok]; wv = w[ok]
        acc_w.index_add_(0, idx, wv)
        acc_c.index_add_(0, idx, wv[:, None] * col[sel][:, None, :].expand(-1, px.shape[1], -1)[ok])
    colr = acc_c / acc_w.clamp_min(1e-6)[:, None]
    alpha = (1 - torch.exp(-1.7 * acc_w))[:, None]
    img = colr * alpha + gpu([0.015, 0.02, 0.025]) * (1 - alpha)
    return img.reshape(W, W, 3).clamp(0, 1).cpu().numpy()


def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def ramp(t, a, b): return ease((t - a) / (b - a))
def lerp(a, b, k): return a + (b - a) * k


# Timeline (seconds)
DUR = 15.6
PH = [("Pre-action 2DGS", 0.2, 4.2), ("Post-action 2DGS", 4.2, 6.8), ("Removal score", 6.8, 9.2), ("Attachment target", 9.2, 10.9), ("Robot trajectory", 10.9, 15.1)]
B0, B1 = 0.0, 3.1                       # build
D0, D1 = 4.2, 6.0                       # dissolve to post
H0, H1 = 6.8, 8.2                       # back to pre + heat
Z0, Z1 = 9.2, 10.5                      # zoom to target
C0, C1 = 10.9, 11.5                     # heat -> rgb
J0, J1 = 11.0, 12.9                     # trajectory draws
P0, P1 = 13.0, 14.3                     # grasp + pull
O0, O1 = 14.3, 15.1                     # zoom out
F0 = 15.1                               # fade to black

# Robot path in image coordinates: from the robot side (right) to just in front of the target.
def bezier(ps, u):
    u = np.asarray(u)[:, None]; (a, b, c, d) = ps
    return (1 - u) ** 3 * a + 3 * (1 - u) ** 2 * u * b + 3 * (1 - u) * u * u * c + u ** 3 * d
PATH = bezier([np.array([W * 1.15, W * 0.86]), np.array([W * 0.82, W * 0.80]), TARGET + [150, 55], TARGET + [16, 4]], np.linspace(0, 1, 160))
PATH = np.vstack([PATH, np.linspace(TARGET + [16, 4], TARGET, 12)])
PULL = np.array([-48, 28], np.float32)

font = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 31)
font_small = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 16)


def camera(t):
    z = 1 + 0.95 * ramp(t, Z0, Z1) * (1 - ramp(t, O0, O1))
    f = lerp(np.array([W / 2, W / 2]), TARGET + [35, 18], ramp(t, Z0, Z1) * (1 - ramp(t, O0, O1)))
    ang = 2 * math.pi * t / 7.5
    par = np.array([math.sin(ang), 0.4 * math.cos(ang)]) * 9
    return z, f, par


def to_screen(pts, z, f, par, depth=None):
    s = (pts - f) * z + W / 2
    if depth is not None: s = s + (depth[:, None] - 0.5) * par
    return s


def frame(t):
    z, f, par = camera(t)
    # --- pre-action splats
    p = pre_s["p"].copy(); op = pre_s["op"].copy(); sa, sb = pre_s["sa"].copy(), pre_s["sb"].copy(); col = pre_s["col"].copy()
    e = ramp(t, start + B0, start + B0 + 0.9)
    p += jitter * (1 - e)[:, None]; sa *= 1 + 1.2 * (1 - e); sb *= 1 + 1.2 * (1 - e); op *= e ** 1.5
    col = lerp(col * 0.5 + 0.03, col, e[:, None])
    # dissolve (removed splats fly off), return in heat colours, then get pulled by the gripper
    out_k = ramp(t, D0 + delay, D0 + delay + 1.2) * (1 - ramp(t, H0 + delay * 0.5, H0 + delay * 0.5 + 0.9))
    pull = ramp(t, P0 + 0.2, P1 + 0.2)
    rm = removed
    p[rm] += fly[rm] * (out_k[rm] ** 1.5)[:, None] + PULL * pull
    op[rm] *= (1 - out_k[rm]) * (1 - ramp(t, P0 + 0.9, P1 + 0.45))
    sa[rm] *= 1 - 0.5 * out_k[rm]; sb[rm] *= 1 - 0.5 * out_k[rm]
    col[rm] = lerp(col[rm], np.array([0.85, 1.0, 0.9]), 0.7 * out_k[rm][:, None])
    hk = ramp(t, H0 + 0.3, H1) * (1 - ramp(t, C0, C1))
    col = lerp(col, heat, hk)
    # --- post-action fill behind the branch
    fo = ramp(t, D0 + 0.3, D1) * (1 - ramp(t, H0, H0 + 0.8)) + ramp(t, P0 + 0.8, P1 + 0.4)
    fo = min(fo, 1.0)
    P = np.vstack([to_screen(p, z, f, par, pz), to_screen(fill_s["p"], z, f, par, fz)])
    img = render(P, np.concatenate([sa, fill_s["sa"]]) * z, np.concatenate([sb, fill_s["sb"]]) * z,
                 np.concatenate([pre_s["th"], fill_s["th"]]), np.vstack([col, fill_s["col"]]),
                 np.concatenate([op, fill_s["op"] * fo]))
    return overlay((img * 255).astype(np.uint8), t, z, f, par)


def glow_line(layer, pts, color, width):
    pts = np.round(pts * 4).astype(np.int32)
    cv2.polylines(layer, [pts], False, color, width, cv2.LINE_AA, shift=2)


def overlay(img, t, z, f, par):
    tz = to_screen(TARGET[None], z, f, par, np.array([0.9]))[0]
    glow = np.zeros_like(img); sharp = img.copy()
    acc = tuple(int(v) for v in (ACCENT * 255))
    # trajectory
    k = ramp(t, J0, J1)
    if k > 0:
        n = max(2, int(k * len(PATH)))
        tp = to_screen(PATH[:n], z, f, par, np.full(n, 0.9))
        glow_line(glow, tp, acc, 10); glow_line(sharp, tp, acc, 4)
        for q in tp[::16]:
            cv2.circle(sharp, tuple(np.round(q).astype(int)), 3, (255, 255, 255), -1, cv2.LINE_AA)
    # target pin
    tk = ramp(t, 10.0, 10.5) * (1 - ramp(t, O0 + 0.2, O1))
    if tk > 0:
        r = int(15 + 4 * math.sin(t * 6))
        ping = (t * 1.2) % 1.0
        cv2.circle(glow, tuple(tz.astype(int)), int(r + 26 * ping), tuple(int(v * (1 - ping) * tk) for v in (255, 255, 255)), 2, cv2.LINE_AA)
        a = sharp.copy()
        cv2.circle(a, tuple(tz.astype(int)), r, (255, 255, 255), 3, cv2.LINE_AA)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            cv2.line(a, (int(tz[0] + dx * (r - 6)), int(tz[1] + dy * (r - 6))), (int(tz[0] + dx * (r + 9)), int(tz[1] + dy * (r + 9))), (255, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(a, tuple(tz.astype(int)), 5, acc, -1, cv2.LINE_AA)
        sharp = cv2.addWeighted(a, tk, sharp, 1 - tk, 0)
    # gripper head: follows the path, then pulls the branch away
    if k > 0:
        head = PATH[min(len(PATH) - 1, int(k * (len(PATH) - 1)))] + PULL * ramp(t, P0 + 0.2, P1 + 0.2)
        hs = to_screen(head[None], z, f, par, np.array([0.9]))[0]
        gk = 1 - ramp(t, O0, O1)
        if gk > 0:
            a = sharp.copy()
            cv2.circle(a, tuple(np.round(hs).astype(int)), 11, (255, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(a, tuple(np.round(hs).astype(int)), 11, acc, 3, cv2.LINE_AA)
            cv2.circle(glow, tuple(np.round(hs).astype(int)), 16, acc, -1, cv2.LINE_AA)
            sharp = cv2.addWeighted(a, gk, sharp, 1 - gk, 0)
    glow = cv2.GaussianBlur(glow, (0, 0), 7)
    out = np.clip(sharp.astype(np.int32) + glow.astype(np.int32) * 0.9, 0, 255).astype(np.uint8)
    # phase label + progress dots
    im = Image.fromarray(out).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for i, (name, a0, a1) in enumerate(PH):
        al = ramp(t, a0, a0 + 0.3) * (1 - ramp(t, a1 - 0.3, a1))
        if al <= 0: continue
        label = f"{i + 1}  {name}"
        tw = d.textlength(label, font=font)
        d.rounded_rectangle((22, 22, 22 + tw + 40, 22 + 54), radius=27, fill=(12, 14, 18, int(190 * al)))
        d.text((42, 29), f"{i + 1}", font=font, fill=(*acc, int(255 * al)))
        d.text((42 + d.textlength(f"{i + 1}  ", font=font), 29), name, font=font, fill=(255, 255, 255, int(255 * al)))
    cur = max([i for i, (_, a0, _) in enumerate(PH) if t >= a0] or [0])
    for i in range(len(PH)):
        x = W / 2 + (i - 2) * 28
        on = i == cur and t < F0
        d.ellipse((x - 7, W - 40, x + 7, W - 26), fill=(*acc, 235) if on else (255, 255, 255, 110))
    im = Image.alpha_composite(im, ov).convert("RGB")
    arr = np.asarray(im).astype(np.float32)
    fade = min(ramp(t, 0, 0.25), 1 - ramp(t, F0, DUR))
    return (arr * fade).astype(np.uint8)


if __name__ == "__main__":
    for ts in (1.2, 3.6, 5.6, 8.4, 10.6, 12.4, 13.8, 14.9):
        Image.fromarray(frame(ts)).save(f"{still_dir}/still_{ts:04.1f}.png")
    if out_path != "-":
        proc = subprocess.Popen([FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{W}", "-r", str(FPS), "-i", "-",
                                 "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            proc.stdin.write(frame(i / FPS).tobytes())
        proc.stdin.close(); proc.wait()
        print("wrote", out_path)
