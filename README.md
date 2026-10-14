# Website Images

Public image assets for website delivery through the jsDelivr CDN. **Everything committed here is public.** Do not upload confidential, customer, licensed-restricted, or otherwise private images.

## Quick start: publish a local folder

Clone this repository on the computer that holds your images, install the tool dependency, then run the publisher. It copies supported files into `assets/incoming/<category>/`, stages them, and can commit and push them to GitHub:

```sh
git clone https://github.com/autosponsor/website-images.git
cd website-images
python -m pip install -r requirements-image.txt
python scripts/publish_images.py "$HOME/site-images" --category content --push
```

Use `--category brand`, `products`, `content`, or `ui`. By default the script stages files for review without committing or pushing; omit `--push` to review, then commit and push manually. It skips hidden files and symlinks, preserves source subfolders, and accepts JPG/JPEG, PNG, WebP, GIF, and SVG. Raster optimization only processes JPG/JPEG, PNG, and static WebP. Animated GIF/WebP and SVG are retained as sources and are not transcoded.

Once the source files are pushed to `main`, GitHub Actions runs tests, generates optimized responsive WebP assets under `assets/processed/<category>/`, validates the output, removes obsolete generated WebP derivatives, and commits the generated files. Inspect the run in the repository's **Actions** tab. Wait for it to succeed before making a release tag. The workflow uses `GITHUB_TOKEN` with repository contents write permission; repository/org policy must allow Actions to write contents.

### Manual alternative

```sh
mkdir -p assets/incoming/content
cp -R "$HOME/site-images/"* assets/incoming/content/
git add assets/incoming/content
git commit -m "Add website images"
git push origin main
```

To run the same image optimizer locally (after installing `requirements-image.txt`):

```sh
python scripts/optimize_images.py
python scripts/validate_assets.py
python -m unittest discover -s tests -v
```

## What the optimizer does

- Accepts static JPG/JPEG, PNG, and WebP source files up to 50 MiB each.
- Corrects EXIF orientation, preserves alpha transparency and embedded ICC color profiles, and emits WebP at quality 82 with high-effort encoding.
- Creates variants at 480, 960, 1440, and 1920 pixels wide only when the source is larger than that width. It also creates a fallback capped at 1920 pixels; it never upscales.
- Mirrors the source folder structure under `assets/processed/`. For example, `assets/incoming/content/hero.jpg` produces `assets/processed/content/hero-480w.webp` etc.
- Removes stale generated `.webp` files that no longer correspond to any supported source, but leaves unrelated files alone. Remove old source files from `assets/incoming/` yourself when you no longer want them; the next workflow run cleans up their generated derivatives.
- Fails rather than silently flattening animations, accepting corrupt images, exceeding the 50 MiB input limit, or allowing two same-folder sources with the same basename to overwrite each other's outputs.

The defaults can be tuned in `scripts/optimize_images.py`. Its command line accepts `--source`, `--output`, and ascending comma-separated `--widths` options.

## Use images on your website

For stable production delivery, create a new Git tag **after** the optimized derivative commit has landed. Example:

```sh
git pull origin main
git tag v1.0.0
git push origin v1.0.0
```

Use the actual generated filenames and widths for your image. The CDN URL pattern is:

```text
https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-960w.webp
```

Use immutable version tags in production and create a new tag when updating assets; avoid `raw.githubusercontent.com` as a production CDN URL.

### Responsive HTML

Set `sizes` to the rendered width in your page, and set `width`/`height` to the real aspect ratio to reserve layout space:

```html
<img
  src="https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero.webp"
  srcset="https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-480w.webp 480w,
          https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-960w.webp 960w,
          https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-1440w.webp 1440w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 80vw, 1200px"
  width="1920"
  height="1080"
  alt="Describe what the image communicates"
  fetchpriority="high"
  decoding="async"
>
```

Use `loading="lazy"` for below-the-fold images, not the main above-the-fold/LCP image. If the source is narrower than a listed `srcset` width, omit that unavailable candidate. For decorative backgrounds, use CSS and media queries instead; HTML `srcset` is generally preferable for content images.

### CSS background

```css
.hero {
  background: center / cover no-repeat
    url("https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero.webp");
}

@media (max-width: 600px) {
  .hero {
    background-image: url("https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-960w.webp");
  }
}
```

## Image preparation and maintenance

- Resize to the largest size the design needs; do not upload oversized originals when a smaller source will do.
- Prefer WebP/AVIF for photos, SVG for suitable vector graphics, and PNG where transparency or lossless detail matters. This pipeline emits WebP; keep animated images and SVG as originals.
- Use clear lowercase hyphenated filenames. Add useful alt text in page markup; use `alt=""` for decorative images.
- Avoid committing editing sources such as PSD/XCF files. GitHub blocks files over 100 MB; this pipeline has a stricter 50 MiB source cap.
- Keep originals in `assets/incoming/` if you may need to regenerate the processed versions. Output validation enforces WebP format and a 20 MiB generated-file cap.
- Versioned URLs are recommended for production because CDN caches can retain content. If an unversioned asset must be refreshed, purge the exact jsDelivr URL or publish a new version tag.

## Repository layout

- `assets/incoming/` — original image sources supplied by the local publisher
- `assets/processed/` — generated, responsive WebP files
- `assets/brand/`, `products/`, `content/`, `ui/` — categories and direct/manual assets
- `scripts/` — local publisher, optimizer, and output validator
- `tests/` — optimizer regression tests
- `.github/workflows/` — GitHub Actions automation
