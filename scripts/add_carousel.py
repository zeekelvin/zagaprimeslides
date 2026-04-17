#!/usr/bin/env python3
"""
ZagaPrime Hub — Add Carousel CLI
Usage:
  python scripts/add_carousel.py --slug connectors --slides /path/to/slides/ [--html /path/to/captions.html]
  python scripts/add_carousel.py --slug my-new-topic --slides /tmp/my_topic/ --html /tmp/my_topic.html

This copies slides and optional HTML into the hub structure, then regenerates index.html.
"""
import argparse, shutil, os, subprocess, sys

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    p = argparse.ArgumentParser(description="Add a carousel set to the ZagaPrime Hub")
    p.add_argument("--slug",   required=True, help="URL-friendly collection name e.g. 'connectors'")
    p.add_argument("--slides", required=True, help="Path to slides directory (contains subfolders or PNGs)")
    p.add_argument("--html",   default=None,  help="Optional HTML package file (becomes index.html)")
    p.add_argument("--title",  default=None,  help="Display title for the index page")
    args = p.parse_args()

    dest = os.path.join(HUB, args.slug)
    slides_dest = os.path.join(dest, "slides")
    os.makedirs(slides_dest, exist_ok=True)

    # Copy slides
    src = args.slides.rstrip("/")
    if os.path.isdir(src):
        # Check if src has subdirs (multi-carousel) or PNGs directly (single set)
        items = os.listdir(src)
        has_subdirs = any(os.path.isdir(os.path.join(src, i)) for i in items)
        if has_subdirs:
            # Multi-carousel: copy each subfolder
            for item in sorted(items):
                item_path = os.path.join(src, item)
                if os.path.isdir(item_path):
                    shutil.copytree(item_path, os.path.join(slides_dest, item), dirs_exist_ok=True)
                    print(f"  Copied: {item}")
        else:
            # Single set: copy PNGs into slides/ directly
            for f in sorted(items):
                if f.lower().endswith('.png'):
                    shutil.copy2(os.path.join(src, f), os.path.join(slides_dest, f))
                    print(f"  Copied: {f}")
    else:
        print(f"Error: --slides path not found: {src}", file=sys.stderr)
        sys.exit(1)

    # Copy HTML package
    if args.html and os.path.exists(args.html):
        shutil.copy2(args.html, os.path.join(dest, "index.html"))
        print(f"  Copied HTML package -> {args.slug}/index.html")

    # Write meta.json for index builder
    import json
    title = args.title or args.slug.replace("-", " ").title()
    meta = {"slug": args.slug, "title": title}
    with open(os.path.join(dest, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # Count slides
    png_count = sum(1 for _, _, files in os.walk(slides_dest) for f in files if f.endswith('.png'))
    print(f"\n  Collection: {args.slug}")
    print(f"  Slides:     {png_count} PNGs")
    print(f"  HTML:       {'yes' if args.html else 'no'}")

    # Rebuild index
    idx_script = os.path.join(HUB, "scripts", "build_index.py")
    if os.path.exists(idx_script):
        print("\n  Rebuilding index.html...")
        subprocess.run([sys.executable, idx_script], cwd=HUB)

    print(f"\n✅ Done. Collection '{args.slug}' added to hub.")
    print(f"   Commit and push to deploy: git add . && git commit -m 'feat: add {args.slug}' && git push")

if __name__ == "__main__":
    main()
