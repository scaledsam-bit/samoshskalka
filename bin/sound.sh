#!/usr/bin/env bash
# sound.sh - read the soundtrack of a reference video and file it in the niche sound bank.
#
#   sound.sh SLUG                 analyse videos/SLUG/reference.mp4, print the map, append to the bank
#   sound.sh SLUG --no-save       print only, do not touch the bank
#   sound.sh --bank               print everything collected so far
#
# Why this exists: nothing can name a track from its audio, and TikTok cannot be crawled from
# here. But every reference the student sends IS a dropshipping product video that already
# works, so the sounds worth having arrive on their own. This files them.
#
# Written for bash 3.2 (stock macOS). No associative arrays, no mapfile.

set -u

HERE=$(cd "$(dirname "$0")/.." && pwd)
BANK="$HERE/library/sounds.jsonl"
SLUG=""; SAVE=1

while [ $# -gt 0 ]; do
  case "$1" in
    --no-save) SAVE=0; shift ;;
    --bank)    [ -f "$BANK" ] && cat "$BANK" || echo "sound: the bank is empty. Analyse a reference first."; exit 0 ;;
    -h|--help) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "sound: unknown option: $1" >&2; exit 2 ;;
    *) [ -z "$SLUG" ] && SLUG="$1" || { echo "sound: unexpected argument: $1" >&2; exit 2; }; shift ;;
  esac
done

[ -n "$SLUG" ] || { echo "sound: no slug given. Try --help" >&2; exit 2; }
REF="$HERE/videos/$SLUG/reference.mp4"
[ -f "$REF" ] || { echo "sound: no reference at videos/$SLUG/reference.mp4" >&2
                   echo "       run /concept or ./bin/fetch.sh first." >&2; exit 2; }
command -v ffprobe >/dev/null || { echo "sound: ffmpeg not installed. Run /start." >&2; exit 3; }

ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$REF" 2>/dev/null | grep -q . || {
  echo "sound: this reference has no audio track. Nothing to analyse, and /edit will build it silent." >&2
  exit 4; }

QA="$HERE/videos/$SLUG/qa/reference"
mkdir -p "$QA"

ffmpeg -nostdin -v error -y -i "$REF" -lavfi "showspectrumpic=s=900x420:mode=combined:legend=1" "$QA/spectrogram.png" 2>/dev/null
ffmpeg -nostdin -v error -y -i "$REF" -filter_complex "showwavespic=s=900x200:colors=white" "$QA/waveform.png" 2>/dev/null

ENV=$(mktemp); PEAK=$(mktemp)
trap 'rm -f "$ENV" "$PEAK"' EXIT INT TERM

ffmpeg -nostdin -i "$REF" -af "astats=metadata=1:reset=11,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>&1 \
  | grep -E 'pts_time|RMS_level' | paste - - \
  | sed -E 's/.*pts_time:([0-9.]+).*RMS_level=([-0-9.]+)/\1 \2/' > "$ENV"
ffmpeg -nostdin -i "$REF" -af "astats=metadata=1:reset=3,ametadata=print:key=lavfi.astats.Overall.Peak_level:file=-" -f null - 2>&1 \
  | grep -E 'pts_time|Peak_level' | paste - - \
  | sed -E 's/.*pts_time:([0-9.]+).*Peak_level=([-0-9.]+)/\1 \2/' > "$PEAK"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$REF" | cut -d, -f1)
SR=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of csv=p=0 "$REF")

SLUG="$SLUG" REF="$REF" DUR="$DUR" SR="$SR" ENVF="$ENV" PEAKF="$PEAK" BANK="$BANK" SAVE="$SAVE" \
python3 - <<'PY'
import os, json, datetime

def read(p):
    out=[]
    for line in open(p):
        f=line.split()
        if len(f)==2:
            try: out.append((float(f[0]), float(f[1])))
            except ValueError: pass
    return out

env  = read(os.environ["ENVF"])
peak = read(os.environ["PEAKF"])
dur  = float(os.environ["DUR"])
slug = os.environ["SLUG"]

if not env:
    raise SystemExit("sound: could not read a loudness envelope from this file.")

