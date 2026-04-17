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

**Step 3** — Push to deploy:
```bash
git add .
git commit -m "feat: add my-collection carousel set"
git push
```

Vercel auto-deploys on every push. Your new collection is live at `/my-collection`.

## Current Collections

| Path | Title | Slides |
|------|-------|--------|
| `/limiting-beliefs` | Limiting Beliefs | 60 |
| `/connectors` | Claude Connectors | 60 |
| `/codes` | 5 Secret Claude Codes | 10 |

## Creating New Carousels

Use the **SKILL.md** file in this repo as a Claude skill. Install it in your Claude environment and any carousel request will automatically use the correct design system, brand voice, and file structure.

## Tech Stack

- **Generator**: Python + Pillow (PIL)
- **Design**: Knox-inspired — Espresso / Terracotta / Cream palette, Poppins Bold
- **Hosting**: Vercel (static site, zero config)
- **Deployment**: Git push → auto-deploy
