# Demo film

Scripts behind the "From demonstration to robot motion" row. The middle video
is an illustration built from two egocentric frames: it does not run or render
a real 2DGS reconstruction.

Run with the `surfel_splatting` conda environment (OpenCV, PyTorch with CUDA).
The scripts use the miniconda `ffmpeg.exe` and the Windows Segoe UI font.

1. Extract frames from `pre_deleaf.mov` and `post_deleaf.mov` (for example
   `ffmpeg -i pre_deleaf.mov -vf fps=4 pred_%03d.png`) and pick a pair with a
   similar viewpoint (`pred_028.png`, `postd_010.png` were used).
2. `full_align.py PRE POST OUT/dl` warps the post frame onto the pre frame and
   saves the change map as `dl_pre.png`, `dl_postw.png`, `dl_diff.npy`.
3. `sim_mask.py OUT` isolates the removed branch (its region of interest is
   hard-coded for this pair) and writes `dl_mask.npy` and `dl_postclean.png`.
4. `sim_film.py OUT demo_pipeline.mp4 STILLS_DIR` renders the film. The
   attachment target (`TARGET`) and robot path (`PATH`) are set at the top.
5. `ego_clip.py CLIPS_DIR demo_egocentric.mp4` joins the pre-action, removal
   and post-action clips with labels.

The robot panel is `IMG_0107.mov` cropped to a square at 3x speed:
`ffmpeg -i IMG_0107.mov -vf "setpts=PTS/3,fps=30,crop=1080:1080:0:640,scale=720:720" -an demo_robot.mp4`.
