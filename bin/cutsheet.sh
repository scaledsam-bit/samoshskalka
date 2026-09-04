#!/usr/bin/env bash
# cutsheet.sh - derive the cut rhythm of a reference video and map generated clips onto it.
#
#   cutsheet.sh REFERENCE                          print the cut sheet
#   cutsheet.sh REFERENCE CLIPSDIR                 map clips onto the segments
#   cutsheet.sh REFERENCE CLIPSDIR --build OUT     build the finished video
#
# Options:  --threshold N (scene sensitivity 0.1-0.9, default 0.30)
#           --min N       (merge segments shorter than N seconds, default 0.35)
#           --height N    (output height, default 1280 for 720p vertical)
#           --fps N       (output frame rate, default 60)
#           --pad         (fill a short clip by holding its last frame instead of refusing)
#           --cuts a,b,c  (use these cut times instead of detecting them)
#
# Detection reads the luma channel only, so a cut between two shots of similar
# brightness can be missed. When the segment count looks wrong, lower --threshold,
# or read the cuts off the timeline once and pass them with --cuts.
#
# Written for bash 3.2 (stock macOS). No associative arrays, no mapfile.

set -u

REF=""; CLIPS=""; OUT=""; THRESH="0.30"; MIN="0.35"; MANUAL=""; HEIGHT="1280"; FPS="60"; PAD=0

while [ $# -gt 0 ]; do
  case "$1" in
    --build|--assemble) OUT="${2:-}"; shift 2 ;;
    --height)    HEIGHT="${2:-}"; shift 2 ;;
    --fps)       FPS="${2:-}";    shift 2 ;;
    --pad)       PAD=1;           shift   ;;
    --threshold) THRESH="${2:-}"; shift 2 ;;
    --min)       MIN="${2:-}";    shift 2 ;;
    --cuts)      MANUAL="${2:-}";  shift 2 ;;
    -h|--help)   sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) if [ -z "$REF" ]; then REF="$1"; elif [ -z "$CLIPS" ]; then CLIPS="$1";
       else echo "cutsheet: unexpected argument: $1" >&2; exit 2; fi; shift ;;
  esac
done

[ -n "$REF" ]   || { echo "cutsheet: no reference video given. Try --help" >&2; exit 2; }
[ -f "$REF" ]   || { echo "cutsheet: reference not found: $REF" >&2; exit 2; }
command -v ffmpeg  >/dev/null || { echo "cutsheet: ffmpeg not installed" >&2; exit 3; }
command -v ffprobe >/dev/null || { echo "cutsheet: ffprobe not installed" >&2; exit 3; }
[ -n "$OUT" ] && [ -z "$CLIPS" ] && { echo "cutsheet: --build needs a clips directory" >&2; exit 2; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REF" 2>/dev/null | cut -d, -f1)
case "$DUR" in ''|N/A) echo "cutsheet: cannot read duration of $REF" >&2; exit 3 ;; esac

TMP=$(mktemp -d "${TMPDIR:-/tmp}/cutsheet.XXXXXX") || exit 3
trap 'rm -rf "$TMP"' EXIT INT TERM

# --- 1. cuts: supplied by hand, or detected ---------------------------------
: > "$TMP/cuts.raw"
if [ -n "$MANUAL" ]; then
  printf '%s\n' "$MANUAL" | tr ',' '\n' | tr -d ' ' | grep -E '^[0-9]+(\.[0-9]+)?$' \
    | sort -n -u > "$TMP/cuts.raw"
  [ -s "$TMP/cuts.raw" ] || { echo "cutsheet: --cuts had no usable numbers: $MANUAL" >&2; exit 2; }
  SRC="given by hand"
else
  ffmpeg -nostdin -v error -i "$REF" -an \
    -filter_complex "select='gt(scene,$THRESH)',metadata=print:file=$TMP/scenes.txt" \
    -f null - 2>/dev/null || true
  [ -f "$TMP/scenes.txt" ] && grep -o 'pts_time:[0-9.]*' "$TMP/scenes.txt" 2>/dev/null \
    | cut -d: -f2 | sort -n -u > "$TMP/cuts.raw"
  SRC="detected at threshold $THRESH"
fi