# --- loud regions -----------------------------------------------------------
TH = -40.0
runs=[]
for t,v in env:
    if v > TH:
        if runs and t - runs[-1][1] <= 0.45: runs[-1][1] = t
        else: runs.append([t,t])
regions=[(a,b) for a,b in runs if b-a >= 0.15]
holes=[]
prev=0.0
for a,b in regions:
    if a-prev >= 0.5: holes.append((prev,a))
    prev=b
if dur-prev >= 0.5: holes.append((prev,dur))

# --- transients -------------------------------------------------------------
hits=[]; window=[]
for t,v in peak:
    if window and v - sum(window)/len(window) > 6 and v > -25: hits.append((t,v))
    window.append(v); window=window[-5:]
merged=[]
for t,v in hits:
    if merged and t-merged[-1][0] < 0.12:
        if v > merged[-1][1]: merged[-1]=(t,v)
    else: merged.append((t,v))

# --- speech or music --------------------------------------------------------
# Music holds a roughly steady level across the whole file and rarely leaves long holes.
# Speech is bursty with real silence between phrases.
loud_share = sum(b-a for a,b in regions)/dur if dur else 0
hole_share = sum(b-a for a,b in holes)/dur if dur else 0
levels=[v for _,v in env if v > -80]
spread = (max(levels)-min(levels)) if levels else 0
if loud_share > 0.85 and hole_share < 0.05:
    kind, why = "music or a continuous bed", "level holds across the whole file with no real gaps"
elif hole_share > 0.15:
    kind, why = "speech and room tone, no music bed", "long silences between bursts, which music does not do"
else:
    kind, why = "mixed or unclear", "neither continuous enough for music nor gappy enough for pure speech"

# --- beat spacing, only worth printing when it is regular -------------------
bpm=None
if len(merged) >= 4:
    gaps=[round(merged[i+1][0]-merged[i][0],3) for i in range(len(merged)-1)]
    gaps=[g for g in gaps if 0.2 <= g <= 2.0]
    if len(gaps) >= 3:
        gaps_sorted=sorted(gaps); med=gaps_sorted[len(gaps_sorted)//2]
        if med>0 and all(abs(g-med) < med*0.18 for g in gaps):
            bpm=round(60.0/med, 1)

print("SOUND  videos/%s/reference.mp4" % slug)
print("  %.3f s   %s Hz   reads as: %s" % (dur, os.environ["SR"], kind))
print("  (%s)" % why)
if bpm: print("  regular beat, about %.1f BPM" % bpm)
print()
print("  LOUD")
for a,b in regions: print("    %6.2f - %6.2f s   (%.2f s)" % (a,b,b-a))
if holes:
    print("  QUIET")
    for a,b in holes: print("    %6.2f - %6.2f s   (%.2f s)" % (a,b,b-a))
print("  TRANSIENTS  (land any new beat of your own on one of these)")
for t,v in merged: print("    %6.2f s   %6.1f dBFS" % (t,v))
if merged:
    hardest=max(merged, key=lambda x: x[1])
    print("  HARDEST     %.2f s at %.1f dBFS" % hardest)
print()
print("  Frames: videos/%s/qa/reference/spectrogram.png and waveform.png" % slug)

if os.environ["SAVE"] == "1":
    bank=os.environ["BANK"]
    os.makedirs(os.path.dirname(bank), exist_ok=True)
    row={"slug":slug,"analysed":datetime.date.today().isoformat(),"duration":round(dur,3),
         "kind":kind,"bpm":bpm,"loud":[[round(a,2),round(b,2)] for a,b in regions],
         "quiet":[[round(a,2),round(b,2)] for a,b in holes],
         "transients":[[round(t,2),round(v,1)] for t,v in merged],
         "hardest": round(max(merged,key=lambda x:x[1])[0],2) if merged else None}
    keep=[]
    if os.path.exists(bank):
        for line in open(bank):
            line=line.strip()
            if not line: continue
            try:
                if json.loads(line).get("slug") != slug: keep.append(line)
            except json.JSONDecodeError: keep.append(line)
    keep.append(json.dumps(row, ensure_ascii=False))
    open(bank,"w").write("\n".join(keep)+"\n")
    print("  Filed in library/sounds.jsonl (%d reference%s collected)" % (len(keep), "" if len(keep)==1 else "s"))
PY
