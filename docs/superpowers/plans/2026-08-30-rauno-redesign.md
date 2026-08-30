# Rauno-Style Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `index.html` as a single-file, dark-only, Rauno-style boxed-column site with hash-routed project subpages, the existing marble shader constrained to viewport edges with vibranium-purple accents, and a cursor spotlight sharing the same accent token.

**Architecture:** One HTML file, one `<script>` block: `SITE` content literal → render functions (`renderHome()`, `renderProject(slug)`) → hash router swapping `#view` innerHTML with eased transitions. WebGL shader and spotlight live outside the router and persist across views.

**Tech Stack:** Vanilla HTML/CSS/JS, WebGL1 fragment shader (existing simplex-noise marble), no frameworks, no build step, no external requests.

## Global Constraints

- Single `index.html`; no new files except this plan/spec (spec: "Single `index.html`, no framework, no build step").
- Dark only: `--bg: #050505`, `--panel: rgba(8,8,10,0.72)`, `--border: rgba(255,255,255,0.08)`, `--text: #ededf0`, `--muted: #9b9ba3`, `--accent: #8B5CF6`, `--accent-deep: #5B21B6`, `--ease: cubic-bezier(0.2, 0, 0, 1)`.
- Type: system UI stack for prose; `ui-monospace` for indices/dates/years/tags.
- No external font/CDN requests anywhere.
- Column: `max-width: 680px`, `padding-inline: 24px`; box gaps ~96px.
- Every hover state has an identical `:focus-visible` twin; `prefers-reduced-motion: reduce` disables reveals/easing/slides.
- Dropped entirely: coin, Three.js import, auth/admin, localStorage data system, light theme.
- Media paths must match files that exist under `assets/` (checkpoint commit `7a2d7f3` has them all).
- Verification baseline for every task: `node --check` on the extracted script block passes; no console errors in the browser.
- Commit after every task (not pushed).

**Old-content source:** `git show 7a2d7f3:index.html` — the `DEFAULTS` literal (projects, achievements, skills) and `<head>` meta tags migrate from there.

---

### Task 1: Stage — skeleton, tokens, edge-constrained shader, spotlight

**Files:**
- Modify: `index.html` (full rewrite of the file)

**Interfaces:**
- Produces: `<main id="view">` (router mount point), `<canvas id="bgCanvas">`, `<div id="spotlight">`, CSS tokens per Global Constraints, `initBackground()` and `initSpotlight()` IIFEs that later tasks never touch.

- [ ] **Step 1: Rewrite `index.html` as the empty stage.** Head: keep charset/viewport/description/OG meta + favicon from `git show 7a2d7f3:index.html`; new `<title>Malek Hassan</title>`. Body: `bgCanvas`, `spotlight`, `<header class="site-head">` (name left; `Projects / Milestones / Contact` anchor links right), empty `<main id="view">`, `<footer>© 2026 Malek Hassan · built by hand, one file</footer>`. All CSS inline in one `<style>`: tokens, reset, column layout, `.box` (panel bg, border, radius 16, padding 36px), reveal/hover/focus rules, reduced-motion block, `(hover: none)` hides spotlight.

- [ ] **Step 2: Port the shader with edge field + accent.** Copy the marble IIFE from `7a2d7f3`, add uniforms `u_accent` (vec3 from `--accent` hex, parsed at init) and `u_band` (float px: `Math.min(180, innerWidth < 720 ? 90 : 180) * dpr`). In `main()` after `lines` is computed:

```glsl
float edgeDist = min(min(gl_FragCoord.x, u_res.x - gl_FragCoord.x),
                     min(gl_FragCoord.y, u_res.y - gl_FragCoord.y));
float edgeFactor = 1.0 - smoothstep(0.0, u_band, edgeDist);
lines *= edgeFactor;
float shimmer = 0.35 + 0.65 * snoise(warp * 2.0 + t * 0.3);
vec3 veinCol = mix(vein, u_accent, clamp(edgeFactor * shimmer, 0.0, 0.55));
vec3 col = mix(bg, veinCol, lines);
```

  `u_band` re-uploaded in `resize()`. WebGL-unavailable fallback: hide canvas, add class `no-gl` on `<html>`; CSS paints `body.no-gl::before` fixed inset radial-gradient purple edge vignette.

