# Removed-branch mask from the change map (left-branch ROI only) and a clean post image that differs only there.
import sys
import cv2, numpy as np
d_dir = sys.argv[1]
A = cv2.imread(f"{d_dir}/dl_pre.png"); B = cv2.imread(f"{d_dir}/dl_postw.png"); d = np.load(f"{d_dir}/dl_diff.npy")
roi = np.zeros_like(d, bool); roi[540:840, 50:494] = True
m = ((d > 11) & roi).astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(m)
keep = np.zeros_like(m)
for i in range(1, n):
    if st[i, cv2.CC_STAT_AREA] > 400: keep[lab == i] = 1
keep = cv2.dilate(keep, np.ones((9, 9), np.uint8))
soft = cv2.GaussianBlur(keep.astype(np.float32), (0, 0), 4)[..., None]
clean = (A * (1 - soft) + B * soft).astype(np.uint8)
np.save(f"{d_dir}/dl_mask.npy", soft[..., 0]); cv2.imwrite(f"{d_dir}/dl_postclean.png", clean)
ov = A.copy(); ov[keep > 0] = (0.5 * ov[keep > 0] + 0.5 * np.array([60, 220, 120])).astype(np.uint8)
cv2.circle(ov, (500, 678), 10, (0, 0, 255), 3)
crop = lambda x: x[450:950, 0:700]
cv2.imwrite(f"{d_dir}/dl_mask_check.jpg", np.hstack([crop(ov), crop(clean)]))
print("mask px", int(keep.sum()))
