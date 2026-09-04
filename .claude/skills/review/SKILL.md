---
description: Quality check the generated clips or the finished video before it goes anywhere. Runs the technical probes, looks at real frames, judges them against the plan and the locked references, and gives a verdict with reasons. Free.
argument-hint: [slug] [clips or final]
arguments: [slug, target]
disable-model-invocation: true
---

Review `videos/$slug`. Target: **$target** (empty means clips if the final does not exist yet,
otherwise the final). Nothing here costs credits.

Two automatic passes and then a human gate. Do not skip to the verdict without running both.

## 1. The technical pass

For each clip, or for the finished file:

```
./bin/qa.sh probe videos/$slug/clips/clip-<N>.mp4 <the duration the plan asks for>
```

It reports length against the plan, a frozen tail, black frames and whether audio exists, and
exits non-zero when something needs an eye. Record each result in `video.json`.

A frozen tail almost always means the motion description was too crowded and the generator ran
out of things to do. That is a `failed N` rewrite, not a reroll.

## 2. The looking pass

```
./bin/qa.sh frames videos/$slug/clips/clip-<N>.mp4 videos/$slug/qa/clip-<N> 6
```

**Read the extracted frames.** Do not judge a clip you have not looked at. For each one, check
in this order, because this is the order they fail in:

1. **Product fidelity.** Compare against the locked reference in `video.json`. Same shape, same
   colour, same label, same proportions. A drifted product is unusable, not a small problem.
2. **Burned-in text, watermarks, logos** the brief did not ask for.
3. **Hands and faces.** Extra fingers, a third hand, a face that morphs between frames.
4. **Camera.** Static where the brief said static. Compare the first and last frame: if the
   framing moved and it should not have, that is a fail.
5. **Continuity.** Same room, same light direction, objects where the previous clip left them,
   counts unchanged.
6. **Style contract.** Read `format/style.md` and check what is visible in a frame: no bokeh,
   no glamour lighting, no colour grading, no plastic skin.

For the finished video, also check the cuts land where the cut sheet says, and that the audio is
in sync with the picture at the first and the last cut.

## 3. The verdict

A short table: clip, verdict, reason. Three verdicts only:

- **pass**
- **reroll** (same prompt again, it was a bad draw)
- **rewrite** (the prompt itself is the problem, say which block)

Then say the one thing that most needs fixing across the whole set. One thing, not six.

## 4. The human gate

Show it to the student and ask them to approve or reject. Their eye beats both passes above and
it is their account it goes on.

**Whatever they say, write the lesson down.** Every rejection appends one line to `rules.md`
under Avoid, every specific piece of praise appends one under Prefer, in their words, with the
because. This is the only mechanism by which the system gets better instead of only faster, and
it works only if it happens every time, automatically, without being asked.

Note which stage caused the problem so the lesson lands where it can be used: a bad concept is a
`/concept` lesson, a bad prompt is a `/prompts` lesson, a bad draw is neither.
