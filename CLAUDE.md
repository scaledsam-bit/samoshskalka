# Organic factory

AI organic video for dropshipping. One product, one proven format borrowed from a competitor,
a set of Seedance clips, cut 1:1 to the original's rhythm, posted TikTok first.

@rules.md

## What this does and does not do

Out of the box every gate is on and it stops at each one. It can run the whole chain unattended,
but only for the gates the student has explicitly handed over in `autopilot.json`, and never for
the limits that file cannot lift. Nothing here becomes automatic by accident.

| Step | Who does it |
|---|---|
| Picking the product | The student. Claude only scores it |
| Picking the concept to copy | The student. Claude only reads the reference |
| Branding images | Claude generates, the student approves and says locked |
| Writing every prompt | Claude, in full |
| Generating the clips | Claude on `/gen`, **or** the student by hand in the UI. Both are supported |
| Deciding a clip is good enough | The student |
| Judging the clips | Claude probes and looks at real frames, the student has the final say |
| The edit | **Claude builds the finished file.** CapCut is optional, for touch-ups |
| Text, captions, hashtags | Claude writes the text. The student burns it in, in TikTok |
| Posting | Claude can schedule through Buffer on `/ship`, **only after an explicit go** |

Nothing publishes itself. `/ship` is the only command that can reach a platform, it schedules
rather than blasts, it defaults to landing in Buffer as a draft, and it never calls the mutation
until the student says go. Any channel Buffer is not connected to stays manual.

## How to answer

Short. Results, not essays. A ledger of clips rather than a description of a ledger. When a
command produces files, say what was produced and where, not how it was produced.

If the student writes in another language, answer in theirs. The prompts themselves are always
written in English regardless, because that is what the models read.

## The one decision that shapes every clip

Before writing any prompt, decide the route for that clip:

- **T2V route.** Prompt only, no start frame, product attached as a reference.
  This is the default. It is faster, it is cheaper, and it does not inherit a bad frame.
- **IMG route.** Rebuild the reference's first frame as an image, then animate from it.
  Use it when the clip has to match a specific viral opening frame closely, when the
  composition is doing the work, or when T2V has already failed the same clip twice.

The two source SOPs disagreed here only because they defaulted differently. The workflow doc
went image first and listed text-to-video as its escape hatch; Adam went text first and never
made images outside branding. They are one pipeline with a switch, and the switch is per clip.

## Hard rules

Read `format/style.md` before writing a single prompt. Those twelve go into every generation
and are never softened to make a stubborn prompt pass.

On top of them:

- **The character is never an image.** People are described inline in the prompt, always.
  Only the product, the packaging and the store design are ever attached as references.
- **The product is 1:1 with the locked reference.** It is never redrawn from memory. If a
  generation comes back with a modified product, that is a reroll, not a keeper.
- **No text and no music inside a generated clip.** The hook text is burned in once, at the end,
  by `/edit`. A clip that comes back with its own text on it is a reroll.
- **Object counts carry across shots.** Three items in the box means three in every later frame.
- **When a prompt keeps failing, rewrite it shorter.** Overstuffed motion description is the
  most common cause of a bad generation. Never fix a failure by adding detail.
- **Every rejection becomes a rule.** Whenever the student rejects or praises something at any
  gate, append one line to `rules.md` in their words, with the because, without being asked.
  This is the only part of the system that makes the output better rather than merely faster,
  and it stops working the moment it becomes optional.

## Pipeline

| Command | What it does | Gate |
|---|---|---|
| `/start` | First-time setup: ffmpeg, Higgsfield, orientation | Run once, on day one |
| `/product <name>` | Intake, Viral DNA score, reference photos registered | You approve the product |
| `/brand <slug>` | Name, logo, box, store concepts, then lock them | **Spends credits.** You say locked |
| `/concept <slug>` | Analyse the competitor video, build the clip plan | You approve the plan |
| `/prompts <slug>` | Write every Seedance prompt for the plan | Free. Nothing is generated |
| `/gen <slug>` | Generate the clips | **Spends credits.** Only on your command |
| `/review <slug>` | Probe and look at the clips, verdict with reasons | You approve or reject |
| `/edit <slug>` | Cut to the original's rhythm, build the finished file | Free |
| `/post <slug>` | Caption, hashtags, hook text | You approve the text |
| `/ship <slug>` | Schedule to the Buffer channels | **You say go.** Not reversible |
| `/auto <target>` | Run the whole chain, honouring `autopilot.json` | Only the gates still on |

