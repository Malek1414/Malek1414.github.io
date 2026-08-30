# Me Gallery + Demo Drop-Folder Pathway — Design

Date: 2026-08-30
Status: Approved (choices confirmed by Malek via Q&A: dedicated Me page; no video, animated grid; Claude curates photos; drop-folder inside the repo)

## Goal

Add a personal "who I am" section to the site — basketball, gym, and life photos —
without touching the existing project pages, and establish a repeatable pathway for
adding future project demo videos, mirroring how the testimonials mp4s were wired.

## Constraints

- Existing per-project demo videos and testimonial mp4s keep rendering exactly as they do today.
- Single-file architecture stays: all content lives in the `SITE` literal in `index.html`, zero external requests beyond assets.
- Visual language stays Rauno-style: boxed 680px column, monospace eyebrows, purple accent `#8B5CF6`, `.reveal` scroll animations.
- Published photos must be EXIF/GPS-stripped and web-sized.

## Design

### 1. Me page (`#/me`)

- Nav gains a `me` link (`#/me`), handled by the existing hash router alongside project slugs.
- New `SITE.me` object:
  - `eyebrow` (git-log style, e.g. `git log --author="malek" --off-hours`),
  - `title`, 1–2 short `paragraphs` (plays basketball currently, trains in the gym, builds things),
  - `gallery`: array of `{ src, caption, portrait? }`.
- `renderMe()` modeled on `renderProject()`: intro box, then an animated photo grid.
- Grid: responsive `grid-template-columns: repeat(auto-fill, minmax(...))`, portrait/landscape aware,
  staggered `.reveal` entrance, hover = subtle scale + purple wash. No lightbox, no video file.
- Home page unchanged except the nav link.

### 2. Photo curation & assets

- Source: `~/Pictures` camera roll (~4.9k files). Curation by contact sheets, picking ~20–30
  basketball / gym / life shots.
- Output: `assets/me/*.jpg` — max edge 1600px, quality ~82, all metadata stripped
  (`-map_metadata -1` / exiftool-free ffmpeg or sips pipeline).
- Each photo gets a short caption in `SITE.me.gallery`.

### 3. Demo drop-folder pathway (testimonials-style)

- New folder: `assets/demos/projects/<project-slug>/` — drop any `.mp4` (or `.png`/`.jpg` still) there.
- New script: `scripts/sync_demos.sh`
  - scans `assets/demos/projects/*/*`,
  - for every mp4 without a sibling poster, extracts a poster frame at 1s via ffmpeg (`<name>.jpg`),
  - prints the ready-to-paste `media:` entry (`{ src, caption: 'TODO', poster }`) per file,
    flagging entries whose `src` is not yet referenced in `index.html`.
- `assets/demos/projects/README.md` documents the convention in three lines.
- No auto-editing of `index.html` — the script prints, the human (or Claude) pastes. Keeps the
  single-file literal authoritative and diff-reviewable.

### 4. Testimonial audit

- Verify every testimonial mp4 in `assets/demos/testimonials/` is referenced by a project.
- Known gap: `loon-link-testimonial.mp4` is unreferenced — check the pre-redesign site
  (commit `7a2d7f3`) for its home (LuneLink apple-scrape demo) and either attach it to the
  right project or note it as intentionally shelved.

## Error handling

- Missing/unloadable images in the gallery: browser default broken-image is unacceptable —
  images get width/height-free `object-fit: cover` containers; if a file 404s the tile still
  renders its caption (graceful, no JS error).
- `sync_demos.sh` is idempotent and safe to re-run; skips existing posters; exits non-zero only
  on ffmpeg failure.

## Testing / verification

- Local: open `index.html` via a local server; check `#/me` route renders, reveals fire, images load;
  check every project page still shows its media (spot-check followcam, offerprofi, second-brain,
  finance-wizz, hustlr).
- `node --check`-style syntax validation of the inline script (extract + parse).
- Deploy to GitHub Pages, verify live.
