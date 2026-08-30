# Me Gallery + Demo Drop-Folder Pathway Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `#/me` page with an animated basketball/gym/life photo gallery, restore the orphaned Loon Link project so its testimonial renders, and create a testimonials-style drop-folder pathway for future project demos.

**Architecture:** Everything stays in the single-file `index.html` (SITE literal + renderers + hash router). New assets land in `assets/me/` and `assets/demos/projects/`. Two small repo scripts (`verify_site.mjs`, `sync_demos.sh`) make the invariants and the demo pathway repeatable.

**Tech Stack:** Vanilla HTML/CSS/JS (single file), bash + node scripts, ffmpeg/sips for image processing.

## Global Constraints

- Existing project media and testimonial wiring must not change paths or captions.
- Purple accent `#8B5CF6` / `--accent`, monospace eyebrows, `.box`/`.reveal` patterns — reuse, don't invent.
- Published photos: max edge 1600px, metadata stripped (`ffmpeg -map_metadata -1`).
- `prefers-reduced-motion` must keep working (reveals appear instantly).
- All content escaped through `esc()` as elsewhere.

---

### Task 1: Verify script + demo drop-folder pathway

**Files:**
- Create: `scripts/verify_site.mjs`
- Create: `scripts/sync_demos.sh`
- Create: `assets/demos/projects/README.md`

**Interfaces:**
- Produces: `node scripts/verify_site.mjs` (exit 0 = inline JS parses + every referenced `assets/`/`output/` path exists); `bash scripts/sync_demos.sh` (prints wired/unwired demo files + ready-to-paste media entries).

- [ ] **Step 1: Write `scripts/verify_site.mjs`**

```js
// Site invariants: every inline <script> parses; every referenced local asset exists.
import fs from 'node:fs';
const html = fs.readFileSync('index.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
if (!scripts.length) { console.error('FAIL: no inline scripts found'); process.exit(1); }
for (const s of scripts) new Function(s); // parse only; throws SyntaxError on bad JS
const refs = new Set(
  [...html.matchAll(/['"](assets\/[^'"]+|output\/[^'"]+)['"]/g)].map(m => m[1])
);
let missing = 0;
for (const a of refs) if (!fs.existsSync(a)) { console.error('MISSING: ' + a); missing++; }
if (missing) process.exit(1);
console.log(`OK: JS parses, ${refs.size} referenced assets exist`);
```

- [ ] **Step 2: Run it against the current site — must pass before anything changes**

Run: `cd /Users/malekhassan/Desktop/personalwebsite && node scripts/verify_site.mjs`
Expected: `OK: JS parses, N referenced assets exist`

- [ ] **Step 3: Write `scripts/sync_demos.sh`**

```bash
#!/usr/bin/env bash
# Testimonials-style pathway for new project demos:
# drop an .mp4/.mov/.webm (or a .png/.jpg still) into assets/demos/projects/<project-slug>/,
# run this script, then paste the printed entry into that project's media[] in index.html.
set -euo pipefail
cd "$(dirname "$0")/.."
root="assets/demos/projects"
found=0
shopt -s nullglob
for f in "$root"/*/*; do
  [ -f "$f" ] || continue
  slug="$(basename "$(dirname "$f")")"
  case "$f" in
    *.mp4|*.mov|*.webm)
      poster="${f%.*}.jpg"
      if [ ! -f "$poster" ]; then
        ffmpeg -y -loglevel error -ss 1 -i "$f" -frames:v 1 -q:v 3 "$poster"
        echo "poster made: $poster"
      fi
      entry="{ src: '$f', caption: 'TODO — describe the demo', poster: '$poster' }" ;;
    *.png|*.jpeg|*.webp)
      entry="{ src: '$f', caption: 'TODO — describe the still' }" ;;
    *.jpg)
      base="${f%.*}"; skip=0
      for ext in mp4 mov webm; do [ -f "$base.$ext" ] && skip=1; done
      [ "$skip" = 1 ] && continue   # it's a poster for a video, not a standalone still
      entry="{ src: '$f', caption: 'TODO — describe the still' }" ;;
    *) continue ;;
  esac
  found=1
  if grep -qF "$f" index.html; then
    echo "wired:   $f"
  else
    echo "UNWIRED: $f  →  add to media[] of project '$slug':"
    echo "         $entry"
  fi
done
[ "$found" = 1 ] || echo "No demos yet. Drop files into $root/<project-slug>/ and re-run."
```

