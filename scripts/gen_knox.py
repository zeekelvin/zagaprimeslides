from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, numpy as np

OUT = "/mnt/user-data/outputs/zagaprime_carousels"
os.makedirs(OUT, exist_ok=True)

# ─── FONTS ─────────────────────────────────────────────────────────────────
F_BOLD   = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_BDIT   = "/usr/share/fonts/truetype/google-fonts/Poppins-BoldItalic.ttf"
F_REG    = "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf"
F_MED    = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
F_MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
F_MONO_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

def fnt(path, sz):
    try: return ImageFont.truetype(path, sz)
    except: return ImageFont.load_default()

W, H = 1080, 1080

# ─── PALETTE (extracted from reference) ─────────────────────────────────────
ESPRESSO    = (18,  10,   5)    # near-black warm dark bg
DARK_BROWN  = (42,  22,   8)    # dark brown
MOCHA       = (72,  40,  18)    # mid brown
TERRA       = (196, 105,  70)   # terracotta/copper accent
TERRA_DARK  = (155,  75,  42)   # darker terra for 3D depth
TERRA_LIGHT = (220, 145, 110)   # light terra for highlights
AMBER_GLOW  = (255, 180,  60)   # warm amber glow
CREAM       = (252, 249, 244)   # slide bg (off-white warm)
NEAR_WHITE  = (248, 245, 240)
INK         = (18,  15,  12)    # near-black text
GRAY_TEXT   = (110, 100,  90)   # muted body text
DOT_COLOR   = (220, 215, 207)   # subtle grid dots
PILL_BORDER = (160, 100,  60)   # pill outline on dark slides
PAINT_COLOR = (210, 185, 160)   # paint stroke color (warm tan)

def noise(img, amt=3):
    a = np.array(img).astype(np.int16)
    n = np.random.randint(-amt, amt, a.shape, dtype=np.int16)
    return Image.fromarray(np.clip(a+n, 0, 255).astype(np.uint8))

def wrap(text, font, max_w, draw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ─── DRAW ASTERISK (3D terracotta star, like reference logo) ────────────────
def draw_asterisk(img, cx, cy, size, angle_offset=0):
    """Draw a 3D-looking 8-arm asterisk in terracotta."""
    overlay = img.copy()
    d = ImageDraw.Draw(overlay)
    arms = 8
    arm_w = max(4, int(size * 0.18))

    # Shadow layer (darker, offset down-right)
    shadow_off = max(3, int(size * 0.08))
    for i in range(arms):
        angle = math.radians(angle_offset + i * (360 / arms))
        ex = cx + shadow_off + math.cos(angle) * size
        ey = cy + shadow_off + math.sin(angle) * size
        d.line([(cx+shadow_off, cy+shadow_off), (ex, ey)],
               fill=TERRA_DARK, width=arm_w+2)

    # Main arms
    for i in range(arms):
        angle = math.radians(angle_offset + i * (360 / arms))
        ex = cx + math.cos(angle) * size
        ey = cy + math.sin(angle) * size
        d.line([(cx, cy), (ex, ey)], fill=TERRA, width=arm_w)

    # Center cap
    cr = int(arm_w * 0.9)
    d.ellipse([cx-cr, cy-cr, cx+cr, cy+cr], fill=TERRA_LIGHT)

    # Arm tips (lighter)
    for i in range(arms):
        angle = math.radians(angle_offset + i * (360 / arms))
        tx = cx + math.cos(angle) * size
        ty = cy + math.sin(angle) * size
        tr = max(2, int(arm_w * 0.55))
        d.ellipse([tx-tr, ty-tr, tx+tr, ty+tr], fill=TERRA_LIGHT)

    return Image.alpha_composite(img.convert('RGBA'), overlay.convert('RGBA')).convert('RGB')

# ─── DOT GRID (like reference inner slides) ────────────────────────────────
def add_dot_grid(draw, spacing=54, dot_r=1):
    for x in range(0, W+spacing, spacing):
        for y in range(0, H+spacing, spacing):
            draw.ellipse([x-dot_r, y-dot_r, x+dot_r, y+dot_r], fill=DOT_COLOR)

# ─── PAINT STROKE BEHIND CATEGORY WORD ─────────────────────────────────────
def draw_paint_stroke(img, x, y, w, h):
    """Warm tan watercolor-like brush stroke behind category text."""
    stroke_layer = Image.new('RGBA', (W, H), (0,0,0,0))
    sd = ImageDraw.Draw(stroke_layer)

    # Main stroke body — irregular horizontal blob
    # Draw multiple overlapping ellipses slightly offset for organic look
    offsets = [
        (0,   0,   w,      h,    180),
        (-20, -5,  w+10,   h-10, 140),
        (10,  3,   w-15,   h+8,  160),
        (-10, -8,  w+20,   h-5,  120),
    ]
    for ox, oy, sw, sh, alpha in offsets:
        c = (*PAINT_COLOR, alpha)
        sd.ellipse([x+ox, y+oy, x+ox+sw, y+oy+sh], fill=c)

    stroke_layer = stroke_layer.filter(ImageFilter.GaussianBlur(radius=18))
    return Image.alpha_composite(img.convert('RGBA'), stroke_layer).convert('RGB')

# ─── WARM GLOW (for dark slides) ────────────────────────────────────────────
def add_warm_glow(img, cx, cy, radius, color, max_alpha=80):
    glow = Image.new('RGBA', (W, H), (0,0,0,0))
    gd   = ImageDraw.Draw(glow)
    steps = 12
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = int(max_alpha * (1 - i/steps) * (i/steps) * 3.5)
        a = min(a, max_alpha)
        gd.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=40))
    return Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB')

