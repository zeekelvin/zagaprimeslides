#!/usr/bin/env python3
"""
ZagaPrime Hub — Index Builder
Scans all collection directories, rebuilds /index.html, and creates slide galleries.
Run: python scripts/build_index.py
"""
import glob
import html
import json
import os

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"scripts", ".vercel", ".git", "node_modules"}

def get_collections():
    cols = []
    for item in sorted(os.listdir(HUB)):
        if item.startswith(".") or item in SKIP: continue
        path = os.path.join(HUB, item)
        if not os.path.isdir(path): continue
        slides_path = os.path.join(path, "slides")
        if not os.path.exists(slides_path): continue

        # Count slides
        pngs = glob.glob(os.path.join(slides_path, "**", "*.png"), recursive=True)

        # Find first cover PNG for thumbnail
        covers = sorted([p for p in pngs if "COVER" in p or "01_" in os.path.basename(p)])
        thumb = None
        if covers:
            rel = os.path.relpath(covers[0], HUB).replace("\\", "/")
            thumb = rel

        # Read meta.json if exists
        meta_path = os.path.join(path, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
        else:
            meta = {"slug": item, "title": item.replace("-", " ").title()}

        has_html = os.path.exists(os.path.join(path, "index.html"))

        # Count carousels (subdirs in slides/)
        subdirs = [d for d in os.listdir(slides_path) if os.path.isdir(os.path.join(slides_path, d))]
        carousel_count = len(subdirs) if subdirs else 1

        slide_groups = []
        direct_pngs = sorted(
            [
                p for p in glob.glob(os.path.join(slides_path, "*.png"))
                if os.path.isfile(p)
            ]
        )
        if direct_pngs:
            slide_groups.append({
                "name": meta.get("title", item),
                "slides": [
                    os.path.relpath(p, HUB).replace("\\", "/")
                    for p in direct_pngs
                ],
            })

        for subdir in sorted(subdirs):
            subdir_path = os.path.join(slides_path, subdir)
            subdir_pngs = sorted(glob.glob(os.path.join(subdir_path, "*.png")))
            if not subdir_pngs:
                continue
            slide_groups.append({
                "name": subdir.replace("_", " "),
                "slides": [
                    os.path.relpath(p, HUB).replace("\\", "/")
                    for p in subdir_pngs
                ],
            })

        cols.append({
            "slug": item,
            "title": meta.get("title", item),
            "slides": len(pngs),
            "carousels": carousel_count,
            "thumb": thumb,
            "has_html": has_html,
            "slide_groups": slide_groups,
        })
    return cols

def build_html(collections):
    cards = ""
    for c in collections:
        thumb_html = f'<img src="/{c["thumb"]}" alt="{c["title"]}" onerror="this.style.display=\'none\'">' if c["thumb"] else '<div class="no-thumb">No preview</div>'
        cards += f"""
    <div class="card">
      <div class="card-thumb">{thumb_html}</div>
      <div class="card-body">
        <div class="card-slug">{c["slug"]}</div>
        <div class="card-title">{c["title"]}</div>
        <div class="card-meta">{c["carousels"]} carousel{"s" if c["carousels"]!=1 else ""} · {c["slides"]} slides</div>
        <div class="card-actions">
          <a href="/{c["slug"]}/slides" class="btn btn-slides">View Slides</a>
          <a href="/{c["slug"]}" class="btn btn-pkg">View Collection</a>
        </div>
      </div>
    </div>"""

    count_txt = f"{len(collections)} collection{'s' if len(collections)!=1 else ''}"
    total_slides = sum(c["slides"] for c in collections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ZagaPrime AI Hub — Carousel Library</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FAF7F2;--dark:#18100A;--terra:#C46945;--terra-l:#E8A87C;--terra-d:#9B4B2A;--line:#E0D8CE;--muted:#8A7D72;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--dark);font-family:'DM Sans',sans-serif;min-height:100vh;}}
.hero{{background:var(--dark);padding:52px 48px 44px;position:relative;overflow:hidden;}}
.hero::after{{content:'';position:absolute;right:-60px;top:-60px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(196,105,69,.18) 0%,transparent 70%);pointer-events:none;}}
.brand{{font-family:'DM Mono',monospace;font-size:11px;color:var(--terra-l);letter-spacing:3px;text-transform:uppercase;margin-bottom:20px;}}
h1{{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(32px,5vw,56px);line-height:1.05;color:#fff;margin-bottom:12px;}}
h1 em{{font-style:normal;color:var(--terra-l);}}
.hero-sub{{color:rgba(255,255,255,.4);font-size:15px;font-weight:300;max-width:520px;line-height:1.7;}}
.stats{{display:flex;gap:40px;margin-top:36px;padding-top:32px;border-top:1px solid rgba(255,255,255,.07);flex-wrap:wrap;}}
.sn{{font-family:'Syne',sans-serif;font-weight:800;font-size:34px;color:var(--terra-l);line-height:1;}}
.sl{{font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.3);text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;}}
.notice{{background:var(--terra);padding:12px 48px;font-family:'DM Mono',monospace;font-size:12px;color:#fff;letter-spacing:.3px;}}
.main{{max-width:1200px;margin:0 auto;padding:48px 48px 80px;}}
.section-head{{margin-bottom:28px;}}
.section-head h2{{font-family:'Syne',sans-serif;font-weight:800;font-size:22px;}}
.section-head p{{font-size:14px;color:var(--muted);margin-top:6px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;}}
.card{{background:#fff;border:1px solid var(--line);transition:border-color .15s,transform .15s;}}
.card:hover{{border-color:var(--terra);transform:translateY(-3px);}}
.card-thumb{{height:200px;overflow:hidden;background:var(--dark);display:flex;align-items:center;justify-content:center;}}
.card-thumb img{{width:100%;height:100%;object-fit:cover;}}
.no-thumb{{color:rgba(255,255,255,.2);font-family:'DM Mono',monospace;font-size:12px;}}
.card-body{{padding:20px;}}
.card-slug{{font-family:'DM Mono',monospace;font-size:10px;color:var(--terra);letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;}}
.card-title{{font-family:'Syne',sans-serif;font-weight:700;font-size:17px;margin-bottom:6px;}}
.card-meta{{font-size:12px;color:var(--muted);margin-bottom:14px;}}
.card-actions{{display:flex;gap:8px;flex-wrap:wrap;}}
.btn{{padding:8px 18px;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;text-decoration:none;transition:.15s;}}
.btn-slides{{border:1px solid var(--line);color:var(--muted);}}
.btn-slides:hover{{background:var(--dark);color:#fff;border-color:var(--dark);}}
.btn-pkg{{background:var(--terra);color:#fff;border:1px solid var(--terra);}}
.btn-pkg:hover{{background:var(--terra-d);border-color:var(--terra-d);}}
.footer{{background:var(--dark);padding:32px 48px;text-align:center;}}
.footer p{{font-family:'DM Mono',monospace;font-size:12px;color:rgba(255,255,255,.3);}}
.footer strong{{color:var(--terra-l);}}
@media(max-width:640px){{.hero,.main,.notice,.footer{{padding-left:20px;padding-right:20px;}}}}
</style>
</head>
<body>
<div class="hero">
  <div class="brand">ZAGAPRIME AI HUB</div>
  <h1>Carousel <em>Library.</em></h1>
  <p>All ZagaPrime Instagram carousel sets — slides, captions, and packages. Each collection is a deployable content drop.</p>
  <div class="stats">
    <div><div class="sn">{len(collections)}</div><div class="sl">Collections</div></div>
    <div><div class="sn">{total_slides}</div><div class="sl">Total Slides</div></div>
    <div><div class="sn">1080</div><div class="sl">px Square</div></div>
  </div>
</div>
<div class="notice">📍 From <strong>@zagaprimeai</strong> — Follow for daily AI systems, tools, and workflows that actually work.</div>
<div class="main">
  <div class="section-head">
    <h2>All Collections</h2>
    <p>{count_txt} · {total_slides} slides total · Updated automatically on every push</p>
  </div>
  <div class="grid">{cards}
  </div>
</div>
<div class="footer">
  <p><strong>ZagaPrime AI Hub</strong> · Built with Claude · Hosted on Vercel · @zagaprimeai</p>
</div>
</body>
</html>"""

def build_slides_html(collection):
    title = html.escape(collection["title"])
    slug = html.escape(collection["slug"])
    total_slides = collection["slides"]
    total_carousels = collection["carousels"]
    package_link = (
        f'<a class="btn btn-primary" href="/{slug}">View Package</a>'
        if collection["has_html"] else ""
    )

    sections = []
    for idx, group in enumerate(collection["slide_groups"], start=1):
        group_name = html.escape(group["name"])
        cards = []
        for slide_idx, slide in enumerate(group["slides"], start=1):
            slide_src = html.escape(slide)
            slide_name = html.escape(os.path.basename(slide))
            cards.append(
                f"""
        <figure class="slide-card">
          <img src="/{slide_src}" alt="{group_name} slide {slide_idx}: {slide_name}" loading="lazy">
          <figcaption>{slide_name}</figcaption>
        </figure>"""
            )

        sections.append(
            f"""
    <section class="group">
      <div class="group-head">
        <div>
          <div class="group-kicker">Carousel {idx}</div>
          <h2>{group_name}</h2>
        </div>
        <div class="group-meta">{len(group["slides"])} slides</div>
      </div>
      <div class="slides-grid">
        {''.join(cards)}
      </div>
    </section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — Slide Gallery</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FAF7F2;--bg2:#F3EDE3;--dark:#18100A;--terra:#C46945;--terra-l:#E8A87C;--terra-d:#9B4B2A;--line:#E0D8CE;--muted:#8A7D72;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--dark);font-family:'DM Sans',sans-serif;}}
.hero{{background:var(--dark);padding:52px 48px 40px;position:relative;overflow:hidden;}}
.hero::after{{content:'';position:absolute;right:-60px;top:-60px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(196,105,69,.18) 0%,transparent 70%);pointer-events:none;}}
.brand{{font-family:'DM Mono',monospace;font-size:11px;color:var(--terra-l);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;}}
h1{{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(30px,5vw,54px);line-height:1.05;color:#fff;margin-bottom:12px;max-width:760px;}}
.hero p{{color:rgba(255,255,255,.5);font-size:15px;font-weight:300;max-width:560px;line-height:1.7;}}
.stats{{display:flex;gap:32px;flex-wrap:wrap;margin-top:32px;padding-top:28px;border-top:1px solid rgba(255,255,255,.08);}}
.sn{{font-family:'Syne',sans-serif;font-weight:800;font-size:34px;color:var(--terra-l);line-height:1;}}
.sl{{font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:1.5px;margin-top:4px;}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px;}}
.btn{{padding:10px 18px;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;text-decoration:none;transition:.15s;border:1px solid var(--line);}}
.btn-primary{{background:var(--terra);border-color:var(--terra);color:#fff;}}
.btn-primary:hover{{background:var(--terra-d);border-color:var(--terra-d);}}
.btn-secondary{{color:#fff;border-color:rgba(255,255,255,.2);}}
.btn-secondary:hover{{background:#fff;color:var(--dark);border-color:#fff;}}
.main{{max-width:1240px;margin:0 auto;padding:40px 48px 80px;}}
.group{{margin-bottom:42px;}}
.group-head{{display:flex;justify-content:space-between;gap:20px;align-items:flex-end;margin-bottom:18px;padding-bottom:16px;border-bottom:1px solid var(--line);}}
.group-kicker{{font-family:'DM Mono',monospace;font-size:11px;color:var(--terra);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;}}
.group-head h2{{font-family:'Syne',sans-serif;font-size:24px;line-height:1.15;}}
.group-meta{{font-size:13px;color:var(--muted);white-space:nowrap;}}
.slides-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;}}
.slide-card{{background:#fff;border:1px solid var(--line);overflow:hidden;}}
.slide-card img{{display:block;width:100%;height:auto;background:var(--bg2);}}
.slide-card figcaption{{padding:12px 14px;font-family:'DM Mono',monospace;font-size:11px;color:var(--muted);border-top:1px solid var(--line);}}
@media(max-width:680px){{.hero,.main{{padding-left:20px;padding-right:20px;}}.group-head{{flex-direction:column;align-items:flex-start;}}}}
</style>
</head>
<body>
<div class="hero">
  <div class="brand">ZAGAPRIME AI HUB</div>
  <h1>{title}</h1>
  <p>Slide gallery for this collection. Use this page to review exports, QA filenames, and share a clean browser view of every carousel in the set.</p>
  <div class="stats">
    <div><div class="sn">{total_carousels}</div><div class="sl">Carousels</div></div>
    <div><div class="sn">{total_slides}</div><div class="sl">Slides</div></div>
    <div><div class="sn">1080</div><div class="sl">px PNG</div></div>
  </div>
  <div class="actions">
    <a class="btn btn-secondary" href="/">Back To Hub</a>
    {package_link}
  </div>
</div>
<div class="main">
  {''.join(sections)}
</div>
</body>
</html>"""

def build_collection_html(collection):
    title = html.escape(collection["title"])
    slug = html.escape(collection["slug"])
    thumb = (
        f'<img src="/{html.escape(collection["thumb"])}" alt="{title} cover preview">'
        if collection["thumb"] else '<div class="preview-empty">No preview available</div>'
    )

    groups = []
    for idx, group in enumerate(collection["slide_groups"], start=1):
        group_name = html.escape(group["name"])
        groups.append(
            f"""
      <div class="group-row">
        <div class="group-num">{idx:02d}</div>
        <div class="group-copy">
          <div class="group-name">{group_name}</div>
          <div class="group-meta">{len(group["slides"])} slides</div>
        </div>
      </div>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title} — Collection</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FAF7F2;--bg2:#F3EDE3;--dark:#18100A;--terra:#C46945;--terra-l:#E8A87C;--terra-d:#9B4B2A;--line:#E0D8CE;--muted:#8A7D72;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--dark);font-family:'DM Sans',sans-serif;}}
.hero{{background:var(--dark);padding:52px 48px 40px;position:relative;overflow:hidden;}}
.hero::after{{content:'';position:absolute;right:-60px;top:-60px;width:360px;height:360px;border-radius:50%;background:radial-gradient(circle,rgba(196,105,69,.18) 0%,transparent 70%);pointer-events:none;}}
.brand{{font-family:'DM Mono',monospace;font-size:11px;color:var(--terra-l);letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;}}
h1{{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(30px,5vw,54px);line-height:1.05;color:#fff;margin-bottom:12px;max-width:760px;}}
.hero p{{color:rgba(255,255,255,.5);font-size:15px;font-weight:300;max-width:600px;line-height:1.7;}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:28px;}}
.btn{{padding:10px 18px;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;text-decoration:none;transition:.15s;border:1px solid var(--line);}}
.btn-primary{{background:var(--terra);border-color:var(--terra);color:#fff;}}
.btn-primary:hover{{background:var(--terra-d);border-color:var(--terra-d);}}
.btn-secondary{{color:#fff;border-color:rgba(255,255,255,.2);}}
.btn-secondary:hover{{background:#fff;color:var(--dark);border-color:#fff;}}
.main{{max-width:1180px;margin:0 auto;padding:40px 48px 80px;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(280px,.8fr);gap:24px;}}
.panel{{background:#fff;border:1px solid var(--line);overflow:hidden;}}
.panel-body{{padding:24px;}}
.panel h2{{font-family:'Syne',sans-serif;font-size:22px;margin-bottom:8px;}}
.panel p{{font-size:14px;color:var(--muted);line-height:1.7;}}
.preview img{{display:block;width:100%;height:auto;background:var(--bg2);}}
.preview-empty{{padding:48px 24px;color:var(--muted);font-family:'DM Mono',monospace;font-size:12px;text-transform:uppercase;letter-spacing:1px;}}
.stats{{display:flex;gap:20px;flex-wrap:wrap;margin-top:18px;}}
.stat{{padding:12px 14px;background:var(--bg2);border:1px solid var(--line);min-width:120px;}}
.stat-num{{font-family:'Syne',sans-serif;font-size:28px;line-height:1;color:var(--terra-d);}}
.stat-lbl{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);margin-top:5px;}}
.groups{{display:flex;flex-direction:column;gap:12px;margin-top:18px;}}
.group-row{{display:flex;gap:14px;align-items:flex-start;padding:14px 0;border-top:1px solid var(--line);}}
.group-row:first-child{{border-top:none;padding-top:0;}}
.group-num{{font-family:'DM Mono',monospace;font-size:12px;color:var(--terra);padding-top:4px;}}
.group-name{{font-family:'Syne',sans-serif;font-size:16px;line-height:1.2;}}
.group-meta{{font-size:12px;color:var(--muted);margin-top:4px;}}
@media(max-width:860px){{.main{{grid-template-columns:1fr;}}}}
@media(max-width:680px){{.hero,.main{{padding-left:20px;padding-right:20px;}}}}
</style>
</head>
<body>
<div class="hero">
  <div class="brand">ZAGAPRIME AI HUB</div>
  <h1>{title}</h1>
  <p>This collection route was auto-generated so every slug in the hub has a stable landing page on Vercel, even when there is no custom captions package yet.</p>
  <div class="actions">
    <a class="btn btn-secondary" href="/">Back To Hub</a>
    <a class="btn btn-primary" href="/{slug}/slides">Open Slide Gallery</a>
  </div>
</div>
<div class="main">
  <section class="panel preview">
    {thumb}
  </section>
  <section class="panel">
    <div class="panel-body">
      <h2>Collection Overview</h2>
      <p>Use this as the default landing page for the collection. If you later create a custom captions page or guide, add `/{slug}/index.html` and it will override this generated fallback.</p>
      <div class="stats">
        <div class="stat"><div class="stat-num">{collection["carousels"]}</div><div class="stat-lbl">Carousels</div></div>
        <div class="stat"><div class="stat-num">{collection["slides"]}</div><div class="stat-lbl">Slides</div></div>
      </div>
      <div class="groups">
        {''.join(groups)}
      </div>
    </div>
  </section>
</div>
</body>
</html>"""

def build_slide_pages(collections):
    for collection in collections:
        slides_dir = os.path.join(HUB, collection["slug"], "slides")
        out = os.path.join(slides_dir, "index.html")
        with open(out, "w") as f:
            f.write(build_slides_html(collection))

def build_collection_pages(collections):
    for collection in collections:
        if collection["has_html"]:
            continue
        out = os.path.join(HUB, collection["slug"], "index.html")
        with open(out, "w") as f:
            f.write(build_collection_html(collection))

if __name__ == "__main__":
    collections = get_collections()
    build_slide_pages(collections)
    build_collection_pages(collections)
    with open(os.path.join(HUB, "index.html"), "w") as f:
        f.write(build_html(collections))
    print(f"✅ index.html rebuilt — {len(collections)} collections, {sum(c['slides'] for c in collections)} slides")
    for c in collections:
        print(f"   /{c['slug']} — {c['title']} ({c['slides']} slides)")
