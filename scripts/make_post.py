#!/usr/bin/env python3
"""
Render a bread.eg Instagram post (1080x1080 PNG) using the brand's
templates: number, breaking, quote.

Header on every template is just the date (top-left, muted mono) -
no "NUMBER OF THE DAY" / "BREAKING" / category label. Footer on every
template is a hairline divider, the source citation, and the bread
logo below the divider, bottom-right.

Usage:
  python3 make_post.py --template number --out ../posts/2026-09-18.png \
    --date "18 SEP 2026" --number "EGP 89bn" \
    --what "Distressed resale units listed in 30 days" \
    --context "6,200 units drew 32,000 buyer requests." \
    --source "AQAR EXIT, VIA MASRAWY"
"""
import argparse
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "fonts")
ASSETS = os.path.join(ROOT, "assets")

INK = "#0a0a0a"
PAPER = "#ffffff"
BONE = "#f4f4f1"
GREY_BODY = "#55554f"
GREY_LIGHT = "#7a7a75"
GREY_ON_INK = "#8a8a84"
GREY_ON_INK_SOURCE = "#6a6a64"
ACCENT_FILL = "#90101a"
ACCENT_DEEP = "#a92321"

SIZE = 1080
PAD = 88


def newsreader(size, weight=800, opsz=None):
    f = ImageFont.truetype(os.path.join(FONTS, "Newsreader-Variable.ttf"), size)
    if opsz is None:
        opsz = max(6, min(72, size * 0.14))
    f.set_variation_by_axes([weight, opsz])
    return f


def mono(size, weight="Regular"):
    name = {"Regular": "JetBrainsMono-Regular.ttf", "Medium": "JetBrainsMono-Medium.ttf", "Bold": "JetBrainsMono-Bold.ttf"}[weight]
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def wrap_by_width(draw, text, font, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_multiline(draw, xy, text, font, fill, max_width, line_gap=1.0):
    x, y = xy
    lines = wrap_by_width(draw, text, font, max_width)
    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * line_gap)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y  # returns y after last line


def footer(img, d, source, source_fg, logo_variant, divider_color):
    """Hairline divider, source citation, logo below the divider (bottom-right). Every template ends with this."""
    logo_name = "bread-logo-white.png" if logo_variant == "white" else "bread-logo.png"
    logo = Image.open(os.path.join(ASSETS, logo_name)).convert("RGBA")
    logo_w = 228
    ratio = logo_w / logo.width
    logo = logo.resize((logo_w, int(logo.height * ratio)), Image.LANCZOS)

    divider_y = SIZE - PAD - 78
    d.line([(PAD, divider_y), (SIZE - PAD, divider_y)], fill=divider_color, width=2)

    logo_y = divider_y + 26
    img.paste(logo, (SIZE - PAD - logo.width, logo_y), logo)

    src_font = mono(24)
    ascent, descent = src_font.getmetrics()
    d.text((PAD, logo_y + (logo.height - (ascent + descent)) // 2), source, font=src_font, fill=source_fg)


def tpl_number(args):
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), args.date, font=mono(26), fill=GREY_LIGHT)

    y = PAD + 100
    max_num_width = SIZE - 2 * PAD
    num_size = 150
    f_num = newsreader(num_size, weight=800, opsz=72)
    while d.textlength(args.number, font=f_num) > max_num_width and num_size > 60:
        num_size -= 6
        f_num = newsreader(num_size, weight=800, opsz=max(6, min(72, num_size * 0.14)))
    d.text((PAD, y), args.number, font=f_num, fill=ACCENT_DEEP)
    y += int(num_size * 1.25) + 20

    f_what = newsreader(52, weight=700, opsz=40)
    y = draw_multiline(d, (PAD, y), args.what, f_what, INK, SIZE - 2 * PAD, line_gap=1.1) + 20

    f_ctx = newsreader(36, weight=500, opsz=20)
    draw_multiline(d, (PAD, y), args.context, f_ctx, GREY_BODY, 840, line_gap=1.35)

    footer(img, d, args.source, GREY_LIGHT, "dark", "#e2e2de")
    return img


def tpl_breaking(args):
    ink_bg = args.bg != "paper"
    bg = INK if ink_bg else BONE
    fg = "#ffffff" if ink_bg else INK
    sub_fg = "#b5b5ae" if ink_bg else GREY_BODY
    date_fg = GREY_ON_INK if ink_bg else GREY_LIGHT
    source_fg = GREY_ON_INK_SOURCE if ink_bg else GREY_LIGHT
    logo_variant = "white" if ink_bg else "dark"
    divider_color = "#2a2a28" if ink_bg else "#dedeD9"

    img = Image.new("RGB", (SIZE, SIZE), bg)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), args.date, font=mono(26), fill=date_fg)

    y = PAD + 90
    f_head = newsreader(88, weight=800, opsz=72)
    y = draw_multiline(d, (PAD, y), args.headline, f_head, fg, SIZE - 2 * PAD, line_gap=1.0) + 36

    f_sub = newsreader(38, weight=500, opsz=20)
    draw_multiline(d, (PAD, y), args.standfirst, f_sub, sub_fg, 860, line_gap=1.35)

    footer(img, d, args.source, source_fg, logo_variant, divider_color)
    return img


def tpl_quote(args):
    img = Image.new("RGB", (SIZE, SIZE), INK)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), args.date, font=mono(26), fill=GREY_ON_INK)

    f_quote = newsreader(84, weight=700, opsz=64)
    y = 260
    y = draw_multiline(d, (PAD, y), args.quote, f_quote, "#ffffff", SIZE - 2 * PAD, line_gap=1.12) + 44

    d.text((PAD, y), args.name, font=newsreader(40, weight=700, opsz=24), fill="#ffffff")
    d.text((PAD, y + 54), args.title, font=newsreader(30, weight=500, opsz=20), fill=GREY_ON_INK)

    footer(img, d, args.source, GREY_ON_INK_SOURCE, "white", "#2a2a28")
    return img


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True, choices=["number", "breaking", "quote"])
    p.add_argument("--out", required=True)
    p.add_argument("--bg", default="ink", choices=["ink", "paper"])
    p.add_argument("--date", default="")
    p.add_argument("--source", default="")
    # number
    p.add_argument("--number", default="")
    p.add_argument("--what", default="")
    p.add_argument("--context", default="")
    # breaking
    p.add_argument("--headline", default="")
    p.add_argument("--standfirst", default="")
    # quote
    p.add_argument("--quote", default="")
    p.add_argument("--name", default="")
    p.add_argument("--title", default="")
    args = p.parse_args()

    if args.template == "number":
        img = tpl_number(args)
    elif args.template == "breaking":
        img = tpl_breaking(args)
    else:
        img = tpl_quote(args)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    img.save(args.out, "PNG")
    print(args.out)


if __name__ == "__main__":
    main()