# ─── PILL / CAPSULE TEXT (for cover slide) ──────────────────────────────────
def draw_pill_text(draw, text, cx, y, font, fill_col, border_col, text_col, pad_x=32, pad_y=14):
    tw  = int(draw.textlength(text, font=font))
    th  = font.size
    bw  = tw + pad_x*2
    bh  = th + pad_y*2
    bx0 = cx - bw//2
    by0 = y
    bx1 = cx + bw//2
    by1 = y + bh
    r   = bh // 2
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=r, fill=fill_col, outline=border_col, width=3)
    draw.text((cx - tw//2, by0 + pad_y), text, font=font, fill=text_col)
    return bh + 8

# ─── SPLIT-COLOR CATEGORY WORD ──────────────────────────────────────────────
def draw_split_category(draw, text, x, y, font_size=112):
    """First ~half of letters in terracotta, rest near-black — like reference."""
    fb = fnt(F_BOLD, font_size)
    split = max(1, len(text) // 2)
    part1 = text[:split]
    part2 = text[split:]
    w1 = int(draw.textlength(part1, font=fb))
    draw.text((x, y), part1, font=fb, fill=TERRA)
    draw.text((x + w1, y), part2, font=fb, fill=INK)
    return int(draw.textlength(text, font=fb)), int(fb.size * 1.15)

# ───────────────────────────────────────────────────────────────────────────
# SLIDE TYPE 1: DARK COVER SLIDE
# ───────────────────────────────────────────────────────────────────────────
def make_cover_slide(carousel_num, total_carousels, main_text_lines, pill_texts, tagline):
    """Dark espresso bg, centered asterisk, pill text labels."""
    img = Image.new('RGB', (W, H), ESPRESSO)

    # Warm glow — upper-left area
    img = add_warm_glow(img, 260, 340, 480, AMBER_GLOW, max_alpha=70)
    # Secondary glow right
    img = add_warm_glow(img, 820, 600, 300, (180, 80, 30), max_alpha=30)

    # Large asterisk centered-upper
    img = draw_asterisk(img, W//2, 300, 200, angle_offset=90)

    draw = ImageDraw.Draw(img)

    # Top brand label
    fb_sm = fnt(F_BOLD,  22)
    fr_sm = fnt(F_REG,   19)
    draw.text((46, 46), "ZAGAPRIME", font=fb_sm, fill=(*TERRA, 255))
    tw = int(draw.textlength("ZAGAPRIME", font=fb_sm))
    draw.text((46 + tw + 10, 49), "AI HUB", font=fr_sm, fill=(*GRAY_TEXT, 180))

    # Carousel dot indicator top-right
    dot_r=5; gap=18
    sx = W - 50 - total_carousels*gap
    for i in range(total_carousels):
        cx_d = sx + i*gap
        fill = (*TERRA, 255) if i == carousel_num-1 else (*GRAY_TEXT, 80)
        draw.ellipse([cx_d-dot_r, 52-dot_r, cx_d+dot_r, 52+dot_r], fill=fill)

    # Main text block — centered below asterisk
    cy = 540
    fb_lg = fnt(F_BOLD, 68)
    fb_md = fnt(F_BOLD, 58)

    for i, line in enumerate(main_text_lines):
        if isinstance(line, tuple) and line[0] == 'pill':
            # Pill label
            fp = fnt(F_BOLD, 52)
            pill_h = draw_pill_text(draw, line[1], W//2, cy,
                                    font=fp,
                                    fill_col=(60, 30, 10, 120),
                                    border_col=(*PILL_BORDER, 220),
                                    text_col=(255, 255, 255, 255))
            cy += pill_h + 10
        else:
            tw = int(draw.textlength(line, font=fb_lg))
            draw.text((W//2 - tw//2, cy), line, font=fb_lg, fill=(255, 255, 255))
            cy += int(fb_lg.size * 1.2)

    # Arrow → bottom right (like reference)
    arrow_font = fnt(F_BOLD, 72)
    draw.text((W - 130, H - 160), "->", font=arrow_font, fill=(*TERRA_LIGHT, 180))

    # Bottom brand info
    fi = fnt(F_REG, 20)
    draw.text((60, H - 75), f"@zagaprimeai", font=fi, fill=(*GRAY_TEXT, 180))
    dot_txt = "·"
    dw = int(draw.textlength(dot_txt, font=fi))
    draw.text((60 + int(draw.textlength("@zagaprimeai", font=fi)) + 14, H-75), dot_txt, font=fi, fill=(*GRAY_TEXT, 100))
    draw.text((60 + int(draw.textlength("@zagaprimeai", font=fi)) + 30, H-75), "zagaprime.ai", font=fi, fill=(*GRAY_TEXT, 140))

    return noise(img, 6)

# ───────────────────────────────────────────────────────────────────────────
# SLIDE TYPE 2: LIGHT INNER SLIDE
# ───────────────────────────────────────────────────────────────────────────
def make_inner_slide(carousel_num, slide_num, total_slides,
                     category_word, headline, body_lines):
    """White bg, dot grid, paint stroke category, bold headline, body."""
    img  = Image.new('RGB', (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # Dot grid
    add_dot_grid(draw)

    # ── Category word + paint stroke (top-left)
    fb_cat = fnt(F_BOLD, 108)
    cat_w  = int(draw.textlength(category_word, font=fb_cat))
    cat_h  = int(fb_cat.size * 1.1)
    cat_x, cat_y = 42, 52

    # Paint stroke behind category word
    stroke_w = cat_w + 40
    stroke_h = int(cat_h * 0.72)
    img  = draw_paint_stroke(img, cat_x - 10, cat_y + int(cat_h*0.18),
                              stroke_w, stroke_h)
    draw = ImageDraw.Draw(img)
    add_dot_grid(draw)  # redraw grid on top of stroke

    # Category text — split color
    draw_split_category(draw, category_word, cat_x, cat_y, font_size=108)

    # ── Small asterisk top-right
    img  = draw_asterisk(img, W - 120, 115, 80, angle_offset=15)
    draw = ImageDraw.Draw(img)
    add_dot_grid(draw)  # keep grid visible

    # ── Slide counter (top right, small)
    fm = fnt(F_MED, 18)
    slide_label = f"{slide_num:02d}/{total_slides:02d}"
    sw = int(draw.textlength(slide_label, font=fm))
    draw.text((W - 50 - sw, 50), slide_label, font=fm, fill=(*GRAY_TEXT, 180))

    # ── Brand watermark (top left, very small)
    fxs = fnt(F_BOLD, 16)
    draw.text((42, 30), "ZAGAPRIME  AI HUB", font=fxs, fill=(*TERRA_DARK, 120))

    # ── Headline (bold, large, below category)
    hy = cat_y + cat_h + 36
    fb_h = fnt(F_BOLD, 52 if len(headline) < 60 else 44 if len(headline) < 85 else 38)
    h_lines = wrap(headline, fb_h, W - 84, draw)
    h_lh = int(fb_h.size * 1.28)
    for line in h_lines:
        draw.text((42, hy), line, font=fb_h, fill=INK)
        hy += h_lh

    # ── Thin terra rule below headline
    hy += 14
    draw.rectangle([42, hy, 180, hy+4], fill=TERRA)
    hy += 28

    # ── Body content
    fb_body = fnt(F_BOLD,  32)
    fr_body = fnt(F_REG,   30)
    fm_body = fnt(F_MED,   30)
    body_lh = 48

    for raw in body_lines:
        if hy > H - 130: break
        if raw == "":
            hy += 20; continue

        is_arrow = raw.startswith("->")
        content  = raw[1:].strip() if is_arrow else raw

        if is_arrow:
            # Arrow bullet with terra accent
            aw = int(draw.textlength("→  ", font=fb_body))
            draw.text((42, hy), "->", font=fb_body, fill=TERRA)
            _draw_body_inline(draw, content, fb_body, fr_body, 42+aw, hy, W-84-aw)
            hy += body_lh
        else:
            wlines = wrap(content, fr_body, W-84, draw)
            for l in wlines:
                if hy > H-130: break
                if "**" in l:
                    _draw_bold_inline_light(draw, l, fb_body, fr_body, 42, hy)
                else:
                    draw.text((42, hy), l, font=fr_body, fill=GRAY_TEXT)
                hy += body_lh

    # ── Bottom thin terra line
    draw.rectangle([0, H-10, W, H], fill=TERRA)

    return noise(img, 3)

def _draw_bold_inline_light(draw, text, fb, fr, x, y):
    parts = text.split("**")
    px = x
    for i, p in enumerate(parts):
        if not p: continue
        f  = fb if i%2==1 else fr
        c  = INK if i%2==1 else GRAY_TEXT
        draw.text((px, y), p, font=f, fill=c)
        px += int(draw.textlength(p, font=f))

def _draw_body_inline(draw, text, fb, fr, x, y, max_w):
    parts = text.split("**")
    px = x
    for i, p in enumerate(parts):
        if not p: continue
        f = fb if i%2==1 else fr
        c = INK if i%2==1 else GRAY_TEXT
        wds = p.split(" ")
        buf = ""
        for w in wds:
            test = (buf+" "+w).strip()
            if px + draw.textlength(test, font=f) <= x + max_w:
                buf = test
            else:
                if buf:
                    draw.text((px, y), buf, font=f, fill=c)
                    px += int(draw.textlength(buf, font=f))
                buf = w
        if buf:
            draw.text((px, y), buf, font=f, fill=c)
            px += int(draw.textlength(buf, font=f))

# ───────────────────────────────────────────────────────────────────────────
# SLIDE TYPE 3: DARK CLOSE/CTA SLIDE
# ───────────────────────────────────────────────────────────────────────────
def make_cta_slide(carousel_num, slide_num, total_slides, cta_word,
                   headline_lines, body_lines):
    """Dark mocha bg, subtle grid, bold white text, terra CTA box."""
    img  = Image.new('RGB', (W, H), (28, 15, 6))
    draw = ImageDraw.Draw(img)

    # Subtle dark grid
    for x in range(0, W+60, 60):
        draw.line([(x,0),(x,H)], fill=(50,30,14,))
    for y in range(0, H+60, 60):
        draw.line([(0,y),(W,y)], fill=(50,30,14))

    # Warm glow bottom-right
    img  = add_warm_glow(img, W-200, H-200, 500, TERRA, max_alpha=50)
    img  = add_warm_glow(img, 150, 200, 350, AMBER_GLOW, max_alpha=35)

    # Small asterisk top-left (logo area)
    img  = draw_asterisk(img, 100, 100, 65, angle_offset=22)

    draw = ImageDraw.Draw(img)

    # Brand label next to asterisk
    fb_brand = fnt(F_BOLD, 20)
    draw.text((170, 82), "ZAGAPRIME AI HUB", font=fb_brand, fill=(*TERRA_LIGHT, 200))

    # Slide counter
    fm = fnt(F_MED, 18)
    sl = f"{slide_num:02d}/{total_slides:02d}"
    draw.text((W-50-int(draw.textlength(sl,font=fm)), 82), sl, font=fm, fill=(*GRAY_TEXT, 140))

    # ── Headline — large bold white + italic emphasis
    fb_xl = fnt(F_BOLD,  78)
    fi_xl = fnt(F_BDIT,  78)
    fb_lg = fnt(F_BOLD,  68)

    hy = 200
    for line in headline_lines:
        if isinstance(line, tuple) and line[0] == 'italic':
            f = fi_xl
            tw = int(draw.textlength(line[1], font=f))
            draw.text((60, hy), line[1], font=f, fill=(255,255,255))
            hy += int(f.size * 1.2)
        else:
            f = fb_xl if len(line) < 20 else fb_lg
            tw = int(draw.textlength(line, font=f))
            draw.text((60, hy), line, font=f, fill=(255,255,255))
            hy += int(f.size * 1.2)

    # Terra underline
    hy += 10
    draw.rectangle([60, hy, 220, hy+5], fill=TERRA)
    hy += 32

    # Body text (white/muted)
    fb_b = fnt(F_BOLD, 30)
    fr_b = fnt(F_REG,  30)
    lh   = 48

    for raw in body_lines:
        if hy > H - 200: break
        if raw == "":
            hy += 18; continue
        wlines = wrap(raw, fr_b, W-120, draw)
        for l in wlines:
            if hy > H-200: break
            if "**" in l:
                parts = l.split("**")
                px = 60
                for i, p in enumerate(parts):
                    if not p: continue
                    f = fb_b if i%2==1 else fr_b
                    c = (255,255,255) if i%2==1 else (180,165,150)
                    draw.text((px, hy), p, font=f, fill=c)
                    px += int(draw.textlength(p, font=f))
            else:
                draw.text((60, hy), l, font=fr_b, fill=(180,165,150))
            hy += lh

    # ── CTA Box
    box_y = H - 155
    fb_cta = fnt(F_BOLD, 29)
    cta_text = f'Drop  "{cta_word}"  in the comments to get your free guide'
    ct_w    = int(draw.textlength(cta_text, font=fb_cta))
    bx0, bx1 = 60, W-60
    draw.rounded_rectangle([bx0, box_y, bx1, box_y+62], radius=10,
                            fill=(*TERRA, 30), outline=(*TERRA, 200), width=2)
    draw.text((W//2 - ct_w//2, box_y+17), cta_text, font=fb_cta, fill=(*TERRA_LIGHT, 255))

    # Bottom
    draw.text((60, H-60), "@zagaprimeai", font=fnt(F_REG,20), fill=(*GRAY_TEXT, 140))

    return noise(img, 6)

# ─── CAROUSEL DATA ─────────────────────────────────────────────────────────
# Structure: cover → 7 inner slides → 1 cta = 9 slides


# ── DATA AND GENERATION LOOP GO IN YOUR CAROUSEL-SPECIFIC SCRIPT ──
# Import this file and use the make_* functions above.
