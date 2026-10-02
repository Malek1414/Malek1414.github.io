#!/bin/zsh
# Turn any video into a site loop: silent, H.264, faststart, two sizes + a poster.
#   scripts/make-loop.sh <input> <start-seconds> <duration-seconds> <name> [crop]
#     crop: "none" (default, keep the source aspect) or "portrait" (centre-crop to 9:16)
#   LUT=assets/grade/cool.cube scripts/make-loop.sh ...   grades it with one of R2R's looks
#     (cool: gym/night · warm: daylight/skin · ifa: venue lighting), the same lut3d R2R renders with
#   XF=0.6 (default) dissolves the loop point; the source needs <seconds>+XF after <start>
# Writes assets/loops/<name>.mp4, <name>-sm.mp4 and <name>.jpg, then point a MEDIA slot at them.
set -euo pipefail
IN="${1:?input video}"; SS="${2:?start}"; DUR="${3:?duration}"; NAME="${4:?name}"; CROP="${5:-none}"
OUT="${0:A:h:h}/assets/loops"; mkdir -p "$OUT"
GRADE=""
# iPhone HLG/BT.2020 goes to SDR first, through the HLG->709 LUT (this ffmpeg has no zscale)
if [[ "$(ffprobe -v error -select_streams v:0 -show_entries stream=color_transfer -of csv=p=0 "$IN")" == arib-std-b67 ]]; then
  GRADE="format=gbrp,lut3d=file=${0:A:h:h}/assets/grade/hlg2709.cube,"
fi
for l in ${(s.:.)${LUT:-}}; do GRADE="${GRADE}format=gbrp,lut3d=file=${l:A},"; done   # LUT=a.cube:b.cube stacks looks in order
SETP="setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv"
case "$CROP" in
  portrait) BASE="crop='min(iw,ih*9/16)':'min(ih,iw*16/9)'," ;;
  *) BASE="" ;;
esac
XF="${XF:-0.6}"   # seconds of the clip's own start dissolved into its end, so the loop has no seam
enc() {  # $1 = longest edge, $2 = output, $3 = crf
  local T=$(python3 -c "print($DUR+$XF)") B=$(python3 -c "print($DUR-$XF)")
  ffmpeg -y -v error -ss "$SS" -t "$T" -i "$IN" -an -filter_complex "\
[0:v]${BASE}${GRADE}scale='if(gt(iw,ih),$1,-2)':'if(gt(iw,ih),-2,$1)':flags=lanczos,fps=30,format=yuv420p,setsar=1,split=2[a][h0];\
[a]trim=start=$XF,setpts=PTS-STARTPTS,split=2[a1][a2];\
[a1]trim=end=$B,setpts=PTS-STARTPTS[body];\
[a2]trim=start=$B,setpts=PTS-STARTPTS[tail];\
[h0]trim=end=$XF,setpts=PTS-STARTPTS[head];\
[tail][head]xfade=transition=fade:duration=$XF:offset=0[seam];\
[body][seam]concat=n=2:v=1,${SETP}[v]" -map "[v]" \
    -c:v libx264 -preset slow -crf "$(( $3 + ${CRF_BUMP:-0} ))" -movflags +faststart "$2"
}
enc 1920 "$OUT/$NAME.mp4" 23
enc 960 "$OUT/$NAME-sm.mp4" 26
ffmpeg -y -v error -ss "$(python3 -c "print($DUR/2)")" -i "$OUT/$NAME.mp4" -frames:v 1 -q:v 3 "$OUT/$NAME.jpg"
ls -lh "$OUT/$NAME".* "$OUT/$NAME-sm.mp4" | awk '{print $5, $9}'
