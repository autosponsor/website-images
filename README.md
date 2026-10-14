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
