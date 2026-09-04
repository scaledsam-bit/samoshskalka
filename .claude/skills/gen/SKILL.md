---
description: Generate the clips for the approved plan through Seedance 2.5. This is the only video command that spends credits and it never runs on its own.
argument-hint: [slug] [optional: clip numbers]
arguments: [slug, clips]
disable-model-invocation: true
---

Generate `videos/$slug`, clips: **$clips** (empty means all of them).

**This command spends credits.** Read `video.json` first and skip every clip already marked
done, so a re-run continues rather than restarting and never pays twice for the same clip.

Optional. A student who generates in the Higgsfield or KIE UI by hand stops at `/prompts` and
never runs this. Nothing downstream depends on it.

## 1. Preflight

Call `get_cost: true` for the batch. Print the total. **Wait for a yes.** Do not carry an
approval over from an earlier batch in the same session.

## 2. Generate

`generate_video` with `model: "seedance_2_5"`, `aspect_ratio: "9:16"`, `resolution: "720p"`,
duration from the plan.

Before each clip, ask one question: **continuation, or scene change?**

- **Continuation** (same room, same moment, the shot just carries on): extract the last frame of
  the previous rendered clip and pass it as `start_image`. It is free, and continuity is perfect
  because it literally is the previous moment. Use it wherever the plan has consecutive clips in
  one scene. This is the cheapest quality you will ever buy.
- **Scene change:** start fresh, by the clip's own route.

Then, by route:

- **T2V clips:** `mode: "t2v"`, locked product element referenced inline in the prompt text.
- **IMG clips:** generate the start frame first with `nano_banana_pro`, inspect it before
  spending on the animation, then animate with the frame as `start_image`.

Re-anchor on a freshly generated frame every fourth chained clip, otherwise quality drifts.

Set `generate_audio: true` so the natural sound is there, and forbid speech in the prompt's
sound block unless the clip actually has a spoken line. Music stays out either way.

Batches of 2 to 12 independent clips go through `generate_video_batch`, then `jobs_wait`.

## 2b. Where the clips go

Download every finished clip to `videos/$slug/clips/clip-<N>.mp4`, where `<N>` is the clip
number from the plan. Record the path in `video.json` under `"clips"`.

This naming is not cosmetic. `/edit` maps clip N onto segment N by reading the last number in
the filename, so a clip saved as `download (3).mp4` lands in the wrong segment and nothing
warns about it.

## 2c. Test mode

If the student says test, or is trying a concept they are unsure of, generate at `480p` with
`seedance_2_0_mini` instead. It costs a fraction, it is enough to see whether the concept and
the motion work, and it is never the thing that gets posted. Write `"test": true` into
`video.json` so nobody mistakes a test set for a finished one later.

## 3. Inspect every clip before accepting it

Four checks, in this order, because they fail in this order:

1. **Product fidelity.** Identical to the locked reference, no recolour, no relabel.
2. **No burned in text**, no watermark, no logo the brief did not ask for.
3. **Camera** did what the brief said, static where static was specified.
4. **Duration** matches the plan, since the edit depends on it.

A clip that fails 1 or 2 is unusable. Reroll it.

## 4. When one fails

Two legitimate moves, in this order:

- **Reroll.** Same prompt again. Seedance has real variance and the second take often lands.
- **Rewrite shorter.** Cut the motion description down, name fewer things, simpler wording.
  Never fix a failing prompt by adding detail.

Cap at **3 paid attempts per clip**. After that keep the best take, set `"flagged": true`,
and move on.

## 5. Optional upscale

Only if the student asks. `upscale_video` with `provider: "bytedance"`, `preset: "aigc"`,
the source width and height, and `fps: 60`. Note honestly: **60 fps doubles the cost**, and
the ByteDance provider targets 1080p, 2k or 4k, so "original resolution, 60 fps only" the way
the Higgsfield web UI does it is not reachable through the API. If that exact behaviour is
wanted, upscale in the UI.

## 6. Log

Append every paid call to `costs.jsonl`. If credits run out, set `"status": "no_credits"` and
stop. Do not retry against an empty wallet.

## 7. Say what it cost

When the set is done, total `costs.jsonl` and report **credits for this video**, plus how many
of the clips were chained continuations rather than fresh generations. Write the total into
`video.json`.

A student who cannot answer "what does one video cost me" cannot decide whether the system is
worth running. Say the number every time, unprompted.
