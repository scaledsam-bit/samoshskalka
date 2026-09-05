---
description: Analyse the competitor video the whole piece is being built from, extract its cut rhythm, and turn it into a clip plan with a route and a duration per clip. Free, nothing is generated.
argument-hint: [slug] [competitor video file, URL or screenshots]
arguments: [slug, reference]
disable-model-invocation: true
---

Build the clip plan for `videos/$slug` from: **$reference**

The bet this whole system makes is: **proven format, new content.** So the reference is not
inspiration, it is a specification. Read it like one.

## 0. Put the reference on disk first

Nothing downstream works until the reference is at a known path, so do this before anything else:

- **A local video file:** copy it to `videos/$slug/reference.mp4`
- **A URL:** run `./bin/fetch.sh <slug> <url>`. It pulls the file down with yt-dlp, saves it
  as `reference.mp4` and prints the cut sheet in one step. It refuses to overwrite an existing
  reference unless `--force`, so re-running costs nothing. If yt-dlp cannot get the link
  (private, region-locked, login-walled), the student saves it by hand and drops it at that path.
  Never fetch from a social platform any other way
- **Screenshots only:** save them into `videos/$slug/reference/` and say plainly that there is
  no cut rhythm to extract, so step 1 is skipped and the durations come from the plan instead

Record the path in `video.json` under `"reference"`. `/edit` reads the same path later, so if
it is not there, the edit step has nothing to work from.

## 1. Get the cut rhythm

If there is a video file, this is deterministic, so do not eyeball it:

```
./bin/cutsheet.sh videos/$slug/reference.mp4
```

That prints every cut timestamp and the length of each segment. Those lengths are the target
durations for the generated clips, and they are what makes the edit mechanical later.

**Sanity check the segment count against the video before trusting it.** Detection reads the
luma channel only, so a cut between two shots of similar brightness is invisible to it. If the
count is too low, try `--threshold 0.15`, and if that still misses, read the cut times off the
timeline once and pass them by hand:

```
./bin/cutsheet.sh videos/$slug/reference.mp4 --cuts 2.0,5.5,7.2
```

If there is only a screenshot of the first frame, there is no rhythm to extract. Say so, and
build the plan from the concept alone.

## 2. Read the scenes

For a longer or more complex reference, also run `video_analysis_create` for a scene by scene
breakdown, and poll `video_analysis_status`. Warn the student first: the longer the video, the
less accurate that analysis is. On a 15 second reel it is reliable; on two minutes it is not.

## 3. Write the plan

One row per clip:

| # | Type | Template | Route | Duration | What happens | References |
|---|---|---|---|---|---|---|

- **Type**: hook, handmade or showcase
- **Template**: T1 to T5 from `format/templates.md`, or GENERAL with a reason
- **Route**: T2V or IMG, per the rule in CLAUDE.md. Default T2V. Say why on every IMG.
- **Duration**: from the cut sheet where there is one, otherwise from `format/animation.md`
- **References**: which locked elements attach, in what order, mapped to `<<<image_1>>>` and so on

Sum the durations and compare to the original's length. If they do not match, the edit will not
match either, and that is worth fixing now rather than after the clips are paid for.

## 4. Flag the risks now

Name them before any credit is spent: content filter risk, product fidelity risk, too many
references in one generation, a scene the model reliably gets wrong. This is cheaper here
than after three failed generations.

## 5. Stop

Write the plan into `video.json`, set `"status": "awaiting_plan_approval"`, show it and wait.
