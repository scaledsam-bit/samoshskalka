# Seedance prompt structure

Every prompt is written in **English** and follows these blocks, in this order. This is the
merge of the 13 block architecture from the AI Video Workflow doc and Appendix B from Adam's
SOP. They were the same structure at two levels of detail. Where they differed, both survive:
Adam's reference-slot header and reference-scoping block, and the workflow doc's separate
IMAGE QUALITY block.

```
<<<image_1>>> <<<image_2>>>          reference slots, in the order the student states

1  OPENING LINE
   A X-second vertical (9:16) UGC video. [Format: reveal / ASMR unboxing / review /
   discovery / hook.] Authentic iPhone-filmed aesthetic. [Overall vibe.]

2  CAMERA & FRAMING
   - camera type and how it is held: tripod / one hand / propped / overhead
   - shot type, centering, distance from subject
   - movement: COMPLETELY STATIC locked  |  natural handheld micro-shake
     (NOT stabilized, NOT gimbal)  <- whichever the brief said
   - "Natural relaxed framing, NOT cinematic, NOT artistic"

3  USE REFERENCE IMAGE [X] FOR [ELEMENT] ONLY
   Say exactly what to take from each reference, and what NOT to copy from it
   (hair / outfit / camera angle / background / layout). Skipping this block is why a
   reference bleeds into the rest of the frame.

4  IMAGE QUALITY
   Deep focus, no bokeh, standard iPhone camera, no colour grading, fine natural grain.

5  THE LOCATION
   Interior or exterior, the surface, the surrounding objects, the background.
   Light: what kind, and ALWAYS which direction it comes from.

6  [OPTIONAL] BEHIND HER / BACKGROUND LIFE
   N people or animals doing goofy things, each on their own rhythm, NOT synchronized.

7  THE AVATAR / THE HANDS / THE PERSON
   Character described INLINE: face, hair, skin, outfit, expression, age, build.
   Faceless variant: only hands visible, ONLY TWO HANDS.
   Never attach a character as an image reference. Characters are always written, not shown.

8  PRODUCT IN THE SCENE
   Where it sits, 1:1 with <<<image_X>>>, how it catches the light.

9  ACTION & DIALOGUE, TIMED PRECISELY
   Xs-Xs: what happens | the exact line spoken | how it is said | what the camera does |
          what the product does | what the background does | [CUT]
   Block by block, through to FINAL BEAT plus hold. End.

10 DIALOGUE DELIVERY
   Line by line: tone, energy, emphasis.

11 VOICE REGISTER
   warm / casual / excited, plus a human comparison ("like she is FaceTiming her friend").
   NOT performative, NOT scripted, NOT announcer.

12 SOUND DESIGN, TIMESTAMPED
   0-Xs ambience | Xs the specific sounds | NO MUSIC.

13 STYLE
   One paragraph: overall vibe plus a colour palette of 5 to 8 colours.

14 CRITICAL RULES
   Numbered, 5 to 10. Always include: camera rule, face and identity lock, hands rule,
   product 100% identical to reference, background identical first frame to last,
   single light source, cut rule, sound rule.

15 DO NOT
   The block from format/negatives.md, verbatim.
```

## Reference slots: three notations for one mechanism

| Where | How you write it | Notes |
|---|---|---|
| Higgsfield / KIE UI, by hand | `@product`, `@avatar`, `@image_1` at the very top | Bare form. Not `@product:UUID`. |
| This project, in the written prompt | `<<<image_1>>>`, `<<<image_2>>>` | Placeholder. The student maps slot to file per clip; the order is not fixed. |
| Via MCP with a saved Element | `<<<element-uuid>>>` inline in the prompt | Backend injects the image and rewrites it to `@element_name`. |

The third one is the reason `/brand` locks assets as Elements: after that, the product reference
travels by id in the prompt text and stops depending on the student attaching the right file.

## Duration

The **student** states the duration for every clip, every time. On hooks this is mandatory and
the model never guesses. Seedance 2.5 accepts 4 to 30 seconds through the API; the useful range
for this format is 3 to 15 and the table in `format/animation.md` is the one to work from.