- [ ] **Step 4: Write `assets/demos/projects/README.md`**

```markdown
# Project demo drop-folder

Same pathway as `../testimonials`, but organized per project:

1. Drop a demo (`.mp4`, `.mov`, `.webm`) or still (`.png`/`.jpg`) into `assets/demos/projects/<project-slug>/`
   (slug = the project's `slug` in `index.html`, e.g. `mozcode`, `contexta`, `oracle`).
2. Run `bash scripts/sync_demos.sh` — it generates a poster frame for every new video and prints
   the exact `media:` entry to paste into that project's `media: [...]` array in `index.html`.
3. Edit the `caption`, run `node scripts/verify_site.mjs`, commit, push.
```

- [ ] **Step 5: Test the pathway end-to-end with a scratch file**

```bash
mkdir -p assets/demos/projects/mozcode
cp assets/demos/hustlr-dark-demo.mp4 assets/demos/projects/mozcode/tmp-test.mp4
bash scripts/sync_demos.sh   # expect: poster made + UNWIRED entry printed
rm assets/demos/projects/mozcode/tmp-test.mp4 assets/demos/projects/mozcode/tmp-test.jpg
bash scripts/sync_demos.sh   # expect: "No demos yet..." (folder now empty)
```

- [ ] **Step 6: Keep empty slug dirs out of git but keep the README**

Git ignores empty dirs automatically — only `README.md` gets committed; nothing extra needed.

- [ ] **Step 7: Commit**

```bash
git add scripts/verify_site.mjs scripts/sync_demos.sh assets/demos/projects/README.md
git commit -m "Add site verify script and testimonials-style demo drop-folder pathway"
```

---

### Task 2: Restore Loon Link project (re-wires orphaned testimonial)

**Files:**
- Modify: `index.html` (SITE.projects array — insert after the `solana-arb-bot` entry, ~line 369; SITE.intro.log ~line 281; og:description meta ~line 9)

**Interfaces:**
- Consumes: existing `mediaFigure`, `renderProject`, router (no changes needed — new slug routes automatically).
- Produces: project slug `loon-link` reachable at `#/loon-link`.

- [ ] **Step 1: Insert the project entry after the solana-arb-bot object**

```js
    { slug: 'loon-link', title: 'Loon Link', tag: 'Web / Intelligence', year: '2025',
      oneLiner: 'Point it at a URL — get back the company behind it.',
      paragraphs: [
        'A company-intelligence crawler. Point it at any URL, choose a crawl depth, and Loon Link spiders the site and returns a clean profile — contact emails, phone numbers, social links, the detected front-end tech stack, and a typed map of every page it found. Crawled companies are saved to revisit anytime.'
      ],
      stack: ['Java', 'Spring Boot', 'Vue 3', 'REST API'],
      github: '', demo: '',
      media: [ { src: 'assets/demos/testimonials/loon-link-testimonial.mp4', caption: 'Apple scrape walkthrough', poster: 'assets/demos/testimonials/loon-link-testimonial.png' } ] },
```

- [ ] **Step 2: Update the two "ten projects" counts**

- `SITE.intro.log`: `'783 commits Mar—Aug 2026 · 11 projects'`
- og:description meta: `"AI systems engineer in Berlin. Eleven projects, one commit log."`

- [ ] **Step 3: Verify**

