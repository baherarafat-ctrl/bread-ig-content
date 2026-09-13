#!/usr/bin/env python3
"""
Render a bread.eg Instagram post (1080x1080 PNG) using the brand's
existing templates: number, breaking, quote.

Usage:
  python3 make_post.py --template number --out ../posts/2026-09-18.png \
    --kicker "NUMBER OF THE DAY - 18 SEP 2026" --number "EGP 89bn" \
    --what "Distressed resale units listed in 30 days" \
    --context "6,200 units drew 32,000 buyer requests." \
    --source "AQAR EXIT, VIA MASRAWY"
"""
import argparse
import os
import textwrap
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


def paste_logo(img, variant="dark", width=266, margin=PAD):
    name = "bread-logo-white.png" if variant == "white" else "bread-logo.png"
    logo = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    ratio = width / logo.width
    logo = logo.resize((width, int(logo.height * ratio)), Image.LANCZOS)
    x = SIZE - margin - logo.width
    y = SIZE - margin - logo.height
    img.paste(logo, (x, y), logo)
    return y  # top-y of logo, for aligning source line baseline


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


def tpl_number(args):
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), args.kicker, font=mono(26), fill=GREY_LIGHT)

    y = PAD + 100
    f_num = newsreader(150, weight=800, opsz=72)
    d.text((PAD, y), args.number, font=f_num, fill=ACCENT_DEEP)
    y += 190

    f_what = newsreader(52, weight=700, opsz=40)
    y = draw_multiline(d, (PAD, y), args.what, f_what, INK, SIZE - 2 * PAD, line_gap=1.1) + 20

    f_ctx = newsreader(36, weight=500, opsz=20)
    y = draw_multiline(d, (PAD, y), args.context, f_ctx, GREY_BODY, 840, line_gap=1.35)

    ry = SIZE - PAD - 32
    d.line([(PAD, ry - 32), (SIZE - PAD, ry - 32)], fill="#e2e2de", width=2)
    d.text((PAD, ry), args.source, font=mono(24), fill=GREY_LIGHT)
    paste_logo(img, "dark", width=266)
    return img


def tpl_breaking(args):
    ink_bg = args.bg != "paper"
    bg = INK if ink_bg else BONE
    fg = "#ffffff" if ink_bg else INK
    sub_fg = "#b5b5ae" if ink_bg else GREY_BODY
    tag_bg = ACCENT_FILL
    kicker_fg = GREY_ON_INK if ink_bg else GREY_LIGHT
    source_fg = GREY_ON_INK_SOURCE if ink_bg else GREY_LIGHT
    logo_variant = "white" if ink_bg else "dark"

    img = Image.new("RGB", (SIZE, SIZE), bg)
    d = ImageDraw.Draw(img)

    tag_font = mono(26, "Bold")
    tag_pad_x, tag_pad_y = 22, 14
    tag_w = d.textlength(args.tag, font=tag_font) + tag_pad_x * 2
    tag_h = tag_font.size + tag_pad_y * 2 + 8
    d.rectangle([PAD, PAD, PAD + tag_w, PAD + tag_h], fill=tag_bg)
    d.text((PAD + tag_pad_x, PAD + tag_pad_y), args.tag, font=tag_font, fill="#ffffff")
    d.text((PAD + tag_w + 20, PAD + tag_pad_y), args.date, font=mono(26), fill=kicker_fg)

    y = PAD + int(tag_h) + 70
    f_head = newsreader(88, weight=800, opsz=72)
    y = draw_multiline(d, (PAD, y), args.headline, f_head, fg, SIZE - 2 * PAD, line_gap=1.0) + 36

    f_sub = newsreader(38, weight=500, opsz=20)
    draw_multiline(d, (PAD, y), args.standfirst, f_sub, sub_fg, 860, line_gap=1.35)

    src_font = mono(24)
    paste_logo(img, logo_variant, width=285)
    ascent, descent = src_font.getmetrics()
    d.text((PAD, SIZE - PAD - ascent - descent), args.source, font=src_font, fill=source_fg)
    return img


def tpl_quote(args):
    img = Image.new("RGB", (SIZE, SIZE), INK)
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), args.kicker, font=mono(26), fill=GREY_ON_INK)

    f_quote = newsreader(84, weight=700, opsz=64)
    y = 340
    y = draw_multiline(d, (PAD, y), args.quote, f_quote, "#ffffff", SIZE - 2 * PAD, line_gap=1.12)

    circle_d = 130
    cy = SIZE - PAD - circle_d
    d.ellipse([PAD, cy, PAD + circle_d, cy + circle_d], fill="#2a2a28")
    tx = PAD + circle_d + 28
    d.text((tx, cy + 20), args.name, font=newsreader(40, weight=700, opsz=24), fill="#ffffff")
    d.text((tx, cy + 74), args.title, font=newsreader(30, weight=500, opsz=20), fill=GREY_ON_INK)

    paste_logo(img, "white", width=228)
    return img


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--template", required=True, choices=["number", "breaking", "quote"])
    p.add_argument("--out", required=True)
    p.add_argument("--bg", default="ink", choices=["ink", "paper"])
    # number
    p.add_argument("--kicker", default="")
    p.add_argument("--number", default="")
    p.add_argument("--what", default="")
    p.add_argument("--context", default="")
    p.add_argument("--source", default="")
    # breaking
    p.add_argument("--tag", default="BREAKING")
    p.add_argument("--date", default="")
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
