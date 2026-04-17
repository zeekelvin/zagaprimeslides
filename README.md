# ZagaPrime AI Hub — Carousel Library

Instagram carousel slide library for ZagaPrime AI Hub. Hosted on Vercel. Every collection lives at its own path.

## Live URL
`https://zagaprime-hub.vercel.app` *(update after first deploy)*

## Structure

```
zagaprime-hub/
├── index.html                    ← Auto-generated hub gallery
├── vercel.json                   ← Vercel static config
├── SKILL.md                      ← Claude skill for consistent carousel creation
│
├── [collection-slug]/
│   ├── index.html                ← Optional: captions, codes package, etc.
│   ├── meta.json                 ← Title, description metadata
│   └── slides/
│       ├── C01_Name/
│       │   ├── 01_COVER.png
│       │   └── ...10 slides
│       └── C0N_Name/
│
└── scripts/
    ├── gen_knox.py               ← Base carousel generator (functions)
    ├── add_carousel.py           ← CLI: add new collection to hub
    └── build_index.py            ← Regenerates index.html
```

## Adding a New Carousel Set

**Step 1** — Generate slides using the ZagaPrime generator:
```bash
python your_generator.py
# slides output to /tmp/my-collection/
```

**Step 2** — Add to hub:
```bash
python scripts/add_carousel.py \
  --slug my-collection \
  --slides /tmp/my-collection/slides/ \
  --html /tmp/my-collection/index.html \
  --title "My Collection Title"
```

This rebuilds:
- `/index.html` for the hub homepage
- `/<slug>/slides/index.html` for a real browser gallery of the exported slides

**Step 3** — Push to deploy:
```bash
git add .
git commit -m "feat: add my-collection carousel set"
git push
```

Vercel auto-deploys on every push. Your new collection is live at `/my-collection`.

## One-Command Generation

Use the brief-driven generator when you want one command to create the slides, captions page, hub metadata, gallery pages, and validation output.

```bash
python3 scripts/generate_collection.py --brief briefs/example-ai-automation.json
```

If you are updating an existing slug:

```bash
python3 scripts/generate_collection.py --brief briefs/example-ai-automation.json --replace
```

The brief format is JSON for now. Start from [briefs/example-ai-automation.json](briefs/example-ai-automation.json) and adjust the collection metadata, slide copy, caption, hashtags, and CTA keyword.

## Current Collections

| Path | Title | Slides |
|------|-------|--------|
| `/limiting-beliefs` | Limiting Beliefs | 60 |
| `/connectors` | Claude Connectors | 60 |
| `/codes` | 5 Secret Claude Codes | 10 |

## Creating New Carousels

Use the **SKILL.md** file in this repo as a Claude skill. Install it in your Claude environment and any carousel request will automatically use the correct design system, brand voice, and file structure.

For repeatable prompts, start from [CONTENT_BRIEF_TEMPLATE.md](CONTENT_BRIEF_TEMPLATE.md). That gives the model the minimum structure needed to keep voice, CTA, slide flow, and deployment output aligned.
If you want the repo itself to generate the content, have the model turn that prompt into a JSON brief and run `scripts/generate_collection.py`.

## Tech Stack

- **Generator**: Python + Pillow (PIL)
- **Design**: Knox-inspired — Espresso / Terracotta / Cream palette, Poppins Bold
- **Hosting**: Vercel (static site, zero config)
- **Deployment**: Git push → auto-deploy

## Local Setup

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_index.py
python3 scripts/validate_hub.py
```

The generator writes to `ZAGAPRIME_OUT` if set; otherwise it defaults to a temp directory so it can run on a normal local machine.
