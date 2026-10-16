# AI agent guide for this repo

Single-page Astro 6 site for the EgoDelta (WACV 2027) project page, deployed to GitHub Pages by `.github/workflows/astro.yml` on pushes to `main`.

## Structure

- `src/pages/index.astro`: the whole page (header, teaser, abstract, results, method, figures, videos, citation).
- `src/data/paper.ts`: title, authors, affiliations, links, abstract, method steps; the BibTeX string is derived from these.
- `src/data/results.ts`: paper Tables 1–5. Bar charts (`charts`) and the trial grid (`trials`) are derived from the tables, so edit numbers only in the tables.
- `src/data/media.ts`: video slots. `VideoPanel.astro` renders a placeholder until `public/<src>` exists at build time.
- `src/components/`: `TabBar` + `TabPanel` (pill tabs; panels share a `sec` key), `ClipTabs` (tabbed video grids), `BarChart` (build-time SVG), `ResultTableView`, `TrialGrid`, `Figure` (optimized `astro:assets` Picture), `Logo` (small-caps text wordmark in Space Grotesk).
- `src/scripts/page.ts`: client behaviour only: tab switching, lazy video loading, chart grow-in and tooltip, BibTeX copy.
- `src/styles/site.css`: plain CSS, no framework. `--ours` is the accent used for every "ours" highlight.

## Conventions

- Prefix public asset URLs with `import.meta.env.BASE_URL`; the deploy passes `--site` and `--base`.
- Fonts (Inter, Space Grotesk for the logo, IBM Plex Mono) come from Astro's font API in `astro.config.ts`.
- `npm run build` runs `astro check` before building; `npm run lint` runs ESLint.
