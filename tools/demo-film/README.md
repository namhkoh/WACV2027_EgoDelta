# Demo film

Scripts behind the "From demonstration to robot motion" tabs. The middle video
in each tab is an illustration built from egocentric frames: it does not run or
render a real 2DGS reconstruction.

Run with the `surfel_splatting` conda environment (OpenCV, PyTorch with CUDA).
The scripts use the miniconda `ffmpeg.exe` and the Windows Segoe UI font.

## Pre/post images

Each film needs `PREFIX_pre.png`, `PREFIX_postclean.png`, `PREFIX_mask.npy` and
`PREFIX_diff.npy` in one directory, in the 1408 px Aria frame.

- Deleafing (`dl`): the pre and post scans share a viewpoint, so the post frame
  is aligned to the pre frame. Pick a pair (`pred_028.png`, `postd_010.png`
  were used), then run `full_align.py PRE POST OUT/dl` and `sim_mask.py OUT`.
  The removed-branch region of interest in `sim_mask.py` is hard-coded.
- Harvesting (`hv`): the clips' viewpoints differ too much to align, so the
  post image is the pre frame (`dur_harvest.mov` before the hand enters) with
  the picked tomatoes filled in:
  `sim_mask_inpaint.py PRE OUT/hv 630 900 800 1020` (the last four numbers are
  the box around the fruit).

## Videos

- `sim_film.py DATA_DIR OUT.mp4 STILLS_DIR PREFIX TX TY PX PY` renders the
  film. `TX TY` is the attachment target in frame pixels and `PX PY` the pull
  direction in output pixels. Used: `dl 500 678 -48 28` and `hv 712 916 30 40`.
  Pass `-` instead of `OUT.mp4` to render only the stills.
- `ego_clip.py CLIPS_DIR OUT.mp4 deleaf|harvest` joins the egocentric clips
  with labels.
- Robot panels are phone clips cropped to a square at 3x speed, e.g.
  `ffmpeg -i IMG_0107.mov -vf "setpts=PTS/3,fps=30,crop=1080:1080:0:640,scale=720:720" -an demo_deleaf_robot.mp4`
  and `crop=1080:1080:640:0` for `IMG_0008.MOV` (harvesting).
