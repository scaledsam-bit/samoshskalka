#!/usr/bin/env bash
# qa.sh - pull the facts and the frames needed to judge a clip or a finished video.
#
#   qa.sh probe  VIDEO [EXPECTED_SECONDS]   technical report, non-zero exit if it fails a check
#   qa.sh frames VIDEO OUTDIR [N]           extract N evenly spaced frames (default 6) to look at
#
# Written for bash 3.2 (stock macOS).

set -u
MODE="${1:-}"; VID="${2:-}"

case "$MODE" in
  probe|frames) : ;;
  *) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
[ -n "$VID" ] && [ -f "$VID" ] || { echo "qa: file not found: ${VID:-<none>}" >&2; exit 2; }
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null || { echo "qa: ffmpeg not installed" >&2; exit 3; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VID" | cut -d, -f1)
case "$DUR" in ''|N/A) echo "qa: cannot read $VID" >&2; exit 3 ;; esac

if [ "$MODE" = "frames" ]; then
  OUT="${3:-}"; N="${4:-6}"
  [ -n "$OUT" ] || { echo "qa: frames needs an output directory" >&2; exit 2; }
  mkdir -p "$OUT" || exit 3
  i=1
  while [ "$i" -le "$N" ]; do
    T=$(awk -v d="$DUR" -v i="$i" -v n="$N" 'BEGIN{printf "%.3f", d*(i-0.5)/n}')
    ffmpeg -nostdin -v error -y -ss "$T" -i "$VID" -vframes 1 -q:v 3 \
      "$OUT/frame-$(printf '%02d' "$i")-at-${T}s.jpg" 2>/dev/null
    i=$((i+1))
  done
  echo "Wrote $N frames from $VID to $OUT"
  ls "$OUT" | sed 's|^|  |'
  exit 0
fi

# --- probe --------------------------------------------------------------------
EXPECT="${3:-}"
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width  -of csv=p=0 "$VID")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$VID")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$VID")
HASA=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VID" | wc -l | tr -d ' ')

printf 'FILE       %s\n' "$VID"
printf 'DURATION   %.3f s\n' "$DUR"
printf 'VIDEO      %sx%s at %s\n' "$W" "$H" "$FPS"
if [ "$HASA" -gt 0 ]; then
  MEAN=$(ffmpeg -nostdin -hide_banner -i "$VID" -af volumedetect -f null - 2>&1 | sed -n 's/.*mean_volume: \(.*\) dB/\1/p')
  printf 'AUDIO      present, mean %s dB\n' "${MEAN:-unknown}"
else
  printf 'AUDIO      NONE\n'
fi

FAIL=0
if [ -n "$EXPECT" ]; then
  OFF=$(awk -v a="$DUR" -v b="$EXPECT" 'BEGIN{d=a-b; if(d<0)d=-d; printf "%.3f", d}')
  BAD=$(awk -v o="$OFF" 'BEGIN{print (o>0.15)?1:0}')
  if [ "$BAD" -eq 1 ]; then
    printf 'LENGTH     FAIL  expected %.3f s, off by %s s\n' "$EXPECT" "$OFF"; FAIL=1
  else
    printf 'LENGTH     ok    expected %.3f s, off by %s s\n' "$EXPECT" "$OFF"
  fi
fi

# a frozen tail usually means the generator ran out of motion
FREEZE=$(ffmpeg -nostdin -v info -i "$VID" -vf "freezedetect=n=-60dB:d=1.0" -map 0:v -f null - 2>&1 \
         | sed -n 's/.*freeze_start: \(.*\)/\1/p' | tail -1)
if [ -n "$FREEZE" ]; then
  printf 'MOTION     WARN  frozen from %s s\n' "$FREEZE"; FAIL=1
else
  printf 'MOTION     ok    no long freeze\n'
fi

# a fully black stretch is a dead clip
BLACK=$(ffmpeg -nostdin -v info -i "$VID" -vf "blackdetect=d=0.5:pic_th=0.98" -f null - 2>&1 \
        | sed -n 's/.*black_start:\([0-9.]*\).*/\1/p' | head -1)
if [ -n "$BLACK" ]; then
  printf 'BLACK      WARN  black frames from %s s\n' "$BLACK"; FAIL=1
else
  printf 'BLACK      ok    none\n'
fi

[ "$FAIL" -eq 1 ] && printf '\nSomething above needs a human eye.\n'
exit "$FAIL"
