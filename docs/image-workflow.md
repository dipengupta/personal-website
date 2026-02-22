# Image Workflow (Practical Setup For This Site)

## Goal
Keep the repo fast and clean while still making it easy to add photos to the site.

## Recommended Approach
- Keep **web-ready images** in Git (`mysite/static/images/...`)
- Keep **original/full-resolution photos** outside Git (Photos/iCloud/Drive/local archive)
- Export/compress a copy before adding it to the repo

This is the best fit for your current setup because:
- deploys stay simple
- no extra storage service needed yet
- git history does not fill with giant originals

## Folder Conventions
- Home carousel: `mysite/static/images/home/`
- Travel page photos: `mysite/static/images/travel/`
- Map pin photos: `mysite/static/images/travel/pins/`
- Local originals (ignored): `mysite/static/images/_originals/` (optional local staging)

## Naming Conventions
Use lowercase kebab-case when possible:
- `acadia-sunrise.jpg`
- `new-orleans-mirror.jpg`
- `pittsburgh-skyline.jpg`

If you already have mixed-case names, the site can still handle them, but consistent names make future edits easier.

## Suggested Sizes (Good Defaults)
- Home carousel images: `1800-2400px` wide, JPEG quality `80-85`
- Gallery images (mugs/magnets): `1600-2200px` wide, JPEG quality `80-85`
- Map pin preview images: `1200-1800px` wide, JPEG quality `78-84`

## Helper Script (macOS)
Use the included script to create a web-friendly copy:

```bash
./scripts/prepare_web_image.sh <input> <output> [max_width] [jpeg_quality]
```

Example:

```bash
./scripts/prepare_web_image.sh ~/Pictures/Acadia/IMG_1234.JPG \
  mysite/static/images/travel/pins/acadia-sunrise.jpg 1600 82
```

## Adding Map Pin Photos
Add the image file under:
- `mysite/static/images/travel/pins/...`

Then add photo metadata to the relevant entry in:
- `mysite/travel_data.py`

Example scaffold:

```python
"photos": [
    {
        "path": "images/travel/pins/acadia-sunrise.jpg",
        "caption": "Cadillac Mountain sunrise",
        "alt": "Sunrise at Acadia National Park"
    }
]
```

Only points with `photos` will show a preview image in the right-side panel.

## When To Revisit This Setup
Consider external image hosting (S3/R2/Cloudflare Images/etc.) if:
- you start adding lots of photos (dozens/hundreds)
- repo size starts growing noticeably
- you want automatic variants/CDN optimization

Until then, curated web images in Git is a good tradeoff.
