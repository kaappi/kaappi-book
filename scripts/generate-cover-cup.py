#!/usr/bin/env python3
"""Regenerate the cover cup illustration (images/cover-cup.png).

Calls the Gemini API (gemini-3-pro-image, 2K output) with the prompt below,
then post-processes the result:
  1. verifies the corners are close to the cover's espresso #180E09,
  2. adds a cosine alpha fade over the outer border band (sized to stay
     clear of the artwork) so the image blends seamlessly into the cover.

Usage:  GEMINI_API_KEY=... python3 scripts/generate-cover-cup.py
Writes: images/cover-cup.png (2048x2048 RGBA)

Image generation is nondeterministic: after regenerating, view the image and
rebuild the cover (make cover) to confirm the steam still reads as a clean
lambda and nothing collides with the title block.
"""
import base64
import json
import math
import os
import sys
import urllib.request

from PIL import Image

MODEL = "gemini-3-pro-image"
OUT = os.path.join(os.path.dirname(__file__), "..", "images", "cover-cup.png")

PROMPT = """\
A premium minimalist illustration for the front cover of a professionally \
published programming book, in a warm flat vector style with subtle soft shading.

Subject: a single elegant cream-colored (#F1E6D1) ceramic coffee cup on a \
matching cream saucer, seen from a slightly elevated three-quarter angle. The \
cup is filled with very dark espresso coffee (#28170D) showing a thin golden \
crema ring (#D6A96D) near the rim. The cup has a simple round handle on the \
right. Gentle warm shading on the ceramic: cream highlights on the left, soft \
tan (#CAB698) shadow on the right, a soft dark shadow beneath the saucer.

The steam: rising from the coffee, a ribbon of pale cream steam forms the \
Greek lowercase letter lambda (this exact glyph: λ). Anatomy, top to \
bottom: a single thin-tipped stroke begins at the top, descends diagonally \
toward the lower LEFT, and about halfway down a SECOND shorter leg branches \
off from it and descends to the lower RIGHT. The two strokes meet at ONE \
Y-style branch point and NEVER cross each other - this is NOT the letter X \
and NOT the Greek chi. Nothing extends above the branch except the one \
descending stroke. Clean, calligraphic, gently tapering like real steam, \
instantly readable as λ. On each side, one very faint thin curved steam \
wisp shaped like a tall parenthesis - left curves like "(", right curves \
like ")".

Lighting and background: a warm amber-brown glow (like candlelight) softly \
radiates from behind and above the cup, brightest just around the cup and \
steam, fading smoothly and continuously outward. The background is deep \
espresso brown, reaching EXACTLY the solid color #180E09 at all four edges \
and corners of the image - a strong, perfectly smooth vignette with no \
banding, so the image can blend invisibly into a #180E09 book cover.

Palette: only warm browns, cream, tan, caramel (#C98C49) and the golden \
crema tone. Flat clean shapes, no outlines, no photorealism, no film grain, \
no texture noise, no lens effects.

Composition: cup and saucer centered horizontally in the lower half, lambda \
steam centered above the cup, generous dark negative space all around, \
nothing cropped by the frame.

Absolutely forbidden: any text, typed letters, words, numbers, captions, \
watermarks, signatures, logos, borders, or frames. The lambda made of steam \
is the only glyph-like shape allowed.\
"""


def generate() -> Image.Image:
    body = {
        "contents": [{"parts": [{"text": PROMPT}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"},
        },
    }
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL}:generateContent",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": os.environ["GEMINI_API_KEY"],
        },
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    for part in resp["candidates"][0]["content"]["parts"]:
        blob = part.get("inlineData") or part.get("inline_data")
        if blob:
            tmp = OUT + ".raw"
            with open(tmp, "wb") as f:
                f.write(base64.b64decode(blob["data"]))
            im = Image.open(tmp).convert("RGB")
            os.remove(tmp)
            return im
    sys.exit("no image in response: " + json.dumps(resp)[:500])


def alpha_fade(im: Image.Image) -> Image.Image:
    W, H = im.size
    # Content bbox (pixels brighter than the dark background) so the fade
    # band never touches the artwork.
    bbox = im.convert("L").point(lambda v: 255 if v > 60 else 0).getbbox()
    margins = (bbox[0] / W, bbox[1] / H, (W - bbox[2]) / W, (H - bbox[3]) / H)
    band = max(0.06, min(0.12, min(margins) - 0.02))
    print(f"content margins {margins}, fade band {band:.3f}")
    bw = int(band * W)

    def ramp(d: int) -> int:
        if d >= bw:
            return 255
        return int(255 * (1 - math.cos(math.pi * d / bw)) / 2)

    alpha = Image.new("L", (W, H), 255)
    px = alpha.load()
    for y in range(H):
        ry = ramp(min(y, H - 1 - y))
        for x in range(W):
            v = min(ramp(min(x, W - 1 - x)), ry)
            if v < 255:
                px[x, y] = v
    im.putalpha(alpha)
    return im


def main() -> None:
    im = generate()
    corners = [im.getpixel(p) for p in
               [(3, 3), (im.width - 4, 3), (3, im.height - 4),
                (im.width - 4, im.height - 4)]]
    print("corner colors (want ~ (24,14,9)):", corners)
    if any(abs(c[i] - t) > 12 for c in corners for i, t in enumerate((24, 14, 9))):
        print("WARNING: corners far from espresso #180E09; the alpha fade "
              "will still blend, but check the result visually.")
    alpha_fade(im).save(OUT)
    print("wrote", os.path.normpath(OUT), im.size)


if __name__ == "__main__":
    main()
