# Post-action image for a removed red fruit: segment it in the pre frame and inpaint it away. Also writes a
# matching soft mask and change map in the same format as sim_mask.py (prefix_pre.png, _postclean.png, _mask.npy, _diff.npy).
import sys
import cv2, numpy as np
pre_p, out, x0, y0, x1, y1 = sys.argv[1], sys.argv[2], *map(int, sys.argv[3:7])
A = cv2.imread(pre_p); h, w = A.shape[:2]
hsv = cv2.cvtColor(A, cv2.COLOR_BGR2HSV)
red = (((hsv[..., 0] < 12) | (hsv[..., 0] > 168)) & (hsv[..., 1] > 80) & (hsv[..., 2] > 50)).astype(np.uint8)
roi = np.zeros_like(red); roi[y0:y1, x0:x1] = 1
m = cv2.morphologyEx(red * roi, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
m = np.zeros_like(m); cv2.drawContours(m, [c for c in cnts if cv2.contourArea(c) > 300], -1, 1, -1)
md = cv2.dilate(m, np.ones((11, 11), np.uint8))
# Fill: a smooth quadratic colour fit to the floor around the hole, plus fine texture from the floor below.
ring = (cv2.dilate(md, np.ones((41, 41), np.uint8)) - cv2.dilate(md, np.ones((5, 5), np.uint8))) > 0
floor = (hsv[..., 1] < 70) & (hsv[..., 2] > 60)
ys, xs = np.nonzero(ring & floor)
def basis(x, y): x, y = x / 1000.0, y / 1000.0; return np.stack([np.ones_like(x), x, y, x * x, y * y, x * y], 1)
coef, *_ = np.linalg.lstsq(basis(xs.astype(float), ys.astype(float)), A[ys, xs].astype(np.float64), rcond=None)
yy, xx = np.mgrid[:h, :w]
smooth = (basis(xx.ravel().astype(float), yy.ravel().astype(float)) @ coef).reshape(h, w, 3)
src = np.roll(A, -92, axis=0).astype(np.float32)
texture = src - cv2.GaussianBlur(src, (0, 0), 5)
soft = np.clip(cv2.GaussianBlur(cv2.dilate(md, np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 4) * 1.7, 0, 1)
clean = (A * (1 - soft[..., None]) + np.clip(smooth + 0.7 * texture, 0, 255) * soft[..., None]).astype(np.uint8)
rng = np.random.default_rng(3)
noise = cv2.GaussianBlur(rng.uniform(0, 1, (h, w)).astype(np.float32), (0, 0), 6) * 40
lab = lambda x: cv2.GaussianBlur(cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), 2)
diff = np.linalg.norm(lab(A) - lab(clean), axis=2) + np.clip(noise - 16, 0, None)
cv2.imwrite(out + "_pre.png", A); cv2.imwrite(out + "_postclean.png", clean)
np.save(out + "_mask.npy", soft); np.save(out + "_diff.npy", diff.astype(np.float32))
ov = A.copy(); ov[md > 0] = (0.5 * ov[md > 0] + 0.5 * np.array([60, 220, 120])).astype(np.uint8)
crop = lambda x: x[y0 - 80:y1 + 60, x0 - 120:x1 + 120]
cv2.imwrite(out + "_mask_check.jpg", cv2.resize(np.hstack([crop(ov), crop(clean)]), None, fx=2, fy=2))
print("mask px", int(md.sum()))
