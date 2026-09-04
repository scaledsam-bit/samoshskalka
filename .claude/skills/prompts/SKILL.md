---
description: Write the full English Seedance prompt for every clip in the approved plan, following the fixed structure. Free. Nothing is generated and nothing is paid for.
argument-hint: [slug] [optional: hook | showcase | handmade | clip numbers]
arguments: [slug, scope]
disable-model-invocation: true
---

Write the prompts for `videos/$slug`. Scope: **$scope** (empty means every clip in the plan).

Read all five constant files first and follow them literally:
`format/style.md`, `format/structure.md`, `format/templates.md`, `format/animation.md`,
`format/negatives.md`.

The plan is already approved in `video.json`. Do not redesign it here. If a clip in the plan
is genuinely unwritable, say which one and why, and leave the rest done.

## Per clip

1. **Duration comes from the plan.** Never invent one, and never round a hook's duration.
2. **Route from the plan.** IMG clips get two prompts: the Nano Banana Pro image prompt using
   the CRITICAL KEEP / CRITICAL CHANGE / DO NOT structure, then the animation prompt for it.
   T2V clips get one prompt.
3. **Fill every block** from `format/structure.md`, in order. An empty block is a decision not
   made, not a block that did not apply.
4. **Map the reference slots** to the locked elements from `video.json`, in the order the plan
   states. Write the mapping above the prompt in plain language so the student can attach the
   right files if they generate in the UI by hand.
5. **The character is written inline.** Never as an attached image.
6. Close with CRITICAL RULES and the DO NOT block verbatim.

## Output

Write each prompt to `videos/$slug/prompts/clip-<N>.txt` as clean, copy-pasteable text with no
commentary inside the file. The student may be pasting this straight into Higgsfield or KIE AI.

In the chat, print a short ledger only: clip number, type, route, duration, one line of what it
is. Not the prompts. They are in the files.

## If the student generates by hand

Most will. Tell them, every time, where the results have to land:

> Download every finished clip into `videos/<slug>/clips/` and name it `clip-1.mp4`,
> `clip-2.mp4` and so on, matching the clip number in the plan.

`/edit` maps clip N onto segment N by the last number in the filename. A clip left as
`download (3).mp4` silently ends up in the wrong place in the edit. This one sentence is the
difference between the cut sheet working and the cut sheet lying.

## Then stop

Say what `/gen` would cost if it ran, and wait. This command never generates.