Run: `node scripts/verify_site.mjs`
Expected: OK (poster + mp4 already exist in assets/demos/testimonials/).

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Restore Loon Link project; re-wire its testimonial reel"
```

---

### Task 3: Curate basketball / gym / life photos into assets/me/

**Files:**
- Create: `assets/me/*.jpg` (~18–28 photos)
- Create (scratch, not committed): contact sheets + manifest in the session scratchpad

**Interfaces:**
- Produces: web-ready JPGs named `me-NN-<word>.jpg` (e.g. `me-01-hoops.jpg`), max edge 1600px, EXIF/GPS stripped. A picks list (path + one-line caption + `tall` flag for portraits) handed to Task 4.

- [ ] **Step 1: Build candidate list + thumbnails (scratchpad)**

```bash
S=/private/tmp/claude-501/-Users-malekhassan-Desktop/4fdc0f84-6d68-4f76-b305-bcbf755425e0/scratchpad
mkdir -p "$S/thumbs" "$S/sheets"
i=0
find /Users/malekhassan/Pictures -maxdepth 1 -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.heic' \) | sort | while read -r f; do
  n=$(printf '%05d' $i)
  sips -s format jpeg --resampleHeightWidthMax 220 "$f" --out "$S/thumbs/$n.jpg" >/dev/null 2>&1 && echo "$n $f" >> "$S/manifest.txt"
  i=$((i+1))
done
wc -l "$S/manifest.txt"
```

- [ ] **Step 2: Tile into contact sheets (8×8 = 64 thumbs/sheet, index order)**

```bash
cd "$S"
ffmpeg -y -loglevel error -pattern_type glob -framerate 1 -i 'thumbs/*.jpg' \
  -vf "scale=220:220:force_original_aspect_ratio=decrease,pad=220:220:(ow-iw)/2:(oh-ih)/2:color=black,tile=8x8" \
  -vsync vfr 'sheets/sheet-%03d.png'
ls sheets | wc -l
```

Sheet `sheet-K.png` position (row r, col c, 0-based) = manifest index `(K-1)*64 + r*8 + c`.

- [ ] **Step 3: View every sheet, shortlist basketball / gym / life shots**

Read each `sheets/sheet-*.png`, record shortlisted manifest indices. Target ~50–70 shortlist.

- [ ] **Step 4: View shortlisted originals individually, final-pick ~18–28**

Convert each shortlisted original to a quick 800px preview (`sips`), Read it, keep the strong ones.
Selection rules: mostly solo shots of Malek; no documents/IDs/screens with text; mix of basketball,
gym, and life/travel; prefer variety of settings. Note portrait vs landscape for the `tall` flag.

- [ ] **Step 5: Process picks into assets/me/**

```bash
mkdir -p assets/me
# per pick (example):
sips -s format jpeg --resampleHeightWidthMax 1600 "$ORIGINAL" --out "$S/stage.jpg" >/dev/null
ffmpeg -y -loglevel error -i "$S/stage.jpg" -map_metadata -1 -q:v 3 "assets/me/me-01-hoops.jpg"
```

Then confirm zero EXIF/GPS survives: `ffprobe -v quiet -show_entries format_tags assets/me/*.jpg` → empty.

- [ ] **Step 6: Commit**

```bash
git add assets/me
git commit -m "Add curated basketball/gym/life photos for the Me page (EXIF-stripped, web-sized)"
```

---

### Task 4: Me page — nav tab, route, animated gallery

**Files:**
- Modify: `index.html` — CSS (after the `/* ── project detail ── */` block), nav (~line 262), `SITE` literal (add `me:` after `intro:`), renderers (add `renderMe` after `renderProject`), router (`routeTarget`, `applyRoute`)

**Interfaces:**
- Consumes: Task 3's picks list; existing `esc()`, `mountHome()` (wires any `.reveal`), `.box`/`.para`/`.eyebrow`/`.back` styles.
- Produces: `#/me` route; nav link `me`.

- [ ] **Step 1: Add gallery CSS**

```css
  /* ── me gallery ── */
  .gallery { display: grid; grid-template-columns: repeat(2, 1fr); grid-auto-rows: 150px; grid-auto-flow: dense; gap: 14px; margin-top: 26px; }
  .gcell { position: relative; grid-row: span 2; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: #000; margin: 0; }
  .gcell.tall { grid-row: span 3; }
  .gcell img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 600ms var(--ease); }
  .gcell::after { content: ""; position: absolute; inset: 0; background: linear-gradient(to top, rgba(5,5,5,0.6), transparent 45%); opacity: 0; transition: opacity 300ms var(--ease); }
  .gcell:hover img { transform: scale(1.04); }
  .gcell:hover::after { opacity: 1; }
  .gcell .gcap { position: absolute; left: 12px; bottom: 10px; z-index: 1; font: 400 11.5px var(--mono); color: var(--text); opacity: 0; transform: translateY(4px); transition: opacity 300ms var(--ease), transform 300ms var(--ease); }
  .gcell:hover .gcap, .gcell:focus-within .gcap { opacity: 1; transform: none; }
  @media (max-width: 720px) { .gallery { grid-auto-rows: 110px; gap: 10px; } }
```