- [ ] **Step 3: Spotlight.** Fixed div, `z-index` above canvas / below content, `pointer-events:none`; JS rAF loop lerps `pos += (target - pos) * 0.12`, writes `--mx/--my`; CSS `background: radial-gradient(600px circle at var(--mx) var(--my), rgba(139,92,246,0.12), transparent 70%)`. Under reduced motion, write target directly (no lerp).

- [ ] **Step 4: Verify.** Extract script blocks → `node --check` each (same python snippet used previously). Serve `python3 -m http.server` + headless screenshot at 1440×900 and 390×844: veins visible only at edges with purple shimmer, center clean, spotlight follows cursor (screenshot after synthetic mousemove), zero console errors.

- [ ] **Step 5: Commit** `git add index.html && git commit -m "Rebuild stage: edge-constrained weave, vibranium spotlight, boxed-column shell"`

### Task 2: Content — the `SITE` literal

**Files:**
- Modify: `index.html` (top of the main script block)

**Interfaces:**
- Produces: `const SITE = { intro: {name, role, bio, links[]}, projects: [{slug, title, tag, year, oneLiner, paragraphs[], media[], stack[], github, demo}], milestones: [{date, title, oneLiner, media?}], skills: [{area, items[]}], contact: {email, github, linkedin, cv} }`.

- [ ] **Step 1: Migrate content.** From `git show 7a2d7f3:index.html` `DEFAULTS`: all 10 projects in row order `mozcode, followcam, offerprofi, contexta, oracle, second-brain, finance-wizz, solana-arb-bot, portfolio, hustlr`. `paragraphs[]` = existing description split at sentence boundaries into 2–3 paragraphs, enriched from the matching achievement text where richer (FollowCam, Offerprofi, Second Brain). `stack[]` = authored from each "Stack:" sentence. `oneLiner` = first clause of the description, ≤ 90 chars, hand-trimmed. Milestones = the 10 achievements (dates as `2026-08` style where known, else year), commit-log film media on the first one. Skills grouped into `Frontend / Backend & AI / Systems & DevOps` from the old skills list. Bio = spec draft verbatim. Contact: email `malek.korashi@gmail.com`, GitHub `Malek1414`, LinkedIn URL from old head/meta if present, CV `output/pdf/Malek_Hassan_CV.pdf` — confirm path is tracked; else `CV.pdf`.

- [ ] **Step 2: Verify data invariants.** `node` one-liner: 10 projects, slugs unique and matching `^[a-z0-9-]+$`, every `media[].src`/`poster` exists on disk (`fs.existsSync`), every project has ≥1 paragraph and ≥1 stack item.

- [ ] **Step 3: Commit** `git commit -am "Add SITE content literal: 10 projects, milestones, skills, contact"`

### Task 3: Home view

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `SITE`.
- Produces: `renderHome(): string` (innerHTML for `#view`), `mountHome()` (calls reveal observer + wires rows); project rows are `<a class="row" href="#/<slug>">`.

- [ ] **Step 1: Implement `renderHome()`** — five `.box` sections per spec: Intro (h1 name, role line, bio, quiet links), Projects (rows: `<span class="idx">01</span><span class="row-body"><span class="row-title">MOZCODE</span><span class="row-sub">one-liner</span></span><span class="row-year">2026</span><span class="row-arrow">→</span>`), Milestones (film `<video>` `preload="none"` poster + click-to-play at top, then timeline rows: mono date · title · one-liner), Skills (inline cluster paragraphs `area — item · item · item`), Contact (email headline `<a>`, then GitHub / LinkedIn / CV row).

