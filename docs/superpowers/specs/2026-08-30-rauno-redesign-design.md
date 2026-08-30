# Personal Site Redesign — Rauno-Style Column, Edge Weave, Vibranium Spotlight

**Date:** 2026-08-30
**Status:** Approved design, pending spec review
**Repo:** Malek1414/Malek1414.github.io (`index.html`, GitHub Pages)

## Goal

Rebuild the personal site around three references, fused:

1. **rauno.me** — centered narrow column, sections as distinct boxes with generous
   space, obsessive hover/transition detail.
2. **The existing site's WebGL "luminous marble" background** — kept, but constrained
   to the viewport edges so it frames the page instead of competing with it.
3. **brittanychiang.com's cursor spotlight** — a radial glow that follows the mouse,
   recolored to a Black-Panther vibranium purple that also tints the edge weave, so
   cursor and frame read as one system.

## Locked decisions

| Decision | Choice |
|---|---|
| Scroll model | Rauno-faithful: centered column, normal scrolling, boxed sections |
| Project details | In-file hash-routed subpages (`#/mozcode`), back-button restores scroll |
| Admin/edit mode | **Dropped** (auth, localStorage data system, GitHub importer all removed) |
| Theme | Dark only, no toggle |
| File structure | Single `index.html`, no framework, no build step |
| Rebuild strategy | Fresh rewrite; carry over only shader, content, media paths, meta tags |
| Safety | Checkpoint-commit current working tree before the rewrite begins |

## Dropped from the current site

Rotating signature coin (and the Three.js vendor import that serves it), password
gate + SHA-256 auth, admin edit UI and all edit buttons, localStorage
DATA_VERSION machinery, GitHub repo importer, light theme, guest-mode logic.
Content survives; chrome does not.

## Architecture

One `index.html` containing:

- `<canvas id="bgCanvas">` — modified marble shader (see Background).
- `<div id="spotlight">` — cursor-following radial glow (see Spotlight).
- `<header>` — name left; right side: `Projects / Milestones / Contact` anchors
  (scroll on home; navigate-home-then-scroll from a detail view).
- `<main id="view">` — swapped by the router between the **home view** and a
  **project detail view**.
- One `<script>` block: content data, router, renderers, interactions, shader.

### Content data

A single `const SITE = { intro, projects[], milestones[], skills[], contact }`
literal — the current `DEFAULTS` content migrated verbatim (descriptions, media
paths, GitHub/demo links), plus per-project `slug` and the fields the detail view
needs. No persistence layer; editing the site = editing this literal.

Project slugs (row order on home):
`mozcode, followcam, offerprofi, contexta, oracle, second-brain, finance-wizz,
solana-arb-bot, portfolio, hustlr`.

### Router

- `#/` (or empty) → home. `#/<slug>` → project detail. Unknown slug → home.
- `hashchange` + initial load dispatch. `document.title` updates per view.
- Leaving home stores `scrollY`; returning restores it after render (no smooth
  scroll on restore). Detail views open scrolled to top.
- View swap animation: outgoing view fades/translates out (150ms), incoming
  fades/rises in (250ms, `cubic-bezier(0.2, 0, 0, 1)`). Under
  `prefers-reduced-motion: reduce`, swaps are instant.

## Layout — home view

- Column: `max-width: 680px`, centered, `padding-inline: 24px`.
- Section boxes: `border: 1px solid rgba(255,255,255,0.08)`, `border-radius: 16px`,
  background `rgba(8,8,10,0.72)` (translucent near-black so the weave never bleeds
  through content), inner padding ~32–40px, ~96px gaps between boxes.
- Sections, in order:
  1. **Intro** — name, one-line role, the bio (below), quiet links (GitHub,
     LinkedIn, email, CV). No photo, no coin.
  2. **Projects** — Rauno-style rows, whole row is a link to the detail view:
     monospace index (`01`), title, one-line description, monospace year,
     arrow glyph. No thumbnails on home; media lives in detail views.
  3. **Milestones** — compact timeline rows: monospace date, title, one-liner.
     The commit-log film (`assets/demos/commit-log-journey.mp4`) is embedded at
     the top of this box as the only media element on the home page.
  4. **Skills** — one paragraph-style inline cluster grouped by area
     (`TypeScript · Python · Swift — …`), not a chip grid.
  5. **Contact** — email as the headline action, then GitHub / LinkedIn / CV.
- Footer line outside the last box: `© 2026 Malek Hassan · built by hand, one file`.

### Bio (Intro copy — approved draft, final wording editable at spec review)

> I'm Malek Hassan. I build AI systems that ship — not demos. Six months ago I
> was studying in Aachen; since then I've open-sourced a context engine, moved
> to Berlin for CODE University, sold software in a week at SummerUP, and won a
> hackathon with a €20 robot cameraman. I like local-first tools, deterministic
> guardrails around AI, and commit logs that read like a story.

## Layout — project detail view

Same 680px column. Contents, top to bottom:

