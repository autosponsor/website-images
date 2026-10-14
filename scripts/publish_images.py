#!/usr/bin/env python3
"""Copy a local image folder into assets/incoming and optionally commit/push it."""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
CATEGORIES = ("brand", "products", "content", "ui")
REPO = Path(__file__).resolve().parent.parent


def run(*args: str, cwd: Path = REPO, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, check=check)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Folder on this computer containing images")
    parser.add_argument("--category", choices=CATEGORIES, default="content", help="Destination asset category")
    parser.add_argument("--push", action="store_true", help="Commit and push only this category to origin/main")
    parser.add_argument("--message", default="Add website images", help="Commit message used with --push")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.is_dir():
        parser.error(f"Source folder does not exist or is not a directory: {source}")

    destination = REPO / "assets" / "incoming" / args.category
    copied = 0
    for item in sorted(source.rglob("*")):
        if not item.is_file() or item.is_symlink() or item.name.startswith("."):
            continue
        if item.suffix.lower() not in SUPPORTED:
            print(f"Skipping unsupported file: {item.relative_to(source)}")
            continue
        target = destination / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        print(f"Copied {item} -> {target.relative_to(REPO)}")
        copied += 1

    if copied == 0:
        print("No supported images found; nothing staged.")
        return 0
    relative_target = destination.relative_to(REPO).as_posix()
    run("git", "add", "--", relative_target)
    print(f"Staged {copied} image file(s) under {relative_target}.")

    if args.push:
        changed = run("git", "diff", "--cached", "--quiet", "--", relative_target, check=False).returncode != 0
        if not changed:
            print("No changes to commit; repository is already up to date.")
            return 0
        run("git", "commit", "--only", "-m", args.message, "--", relative_target)
        run("git", "push", "origin", "main")
        print("Pushed successfully. GitHub Actions will generate optimized variants.")
    else:
        print("Review staged changes, then commit and push to main to trigger GitHub Actions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
