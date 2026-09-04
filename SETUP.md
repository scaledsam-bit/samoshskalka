# Setup

There are two steps, and Claude does the second one for you.

## 1. Open this folder in Claude Code

This is **not a file you upload into Claude.** It is a project folder that Claude Code opens.

In the Claude app: click the **Code** tab, choose **Local** as the environment, click
**Select folder**, and pick this `organic-factory` folder.

Using the terminal instead? `cd organic-factory && claude`, and accept the trust prompt the
first time so the project's permissions actually apply.

## 2. Type this

```
/start
```

That is it. It checks whether you have ffmpeg and offers to install it, checks whether
Higgsfield is connected and walks you through signing in, asks you two questions about your
niche, explains the commands, and offers to start your first product.

## If /start is not in the list

Type `/` in the prompt box. You should see **start, product, brand, concept, prompts, gen,
review, edit, post, ship, auto**. If you do not, Claude Code is pointed at the wrong folder. Go
back to step 1 and select the `organic-factory` folder itself, not a folder above or below it.

## What this does and does not do

**It does:** write every prompt in full, generate the clips if you want, check them itself and
show you what it found, **build the finished video** cut to the original's rhythm with the
original soundtrack and your hook text burned in, at 720p 60 fps, and schedule it to your Buffer
channels once you say go.

**It does not:**

- **Post behind your back.** Buffer is the scheduler and `/ship` drives it, but out of the box
  it prints the plan, waits for your go, and lands as a draft. Flip `publish_mode` to `"queue"`
  in `autopilot.json` and finished videos go into your Buffer queue and post themselves.
- **Pick your product or your concept.** It scores the product and reads the reference video,
  but the calls are yours.
- **Decide a clip is good enough.** It gives you a verdict with reasons. You have the final say.
- **Spend money on its own.** Only `/brand` and `/gen` use credits, only when you type them,
  and both show you the price first.

CapCut is now optional. The exported file is uploadable as it is, and you only open it in
CapCut if you want to nudge something the machine cannot judge.

**It can run unattended.** Every gate starts on, and you hand them over one at a time in
`autopilot.json` once a gate has stopped catching problems. `/auto <product>` then runs the whole
chain. GUIDE.pdf has a page on doing that without burning credits.

Read `GUIDE.pdf` in this folder for how the whole thing works.

## When something goes wrong

- `/start` again. It is safe to re-run and it re-checks everything.
- `/context` shows which files actually loaded. `CLAUDE.md` and `rules.md` should both be there.
- `/mcp` shows the Higgsfield connection state.
- Every command is safe to re-run. Each reads `videos/<slug>/video.json` first and skips what is
  already done, so a crash or a restart costs you neither credits nor work.
