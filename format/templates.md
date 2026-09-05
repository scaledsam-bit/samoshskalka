# Proven templates

Five formats that already work, plus the fallback. Pick one before writing the prompt, then
fill in the skeleton from `format/structure.md`. The template decides blocks 1, 2 and 7.

## T1 · 3-2-1 REVEAL
Static tripod. Countdown "Three... Two... One!", the cover comes down, the product is revealed.
Goofy background characters, each on their own rhythm. Hook length, 4 to 6 s.

## T2 · ASMR UNBOXING
Faceless overhead. Hands only, two hands. Tight jump cuts, crisp specific sounds, no music.
Works because the sound carries it: name every sound with its timestamp.

## T3 · SELFIE HOOK
Excited handheld, front facing, natural micro shake. Direct speech into the camera.
The one place where camera movement is correct rather than a mistake.

## T4 · UGC PRODUCT REVIEW
Mix of front and back camera. Conversational, unscripted register. Longer, 8 to 14 s.

## T5 · STORE DISCOVERY
Back camera, no face. Finding the product on a shelf. Reads as accidental, so the framing has
to be slightly wrong on purpose: off centre, a beat late.

## HOUSE · the default three act

**This is the shape unless a reference explicitly says otherwise.** Every video the student
builds is these three acts in this order, and a plan that does not have them needs a reason.

| Act | Type | Template | Camera | Length |
|---|---|---|---|---|
| 1 | hook | whichever T1-T5 the reference uses | as the reference | from the cut sheet, else 4-6 s |
| 2 | unbox | T2 · ASMR unboxing, POV | **completely static**, hands only, two hands | 6-8 s |
| 3 | showcase | GENERAL | slow handheld move in; copy the movement 1:1 if the reference has action | 7-8 s |

Act 2 is a handmade clip, so `animation.md` applies without exception: the camera does not
move even when the reference moved it. Copying a camera move into an unboxing is the single
most common reason one reads as fake.

**Only act 1 needs a reference video.** Acts 2 and 3 are formulaic and come from this file, so
the student sends the hook they want copied and describes the other two in a sentence each.

### What this costs at the edit

`bin/cutsheet.sh` maps clip N onto segment N of the reference and takes the reference's audio,
so it can only build a video **as long as the reference**. Two honest paths:

- **Reference covers all three acts.** Everything is 1:1, the cut sheet drives the whole build,
  nothing special happens. Prefer this: ask for a reference with the full shape.
- **Reference covers only the hook.** Act 1 builds 1:1 against the reference; acts 2 and 3 are
  appended after it and are not covered by the reference's rhythm or its soundtrack. Say this
  out loud in the plan rather than letting the student discover it in the export.

## GENERAL
Anything that does not fit the five. Fill the universal skeleton from `format/structure.md`
and say in the clip plan why none of the templates applied. If the same "general" shape shows
up three times, it has earned a template: write it into this file.
