---
description: First-time setup and orientation. Checks ffmpeg and the Higgsfield connection, confirms the project loaded correctly, explains the pipeline, and offers to start the first product. Use when someone opens this project for the first time, says they are set up wrong, asks how to begin, or nothing seems to be working yet.
argument-hint: []
---

Set this student up. They just opened the folder and know nothing yet. Nothing here costs credits.

Be brief and do the checks yourself rather than telling them to run things. Report each check on
one line as it passes or fails. If they write in another language, answer in theirs.

## 1. Confirm the project actually loaded

Read `CLAUDE.md` and confirm `rules.md` and `format/style.md` are present. If any are missing,
they selected the wrong folder: say so plainly, tell them to pick the `organic-factory` folder
itself rather than a folder above or below it, and stop. Nothing else matters until this passes.

## 2. ffmpeg

```
ffmpeg -version
```

If it is missing, offer to install it and run `brew install ffmpeg` once they say yes. On
Windows, point them at `winget install Gyan.FFmpeg` instead, since brew is not there.

Say what it is for in one line: without it `/edit` cannot read the competitor video, which is
the step that saves the most time.

## 3. Higgsfield

Check whether the Higgsfield MCP server is connected. If it is not, tell them to type `/mcp`,
sign in through the browser, and come back to `/start`. Do not try to authenticate for them,
you cannot.

Say what it is for: `/brand` and `/gen` need it. `/product`, `/concept`, `/prompts` and `/edit`
work without it, so they are not blocked from trying the system today.

## 4. Ask two questions, then write them down

Ask both at once, and keep it to these two:

1. What niche or kind of product are they running?
2. Have they published organic videos before? If yes, roughly how many and what worked?

Write the answers into `rules.md` under Prefer as one or two lines. This is the file that makes
the output better over time, and it starts working from the first video if it is not empty.

## 4b. Buffer, only if they ask

Publishing through Buffer needs `BUFFER_TOKEN` and `BUFFER_ORG_ID` in their shell profile plus a
public place to host the finished file. Mention that it exists, do not walk them through it on
day one, and never write a token into this project. Posting by hand works from the first video.

## 5. Explain the pipeline in ten lines, not sixty

One line per command, in order, plus which two cost credits. Then say the one thing that is
easy to get wrong: clips must be saved as `clip-1.mp4`, `clip-2.mp4` and so on in
`videos/<slug>/clips/`, because `/edit` maps clip N onto segment N by that number.

Point at `GUIDE.pdf` in the folder for the rest. Do not repeat the guide in the chat.

## 6. Offer the first run

Ask if they want to start now. If yes, run `/product` with whatever product they name. If they
have nothing in mind, suggest they run it on any product they have seen recently just to watch
the flow, since `/product` and `/concept` cost nothing.
