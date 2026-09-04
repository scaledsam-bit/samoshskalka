---
description: Intake a new product, score it against the Viral DNA filter, register its reference photos and open the state file. Nothing is generated and nothing is paid for.
argument-hint: [product name, link or photos]
arguments: [product]
disable-model-invocation: true
---

New product: **$product**

Read `products.csv` first. If the same product or the same niche plus format combination is
already in there, say so before anything else. Running the same concept twice cannibalises both.

## 1. Viral DNA score

Score the product out of 6, one line each, and say the number out loud:

1. **Niche identity.** Does it speak to a clear tribe (boy moms, FarmTok, ravers)?
2. **Novel format.** Is the object itself new to look at?
3. **Giftability.** Would someone buy it for another person?
4. **Portable proof of concept.** Does it demonstrate in a single shot, with no explaining?
5. **Meme and share potential.** Is there a reason to send it to a friend?
6. **"Where has this been my whole life".** Does it solve something the viewer already resents?

Under 4 out of 6: say plainly that it is weak and which two axes are missing. Do not soften it.

## 2. Reference photos

The student supplies the product photos, screenshots or a link. These are the holy base for
the entire rest of the pipeline, so check them before accepting:

- The product is fully visible, not cropped
- No competitor watermark, no competitor face
- At least one shot with a readable label or logo if the product has one

## 3. Open the state file

Create `videos/<YYYY-MM-DD>-<slug>/video.json` with the product, the niche, the score with its
reasoning, and the reference photo paths. Set `"status": "awaiting_product_approval"`.

Copy the product photos into `videos/<slug>/reference/` so they stop depending on wherever the
student happened to leave them.

**Say the full folder name out loud and tell the student that is the `<slug>` every later
command takes**, date included. Getting this wrong is the most common way the next command
looks broken when it is not.

## 4. Stop

Show the score and ask whether to continue to branding. Generate nothing.
