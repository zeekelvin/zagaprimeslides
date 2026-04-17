#!/usr/bin/env python3
"""
ZagaPrime Hub — Validator
Checks collection structure, generated pages, and slide dimensions.

Run:
  python3 scripts/validate_hub.py
"""
import json
from pathlib import Path

from PIL import Image

HUB = Path(__file__).resolve().parent.parent
SKIP = {"scripts", ".vercel", ".git", "node_modules"}
EXPECTED_SIZE = (1080, 1080)


def fail(errors, message):
    errors.append(message)


def validate_collection(path, errors):
    slides_dir = path / "slides"
    if not slides_dir.exists():
        return

    meta_path = path / "meta.json"
    if not meta_path.exists():
        fail(errors, f"{path.name}: missing meta.json")
    else:
        try:
            json.loads(meta_path.read_text())
        except json.JSONDecodeError as exc:
            fail(errors, f"{path.name}: invalid meta.json ({exc})")

    if not (path / "index.html").exists():
        fail(errors, f"{path.name}: missing collection index.html")

    if not (slides_dir / "index.html").exists():
        fail(errors, f"{path.name}: missing slides/index.html")

    subdirs = sorted([d for d in slides_dir.iterdir() if d.is_dir()])
    if not subdirs:
        subdirs = [slides_dir]

    for group in subdirs:
        pngs = sorted(group.glob("*.png"))
        if not pngs:
            fail(errors, f"{path.name}/{group.name}: no PNG slides found")
            continue

        if len(pngs) != 10:
            fail(errors, f"{path.name}/{group.name}: expected 10 slides, found {len(pngs)}")

        names = {p.name for p in pngs}
        if "01_COVER.png" not in names:
            fail(errors, f"{path.name}/{group.name}: missing 01_COVER.png")
        if "10_CLOSE.png" not in names:
            fail(errors, f"{path.name}/{group.name}: missing 10_CLOSE.png")

        for png in pngs:
            try:
                with Image.open(png) as img:
                    if img.size != EXPECTED_SIZE:
                        fail(errors, f"{path.name}/{group.name}/{png.name}: expected {EXPECTED_SIZE}, found {img.size}")
            except Exception as exc:  # pragma: no cover - defensive CLI check
                fail(errors, f"{path.name}/{group.name}/{png.name}: unreadable PNG ({exc})")


def main():
    errors = []

    if not (HUB / "index.html").exists():
        fail(errors, "hub: missing root index.html")

    for item in sorted(HUB.iterdir()):
        if item.name.startswith(".") or item.name in SKIP or not item.is_dir():
            continue
        validate_collection(item, errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Validation passed:")
    print(" - root index.html present")
    print(" - collection landing pages present")
    print(" - slide gallery pages present")
    print(" - slide groups have expected 10-slide structure")
    print(" - PNG dimensions are 1080x1080")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
