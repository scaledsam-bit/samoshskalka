---
description: Run the whole pipeline for one video without stopping at the gates the student has chosen to hand over. Reads autopilot.json and honours it exactly. Spends credits.
argument-hint: [slug or product]
arguments: [target]
disable-model-invocation: true
---

Run the pipeline for **$target** end to end. **This spends credits.**

## 1. Read the settings first, and say them out loud

Read `autopilot.json`. If `enabled` is false, stop and say so: `/auto` does nothing until the
student turns it on, and that is deliberate.

Print, before doing anything: which gates are being passed automatically, which still stop for
them, the credit ceiling, and how many videos this run will make. If they are about to spend
money on a run where nobody is watching, they should see the shape of it first.

## 2. Hard floors that autopilot never lifts

These hold no matter what the file says. They are not preferences.

- **The credit ceiling is absolute.** `max_credits_per_video` at 0 means unset, and unset means
  ask before the first paid call. Once set, stop the moment the run would cross it, mid video if
  necessary, and write `"status": "credit_ceiling"` into `video.json`.
- **Retries stay capped** at 3 per clip and 3 per image, exactly as when a human is watching.
- **Empty wallet is a pause, not a failure.** Write `"status": "no_credits"` and stop. Never
  retry against an empty wallet.
- **`stop_after_consecutive_rejections` ends the run.** If the student rejected the last two
  videos, the settings are wrong somewhere and making a third unattended just burns credits.
- **`/ship` still obeys `publish_mode`.** On `draft` it can only create drafts. Nothing goes
  into a live queue on autopilot unless the student set `publish_mode` to `queue` themselves.

## 3. Run the chain

`/product` → `/brand` → `/concept` → `/prompts` → `/gen` → `/review` → `/edit` → `/post` → `/ship`.

Each key in `auto_approve` controls exactly one gate. Do not interpret them any other way:

| Key | The gate it passes |
|---|---|
| `product` | `/product` asking whether to continue after the Viral DNA score |
| `brand` | `/brand` waiting for the student to say **locked** |
| `plan` | `/concept` waiting for the clip plan to be approved |
| `clips` | `/review` waiting for a human verdict on the generated clips |
| `publish` | `/ship` waiting for a go, and whether `/ship` runs at all |

A gate whose key is false stops the run and waits, even in the middle of an otherwise unattended
run. `/prompts` and `/edit` have no gate and always run.

**One video per invocation** unless the student names several products. `max_videos_per_run` is
the hard ceiling on that either way: stop when the run reaches it and say so, rather than
carrying on because there is more to do.

`/review` is special. Even when `clips` is auto approved, **run the review anyway** and act on
its verdict: reroll what it says to reroll, rewrite what it says to rewrite, inside the retry
cap. Auto approving the gate means not waiting for a human, not skipping the check.

## 4. Report at the end

One block: what was made, what it cost, which gates were passed automatically, which clips were
flagged, and anything the review would have asked a human about. Then the finished file.

If a gate stopped the run, say which one and why, at the top rather than the bottom.

## 5. Keep teaching it

Autopilot does not switch off the learning loop. When the student reacts to the finished video,
their reaction still becomes a line in `rules.md`, with the because. A run nobody comments on
teaches nothing, and a system that stops learning stops being worth running unattended.
