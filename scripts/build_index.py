#!/usr/bin/env python3
"""
ZagaPrime Hub — Index Builder
Scans all collection directories and regenerates /index.html.
Run: python scripts/build_index.py
"""
import os, json, glob

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

        cols.append({
            "slug":     item,
            "title":    meta.get("title", item),
            "slides":   len(pngs),
            "carousels": carousel_count,
            "thumb":    thumb,
            "has_html": has_html,
        })
    return cols

def build_html(collections):
    cards = ""
    for c in collections:
        thumb_html = f'<img src="/{c["thumb"]}" alt="{c["title"]}" onerror="this.style.display=\'none\'">' if c["thumb"] else '<div class="no-thumb">No preview</div>'
        html_link = f'<a href="/{c["slug"]}" class="btn btn-pkg">View Package</a>' if c["has_html"] else ""
        cards += f"""
    <div class="card">
      <div class="card-thumb">{thumb_html}</div>
      <div class="card-body">
        <div class="card-slug">{c["slug"]}</div>
        <div class="card-title">{c["title"]}</div>
        <div class="card-meta">{c["carousels"]} carousel{"s" if c["carousels"]!=1 else ""} · {c["slides"]} slides</div>
        <div class="card-actions">
          <a href="/{c["slug"]}/slides" class="btn btn-slides">View Slides</a>
          {html_link}
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

if __name__ == "__main__":
    collections = get_collections()
    html = build_html(collections)
    out = os.path.join(HUB, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"✅ index.html rebuilt — {len(collections)} collections, {sum(c['slides'] for c in collections)} slides")
    for c in collections:
        print(f"   /{c['slug']} — {c['title']} ({c['slides']} slides)")
