# Align the post frame onto the pre frame over the whole fisheye circle and save the change map.
import sys
import cv2, numpy as np
pre_p, post_p, out = sys.argv[1:4]
A, B = cv2.imread(pre_p), cv2.imread(post_p)
h, w = A.shape[:2]; cx, cy, R = w / 2, h / 2, 0.47 * w
yy, xx = np.mgrid[:h, :w]; circ = (((xx - cx) ** 2 + (yy - cy) ** 2) < R ** 2).astype(np.uint8)
sift = cv2.SIFT_create(8000)
ka, da = sift.detectAndCompute(cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), circ)
kb, db = sift.detectAndCompute(cv2.cvtColor(B, cv2.COLOR_BGR2GRAY), circ)
m = cv2.BFMatcher().knnMatch(db, da, k=2)
good = [a for a, b in m if a.distance < 0.7 * b.distance]
src = np.float32([kb[a.queryIdx].pt for a in good]); dst = np.float32([ka[a.trainIdx].pt for a in good])
H, inl = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
Bw = cv2.warpPerspective(B, H, (w, h))
la, lb = (cv2.GaussianBlur(cv2.cvtColor(x, cv2.COLOR_BGR2LAB).astype(np.float32), (0, 0), 4) for x in (A, Bw))
d = np.linalg.norm(la - lb, axis=2) * circ
cv2.imwrite(out + "_pre.png", A); cv2.imwrite(out + "_postw.png", Bw); np.save(out + "_diff.npy", d)
vis = cv2.applyColorMap(np.clip(d * 4, 0, 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
grid = A.copy()
for g in range(0, w, 100):
    cv2.line(grid, (g, 0), (g, h), (255, 255, 255), 1); cv2.putText(grid, str(g), (g + 2, 20), 0, 0.5, (255, 255, 255), 1)
    cv2.line(grid, (0, g), (w, g), (255, 255, 255), 1); cv2.putText(grid, str(g), (2, g + 16), 0, 0.5, (255, 255, 255), 1)
cv2.imwrite(out + "_check.jpg", cv2.resize(np.hstack([grid, vis]), None, fx=0.5, fy=0.5))
print("inliers", int(inl.sum()))
