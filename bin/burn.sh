#!/usr/bin/env bash
# burn.sh - burn the hook text into a finished video.
#
#   burn.sh IN OUT "the hook text"
#
# Options:  --seconds N   how long the text stays up (default: the whole video)
#           --top P       vertical position as a percentage of height (default 22)
#           --size N      font size in pixels at 720 width (default 46)
#           --plain       white text with a shadow instead of the dark rounded box
#
# Two rendering paths, picked automatically:
#   drawtext, when this ffmpeg was built with libfreetype
#   a PNG overlay rendered with Python and Pillow, when it was not
# Written for bash 3.2 (stock macOS).

set -u
IN="${1:-}"; OUT="${2:-}"; TEXT="${3:-}"
SECONDS_UP=""; TOP="22"; SIZE="46"; STYLE="box"
shift 3 2>/dev/null || true
while [ $# -gt 0 ]; do
  case "$1" in
    --seconds) SECONDS_UP="${2:-}"; shift 2 ;;
    --top)     TOP="${2:-}";        shift 2 ;;
    --size)    SIZE="${2:-}";       shift 2 ;;
    --plain)   STYLE="plain";       shift   ;;
    *) echo "burn: unexpected argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$IN" ] && [ -f "$IN" ] || { sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ -n "$OUT" ] || { echo "burn: no output path" >&2; exit 2; }
[ -n "$TEXT" ] || { echo "burn: no text given" >&2; exit 2; }
command -v ffmpeg >/dev/null || { echo "burn: ffmpeg not installed" >&2; exit 3; }

W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width  -of csv=p=0 "$IN")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$IN")
[ -n "$W" ] || { echo "burn: cannot read $IN" >&2; exit 3; }
mkdir -p "$(dirname "$OUT")" || exit 3

FONT=""
for f in "/System/Library/Fonts/Supplemental/Arial Bold.ttf" \
         "/System/Library/Fonts/HelveticaNeue.ttc" \
         "/System/Library/Fonts/Helvetica.ttc" \
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; do
  [ -f "$f" ] && { FONT="$f"; break; }
done
[ -n "$FONT" ] || { echo "burn: no usable font found" >&2; exit 3; }

ENABLE=""
[ -n "$SECONDS_UP" ] && ENABLE=":enable='lte(t,$SECONDS_UP)'"

if ffmpeg -hide_banner -filters 2>/dev/null | grep -qw drawtext; then
  # --- path 1: drawtext ---
  ESC=$(printf '%s' "$TEXT" | sed "s/\\\\/\\\\\\\\/g; s/:/\\\\:/g; s/'/\\\\\\\\'/g; s/%/\\\\%/g")
  Y=$(awk -v h="$H" -v t="$TOP" 'BEGIN{printf "%d", h*t/100}')
  if [ "$STYLE" = "box" ]; then
    VF="drawtext=fontfile=${FONT}:text='${ESC}':fontsize=${SIZE}:fontcolor=white:x=(w-tw)/2:y=${Y}:box=1:boxcolor=black@0.55:boxborderw=18${ENABLE}"
  else
    VF="drawtext=fontfile=${FONT}:text='${ESC}':fontsize=${SIZE}:fontcolor=white:x=(w-tw)/2:y=${Y}:shadowcolor=black@0.7:shadowx=2:shadowy=2${ENABLE}"
  fi
  ffmpeg -nostdin -v error -y -i "$IN" -vf "$VF" \
    -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT" || exit 4
  METHOD="drawtext"
else
  # --- path 2: render the text to a transparent PNG, then overlay it ---
  command -v python3 >/dev/null || { echo "burn: this ffmpeg has no drawtext and python3 is missing. Install a full ffmpeg (brew install ffmpeg) or python3." >&2; exit 3; }
  TMP=$(mktemp -d "${TMPDIR:-/tmp}/burn.XXXXXX") || exit 3
  trap 'rm -rf "$TMP"' EXIT INT TERM
  python3 - "$TMP/text.png" "$W" "$H" "$TEXT" "$FONT" "$SIZE" "$TOP" "$STYLE" <<'PY' || { echo "burn: could not render the text. Pillow missing? pip3 install pillow" >&2; exit 3; }
import sys
from PIL import Image, ImageDraw, ImageFont
out, W, H, text, font_path, size, top, style = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5], int(sys.argv[6]), float(sys.argv[7]), sys.argv[8]
size = max(12, int(size * W / 720.0))
font = ImageFont.truetype(font_path, size)
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
maxw = int(W * 0.84)
words, lines, cur = text.split(), [], ""
for w in words:
    t = (cur + " " + w).strip()
    if d.textlength(t, font=font) <= maxw or not cur: cur = t
    else: lines.append(cur); cur = w
if cur: lines.append(cur)
lh = int(size * 1.28)
block_h = lh * len(lines)
y0 = int(H * top / 100.0)
pad_x, pad_y = int(size * 0.55), int(size * 0.42)
widest = max(d.textlength(l, font=font) for l in lines)
if style == "box":
    x0 = (W - widest) / 2 - pad_x
    box = [x0, y0 - pad_y, x0 + widest + pad_x * 2, y0 + block_h + pad_y]
    d.rounded_rectangle(box, radius=int(size * 0.34), fill=(0, 0, 0, 140))
for i, line in enumerate(lines):
    lw = d.textlength(line, font=font)
    x, y = (W - lw) / 2, y0 + i * lh
    if style != "box":
        d.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 190))
    d.text((x, y), line, font=font, fill=(255, 255, 255, 255))
img.save(out)
print("lines=%d size=%d" % (len(lines), size))
PY
  if [ -n "$SECONDS_UP" ]; then
    OV="[0:v][1:v]overlay=0:0:enable='lte(t,$SECONDS_UP)'"
  else
    OV="[0:v][1:v]overlay=0:0"
  fi
  ffmpeg -nostdin -v error -y -i "$IN" -i "$TMP/text.png" -filter_complex "$OV" \
    -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a copy -movflags +faststart "$OUT" || exit 4
  METHOD="png overlay"
fi

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | cut -d, -f1)
printf 'BURNED  %s  (%s, %.3f s)\n' "$OUT" "$METHOD" "$DUR"
printf 'Text: %s\n' "$TEXT"
