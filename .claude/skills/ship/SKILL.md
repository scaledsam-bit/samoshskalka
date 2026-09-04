---
description: Schedule the finished video to the connected Buffer channels. Prints the whole plan first and never calls the mutation without an explicit go.
argument-hint: [slug]
arguments: [slug]
disable-model-invocation: true
---

Schedule `videos/$slug` to Buffer.

**Publishing is not reversible from here.** Print the plan, wait for the student to say go, and
only then call the mutation. Never treat an earlier approval in the session as covering this one.

## Before anything

1. `video.json` must have the video approved by `/review`. If it is not, stop and say so.
2. The finished file must have the hook text burned in. Buffer uploads a file and cannot add
   text later, so a file without text ships without a hook. Check `video.json` for the burn step.
3. `BUFFER_TOKEN` and `BUFFER_ORG_ID` must be in the environment. If they are not, stop and tell
   the student to put them in their shell profile. Never write a token into this project.

## 1. The video needs a public URL

Buffer's `VideoAssetInput.url` is a required String and it takes a URL, not a file. There is no
upload endpoint, so the finished MP4 has to be reachable on the public internet first.

- If `bin/upload.sh` exists, run it with the file and use the URL it prints. The student writes
  that script for whatever host they use; this project does not pick one for them.
- If it does not exist, ask the student to upload `videos/$slug/out/final.mp4` somewhere public
  and paste the URL back.

Store the URL in `video.json`. A URL that needs a login fails at Buffer's end, not at yours.

## 2. Read the channels, do not assume them

```
{ channels(input: {organizationId: "<BUFFER_ORG_ID>"}) { id service name } }
```

POST as JSON to `https://api.buffer.com` with `Authorization: Bearer $BUFFER_TOKEN`. Not
`graph.buffer.com`, not `api.bufferapp.com`; both reject this token type.

Show the student the list and let them pick. A channel they expect but do not see is simply not
connected in Buffer, and no amount of retrying here adds it.

## 3. Build the posts

One per channel, using that channel's caption from `accounts.json` when it exists, otherwise the
caption `/post` wrote. **Stagger the times across the day.** Several accounts posting in the same
minute is a pattern, and it is the kind platforms notice.

```
mutation {
  createPost(input: {
    channelId: "<channel id>"
    text: "<caption for this channel>"
    assets: [{ video: { url: "<public mp4 url>", metadata: { title: "<slug>" } } }]
    dueAt: "<staggered ISO timestamp>"
    schedulingType: automatic
    saveToDraft: true
    aiAssisted: true
  }) { id }
}
```

**`saveToDraft: true` is the default and it is deliberate.** It lands in Buffer where the student
can look at it before anything goes out. Set it false only when they explicitly ask for the post
to go straight into the queue.

## 4. Show the plan, then wait

Print every post: channel, service, time, first line of caption, draft or queued. Then stop.
**Do not call the mutation until the student says go.**

## 5. After scheduling

Append the row to `products.csv`: slug, product, niche, concept source, format, clip count,
publish date. Leave views blank. Filling it in later is what stops the next product repeating
this one.

## The AI label

`aiAssisted` is Buffer's own marker, not Instagram's or TikTok's AI content label, and those do
not appear to be settable through Buffer. So either the disclosure lives in the caption template
or the student applies the platform's label by hand afterwards. Say which one they are choosing
rather than letting it pass silently.

## TikTok

Buffer supports TikTok as a channel, but only if the student has connected it. If TikTok is not
in the list, that one stays manual: the same finished file, uploaded from the phone. The text is
already burned in, so there is nothing to add there any more.