And inside the existing `@media (prefers-reduced-motion: reduce)` block:

```css
    .gcell img, .gcell::after, .gcell .gcap { transition: none; }
    .gcell:hover img { transform: none; }
```

- [ ] **Step 2: Add nav link (before contact)**

```html
    <a href="#projects">projects</a>
    <a href="#milestones">milestones</a>
    <a href="#/me">me</a>
    <a href="#contact">contact</a>
```

- [ ] **Step 3: Add `me:` to SITE (right after `intro: {...},`)** — captions come from Task 3 picks

```js
  me: {
    title: 'Off the keyboard',
    paragraphs: [
      "The commit log is half the story. I play basketball — pickup runs and league games, the same footage FollowCam was built to film — and I'm in the gym most mornings before the first commit of the day.",
      "The rest: Cairo to Aachen to Berlin, building things with friends, and a camera roll that fills up about as fast as the git log."
    ],
    gallery: [
      { src: 'assets/me/me-01-hoops.jpg', caption: 'league night', tall: true }
      // ... one entry per Task 3 pick, captions written from what's in the photo
    ]
  },
```

- [ ] **Step 4: Add `renderMe()` after `renderProject()`**

```js
function renderMe() {
  const paras = SITE.me.paragraphs.map(p => `<p class="para">${esc(p)}</p>`).join('');
  const g = SITE.me.gallery.map((ph, i) => `
    <figure class="gcell${ph.tall ? ' tall' : ''} reveal" style="transition-delay:${(i % 6) * 60}ms">
      <img loading="lazy" src="${esc(ph.src)}" alt="${esc(ph.caption)}">
      <figcaption class="gcap">${esc(ph.caption)}</figcaption>
    </figure>`).join('');
  return `
  <article class="box" aria-label="Me">
    <a class="back" href="#/"><span class="arr" aria-hidden="true">←</span> Index</a>
    <span class="eyebrow"><span class="tilde">~/</span>me</span>
    <h1>${esc(SITE.me.title)}</h1>
    ${paras}
    <div class="gallery">${g}</div>
  </article>`;
}
```

- [ ] **Step 5: Route it**

In `routeTarget()`, before the project lookup:

```js
  if (raw === '#/me') return { kind: 'me' };
```

In `applyRoute()`:
- scroll bookkeeping: `if (currentKind === 'home' && (t.kind === 'project' || t.kind === 'me')) homeScrollY = scrollY;`
- in `swap()`, add a branch before the project else:

```js
    } else if (t.kind === 'me') {
      view.innerHTML = renderMe();
      mountHome(); // wires .reveal observers (respects reduced motion)
      document.title = 'Malek Hassan — Me';
      requestAnimationFrame(() => scrollTo({ top: 0, left: 0, behavior: 'instant' }));
      currentKind = 'me';
    } else {
```

- nav highlight: replace the aria-current toggle with

```js
  document.querySelectorAll('.site-head nav a').forEach(a => {
    const me = a.getAttribute('href') === '#/me';
    a.toggleAttribute('aria-current', me ? t.kind === 'me' : t.kind === 'home');
  });
```

- [ ] **Step 6: Verify**

```bash
node scripts/verify_site.mjs
python3 -m http.server 8901 &  # then browser-check #/me, a project page, home; kill server
```

Checks: `#/me` renders grid with staggered reveals; back link restores home scroll; project pages unchanged; mobile width 375px looks right; reduced-motion shows everything instantly.

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "Add Me page: hash-routed animated gallery of basketball/gym/life photos"
```

---

### Task 5: Full verification + deploy

**Files:** none new.

- [ ] **Step 1: Run `node scripts/verify_site.mjs` + `bash scripts/sync_demos.sh`** — both clean.
- [ ] **Step 2: Browser spot-check** (local server): home, `#/me`, `#/loon-link`, `#/followcam`, `#/offerprofi`, `#/second-brain`, `#/finance-wizz`, `#/hustlr` — every video renders with poster + controls.
- [ ] **Step 3: Push to main** (`git push`), wait ~40s, verify https://malek1414.github.io/#/me and one project page live.
