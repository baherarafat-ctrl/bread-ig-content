# bread-ig-content

Image generation + hosting for the `bread.eg` Instagram account
("Egypt real estate & investment news"). Public repo so
`raw.githubusercontent.com` links are fetchable by Instagram's
Content Publishing API (`image_url` must be a public URL).

## What's here

- `fonts/` — Newsreader (variable) + JetBrains Mono, the brand's two typefaces
- `assets/` — bread. logo (dark + white variants)
- `scripts/make_post.py` — renders a 1080x1080 PNG in one of three brand
  templates: `number`, `breaking` (ink or paper background via `--bg`),
  `quote`. Every template shares the same header/footer: just the date
  top-left (no category label/eyebrow text), and a hairline divider with
  the source citation + bread logo below it, bottom-right.
- `scripts/publish_post.py` — publishes an already-hosted image to
  Instagram via the Graph API (create container, poll, publish).
  Reads `IG_USER_ID` and `IG_ACCESS_TOKEN` from the environment.
- `posts/` — each day's rendered PNGs land here, committed and pushed so
  they're publicly fetchable at
  `https://raw.githubusercontent.com/baherarafat-ctrl/bread-ig-content/main/posts/<file>.png`
- `examples/` — sample renders for reference, not real posts

## Daily pipeline (what the scheduled agent does)

1. Read that day's "Egypt Real Estate Daily" digest email (Gmail), find
   the "SOCIAL MEDIA POST IDEAS" section, pick this slot's item.
2. Strip emoji, adapt to brand caption pattern (see below), pick a template.
3. `python3 scripts/make_post.py --template ... --out posts/YYYY-MM-DD-slotN.png ...`
4. `git add posts/... && git commit -m "..." && git push`
5. `python3 scripts/publish_post.py --image-url https://raw.githubusercontent.com/baherarafat-ctrl/bread-ig-content/main/posts/YYYY-MM-DD-slotN.png --caption "..."`

## Caption pattern (as of Sept 2026)

- Short: one line of fact (with the key number), one line on what it
  means for a buyer. No "context" paragraph, no filler.
- No hashtags.
- Followed by a 1-2 line Arabic translation/summary of the same two
  points (not a literal word-for-word translation - a natural, concise
  Arabic rendering of the same fact + takeaway).
- No emoji anywhere, in either language.

Example:
```
Egypt tendered EGP 15.68 billion in New Cairo land across six plots in Third Settlement, North Rehab and Beit Al Watan.
Fresh supply at this scale often signals new project launches within the next 12 to 24 months.

طرحت الحكومة المصرية أراضي بقيمة 15.68 مليار جنيه في القاهرة الجديدة على ست قطع بالتجمع الثالث والرحاب الشمالي وبيت الوطن.
هذا الطرح قد يمهّد لإطلاق مشروعات جديدة خلال العام إلى العامين القادمين.
```

Brand rules: no emoji, no gradients, Newsreader/JetBrains Mono only,
ink (#0a0a0a) / paper (#ffffff) / bone (#f4f4f1) / deep red accent,
logo bottom-right below a hairline divider, date-only header (no
category label), one idea per post, never two red tiles back to back.
