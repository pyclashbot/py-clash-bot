# detection/ — image recognition

`image_rec.py` is the template-matching API over OpenCV (`TM_CCOEFF_NORMED`, grayscale):
- `find_image(image, folder, tolerance=0.88, subcrop=None)` → `(x, y)` or `None`. `folder` is a subdir of `reference_images/`; **any** template in it matching counts (matched in parallel). `subcrop=(x1,y1,x2,y2)` searches a region and offsets the result back to full-image coords.
- `compare_images(image, template, threshold=0.8)` → `[y, x]` or `None` — note the **flipped [y, x]** convention vs `find_image`'s `(x, y)`.

## Adding a detectable screen / button

Drop reference PNGs into `reference_images/<descriptive_folder>/` and call `find_image(screenshot, "<folder>")`. Crop a tight region around the element so unrelated screen content can't false-match.

## Gotchas

- Matching is **grayscale** — color-only differences are invisible to it; use the bot layer's pixel/color checks for those.
- No resolution scaling: templates must be captured at the same ~419×633 emulator resolution (see root `AGENTS.md`).
- Reference images load via `utils.image_handler` which accepts `.png` only and rejects all-white/all-black images.
