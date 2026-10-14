#!/usr/bin/env python3
"""Build deterministic responsive WebP derivatives from assets/incoming."""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageOps, UnidentifiedImageError

DEFAULT_WIDTHS = (480, 960, 1440, 1920)
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}
MAX_INPUT_BYTES = 50 * 1024 * 1024
QUALITY = 82


def _save_webp(image: Image.Image, path: Path, icc_profile: bytes | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    options: dict[str, object] = {"quality": QUALITY, "method": 6}
    if icc_profile:
        options["icc_profile"] = icc_profile
    image.save(path, "WEBP", **options)


def optimize(source_root: Path, output_root: Path, widths: tuple[int, ...] = DEFAULT_WIDTHS) -> tuple[int, int]:
    """Create derivatives transactionally, remove stale generated WebPs, return counts."""
    if not widths or any(w <= 0 for w in widths) or tuple(sorted(set(widths))) != widths:
        raise ValueError("Widths must be unique positive integers in ascending order")

    sources = sorted(
        p for p in source_root.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED
    ) if source_root.exists() else []
    seen_stems: set[Path] = set()
    for source in sources:
        stem = source.relative_to(source_root).with_suffix("")
        if stem in seen_stems:
            raise ValueError(f"Multiple source files produce the same output name: {stem}")
        seen_stems.add(stem)
        if source.stat().st_size > MAX_INPUT_BYTES:
            raise ValueError(f"Input exceeds 50 MiB: {source}")

    desired: set[Path] = set()
    written = 0
    # Build everything in a temporary tree first. Bad input never leaves half-updated output.
    with tempfile.TemporaryDirectory(prefix="website-images-") as temporary:
        staging_root = Path(temporary)
        for source in sources:
            relative = source.relative_to(source_root)
            stem = relative.with_suffix("")
            try:
                with Image.open(source) as opened:
                    if getattr(opened, "n_frames", 1) > 1:
                        raise ValueError(f"Animated input is not converted; keep/serve it separately: {source}")
                    icc_profile = opened.info.get("icc_profile")
                    image = ImageOps.exif_transpose(opened)
                    image.load()
                    image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            except (UnidentifiedImageError, OSError) as exc:
                raise ValueError(f"Cannot decode image {source}: {exc}") from exc

            original_width, original_height = image.size
            if original_width <= 0 or original_height <= 0:
                raise ValueError(f"Invalid image dimensions: {source}")

            def write_variant(width: int, suffix: str) -> None:
                nonlocal written
                height = max(1, round(original_height * width / original_width))
                variant = image if width == original_width else image.resize((width, height), Image.Resampling.LANCZOS)
                output_relative = stem.parent / f"{stem.name}{suffix}.webp"
                _save_webp(variant, staging_root / output_relative, icc_profile)
                desired.add(output_relative)
                written += 1
                print(f"{source} -> {output_root / output_relative} ({width}x{height})")

            for width in widths:
                if width < original_width:
                    write_variant(width, f"-{width}w")
            write_variant(min(original_width, widths[-1]), "")

        # Publish the completed new tree, then remove only generated stale WebP files.
        for relative in desired:
            target = output_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(staging_root / relative, target)

    removed = 0
    if output_root.exists():
        for candidate in output_root.rglob("*.webp"):
            if candidate.relative_to(output_root) not in desired:
                candidate.unlink()
                removed += 1
        for directory in sorted((p for p in output_root.rglob("*") if p.is_dir()), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
    print(f"Generated/updated {written} WebP file(s); removed {removed} stale derivative(s).")
    return written, removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("assets/incoming"), help="Source image directory")
    parser.add_argument("--output", type=Path, default=Path("assets/processed"), help="Generated WebP directory")
    parser.add_argument("--widths", default=",".join(map(str, DEFAULT_WIDTHS)), help="Comma-separated widths, ascending")
    args = parser.parse_args()
    try:
        widths = tuple(int(v) for v in args.widths.split(",") if v.strip())
        optimize(args.source, args.output, widths)
    except (ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
