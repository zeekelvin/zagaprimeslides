#!/usr/bin/env python3
"""
ZagaPrime Hub — Brief-To-Collection Generator

Creates a full collection from a JSON brief:
- renders 1080x1080 slides
- writes collection metadata
- builds a reusable captions/package page
- rebuilds the hub index + slide galleries
- validates the result

Run:
  python3 scripts/generate_collection.py --brief briefs/example-ai-automation.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from html import escape
from pathlib import Path
from typing import Any

from gen_knox import make_cover_slide, make_cta_slide, make_inner_slide

HUB = Path(__file__).resolve().parent.parent
TOTAL_SLIDES = 10


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "collection"


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    return cleaned or "Slide"


def read_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def load_brief(path: Path) -> dict[str, Any]:
    data = read_json(path)
    if "collection" not in data or "carousels" not in data:
        raise ValueError("Brief must include top-level 'collection' and 'carousels' keys.")
    if not isinstance(data["carousels"], list) or not data["carousels"]:
        raise ValueError("Brief must include at least one carousel.")
    return data


def require(value: Any, name: str) -> Any:
    if value in (None, "", []):
        raise ValueError(f"Missing required field: {name}")
    return value


def normalize_cover_lines(lines: list[Any]) -> list[Any]:
    normalized = []
    for item in lines:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict) and "pill" in item:
            normalized.append(("pill", str(item["pill"])))
        else:
            raise ValueError("cover_lines entries must be strings or objects like {'pill': 'TEXT'}")
    return normalized


def normalize_close_lines(lines: list[Any]) -> list[Any]:
    normalized = []
    for item in lines:
        if isinstance(item, str):
            normalized.append(item)
        elif isinstance(item, dict) and "italic" in item:
            normalized.append(("italic", str(item["italic"])))
        else:
            raise ValueError("close.headline_lines entries must be strings or objects like {'italic': 'TEXT'}")
    return normalized


def validate_brief(data: dict[str, Any]) -> None:
    collection = data["collection"]
    require(collection.get("slug"), "collection.slug")
    require(collection.get("title"), "collection.title")

    for idx, carousel in enumerate(data["carousels"], start=1):
        prefix = f"carousels[{idx - 1}]"
        require(carousel.get("folder"), f"{prefix}.folder")
        require(carousel.get("title"), f"{prefix}.title")
        require(carousel.get("cover_lines"), f"{prefix}.cover_lines")
        require(carousel.get("slides"), f"{prefix}.slides")
        require(carousel.get("close"), f"{prefix}.close")

        slides = carousel["slides"]
        if len(slides) != 8:
            raise ValueError(f"{prefix}.slides must contain exactly 8 entries for slides 02-09.")

        for slide_idx, slide in enumerate(slides, start=2):
            slide_prefix = f"{prefix}.slides[{slide_idx - 2}]"
            require(slide.get("label"), f"{slide_prefix}.label")
            require(slide.get("headline"), f"{slide_prefix}.headline")
            require(slide.get("body"), f"{slide_prefix}.body")
            if not isinstance(slide["body"], list):
                raise ValueError(f"{slide_prefix}.body must be a list of strings.")

        close = carousel["close"]
        require(close.get("cta_word"), f"{prefix}.close.cta_word")
        require(close.get("headline_lines"), f"{prefix}.close.headline_lines")
        require(close.get("body"), f"{prefix}.close.body")
        if not isinstance(close["body"], list):
            raise ValueError(f"{prefix}.close.body must be a list of strings.")


def render_collection_page(collection: dict[str, Any], carousels: list[dict[str, Any]]) -> str:
    title = escape(collection["title"])
    subtitle = escape(collection.get("description", "Branded ZagaPrime carousel package with captions, hooks, and CTA alignment."))
    slug = escape(collection["slug"])
    stats_total_slides = len(carousels) * TOTAL_SLIDES
    guide = collection.get("guide") or {}
    guide_html = ""
    guide_url = guide.get("url")
    if guide.get("title") or guide.get("description") or guide_url:
        link_html = f'<a class="resource-link" href="{escape(guide_url)}" target="_blank" rel="noreferrer">Open Resource</a>' if guide_url else ""
        guide_html = f"""
  <section class="resource">
    <div class="section-label">Guide</div>
    <h2>{escape(guide.get("title", "Featured Resource"))}</h2>
    <p>{escape(guide.get("description", "Add a guide link in the brief when you want this collection to drive to a hosted webpage or lead magnet."))}</p>
    {link_html}
  </section>"""

    tabs = []
    sections = []
    for idx, carousel in enumerate(carousels):
        active = " active" if idx == 0 else ""
        tab_id = f"carousel-{idx + 1}"
        hashtags = " ".join(carousel.get("hashtags", []))
        caption = carousel.get("caption", "")
        cta_word = escape(carousel["close"]["cta_word"])
        preview = f"/{slug}/slides/{escape(carousel['folder'])}/01_COVER.png"

        tags_html = "".join(
            f'<span class="tag">{escape(tag)}</span>' for tag in carousel.get("hashtags", [])
        ) or '<span class="tag muted">No hashtags supplied</span>'

        tabs.append(
            f'<button class="tab{active}" onclick="showCarousel(\'{tab_id}\', this)">{idx + 1:02d}. {escape(carousel["title"])}</button>'
        )
        sections.append(
            f"""
  <section id="{tab_id}" class="carousel-section{active}">
    <div class="carousel-head">
      <div>
        <div class="section-label">{escape(carousel["folder"])}</div>
        <h2>{escape(carousel["title"])}</h2>
        <p>{escape(carousel.get("summary", "Use the caption, CTA keyword, and slide gallery together when you post this carousel."))}</p>
      </div>
      <img class="preview" src="{preview}" alt="{escape(carousel['title'])} cover preview">
    </div>

    <div class="grid">
      <article class="panel">
        <div class="panel-head">Caption</div>
        <div class="panel-body">
          <pre class="copy-block" id="{tab_id}-caption">{escape(caption)}</pre>
          <button class="copy-btn" onclick="copyText('{tab_id}-caption', this)">Copy Caption</button>
        </div>
      </article>

      <article class="panel">
        <div class="panel-head">CTA</div>
        <div class="panel-body">
          <div class="cta-pill">Keyword: {cta_word}</div>
          <p class="panel-copy">Close slide line: Drop "{cta_word}" in the comments to get your free guide.</p>
          <a class="inline-link" href="/{slug}/slides">Open Slide Gallery</a>
        </div>
      </article>

      <article class="panel panel-wide">
        <div class="panel-head">Hashtags</div>
        <div class="panel-body">
          <div class="tags">{tags_html}</div>
          <pre class="copy-block" id="{tab_id}-hashtags">{escape(hashtags)}</pre>
          <button class="copy-btn" onclick="copyText('{tab_id}-hashtags', this)">Copy Hashtags</button>
        </div>
      </article>
    </div>
  </section>"""
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Content Package</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FAF7F2;--bg2:#F3EDE3;--ink:#18100A;--terra:#C46945;--terra-d:#9B4B2A;--terra-l:#E8A87C;--muted:#8A7D72;--line:#E0D8CE;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--ink);font-family:'DM Sans',sans-serif;}}
.hero{{background:var(--ink);padding:56px 48px 48px;position:relative;overflow:hidden;}}
.hero::after{{content:'';position:absolute;right:-80px;top:-80px;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle,rgba(196,105,69,.18) 0%,transparent 70%);}}
.brand{{position:relative;z-index:1;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:var(--terra-l);margin-bottom:18px;}}
h1{{position:relative;z-index:1;font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(34px,5vw,60px);line-height:1.05;color:#fff;max-width:760px;margin-bottom:14px;}}
.hero p{{position:relative;z-index:1;color:rgba(255,255,255,.5);font-size:15px;line-height:1.75;max-width:640px;}}
.stats{{position:relative;z-index:1;display:flex;gap:36px;flex-wrap:wrap;margin-top:34px;padding-top:28px;border-top:1px solid rgba(255,255,255,.08);}}
.stat-num{{font-family:'Syne',sans-serif;font-size:34px;color:var(--terra-l);line-height:1;}}
.stat-label{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:rgba(255,255,255,.35);margin-top:5px;}}
.hero-actions{{position:relative;z-index:1;display:flex;gap:10px;flex-wrap:wrap;margin-top:28px;}}
.btn{{display:inline-flex;align-items:center;justify-content:center;padding:10px 18px;border:1px solid var(--line);font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;text-decoration:none;transition:.15s;}}
.btn-dark{{border-color:rgba(255,255,255,.2);color:#fff;}}
.btn-dark:hover{{background:#fff;color:var(--ink);border-color:#fff;}}
.btn-fill{{background:var(--terra);border-color:var(--terra);color:#fff;}}
.btn-fill:hover{{background:var(--terra-d);border-color:var(--terra-d);}}
.main{{max-width:1180px;margin:0 auto;padding:34px 48px 80px;}}
.tabs{{display:flex;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--line);padding-bottom:18px;}}
.tab{{background:none;border:none;border-bottom:3px solid transparent;padding:10px 0;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);cursor:pointer;}}
.tab.active{{color:var(--terra);border-bottom-color:var(--terra);}}
.carousel-section{{display:none;padding-top:30px;}}
.carousel-section.active{{display:block;}}
.carousel-head{{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:24px;align-items:start;margin-bottom:24px;}}
.section-label{{font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--terra);margin-bottom:8px;}}
.carousel-head h2,.resource h2{{font-family:'Syne',sans-serif;font-size:28px;line-height:1.1;margin-bottom:10px;}}
.carousel-head p,.resource p{{font-size:14px;color:var(--muted);line-height:1.7;}}
.preview{{width:100%;border:1px solid var(--line);background:var(--bg2);}}
.grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;}}
.panel{{background:#fff;border:1px solid var(--line);}}
.panel-wide{{grid-column:1 / -1;}}
.panel-head{{padding:14px 18px;border-bottom:1px solid var(--line);font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;color:var(--muted);}}
.panel-body{{padding:18px;}}
.panel-copy{{font-size:14px;color:var(--muted);line-height:1.7;margin-top:14px;}}
.copy-block{{white-space:pre-wrap;font-family:'DM Sans',sans-serif;font-size:14px;line-height:1.8;color:var(--ink);background:var(--bg);padding:16px;border:1px solid var(--line);}}
.copy-btn{{margin-top:12px;padding:10px 16px;border:1px solid var(--line);background:#fff;color:var(--muted);font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;cursor:pointer;}}
.copy-btn:hover{{background:var(--terra);border-color:var(--terra);color:#fff;}}
.cta-pill{{display:inline-block;padding:10px 14px;background:var(--ink);color:var(--terra-l);font-family:'DM Mono',monospace;font-size:12px;letter-spacing:1.3px;text-transform:uppercase;}}
.inline-link,.resource-link{{display:inline-block;margin-top:14px;color:var(--terra-d);text-decoration:none;font-family:'DM Mono',monospace;font-size:11px;letter-spacing:1px;text-transform:uppercase;}}
.tags{{display:flex;gap:8px;flex-wrap:wrap;}}
.tag{{padding:7px 12px;background:var(--bg2);border:1px solid var(--line);font-family:'DM Mono',monospace;font-size:11px;color:var(--terra-d);}}
.tag.muted{{color:var(--muted);}}
.resource{{margin-top:34px;background:#fff;border:1px solid var(--line);padding:22px;}}
@media(max-width:900px){{.carousel-head{{grid-template-columns:1fr;}}.preview{{max-width:300px;}}.grid{{grid-template-columns:1fr;}}}}
@media(max-width:680px){{.hero,.main{{padding-left:20px;padding-right:20px;}}}}
</style>
</head>
<body>
<div class="hero">
  <div class="brand">ZAGAPRIME AI HUB</div>
  <h1>{title}</h1>
  <p>{subtitle}</p>
  <div class="stats">
    <div><div class="stat-num">{len(carousels)}</div><div class="stat-label">Carousels</div></div>
    <div><div class="stat-num">{stats_total_slides}</div><div class="stat-label">Slides</div></div>
    <div><div class="stat-num">1080</div><div class="stat-label">PNG Export</div></div>
  </div>
  <div class="hero-actions">
    <a class="btn btn-dark" href="/">Back To Hub</a>
    <a class="btn btn-fill" href="/{slug}/slides">Open Slide Gallery</a>
  </div>
</div>
<div class="main">
  <div class="tabs">
    {''.join(tabs)}
  </div>
  {''.join(sections)}
  {guide_html}
</div>
<script>
function showCarousel(id, button) {{
  document.querySelectorAll('.carousel-section').forEach((section) => section.classList.remove('active'));
  document.querySelectorAll('.tab').forEach((tab) => tab.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  button.classList.add('active');
}}
async function copyText(id, button) {{
  const text = document.getElementById(id).innerText;
  await navigator.clipboard.writeText(text);
  const prev = button.innerText;
  button.innerText = 'Copied';
  setTimeout(() => button.innerText = prev, 1200);
}}
</script>
</body>
</html>"""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def render_carousel(slides_dir: Path, carousel: dict[str, Any], total_carousels: int, carousel_num: int) -> None:
    folder = slides_dir / carousel["folder"]
    folder.mkdir(parents=True, exist_ok=True)

    cover_lines = normalize_cover_lines(carousel["cover_lines"])
    cover = make_cover_slide(
        carousel_num=carousel_num,
        total_carousels=total_carousels,
        main_text_lines=cover_lines,
        pill_texts=[],
        tagline=carousel.get("tagline", ""),
    )
    cover.save(folder / "01_COVER.png")

    for slide_num, slide in enumerate(carousel["slides"], start=2):
        filename = f"{slide_num:02d}_{safe_name(slide['label'])}.png"
        image = make_inner_slide(
            carousel_num=carousel_num,
            slide_num=slide_num,
            total_slides=TOTAL_SLIDES,
            category_word=slide["label"],
            headline=slide["headline"],
            body_lines=slide["body"],
        )
        image.save(folder / filename)

    close = carousel["close"]
    cta = make_cta_slide(
        carousel_num=carousel_num,
        slide_num=TOTAL_SLIDES,
        total_slides=TOTAL_SLIDES,
        cta_word=close["cta_word"],
        headline_lines=normalize_close_lines(close["headline_lines"]),
        body_lines=close["body"],
    )
    cta.save(folder / "10_CLOSE.png")


