"""
Why this file exists: asking an AI image model to "use color #1570EF" is
unreliable -- text-to-image models are bad at hitting exact hex codes. So
instead, we generate a LOOSE, decorative illustration from the AI (no color
instructions), then composite it into a fixed brand template using Pillow,
where WE control every color, font, and layout pixel-exactly. This is the
same idea as Canva Autofill / Bannerbear -- separate "creative asset" from
"brand template."

Output: 1080x1350 (IG portrait feed) or 1080x1920 (story/reel cover) PNGs
that are guaranteed on-brand no matter what the illustration looks like.
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config import BRAND_KIT

def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

BLUE = _hex(BRAND_KIT["primary_blue"])
NAVY = _hex(BRAND_KIT["navy_text"])
BG = _hex(BRAND_KIT["background"])
GREEN = _hex(BRAND_KIT["trust_green"])
AMBER = _hex(BRAND_KIT["accent_amber"])
WHITE = (255, 255, 255)


def _font(path, size):
    return ImageFont.truetype(path, size)


def _wrap_and_draw(draw, text, font, max_width, xy, fill, line_spacing=1.15, anchor_top=True):
    lines = textwrap.wrap(text, width=22)  # width tuned for Poppins Bold at our sizes
    y = xy[1]
    for line in lines:
        draw.text((xy[0], y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        line_h = (bbox[3] - bbox[1]) * line_spacing
        y += line_h
    return y  # returns final y, useful for stacking more text below


def render_feed_slide(headline: str, illustration_path: str, out_path: str,
                       kicker: str = None, show_cta: bool = True,
                       width=1080, height=1350):
    """
    Standard branded feed post / carousel slide.
    Layout: colored top brand bar -> illustration panel -> headline -> kicker/CTA footer.
    """
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)

    # Top brand bar
    bar_h = 70
    draw.rectangle([0, 0, width, bar_h], fill=BLUE)
    logo_font = _font(BRAND_KIT["font_bold"], 34)
    draw.text((40, 15), BRAND_KIT["logo_wordmark"], font=logo_font, fill=WHITE)

    # Illustration panel (rounded, inset)
    illus_pad = 50
    illus_h = int(height * 0.42)
    illus_box = (illus_pad, bar_h + 40, width - illus_pad, bar_h + 40 + illus_h)
    try:
        illus = Image.open(illustration_path).convert("RGB")
        # cover-fit into box
        box_w, box_h = illus_box[2] - illus_box[0], illus_box[3] - illus_box[1]
        scale = max(box_w / illus.width, box_h / illus.height)
        illus = illus.resize((int(illus.width * scale), int(illus.height * scale)))
        left = (illus.width - box_w) // 2
        top = (illus.height - box_h) // 2
        illus = illus.crop((left, top, left + box_w, top + box_h))

        # rounded-corner mask
        mask = Image.new("L", (box_w, box_h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, box_w, box_h], radius=32, fill=255)
        canvas.paste(illus, (illus_box[0], illus_box[1]), mask)
    except Exception as e:
        print(f"[template_render] illustration paste failed ({e}), using solid panel")
        draw.rounded_rectangle(illus_box, radius=32, fill=_hex("#DCE7FB"))

    # thin brand-colored frame around illustration
    draw.rounded_rectangle(illus_box, radius=32, outline=BLUE, width=4)

    # Kicker (small label above headline, e.g. problem-solved tag)
    y = illus_box[3] + 55
    if kicker:
        kicker_font = _font(BRAND_KIT["font_semibold"], 30)
        draw.text((illus_pad, y), kicker.upper(), font=kicker_font, fill=GREEN)
        y += 48

    # Headline
    headline_font = _font(BRAND_KIT["font_bold"], 58)
    y = _wrap_and_draw(draw, headline, headline_font, width - 2 * illus_pad, (illus_pad, y), NAVY)

    # Footer: tagline + CTA pill
    footer_y = height - 130
    draw.line([(illus_pad, footer_y - 20), (width - illus_pad, footer_y - 20)], fill=_hex("#D9E2EC"), width=2)
    tag_font = _font(BRAND_KIT["font_semibold"], 26)
    draw.text((illus_pad, footer_y), BRAND_KIT["kicker_tagline"], font=tag_font, fill=NAVY)

    if show_cta:
        cta_font = _font(BRAND_KIT["font_semibold"], 26)
        cta_text = "Download Bataiyo ->"
        bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
        cta_w = bbox[2] - bbox[0] + 50
        cta_x = width - illus_pad - cta_w
        draw.rounded_rectangle([cta_x, footer_y - 8, width - illus_pad, footer_y + 40], radius=24, fill=BLUE)
        draw.text((cta_x + 25, footer_y - 2), cta_text, font=cta_font, fill=WHITE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    return out_path


def render_reel_cover(headline: str, illustration_path: str, out_path: str,
                       width=1080, height=1920):
    """Vertical branded cover frame, reused as the reel's first frame/thumbnail."""
    canvas = Image.new("RGB", (width, height), NAVY)
    draw = ImageDraw.Draw(canvas)

    try:
        illus = Image.open(illustration_path).convert("RGB")
        scale = max(width / illus.width, (height * 0.6) / illus.height)
        illus = illus.resize((int(illus.width * scale), int(illus.height * scale)))
        canvas.paste(illus, (0, 0))
        # dark gradient overlay for text legibility
        gradient = Image.new("L", (1, height), 0)
        for y in range(height):
            gradient.putpixel((0, y), int(255 * (y / height) ** 2))
        gradient = gradient.resize((width, height))
        overlay = Image.new("RGB", (width, height), NAVY)
        canvas = Image.composite(overlay, canvas, gradient)
        draw = ImageDraw.Draw(canvas)
    except Exception as e:
        print(f"[template_render] reel cover illustration failed ({e})")

    draw.rectangle([0, 0, width, 90], fill=BLUE)
    logo_font = _font(BRAND_KIT["font_bold"], 40)
    draw.text((40, 20), BRAND_KIT["logo_wordmark"], font=logo_font, fill=WHITE)

    headline_font = _font(BRAND_KIT["font_bold"], 68)
    _wrap_and_draw(draw, headline, headline_font, width - 100, (50, height - 420), WHITE)

    tag_font = _font(BRAND_KIT["font_semibold"], 32)
    draw.text((50, height - 100), BRAND_KIT["kicker_tagline"], font=tag_font, fill=WHITE)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    return out_path


if __name__ == "__main__":
    # smoke test with a solid placeholder illustration
    placeholder = "output/_placeholder.png"
    os.makedirs("output", exist_ok=True)
    Image.new("RGB", (800, 800), _hex("#DCE7FB")).save(placeholder)
    render_feed_slide(
        "Why your plumber's 5-star rating might be fake",
        placeholder,
        "output/test_feed_slide.png",
        kicker="Fake Reviews",
    )
    print("Saved output/test_feed_slide.png")
