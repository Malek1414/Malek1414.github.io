<p align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/banner-dark.svg">
  <img alt="malek1414.github.io: a smiling pixel basketball dribbling under a hoop with an M on the backboard" src="assets/readme/banner-light.svg" width="100%">
</picture>
</p>

<p align="center">
  <a href="https://malek1414.github.io/"><b>Live site</b></a> &nbsp;·&nbsp;
  <a href="https://malek1414.github.io/resume.html"><b>Resume</b></a> &nbsp;·&nbsp;
  <a href="output/pdf/Malek_Hassan_CV.pdf"><b>CV (PDF)</b></a> &nbsp;·&nbsp;
  <a href="https://github.com/Malek1414"><b>GitHub</b></a>
</p>

<p align="center">
  <img alt="HTML" src="https://img.shields.io/badge/HTML-single_file-e34f26?style=flat-square&logo=html5&logoColor=white">
  <img alt="CSS" src="https://img.shields.io/badge/CSS-hand_written-663399?style=flat-square&logo=css&logoColor=white">
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-no_framework-f7df1e?style=flat-square&logo=javascript&logoColor=black">
  <img alt="GitHub Pages" src="https://img.shields.io/badge/hosted_on-GitHub_Pages-222?style=flat-square&logo=github&logoColor=white">
  <img alt="ffmpeg" src="https://img.shields.io/badge/video-ffmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white">
</p>

**My personal site: who I am, what I've built, and how to reach me.** I'm Malek Hassan, an AI systems engineer in Berlin. The site is one hand-built `index.html` with no framework and no build step, served straight from this repo by GitHub Pages at **https://malek1414.github.io/**.

It opens on a looping court clip, then walks through my projects, skills and contact details. Each project has its own page with its stack, links and demo videos, and there's a "Me" page with a photo gallery from off the keyboard.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/divider-dark.svg">
  <img alt="" src="assets/readme/divider-light.svg" width="100%">
</picture>

## What's on it

| Route | What it shows |
|---|---|
| `#/` | Intro, the project index, skills and contact, each over its own background video loop |
| `#/<slug>` | One project: one-liner, write-up, stack, GitHub and demo links, demo videos, and prev/next links |
| `#/me` | "Off the keyboard": a short bio and the photo gallery |
| `resume.html` | A technical resume page |
| `output/pdf/Malek_Hassan_CV.pdf` | The CV as a PDF, linked from the intro |

## How it works

Everything lives in `index.html`:

- **One data object.** A `SITE` literal holds the intro, the "Me" page, every project (slug, title, tag, year, paragraphs, stack, links, media), the skills and the contact links. Adding a project means adding an entry there.
- **Renderers and a hash router.** `renderHome()`, `renderProject()` and `renderMe()` build the page from `SITE`; the router reads `location.hash` (`#/`, `#/me`, `#/<slug>`) and picks one.
- **Media slots.** A second table maps slots like `bg.intro` or `work.vidbridge` to a video loop, a smaller version for screens under 720 px and a poster frame. A `prefers-reduced-motion` rule calms the page down for people who ask for it.

There is no build step. GitHub Pages serves the `main` branch as it is.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/divider-dark.svg">
  <img alt="" src="assets/readme/divider-light.svg" width="100%">
</picture>

## Scripts

| Script | What it does |
|---|---|
| `node scripts/verify_site.mjs` | Checks that every inline `<script>` parses and every `assets/` or `output/` path referenced in `index.html` exists |
| `bash scripts/sync_demos.sh` | Lists demo files dropped into `assets/demos/projects/<slug>/`, makes a poster for new videos with ffmpeg, and prints a ready-to-paste `media[]` entry |
| `scripts/make-loop.sh <input> <start> <duration> <name> [crop]` | Turns any video into a site loop with ffmpeg: silent, H.264, faststart, two sizes plus a poster. `LUT=assets/grade/cool.cube` grades it with one of the looks in `assets/grade/` |
| `python3 scripts/generate_cv.py` | Builds the one-page CV PDF with ReportLab into `output/pdf/Malek_Hassan_CV.pdf` |
| `scripts/grade_me_gallery.lua` | Run from DaVinci Resolve's console: imports the gallery originals, applies per-scene grades and exports metadata-free JPEG stills |

To look at the site locally, serve the folder and open it in a browser, the same way the plans in `docs/superpowers/` do:

```bash
python3 -m http.server 8901   # then open http://localhost:8901/
node scripts/verify_site.mjs  # inline JS parses, referenced assets exist
```

## Structure

```
index.html            the whole site: styles, SITE data, renderers, router
resume.html           technical resume page
assets/loops/         background video loops (full, -sm, poster)
assets/demos/         project demo videos and stills
assets/me/            "Me" gallery photos
assets/grade/         .cube LUTs used by make-loop.sh
assets/brand/         the M mark and favicon
output/pdf/           generated CV
scripts/              verify, demo, loop, CV and gallery helpers
docs/superpowers/     design specs and plans for past redesigns
```

Large full-length films are kept out of the repo (see `.gitignore`); only `assets/film/intro-web.mp4` is committed.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/readme/divider-dark.svg">
  <img alt="" src="assets/readme/divider-light.svg" width="100%">
</picture>

<p align="center">
  <img alt="" src="assets/readme/logo.svg" width="72"><br>
  <sub>Built by <a href="https://github.com/Malek1414">Malek Hassan</a> in Berlin.</sub>
</p>
