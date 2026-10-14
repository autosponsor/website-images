# Website Images

Public image assets for website delivery through the jsDelivr CDN.

## Use an image in your site

Use a **tagged release version** in production URLs so a future asset update cannot unexpectedly change a live page:

```html
<img
  src="https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/content/example.webp"
  alt="Describe the image"
  loading="lazy"
  decoding="async"
>
```

For CSS:

```css
background-image: url("https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/ui/example.svg");
```

Replace `v1.0.0` with the tag you have published and `example.webp` with the committed file path. You can also browse the repository directly at GitHub. Avoid using `raw.githubusercontent.com` as your production CDN URL.

## Folders

- `assets/brand/` — logos, marks, and brand graphics
- `assets/products/` — product photography and illustrations
- `assets/content/` — editorial, blog, and campaign images
- `assets/ui/` — icons and interface graphics

## Publishing an update

1. Add optimized assets under the appropriate folder.
2. Use descriptive, lowercase, hyphen-separated filenames, e.g. `summer-campaign-hero.webp`.
3. Commit and push to `main`.
4. Create and push a release tag (for example `v1.0.0`) for a production snapshot:

   ```sh
   git tag v1.0.0
   git push origin v1.0.0
   ```

5. Use the versioned jsDelivr URL in your site. When changing an asset, publish a new tag and update the URL rather than overwriting a version in use.

## Asset guidance

- Prefer **WebP** or **AVIF** for photographs; use **SVG** for simple logos and icons; use **PNG** when transparency or lossless detail is needed.
- Resize images to the largest dimensions actually needed by the site and compress before committing. Keep files comfortably below GitHub's 100 MB per-file limit; smaller files also improve page performance.
- Give files clear names and keep paths stable. Do not commit secrets, private/customer images, or anything that should not be publicly accessible.
- Include meaningful `alt` text in the website markup (or empty `alt=""` for decorative images).

## Cache behavior

jsDelivr caches content. Versioned URLs are immutable in practice and are recommended for production. If you must update a file before making a new version tag, use jsDelivr's purge endpoint for that exact URL; preferably publish a new tag instead.

## Automated local-folder upload and optimization

GitHub Actions cannot directly inspect an arbitrary folder on your computer. The safe, simple flow is to sync that folder into this repository with Git and push it; the workflow then generates responsive WebP derivatives in GitHub.

1. Clone once and set your local image folder (example: `~/site-images`) as `SOURCE_DIR`:

   ```sh
   git clone https://github.com/autosponsor/website-images.git
   cd website-images
   mkdir -p assets/incoming/content
   cp -R "$HOME/site-images/"* assets/incoming/content/
   git add assets/incoming/content
   git commit -m "Add website images"
   git push origin main
   ```

2. The **Optimize uploaded images** workflow runs on the push and writes WebP variants to `assets/processed/content/`. Check its run under the repository's **Actions** tab. The workflow needs the repository's default `GITHUB_TOKEN` to have read/write contents permission; the workflow declares that permission explicitly.
3. Publish a new Git tag after the generated files are committed, then use that tag in production CDN URLs as shown below. Do not use an old tag for newly added files.

The workflow accepts JPG/JPEG, PNG, and WebP input and generates 480, 960, 1440, and 1920-pixel variants when smaller than the source, plus a full-size (capped at 1920 px wide) fallback. It does not upscale. Keep originals in `assets/incoming/` so you can regenerate derivatives later. For GIF animation and SVG, retain and serve the original instead of converting them through this raster pipeline.

### Responsive HTML example

Replace `v1.0.0` with the release tag that includes these files; use the actual generated filenames and widths for your image. The `sizes` value should reflect the rendered layout in your site.

```html
<img
  src="https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero.webp"
  srcset="https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-480w.webp 480w,
          https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-960w.webp 960w,
          https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-1440w.webp 1440w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 80vw, 1200px"
  width="1920"
  height="1080"
  alt="Describe what the hero image communicates"
  fetchpriority="high"
  decoding="async"
>
```

For below-the-fold images, use `loading="lazy"` instead of `fetchpriority="high"`. Do not lazy-load the main above-the-fold/LCP image.

### Responsive CSS background example

```css
.hero {
  background-image: url("https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero.webp");
  background-size: cover;
  background-position: center;
}

@media (max-width: 600px) {
  .hero {
    background-image: url("https://cdn.jsdelivr.net/gh/autosponsor/website-images@v1.0.0/assets/processed/content/hero-960w.webp");
  }
}
```

HTML `srcset` is generally preferable for content images because the browser chooses a suitable resource based on viewport and pixel density. CSS media queries are suitable for decorative backgrounds.