# --- 2. segments, merging anything under --min ------------------------------
awk -v dur="$DUR" -v min="$MIN" '
  { if ($1+0 > 0 && $1+0 < dur+0) c[++n]=$1+0 }
  END{
    prev=0; k=0
    for(i=1;i<=n;i++){ if(c[i]-prev >= min+0){ k++; s[k]=prev; e[k]=c[i]; prev=c[i] } }
    if(dur-prev >= min+0 || k==0){ k++; s[k]=prev; e[k]=dur+0 } else { e[k]=dur+0 }
    for(i=1;i<=k;i++) printf "%d %.3f %.3f %.3f\n", i, s[i], e[i], e[i]-s[i]
  }' "$TMP/cuts.raw" > "$TMP/segments.txt"

NSEG=$(wc -l < "$TMP/segments.txt" | tr -d ' ')

printf 'REFERENCE  %s\n' "$REF"
printf 'DURATION   %.3f s      SEGMENTS  %s      CUTS  %s\n\n' "$DUR" "$NSEG" "$SRC"
if [ "$NSEG" -le 1 ] && [ -z "$MANUAL" ]; then
  printf 'Only one segment found. Either the reference really is one shot, or the cuts fall\n'
  printf 'between shots of similar brightness, which luma detection misses. Try --threshold 0.15,\n'
  printf 'or read the cut times off the timeline and pass them with --cuts 2.0,5.5,7.2\n\n'
fi

if [ -z "$CLIPS" ]; then
  printf '  #   START      END     LENGTH\n'
  awk '{printf "  %-3d %8.3f %8.3f %9.3f\n", $1,$2,$3,$4}' "$TMP/segments.txt"
  printf '\nNo clips directory given, so no mapping. Cut times above are the CapCut targets.\n'
  exit 0
fi

# --- 3. map clips onto segments ---------------------------------------------
[ -d "$CLIPS" ] || { echo "cutsheet: clips directory not found: $CLIPS" >&2; exit 2; }

find "$CLIPS" -maxdepth 1 -type f \( -name '*.mp4' -o -name '*.mov' -o -name '*.MP4' -o -name '*.MOV' \) \
  | while IFS= read -r f; do
      stem=$(basename "$f"); stem="${stem%.*}"
      n=$(printf '%s' "$stem" | grep -oE '[0-9]+' | tail -1 | sed -E 's/^0+([0-9])/\1/' | cut -c1-9)
      [ -z "$n" ] && n=999999
      printf '%s\t%s\n' "$((10#$n))" "$f"
    done | sort -n -k1,1 | cut -f2- > "$TMP/clips.txt"

NCLIP=$(wc -l < "$TMP/clips.txt" | tr -d ' ')
[ "$NCLIP" -gt 0 ] || { echo "cutsheet: no .mp4/.mov files in $CLIPS" >&2; exit 2; }

printf '  #   SEG LEN   CLIP                          CLIP LEN    TRIM   STATUS\n'
: > "$TMP/plan.txt"; WARN=0

i=0
while read -r idx s e len; do
  i=$((i+1))
  clip=$(sed -n "${i}p" "$TMP/clips.txt")
  if [ -z "$clip" ]; then
    printf '  %-3d %8.3f   %-28s %9s %7s   MISSING clip\n' "$idx" "$len" "-" "-" "-"
    WARN=$((WARN+1)); continue
  fi
  cdur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip" 2>/dev/null | cut -d, -f1)
  case "$cdur" in ''|N/A) cdur=0 ;; esac
  line=$(awk -v c="$cdur" -v l="$len" 'BEGIN{
      t=c-l; pct=(c>0)? (t/c)*100 : 0
      st="ok"
      if (t < -0.05)      st="SHORT by " sprintf("%.2f",-t) "s"
      else if (pct > 40)  st="heavy trim " sprintf("%.0f",pct) "%"
      printf "%.3f\t%.3f\t%s", c, t, st }')
  cd2=$(printf '%s' "$line" | cut -f1); tr2=$(printf '%s' "$line" | cut -f2); st2=$(printf '%s' "$line" | cut -f3)
  case "$st2" in ok) : ;; *) WARN=$((WARN+1)) ;; esac
  printf '  %-3d %8.3f   %-28s %9.3f %7.3f   %s\n' "$idx" "$len" "$(basename "$clip")" "$cd2" "$tr2" "$st2"
  printf '%s\t%s\n' "$clip" "$len" >> "$TMP/plan.txt"