**Autopilot.** `autopilot.json` says which gates Claude may pass on its own. Read it before
`/auto` and honour it exactly. Some things it can never lift: the credit ceiling, the retry caps,
the pause on an empty wallet, and `publish_mode`. A gate that is off is off, even mid run.

`/start` is the only command a new student needs to know. It checks their machine, explains
the rest, and hands them to `/product`. If someone is lost or nothing is working, send them there.

`/prompts` and `/gen` are deliberately separate. A student who generates in the Higgsfield or
KIE UI by hand stops at `/prompts` and never runs `/gen`, and the system still does its job.

## Money

- `/brand` and `/gen` are the only commands that spend credits. Never start a paid generation
  outside them, and never as a side effect of a question.
- Cap retries at **3 per clip**. After that keep the best take and set `"flagged": true`.
- Preflight with `get_cost: true` before a batch, and show the number before spending it.
- If credits run out: write `"status": "no_credits"` into `video.json` and stop. Do not retry
  against an empty wallet.
- Append every paid call to `videos/<slug>/costs.jsonl` as `{"stage","model","credits"}`.

## In-session vocabulary

These work inside any command and are shorthand rather than skills:

| Say | Means |
|---|---|
| `lock <element>` | Freeze camera, room, look or product for every later prompt in this session |
| `fix N <tag>` | Repair one clip: angle, identity, lighting, background, product, blur, clothing |
| `failed N` | Rewrite clip N's prompt shorter and simpler, safer wording |
| `1:1` | Recreate the attached screenshot exactly, three takes |
| `hook` / `showcase` / `handmade` | Produce only that bucket of clips |

## Files

`<slug>` is the **dated folder name** that `/product` created, for example
`2026-09-02-magnetic-lashes`. Every later command takes that same string.

```
videos/<slug>/
  video.json          state, written by every command, read first by every command
  reference.mp4      the competitor video the piece is built from  (put there by /concept)
  reference/         screenshots, when there is no video
  prompts/clip-1.txt  one finished prompt per clip                  (written by /prompts)
  clips/clip-1.mp4    the generated clips, numbered to match the plan
  cutsheet.txt        the cut sheet                                 (written by /edit)
  qa/clip-N/          frames pulled for review                      (written by /review)
  out/final.mp4       the finished 720x1280 60fps upload             (written by /edit)
  costs.jsonl         one line per paid call
```

**The clip filenames matter.** `bin/cutsheet.sh` orders clips by the last number in the
filename and maps clip N onto segment N. `clip-1.mp4`, `clip-2.mp4`, `clip-10.mp4` is correct
and sorts properly. A clip saved under any other name lands in the wrong segment silently.

## State

`video.json` carries at least these keys. Add more freely, never rename these:

```json
{
  "slug": "2026-09-02-magnetic-lashes",
  "product": "", "niche": "", "viral_dna": {"score": 0, "reasons": []},
  "status": "awaiting_product_approval",
  "locked": {"produkt": "element-uuid", "box": "element-uuid"},
  "reference": {"path": "", "cuts": [], "segments": []},
  "plan": [{"n": 1, "type": "hook", "template": "T3", "route": "T2V",
            "duration": 5.0, "desc": "", "refs": []}],
  "clips": [{"n": 1, "path": "", "status": "done", "attempts": 1, "flagged": false}]
}
```

`status` moves through: `awaiting_product_approval`, `branding`, `awaiting_plan_approval`,
`prompts_ready`, `generating`, `clips_ready`, `edited`, `published`, or `no_credits`.

All progress lives in `videos/<slug>/video.json`. Never hold it only in the conversation.

Every command reads `video.json` first and skips what is already done, so re-running after a
crash continues instead of restarting, and never re-spends on something already generated.
