# Project demo drop-folder

Same pathway as `../testimonials`, but organized per project:

1. Drop a demo (`.mp4`, `.mov`, `.webm`) or still (`.png`/`.jpg`) into `assets/demos/projects/<project-slug>/`
   (slug = the project's `slug` in `index.html`, e.g. `mozcode`, `contexta`, `oracle`).
2. Run `bash scripts/sync_demos.sh` — it generates a poster frame for every new video and prints
   the exact `media:` entry to paste into that project's `media: [...]` array in `index.html`.
3. Edit the `caption`, run `node scripts/verify_site.mjs`, commit, push.