- [ ] **Step 2: Interaction CSS** per spec table: row hover/focus-visible → `background: rgba(139,92,246,0.06)`, title→`--text`, arrow `translateX(4px)`, idx→`--accent`, all 200ms `--ease`; box border warms to `rgba(139,92,246,0.25)` on hover (300ms); link underlines draw in 180ms; IntersectionObserver reveal (threshold .15, once): `opacity 0→1`, `translateY(8px)→0`.

- [ ] **Step 3: Verify.** Screenshots 1440/390: column centered, boxes distinct, film poster renders, rows align, hover state screenshot (synthetic), tab-through shows focus rings mirroring hover. `node --check` clean.

- [ ] **Step 4: Commit** `git commit -am "Home view: intro, project rows, milestones with film, skills, contact"`

### Task 4: Router + project detail views

**Files:**
- Modify: `index.html`

**Interfaces:**
- Consumes: `SITE`, `renderHome()/mountHome()`.
- Produces: `renderProject(slug): string`, `router()` bound to `hashchange` + load; `homeScrollY` module-level save/restore.

- [ ] **Step 1: Router.** Parse `location.hash`: `''`/`#/` → home; `#/<slug>` found in SITE → detail; unknown → `location.replace('#/')`. On navigate away from home: store `homeScrollY = scrollY`. Swap: add `.leaving` to `#view` (150ms fade/`translateY(-6px)`), then replace innerHTML, add `.entering` (250ms fade/rise, `--ease`), then restore scroll (home: `scrollTo(0, homeScrollY)` instant; detail: top). `document.title = 'Malek Hassan — <Title>'` on detail, `'Malek Hassan'` on home. Reduced motion: skip classes, swap instantly.

- [ ] **Step 2: `renderProject(slug)`** per spec: `← Index` back link (`href="#/"`), h1 title, mono tag+year line, paragraphs, media gallery (video: `preload="none"`, poster, `controls`, portrait items get `.portrait` class using existing `aspect`/`fit` hints; images: `loading="lazy"`), stack chips row, GitHub/demo buttons (only when non-empty), prev/next footer rows (wrap-around, same `.row` style).

- [ ] **Step 3: Verify routes.** Headless: load `/#/followcam` directly (detail renders), navigate home→mozcode→back (scroll position restored exactly), unknown `#/nope` lands home, refresh on `#/hustlr` stays on hustlr, portrait media contained. Screenshots: MOZCODE (text-only project), HUSTLR (portrait media), one prev/next footer.

- [ ] **Step 4: Commit** `git commit -am "Hash router and project detail views with scroll restore"`

### Task 5: Polish, accessibility, final sweep

**Files:**
- Modify: `index.html`

- [ ] **Step 1: A11y pass.** Landmarks in place; single h1 per view; `::selection { background: rgba(91,33,182,0.4) }`; verify muted-on-panel contrast ≥ 4.5:1 (`#9b9ba3` on `#08080a` ≈ 7.9:1 — confirm computed); skip-to-content link; `aria-current` on header anchors while home.

- [ ] **Step 2: Reduced-motion + no-GL passes.** Toggle `prefers-reduced-motion` emulation: no reveals/slides/eased spotlight, instant swaps. Force `no-gl` class: CSS vignette shows.

- [ ] **Step 3: Full verification sweep** (spec §Verification): `node --check`; screenshots 1440/390 of home + 2 details; route battery from Task 4 re-run; console clean; no external requests in network log; `git grep -c 'PASS_HASH\|localStorage\|signatureCoin' index.html` → 0 matches.

- [ ] **Step 4: Commit** `git commit -am "Polish: a11y, reduced motion, no-GL fallback, final sweep"`

## Self-review notes

- Spec coverage: layout/boxes (T1/T3), bio (T2), rows+hover table (T3), router/subpages/scroll-restore (T4), shader edge+accent (T1), spotlight (T1), tokens/type (T1), dropped-features check + a11y + reduced motion + verification (T5). No gaps found.
- Names used consistently: `SITE`, `renderHome`, `mountHome`, `renderProject`, `router`, `homeScrollY`, `#view`, `.row`, `.box`.
- No TBDs; GLSL and interaction values are exact.