done < "$TMP/segments.txt"

EXTRA=$((NCLIP - NSEG))
printf '\n'
[ "$EXTRA" -gt 0 ] && printf 'NOTE  %d clip(s) beyond the last segment, unused.\n' "$EXTRA"
[ "$WARN" -gt 0 ]  && printf 'WARN  %d segment(s) need attention before the edit.\n' "$WARN"
[ "$WARN" -eq 0 ] && [ "$EXTRA" -le 0 ] && printf 'All segments covered.\n'

[ -z "$OUT" ] && exit 0

# --- 4. build the finished video ---------------------------------------------
WIDTH=$(awk -v h="$HEIGHT" 'BEGIN{w=int(h*9/16); if(w%2)w++; print w}')

# a short clip leaves a hole the edit cannot fix, so refuse unless --pad was asked for
if [ "$PAD" -eq 0 ]; then
  : > "$TMP/shorts.txt"
  while IFS="$(printf '\t')" read -r clip len; do
    cd2=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip" 2>/dev/null | cut -d, -f1)
    [ -z "$cd2" ] && cd2=0
    awk -v c="$cd2" -v l="$len" -v n="$(basename "$clip")" \
        'BEGIN{ if (c+0-l < -0.05) printf "  %s is %.2fs, needs %.2fs\n", n, c, l }' >> "$TMP/shorts.txt"
  done < "$TMP/plan.txt"
  if [ -s "$TMP/shorts.txt" ]; then
    printf '\nNot building. These clips are shorter than the segment they must fill:\n' >&2
    cat "$TMP/shorts.txt" >&2
    printf '\nRegenerate them at the length the plan asks for. Holding a frame to cover the gap\n' >&2
    printf 'is visible on playback, so it is opt-in: re-run with --pad if you accept that.\n' >&2
    exit 5
  fi
fi

printf '\nBuilding %sx%s at %s fps...\n' "$WIDTH" "$HEIGHT" "$FPS"
mkdir -p "$(dirname "$OUT")" || exit 3
: > "$TMP/concat.txt"; k=0
while IFS="$(printf '\t')" read -r clip len; do
  k=$((k+1))
  seg="$TMP/seg_$(printf '%04d' "$k").mp4"
  ffmpeg -nostdin -v error -y -i "$clip" \
    -vf "scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:-1:-1:color=black,setsar=1,fps=${FPS},tpad=stop_mode=clone:stop_duration=10,trim=duration=$len,setpts=PTS-STARTPTS,format=yuv420p" \
    -an -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.1 "$seg" \
    || { echo "cutsheet: failed on $clip" >&2; exit 4; }
  printf "file '%s'\n" "$seg" >> "$TMP/concat.txt"
done < "$TMP/plan.txt"

ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$TMP/concat.txt" -c copy "$TMP/video.mp4" || exit 4
VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TMP/video.mp4" | cut -d, -f1)

if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$REF" 2>/dev/null | grep -q .; then
  ffmpeg -nostdin -v error -y -i "$TMP/video.mp4" -i "$REF" \
    -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -ar 48000 \
    -af "apad" -t "$VDUR" -movflags +faststart "$OUT" || exit 4
  AUDIO="original soundtrack"
else
  ffmpeg -nostdin -v error -y -i "$TMP/video.mp4" -c:v copy -movflags +faststart "$OUT" || exit 4
  AUDIO="silent, the reference had no audio track"
fi

FIN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" | cut -d, -f1)
RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$OUT")
DRIFT=$(awk -v a="$FIN" -v b="$DUR" 'BEGIN{d=a-b; if(d<0)d=-d; printf "%.3f", d}')

printf '\nREADY  %s\n' "$OUT"
printf '  %s  %.3f s  %s fps  %s\n' "$RES" "$FIN" "$FPS" "$AUDIO"
printf '  reference %.3f s, drift %s s\n' "$DUR" "$DRIFT"
[ "$PAD" -eq 1 ] && printf '  NOTE built with --pad, any short clip holds its last frame\n'
printf '\nWatch it once, then upload to TikTok and add the hook text there.\n'
