# bread-ig-content

Image generation + hosting for the `bread.eg` Instagram account
("Egypt real estate & investment news"). Public repo so
`raw.githubusercontent.com` links are fetchable by Instagram's
Content Publishing API (`image_url` must be a public URL).

## What's here

- `fonts/` — Newsreader (variable) + JetBrains Mono, the brand's two typefaces
- `assets/` — bread. logo (dark + white variants)
- `scripts/make_post.py` — renders a 1080x1080 PNG in one of three brand
  templates: `number` (Number of the Day), `breaking` (Breaking Headline,
  ink or paper background via `--bg`), `quote` (On the Record)
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
2. Strip emoji, adapt to brand caption pattern (one-line fact, two lines
   context, what it means for a buyer, 5-8 hashtags), pick a template.
3. `python3 scripts/make_post.py --template ... --out posts/YYYY-MM-DD-slotN.png ...`
4. `git add posts/... && git commit -m "..." && git push`
5. `python3 scripts/publish_post.py --image-url https://raw.githubusercontent.com/baherarafat-ctrl/bread-ig-content/main/posts/YYYY-MM-DD-slotN.png --caption "..."`

Brand rules: no emoji, no gradients, Newsreader/JetBrains Mono only,
ink (#0a0a0a) / paper (#ffffff) / bone (#f4f4f1) / deep red accent,
logo bottom-right, one idea per post, never two red tiles back to back.
