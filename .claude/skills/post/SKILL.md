---
description: Write the hook text, caption and hashtags, and print the TikTok-first posting checklist. Never posts anything.
argument-hint: [slug]
arguments: [slug]
disable-model-invocation: true
---

Prepare the post for `videos/$slug`.

**This command never posts.** It writes the text and lays out the options. Publishing happens
either through `/ship`, which asks first, or by hand from the phone.

## 1. Hook text

The line `/edit` burns into the video. Rules:

- Under four words wherever it can be. It plays on mute more often than not
- Not a question opener unless the format is built on one
- Say it the way the tribe says it, not the way an ad would

## 2. Caption and hashtags

- Caption: the proven shape is a short direct question plus one emoji that fits the tribe.
  "Would you get one? 👀" is the reference version. Match the emoji to the niche, not to the product
- Hashtags: for the target audience, not for the object. Boy moms, not plastic
- Say plainly if the video is AI generated and the platform expects that disclosure

## 3. Two ways to publish, they pick one

**Through Buffer:** run `/ship $slug`. It schedules the finished file to whatever channels they
have connected, staggered across the day, landing as drafts by default. Whatever Buffer is not
connected to is not covered by it.

**By hand:** the file already has the text and the sound in it, so it is one upload per platform
with nothing left to add. `videos/<slug>/out/final-text.mp4` to Google Drive, down to the phone,
then TikTok, Instagram, Facebook.

## 4. The trade off, stated once

The sound is baked in, so a TikTok post does not run on an official trending sound and will not
attach to that trend. That is the price of one file that works everywhere. When a specific trend
depends on the official sound, add it natively in TikTok for that one video and accept the extra
handling on the other platforms.

## 5. Close the loop

Append the row to `products.csv`: slug, product, niche, concept source, format, clip count,
publish date. Leave views blank. Filling it in later is what makes the log worth keeping and
what stops the next product repeating this one.
