# Demo media

Drop project/achievement demo recordings here. The site shows them as
autoplaying, muted, looping frames at the top of each card (RobertHQ style),
and quietly hides the frame if a file isn't present yet.

## Expected files (already wired in `index.html`)

- `oracle.mp4` + `oracle.jpg` — ORACLE demo loop and its poster frame
- `finance-wizz.mp4` + `finance-wizz.jpg` — finance-wizz demo loop and poster

The `.jpg` poster is the frozen frame shown before the video loads. It's
optional but makes the first paint look intentional.

## Recording tips

- Record the app actually working, then trim to a short loop (8–20s).
- Export `.mp4` (H.264) for broad support; `.webm` also works.
- Keep clips small — a few MB each — so cards stay fast. No audio needed.
- Roughly 16:10 framing fills the card cleanly; other ratios are cropped.

## Other formats

- `.gif` works too (loops on its own, no poster needed).
- A static screenshot (`.jpg` / `.png`) shows as a frozen frame — a fine
  fallback when you don't have a recording yet.

## Adding more

For any other project or achievement, log in as admin and use the
Demo Media / Poster / Caption fields in the edit dialog. You can paste a
path like `assets/demos/clip.mp4` or a full `https://` URL.
