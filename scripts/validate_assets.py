#!/usr/bin/env python3
"""Check generated assets are decodable, reasonably sized WebP files."""
from pathlib import Path
import sys
from PIL import Image, UnidentifiedImageError

ROOT = Path("assets/processed")
MAX_OUTPUT_BYTES = 20 * 1024 * 1024


def main() -> int:
    bad = []
    files = sorted(ROOT.rglob("*")) if ROOT.exists() else []
    images = [p for p in files if p.is_file()]
    for path in images:
        if path.suffix.lower() != ".webp":
            bad.append(f"Unexpected non-WebP generated file: {path}")
            continue
        if path.stat().st_size > MAX_OUTPUT_BYTES:
            bad.append(f"Generated file exceeds 20 MiB: {path}")
        try:
            with Image.open(path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            bad.append(f"Invalid image {path}: {exc}")
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    print(f"Validated {len(images)} generated WebP file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
