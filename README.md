# HK FITNESS — one-page coaching site

A static, dependency-free site for a personal coach. Black, white and gold; heavy athletic type;
deliberate motion. No build step, no framework — the files you see are the files that ship.

## Before going live

The contact details, social handles and address are the real ones. The site is served from
`https://hk-fitness.com/`, with `www` redirecting to the bare domain.

| What | Value | Where |
| --- | --- | --- |
| Domain | `https://hk-fitness.com/` | `index.html` (canonical, `og:url`, `og:image`, `twitter:image`, JSON-LD), `robots.txt`, `sitemap.xml`, `404.html`, `site.webmanifest` (`start_url`, `scope`) |
| WhatsApp | `+60 18-286 9298` (`60182869298` in links) | `index.html` — contact button, contact list, footer, floating button |
| Email | `henrykoh92@gmail.com` | `index.html` — contact button, contact list, footer, JSON-LD `email` |
| Instagram | `instagram.com/hkfitness_studio` | `index.html` — contact list, footer, JSON-LD `sameAs` |
| Facebook | `facebook.com/henry.koh.50` | `index.html` — contact list, footer, JSON-LD `sameAs` |
| Coach name | not shown anywhere | the copy says "the coach" — add a name if you want it public |
| Location | `87-1, Jalan 1/17, Taman Fadason, 52000 Kepong, Kuala Lumpur` | `index.html` — contact list, footer, FAQ ("Where is the studio?") and JSON-LD `address` / `areaServed` |

Client photographs in `assets/img/results/` are published with the assumption of written client
consent. Confirm that before deploying, and keep the "Individual results vary" line in the footer.

## Logo and icons

The header mark, favicon and app icons are all generated from the bear mascot in
`HK_FITNESS_Signboard.pdf` — see `MARK_CROP` in `tools/build-images.py`. Re-run the pipeline after
changing the crop; nothing in the HTML points at a hand-made logo file.

## Studio photographs

`assets/img/studio/gym-01.jpg` … `gym-06.jpg` are copies of the room photos in `My Picture/Gym Room/`,
made by `build_studio()` in `tools/build-images.py`. The carousel shows every frame whole: each slide
is cut to the 608×1080 ratio of the source, so nothing is cropped, resampled or sharpened — a straight
file copy keeps the originals intact.

To change a photo, replace the file in `My Picture/Gym Room/`, keep its entry in `STUDIO_PHOTOS`, and
update the matching slide in `index.html` (order, alt text and caption). Then run
`python tools/build-images.py`. The slide order in `STUDIO_PHOTOS` and the slides in the page must
match, because the build names the output files `gym-01` … `gym-06`.

If a replacement has a different aspect ratio, update `--slide-h` and `--slide-w` on `.studio-slider` in
`assets/css/style.css` as well; the carousel sizes each slide from that height and ratio.

## Local preview

```powershell
python -m http.server 4173
```

Then open <http://localhost:4173>. A plain file open also works, but a server matches production
behaviour for the manifest, 404 page and root-relative paths.

## Deploy to GitHub Pages

The site publishes at <https://hk-fitness.com/> from the `main` branch of
<https://github.com/kiatyao95/HKFitness>.

1. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. Every push to `main` runs `.github/workflows/deploy.yml` and publishes the site.

The workflow assembles a `_site/` artifact first, so `tools/`, the source `.txt` files, the signboard
PDF and this README are not published.

```powershell
git add .
git commit -m "Update site"
git push
```

`My Picture/` (raw client and coach photography) and `_tmp/` are git-ignored and stay local.

The canonical link, Open Graph URLs, JSON-LD `@id`s, the sitemap and the manifest all carry the
custom domain, and `404.html` uses root-relative paths (`/assets/…`) because the domain root is the
site root. Keep them in step if the domain ever changes.

### Custom domain

`hk-fitness.com` is registered at GoDaddy, which also hosts the DNS. Two record sets make GitHub
Pages answer for it:

| Type | Name | Value |
| --- | --- | --- |
| A | `@` | `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` |
| CNAME | `www` | `kiatyao95.github.io` |

The A records are GitHub's published addresses and the `www` CNAME points at the account host, not
at a repository. Any `Parked` A record or domain forwarding at GoDaddy overrides them — remove both.

The domain is entered in **Settings → Pages → Custom domain**, not in a `CNAME` file: this site
publishes with a GitHub Actions workflow, and a `CNAME` file only applies to branch-based
publishing. **Enforce HTTPS** issues the certificate, after which GitHub redirects both
`www.hk-fitness.com` and the old `kiatyao95.github.io/HKFitness/` URL to the canonical domain.

`robots.txt` is read from the domain root now, so its `Sitemap:` line takes effect.

## What is included

- `index.html` — the whole page: hero, name story, training, method, studio carousel, results
  comparison, coach, FAQ, contact.
- `assets/css/style.css` — design tokens, layout, motion. Brand gold is `#f8c008`, sampled from the
  signboard artwork.
- `assets/js/main.js` — header state, mobile menu, scroll reveals, before/after slider, result
  switcher, studio carousel. Degrades gracefully: without JS the content is visible and the FAQ still opens.
- `404.html`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, icons.
- `tools/build-images.py` — rebuilds every derivative image from the source material (`My Picture/`,
  `HK_FITNESS_Signboard.pdf`). Requires `pillow` and `pymupdf`; run `python tools/build-images.py`
  from the project root.

## SEO

- One `<h1>`, one canonical URL, Open Graph and Twitter cards, a 1200×630 social image.
- Structured data as a single `@graph`: `HealthClub` + `LocalBusiness`, `WebSite`, and `FAQPage`.
  The FAQ answers in the JSON-LD are the same text shown on the page — if you edit a FAQ answer,
  edit both, or Google may ignore the rich result.
- `robots.txt` allows the site and blocks the source folders; `sitemap.xml` lists the single page
  with image entries. Update `lastmod` when the content changes.
- Fonts are loaded from Google Fonts with `display=swap`; the rest of the site has no third-party
  requests, no trackers and no cookies.

## Accessibility and motion

Skip link, landmarks, visible focus rings, keyboard-operable comparison slider (native range input),
`aria-pressed` on the result thumbnails, and a mobile menu that traps focus and closes on `Esc`.

All animation is transform/opacity only. It runs for every visitor: the site deliberately does not
respond to `prefers-reduced-motion: reduce`, so the ribbon and the reveals play even on devices that
ask for less motion. To honour that setting again, reinstate the reduced-motion block in
`assets/css/style.css` and the `reduceMotion` checks in `assets/js/main.js`.

## Editing the copy

Text lives directly in `index.html`; there is no CMS or templating. Section copy is grouped under
comments such as `<!-- 07 · FAQ -->` so it is easy to find. Keep the tone plain and specific — the
brief in `Color Theme Specs.txt` is explicit about avoiding generic marketing language.
