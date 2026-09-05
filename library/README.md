# Reusable clips

Acts 2 and 3 do not change between videos. They are generated **once per product**, kept here,
and copied into each new video's `clips/` folder at generation time. Only the hook is new.

```
library/<product-slug>/
  kit.json            the standing caption, hashtags, hook text and sound for this product
  prompts/unbox.txt   the prompt that produced the clip, kept so it can be regenerated
  prompts/showcase.txt
  clips/unbox.mp4     generated once, reused in every video
  clips/showcase.mp4
  sound.mp3           the standing audio bed, if there is one
```

## The rule

`/gen` generates the hook only. Before it starts, it copies the library clips into
`videos/<slug>/clips/` under the right clip numbers, and it never re-spends on a clip that
already exists here. Regenerating a library clip is a deliberate act, not a side effect:
the student asks for it by name.

## Numbering

`bin/cutsheet.sh` maps clip N onto segment N by the last number in the filename, so the copies
are named for their position in the plan, not for what they are: a two-clip hook makes the
unboxing `clip-3.mp4` and the showcase `clip-4.mp4`.
