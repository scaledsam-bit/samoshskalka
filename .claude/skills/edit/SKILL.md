---
description: Build the finished video. Cuts every clip to the original's exact rhythm, lays the original soundtrack under it, and exports an uploadable 9:16 file. Free, nothing is generated.
argument-hint: [slug]
arguments: [slug]
disable-model-invocation: true
---

Build the finished video for `videos/$slug`. Nothing here costs credits.

The edit copies the format: same cuts, same rhythm, same sound, new footage. Under this system
that step contains no creative decision at all, so it is arithmetic and the machine does it.

## 1. The cut sheet

```
./bin/cutsheet.sh videos/$slug/reference.mp4 videos/$slug/clips
```

Per segment it prints the length, which clip fills it, and the trim. Write it to
`videos/$slug/cutsheet.txt`. If `/concept` had to pass the cuts by hand with `--cuts`, pass the
same list here. The two commands must work off the same segment list.

Read the sheet before building. A clip marked **SHORT** is a hole nothing downstream fixes.

## 2. Build it

```
./bin/cutsheet.sh videos/$slug/reference.mp4 videos/$slug/clips --build videos/$slug/out/final.mp4
```

Output is 720x1280 at 60 fps with the original soundtrack, faststart, ready to upload. That
matches the export spec the format asks for, so nothing has to be re-encoded later.

It **refuses to build** when any clip is shorter than the segment it has to fill, and names
them. That is correct: regenerate those clips at the length the plan asks for. Only if the
student explicitly accepts a visible frame hold should you re-run with `--pad`.

`--height` and `--fps` override the defaults if they ever need to.

## 3. Burn the hook text in

```
./bin/burn.sh videos/$slug/out/final.mp4 videos/$slug/out/final-text.mp4 "<the hook line>"
```

The text goes into the file now, not in TikTok later. That is what lets the same finished file
go to every platform, including Buffer, which uploads a file and cannot add text afterwards.

Take the hook line from `/post` if it has run, otherwise write it here and keep it under four
words wherever it can be. It plays on mute more often than not.

`--seconds N` drops the text after N seconds, `--top P` moves it up or down, `--size N` changes
the size, `--plain` swaps the dark box for a shadow. Defaults sit in the upper third with a dark
rounded box, which stays readable over any footage.

Look at a frame before moving on:

```
./bin/qa.sh frames videos/$slug/out/final-text.mp4 videos/$slug/qa/text 3
```

Read them. Text that collides with the product, or sits where the platform puts its own UI, is
the whole hook wasted.

## 4. Check it before anyone sees it

```
/review $slug final
```

Never hand over a file you have not probed and looked at.

## 5. If they want to touch it up

The file is finished and uploadable as it is. CapCut is optional now, for when they want to
nudge something the machine cannot judge. If they do open it there, keep the export at 720p
60 fps, no Smart HDR, no extras.

## 6. One thing to pass on

The soundtrack comes off the competitor's video. That is the format being copied and it is also
somebody else's audio. Worth the student knowing that is what they are doing, particularly with
a brand account attached to it.

## 7. Report

Show the output path, its duration against the reference, the drift, and anything the review
flagged. Then `/post` for the caption, and `/ship` if they publish through Buffer.
