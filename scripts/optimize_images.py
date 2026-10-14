#!/usr/bin/env python3
"""Create responsive WebP derivatives from assets/incoming raster images."""
from pathlib import Path
from PIL import Image, ImageOps

SOURCE = Path("assets/incoming")
DEST = Path("assets/processed")
WIDTHS = (480, 960, 1440, 1920)
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}


def main() -> None:
    sources = sorted(p for p in SOURCE.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not sources:
        print(f"No supported raster images found under {SOURCE}; nothing to do.")
        return

    made = 0
    for path in sources:
        relative = path.relative_to(SOURCE)
        with Image.open(path) as opened:
            image = ImageOps.exif_transpose(opened)
            image.load()
            # Keep alpha where present; otherwise encode as RGB.
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            original_width, original_height = image.size
            stem = relative.with_suffix("")
            for width in WIDTHS:
                if width >= original_width:
                    continue  # never upscale; largest available source remains usable as fallback
                height = round(original_height * width / original_width)
                variant = image.resize((width, height), Image.Resampling.LANCZOS)
                output = DEST / stem.parent / f"{stem.name}-{width}w.webp"
                output.parent.mkdir(parents=True, exist_ok=True)
                variant.save(output, "WEBP", quality=82, method=6)
                print(f"{path} -> {output} ({width}x{height})")
                made += 1

            # Always emit one full-size, capped-at-1920 fallback.
            fallback_width = min(original_width, 1920)
            fallback_height = round(original_height * fallback_width / original_width)
            fallback = image.resize((fallback_width, fallback_height), Image.Resampling.LANCZOS) if fallback_width != original_width else image
            output = DEST / stem.parent / f"{stem.name}.webp"
            output.parent.mkdir(parents=True, exist_ok=True)
            fallback.save(output, "WEBP", quality=82, method=6)
            print(f"{path} -> {output} ({fallback_width}x{fallback_height})")
            made += 1
    print(f"Generated {made} optimized WebP file(s).")


if __name__ == "__main__":
    main()