1. Back link (`← Index`) — returns to home, restores scroll.
2. Title (large), tag + year in monospace.
3. Long description — the existing per-project copy, split into readable
   paragraphs (source: current `DEFAULTS.projects[].description` +, where the
   matching achievement has richer copy, that text).
4. Media gallery — the project's existing `media[]` (mp4 with poster, images);
   portrait media uses `aspect`/`fit` hints as today; lazy-loaded,
   `preload="none"`, click-to-play with poster.
5. Stack — chips row from an authored `stack: []` array per project in `SITE`
   (populated once during the rewrite from each description's "Stack:" sentence;
   no runtime string parsing).
6. Links — GitHub / live demo buttons where present.
7. Prev / next project footer (wraps around), same row style as home.

## Background — edge-constrained weave

Modify the existing fragment shader (keep the simplex noise + band field):

- New uniform `u_accent` (vec3, set from `--accent` at init).
- **Edge field:** compute distance to the nearest viewport edge in pixels;
  `edgeFactor = 1.0 - smoothstep(0.0, u_band, minEdgeDist)` where `u_band`
  ≈ 180px (scaled by DPR; reduced to ~90px under 720px viewport width).
  Multiply `lines` by `edgeFactor` — veins at full strength at the edges and
  corners, zero behind the column.
- **Purple accent:** near the edges, lerp vein color from the current grey
  toward `u_accent`, weighted by `edgeFactor * shimmer`, where
  `shimmer = 0.35 + 0.65 * snoise(warp * 2.0 + t * 0.3)` — a slow, living
  purple that never fully saturates (cap the lerp at ~0.55).
- Everything else (grain, animation speed, resolution handling) unchanged.
- If WebGL is unavailable: canvas hides; a static CSS fallback paints a faint
  purple edge vignette (`radial-gradient` insets) so the frame idea survives.

## Cursor spotlight (Brittany technique, Rauno easing)

- Fixed, full-viewport, `pointer-events: none` div above the canvas, below content:
  `background: radial-gradient(600px circle at var(--mx) var(--my),
  rgba(139,92,246,0.12), transparent 70%)`.
- Position eased in a rAF loop: `pos += (target - pos) * 0.12` — the glow trails
  the cursor slightly instead of sticking to it.
- Hidden on touch-only devices (`(hover: none)`) and under reduced motion the
  easing is dropped (glow still renders, positioned directly).

## Design tokens

```css
--bg: #050505;          --panel: rgba(8,8,10,0.72);
--border: rgba(255,255,255,0.08);
--text: #ededf0;        --muted: #9b9ba3;
--accent: #8B5CF6;      /* vibranium glow — spotlight, hovers, shader uniform */
--accent-deep: #5B21B6; /* borders, active states, selection */
--ease: cubic-bezier(0.2, 0, 0, 1);
```

Type: system UI stack for prose (`-apple-system, Inter, Segoe UI, sans-serif`);
`ui-monospace / SF Mono` for indices, dates, years, tags — the commit-log motif.
Selection color: `--accent-deep` at 40%. No external font requests.

## Interaction spec (the Rauno layer)

| Element | Rest | Hover / focus-visible |
|---|---|---|
| Section box | border `--border` | border-color warms to `rgba(139,92,246,0.25)` (300ms) |
| Project row | muted title, dim arrow | 6% `--accent` wash, title → `--text`, arrow slides 4px right, index turns `--accent` (200ms, `--ease`) |
| Inline link | underline transparent | underline draws in left→right (180ms) |
| Buttons (GitHub/demo) | 1px border | background `--accent-deep` 20%, slight rise (2px) |
| Back link | muted | arrow slides 3px left, text brightens |

- Scroll reveal: each box starts `opacity: 0; translateY(8px)`, transitions in
  once via IntersectionObserver (threshold 0.15). Runs once per page load.
- Every hover state has an identical `:focus-visible` twin.
- `prefers-reduced-motion: reduce`: no reveals, no eased spotlight, instant
  view swaps, no arrow slides — color changes only.

## Accessibility & semantics

Landmarks (`header/main/footer`, `nav`), one `h1` per view, project rows are
real `<a href="#/slug">` elements, all media has captions/alt, contrast ≥ 4.5:1
for text on `--panel` (muted grey checked against panel color), keyboard path
covers every interactive element in visual order.

## Verification

1. `node --check` on the extracted script block.
2. Local server + screenshots: 1440px and 390px widths; home, one landscape-media
   detail (MOZCODE), one portrait-media detail (HUSTLR).
3. Route tests: direct load of `#/followcam`, unknown slug, back-button scroll
   restore, browser refresh on a detail view.
4. Shader: verify veins are invisible behind the column at 1440px and 390px;
   edge band visibly purple-shimmering; fallback path (WebGL disabled) shows CSS
   vignette.
5. Reduced-motion pass with the macOS setting enabled.
6. Video elements: poster shows, nothing autoplays except intended, no console
   errors.

## Rollback

Checkpoint commit of the pre-rewrite working tree happens before any rewrite
edits. The old design remains recoverable via `git checkout <checkpoint> -- index.html`.
