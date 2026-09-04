---
description: Build the brand around the product (name, logo, retail box, store concepts) with Nano Banana Pro, then lock the approved assets as reusable references. This command spends credits.
argument-hint: [slug]
arguments: [slug]
disable-model-invocation: true
---

Brand `videos/$slug`. **This command spends credits.** Read `video.json` first and skip
whatever is already locked, so a re-run continues rather than restarting.

This is the **only** phase that makes images. Every later clip is text to video with these
locked assets attached. That is the whole reason the images here have to be right.

## 1. Name and direction

Propose 5 names with one line each on which tribe the name is talking to. Two directions:

- **Cartoon retro badge family** (the SpeedNest, PEAKBEAT, ToastyToes shape)
- **Niche specific** (the Snoozly, LUCID shape), built from the tribe rather than the category

Ask which direction before generating anything.

## 2. Generate

`generate_image` with `model: "nano_banana_pro"`, `resolution: "2k"`. In order:

1. Logo
2. Retail box or packaging, one per product edition if there are several
3. Store concepts, only if the student wants them: how it looks on the Shopify page

Preflight the batch with `get_cost: true` and show the number before spending it.

Attach the product reference photos to every generation. The product in the box render must be
the actual product, not a redrawn approximation.

Iterate until the student says **locked**. Cap at 3 paid attempts per asset; after that keep
the best and set `"flagged": true`.

## 3. Lock

Once the student says locked, register each approved asset as a reusable reference element:
`show_reference_elements` with `action: "create"`.

Write the returned element ids into `video.json` under `"locked"`. From this point on, every
prompt references the product by that id as `<<<element-uuid>>>` and the student stops having
to attach the right file to the right generation. This is what "locked" actually buys.

Nothing after this phase draws the product or the box from imagination. Ever.

## 4. Log and stop

Append every paid call to `costs.jsonl`. If credits run out, set `"status": "no_credits"` and
stop. Show the locked set and ask to continue to `/concept`.
