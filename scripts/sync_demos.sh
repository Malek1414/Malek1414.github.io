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
