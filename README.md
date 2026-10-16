# EgoDelta project page

Project page for **EgoDelta: From Egocentric Scene Change to 3D Attachment Targets for Agricultural Manipulation** (WACV 2027, Applications Track).

The page is a single Astro page. Pushing to `main` builds it and deploys it to GitHub Pages through `.github/workflows/astro.yml`. GitHub Pages must be set to deploy from **GitHub Actions** (Settings → Pages → Source).

## Where things live

| What | File |
| --- | --- |
| Title, authors, affiliations, links, abstract, method steps, BibTeX | `src/data/paper.ts` |
| Numbers behind the bar charts, result tables and trial grid (paper Tables 1–5) | `src/data/results.ts` |
| Video slots (teaser, demonstrations, robot execution) | `src/data/media.ts` |
| Paper figures | `src/assets/figures/` |
| Page layout | `src/pages/index.astro` |
| Styles (the accent colour is `--ours` at the top) | `src/styles/site.css` |

## Before the camera-ready

- Check the author list and affiliations in `src/data/paper.ts` against the camera-ready. The BibTeX entry is generated from the same list.
- Add a `url` to each link button (Paper, arXiv, Code, Video). Buttons without one show as "soon".
- If the camera-ready figures change, overwrite the PNGs in `src/assets/figures/`. Figure 1 was extracted from the submission PDF at only 1070 px wide, so a higher-resolution export is worth swapping in.

## Adding videos

Each video slot shows a "video coming soon" placeholder until a file exists at its path, so adding a video only means copying it to the right name under `public/videos/`. No code changes are needed. The expected files are:

| Section | Files in `public/videos/` |
| --- | --- |
| Teaser tabs | `teaser_harvesting.mp4`, `teaser_deleafing.mp4` |
| Sample demonstration (one row) | `demo_egocentric.mp4`, `demo_pre_2dgs.mp4`, `demo_post_2dgs.mp4`, `demo_target.mp4` |
| Robot execution, learned policy | `robot_harvest1_policy.mp4`, `robot_harvest2_policy.mp4`, `robot_deleaf1_policy.mp4` to `robot_deleaf3_policy.mp4` |

To rename clips, add more tabs, or change panel labels, edit `src/data/media.ts`. Videos play muted and looped and only load when their tab is opened. H.264 MP4s of a few MB each work best; for example:

```bash
ffmpeg -i input.mov -vf "scale=1280:-2" -c:v libx264 -crf 26 -preset slow -an -movflags +faststart public/videos/robot_harvest1_policy.mp4
```

## Local development

Requires Node.js 24 or later.

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # type-check, then build into dist/
npm run lint
```

## Credits

Built on Roman Hauksson-Neill's [academic project page template](https://github.com/RomanHauksson/academic-project-astro-template) (CC BY-SA 4.0).
