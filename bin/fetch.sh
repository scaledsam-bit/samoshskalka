#!/usr/bin/env bash
# fetch.sh - pull a competitor video down from a link and print its cut sheet.
#
#   fetch.sh SLUG URL                      download to videos/SLUG/reference.mp4, print the cut sheet
#   fetch.sh SLUG URL --cuts 2.9           pass cut times straight through to cutsheet.sh
#   fetch.sh SLUG URL --threshold 0.15     scene sensitivity, same meaning as in cutsheet.sh
#
# Options:  --force        overwrite an existing reference.mp4 instead of refusing
#           --no-cutsheet  download only, skip the cut sheet
#
# Needs yt-dlp:  brew install yt-dlp        (macOS)
#                winget install yt-dlp.yt-dlp  (Windows)
#
# Written for bash 3.2 (stock macOS). No associative arrays, no mapfile.

set -u

SLUG=""; URL=""; FORCE=0; DOCUT=1; PASS=""

while [ $# -gt 0 ]; do
  case "$1" in
    --force)       FORCE=1; shift ;;
    --no-cutsheet) DOCUT=0; shift ;;
    --cuts|--threshold|--min) PASS="$PASS $1 ${2:-}"; shift 2 ;;
    -h|--help)     sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "fetch: unknown option: $1" >&2; exit 2 ;;
    *) if [ -z "$SLUG" ]; then SLUG="$1"; elif [ -z "$URL" ]; then URL="$1";
       else echo "fetch: unexpected argument: $1" >&2; exit 2; fi; shift ;;
  esac
done

[ -n "$SLUG" ] || { echo "fetch: no slug given. Try --help" >&2; exit 2; }
[ -n "$URL" ]  || { echo "fetch: no url given. Try --help" >&2; exit 2; }

HERE=$(cd "$(dirname "$0")/.." && pwd)
DIR="$HERE/videos/$SLUG"
REF="$DIR/reference.mp4"

[ -d "$DIR" ] || { echo "fetch: no such video folder: videos/$SLUG" >&2
                   echo "       run /product first, it creates the dated folder." >&2; exit 2; }

if [ -f "$REF" ] && [ "$FORCE" -eq 0 ]; then
  echo "fetch: videos/$SLUG/reference.mp4 already exists." >&2
  echo "       Re-running a command must never cost you work, so this refuses by default." >&2
  echo "       Pass --force if you really mean to replace it." >&2
  exit 4
fi

command -v yt-dlp >/dev/null || {
  echo "fetch: yt-dlp is not installed." >&2
  echo "       macOS:   brew install yt-dlp" >&2
  echo "       Windows: winget install yt-dlp.yt-dlp" >&2
  exit 3; }
command -v ffprobe >/dev/null || { echo "fetch: ffmpeg not installed. Run /start." >&2; exit 3; }

echo "Downloading into videos/$SLUG/ ..."
TMP="$DIR/.reference.part.mp4"
rm -f "$TMP"
yt-dlp --no-playlist --no-warnings \
       -f 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b' \
       --merge-output-format mp4 \
       -o "$TMP" "$URL" || {
  echo "" >&2
  echo "fetch: yt-dlp could not get that link." >&2
  echo "       Private, region-locked and login-walled posts all fail here." >&2
  echo "       Save the file by hand and drop it at videos/$SLUG/reference.mp4 instead." >&2
  rm -f "$TMP"; exit 5; }

[ -s "$TMP" ] || { echo "fetch: download produced nothing." >&2; rm -f "$TMP"; exit 5; }
mv "$TMP" "$REF"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REF" | cut -d, -f1)
WH=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$REF")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$REF")
ROT=$(ffprobe -v error -select_streams v:0 -show_entries stream_side_data=rotation -of csv=p=0 "$REF" 2>/dev/null | tr -d ' ' | head -1)
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$REF" 2>/dev/null | grep -q .; then
  AUD="yes"; else AUD="NO - /edit will have no soundtrack to lay under the cut"; fi

printf '\nSAVED  videos/%s/reference.mp4\n' "$SLUG"
printf '  %s  %.3f s  %s fps  audio: %s\n' "$WH" "$DUR" "$FPS" "$AUD"

case "$ROT" in
  ''|0|side_data) : ;;
  *) printf '\nNOTE  this file carries rotation metadata (%s).\n' "$ROT"
     printf '      Pull frames with:  ffmpeg -noautorotate -ss T -i REF -frames:v 1 out.png\n'
     printf '      Harmless for the build: cutsheet.sh takes only audio from the reference.\n' ;;
esac

[ "$DOCUT" -eq 1 ] || exit 0

printf '\n'
# shellcheck disable=SC2086
exec "$HERE/bin/cutsheet.sh" "$REF" $PASS