def generate_collection(brief: dict[str, Any]) -> Path:
    collection = brief["collection"]
    slug = collection["slug"]
    dest = HUB / slug
    slides_dir = dest / "slides"
    slides_dir.mkdir(parents=True, exist_ok=True)

    for idx, carousel in enumerate(brief["carousels"], start=1):
        render_carousel(slides_dir, carousel, len(brief["carousels"]), idx)

    write_json(dest / "meta.json", {"slug": slug, "title": collection["title"]})
    (dest / "index.html").write_text(render_collection_page(collection, brief["carousels"]))
    return dest


def ensure_clean_collection_target(dest: Path) -> None:
    if not dest.exists():
        return
    slides_dir = dest / "slides"
    if slides_dir.exists():
        for path in sorted(slides_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
    if (dest / "meta.json").exists():
        (dest / "meta.json").unlink()
    if (dest / "index.html").exists():
        (dest / "index.html").unlink()


def run_script(script_name: str) -> None:
    script = HUB / "scripts" / script_name
    subprocess.run([sys.executable, str(script)], cwd=HUB, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a full ZagaPrime collection from a JSON brief.")
    parser.add_argument("--brief", required=True, help="Path to a JSON brief file.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing collection with the same slug.")
    args = parser.parse_args()

    brief_path = Path(args.brief).resolve()
    brief = load_brief(brief_path)
    validate_brief(brief)

    slug = brief["collection"]["slug"]
    dest = HUB / slug
    if dest.exists():
        if not args.replace:
            raise SystemExit(f"Collection '{slug}' already exists. Re-run with --replace to overwrite it.")
        ensure_clean_collection_target(dest)

    generate_collection(brief)
    run_script("build_index.py")
    run_script("validate_hub.py")
    print(f"Generated collection: /{slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
