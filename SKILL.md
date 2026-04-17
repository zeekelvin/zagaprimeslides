---
name: zagaprime-carousel-creator
description: Create ZagaPrime AI Hub branded Instagram carousel slides in the Knox-inspired design system. Use this skill ANY TIME the user asks to create, generate, design, or build Instagram carousels, slides, poster images, or social media content for ZagaPrime AI Hub. Also triggers when user wants to add a new carousel set to the hub package, deploy content, or create educational AI content for Instagram. This skill captures the full design system, brand voice, content framework, and file-output pipeline so every carousel is instantly consistent and deployment-ready.
---

# ZagaPrime Carousel Creator

Generates branded Instagram carousel slide images (1080×1080px PNG) in the **Knox-inspired ZagaPrime design system**, outputs them into the hub repo structure, and keeps a deployment-ready Vercel package up to date.

---

## Brand System

**Palette**
| Token | Value | Use |
|-------|-------|-----|
| ESPRESSO | `#120A05` | Dark slide BG |
| CREAM | `(252,249,243)` | Light slide BG |
| TERRA | `(196,105,69)` | Primary accent, category word colour 1 |
| TERRA_DARK | `(155,75,42)` | Category word colour 2, shadows |
| TERRA_LIGHT | `(220,145,110)` | Arm tips, pill text |
| INK | `(18,16,24)` | Headline text |
| GRAY | `(130,118,112)` | Body text |
| DOT | `(220,215,207)` | Grid dots on light slides |
| AMBER_GLOW | `(255,180,60)` | Warm glow on dark covers |

**Fonts** (Poppins via Google Fonts — available in `/usr/share/fonts/truetype/google-fonts/`)
- `Poppins-Bold.ttf` — headlines, category word, code names
- `Poppins-BoldItalic.ttf` — italic emphasis on dark CTA slides
- `Poppins-Regular.ttf` / `Poppins-Medium.ttf` — body text
- `LiberationMono-Bold.ttf` — badges, slide counters

**Logo element**: 8-arm terracotta asterisk drawn programmatically with 3D shadow depth.

---

## Slide Architecture — 3 Types

### Type 1: COVER (dark slide)
- Background: espresso `#120A05` with warm amber glow upper-left
- Centered asterisk logo (~200px)
- Centered text with pill/capsule labels for key phrases
- Brand label top-left: `ZAGAPRIME  AI HUB`
- Progress dots top-right (one per carousel in the series)
- Arrow `→` bottom-right, subtle
- Footer: `@zagaprimeai · zagaprime.ai`

### Type 2: INNER (light slide)
- Background: warm cream `(252,249,243)` with dot grid (54px spacing, 1px dots)
- **Top-left**: Category word in large bold (96px) with **paint stroke** behind it
  - Split-colour: first ~half of letters = TERRA, rest = INK
  - Paint stroke = warm tan blur blob (`ImageFilter.GaussianBlur(18)`)
- **Top-right**: Small asterisk (75–80px) + slide counter `NN/NN`
- **Brand watermark**: `ZAGAPRIME  AI HUB` tiny text top-left above category
- **Headline**: Bold 38–64px (size scales to text length), INK colour
- **Terra rule**: 4px horizontal bar below headline
- **Body**: Regular 29–30px, gray text, supports `**bold**` inline and `→` arrow bullets
- **Bottom**: 10px TERRA bar full width

### Type 3: CLOSE (dark CTA slide)
- Background: very dark brown `(28,15,6)` with subtle square grid lines
- Warm glow bottom-right corner
- Asterisk top-left at ~65px with brand label beside it
- **Large headline**: Bold 68–78px white, italic variant for emphasis lines
- Terra underline rule
- Body text: white (bold) and warm muted (regular)
- **CTA pill box**: TERRA-outlined rounded rectangle, bottom of slide
  - Text: `Drop "[KEYWORD]" in the comments to get your free guide`
- Footer: `@zagaprimeai`

---

## Content Framework — 10-Slide Structure

```
Slide 01  COVER      Dark branded cover
Slide 02  [LABEL]    First hook/opening — use carousel-specific label (Reality, Truth, Mindset, etc.)
Slide 03  Problem    The problem being addressed
Slide 04  Cost       What it costs to ignore this
Slide 05  Shift      The mindset/frame shift needed
Slide 06  System     The ZagaPrime system/solution
Slide 07  Results    What changes / outcomes
Slide 08  Decision   The choice the reader faces
Slide 09  Moment     The crescendo / emotional peak
Slide 10  CLOSE      Dark CTA slide
```

**NEVER use "HOOK" or "CTA" as visible category words on slides.**

Category word substitution for slide 02 (first hook):
| Carousel topic | Label |
|---------------|-------|
| Limiting beliefs | Reality / The Math / Truth / Mindset / Insight / The Trap |
| Tutorial | Step 1 |
| Tools list | Truth |
| Custom (code slides) | Use the code trigger itself (e.g. `/self`) |

---

## Content Voice

- **Tone**: Direct, street-smart, technically credible, empowering — never preachy
- **Target**: SMB owners, entrepreneurs, non-technical founders, AI newbies
- **Sentence style**: Short. Punchy. Occasional one-liners that stop the scroll.
- **Bold usage** (`**text**`): Mark the key stat, transformation phrase, or call to action
- **Arrow bullets**: Use `→` not `-` or `•`
- **Limiting belief format**: Each carousel kills one belief → delivers one transformation
- **CTA keywords**: One word per carousel, all-caps (AUTOMATE, STACK, WORKFLOW, CONNECT, CODES, etc.)

---

## Python Generator System

The generator lives at `scripts/gen_knox.py` in the hub repo.

### Core functions (always copy these into new generator files)

```python
# Base canvas + aesthetic elements
make_canvas(accent_color)       # cream bg, dot grid, paint stroke setup
add_dot_grid(draw)              # 54px dot spacing, DOT_COLOR
draw_paint_stroke(img, x, y, w, h)   # warm tan blur blob
draw_asterisk(img, cx, cy, size)     # 8-arm terracotta logo
add_warm_glow(img, cx, cy, r, color) # radial glow for dark slides
draw_split_category(draw, text, x, y, font_size=96)  # split terra/ink

# Slide builders
make_cover_slide(carousel_num, total, cover_lines, [], tag)
make_inner_slide(carousel_num, slide_num, total, label, headline, body)
make_cta_slide(carousel_num, slide_num, total, cta_word, headline_lines, body)
```

### Cover line format
```python
cover_lines = [
    "Plain text line",
    ('pill', "Text inside capsule"),
    "Another plain line",
    ('pill', "Second capsule"),
]
```

### Body line format
```python
body = [
    "Regular body line",
    "**Bold text inline** using double asterisks",
    "→ Arrow bullet with **bold highlight** mid-line",
    "",   # empty string = spacing gap
]
```

---

## Repo & Deployment Structure

```
zagaprime-hub/
├── index.html                    ← Hub gallery (auto-generated)
├── vercel.json                   ← Static deploy config
├── README.md
├── SKILL.md                      ← This file
│
├── [collection-slug]/            ← One dir per carousel set
│   ├── index.html                ← Captions / interactive package (if exists)
│   └── slides/
│       ├── C01_Folder/
│       │   ├── 01_COVER.png
│       │   └── ...
│       └── C02_Folder/
│
└── scripts/
    ├── gen_knox.py               ← Base generator (functions only, no data)
    ├── add_carousel.py           ← CLI: adds a new collection to the hub
    └── build_index.py            ← Regenerates the main index.html
```

**Vercel URL pattern**:
- `/` → Main hub gallery
- `/connectors` → Connector captions & tags
- `/codes` → 100 Claude codes interactive package
- `/limiting-beliefs` → Limiting beliefs carousel set
- `/[new-collection]` → Any future addition

---

## Adding a New Carousel Set

When the user requests a new carousel set:

1. **Generate the slides** using `gen_knox.py` pattern — output to `/tmp/[slug]/`
2. **Create the collection directory** in the hub: `hub/[slug]/slides/`
3. **Copy slides** into `hub/[slug]/slides/[C0N_Name]/`
4. **If there's an HTML package** (captions, codes, etc.) → save as `hub/[slug]/index.html`
5. **Run** `scripts/build_index.py` to regenerate `hub/index.html`
6. **Commit and push** → Vercel auto-deploys

### build_index.py output format
The index page must show:
- ZagaPrime branded header (dark espresso, terracotta asterisk)
- Card grid — one card per collection
- Each card: collection name, slide count, thumbnail of first cover slide, link to `/[slug]`
- If `index.html` exists in the collection → link "View Captions / Package"
- If slides exist → link "View Slides"

---

## Output Checklist

Before marking a carousel set complete:
- [ ] 10 slides per carousel (01_COVER → 10_CLOSE)
- [ ] No "HOOK" or "CTA" visible on any slide
- [ ] All slides 1080×1080px PNG
- [ ] Cover slide has correct carousel dot count for the series
- [ ] CTA keyword visible in close slide CTA box
- [ ] Slides copied to `hub/[slug]/slides/`
- [ ] `index.html` created if captions/package exists
- [ ] `hub/index.html` regenerated via `build_index.py`
- [ ] Commit message: `feat: add [collection-name] carousel set`

---

## Reference Files

- `scripts/gen_knox.py` — Full generator with all functions. Read before generating new carousels.
- `scripts/add_carousel.py` — CLI tool. Run `python scripts/add_carousel.py --help` for usage.
- `scripts/build_index.py` — Index regenerator. Run after any addition.
