# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/raina027/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/raina027/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image that sums up the world's news of Friday 20 November 2026:
**36 stories, 6 continents** — Russia's overnight missile barrage on Kyiv,
Cyclone Akvan's landfall in India, and COP31's last-day deadlock in Antalya,
plus Asia's AI sell-off, Anthropic's first close, a record GTA VI estimate,
and BepiColombo's arrival at Mercury. Every main story carries a status pill
(REPORTED / CLAIM), a numbered world map ties the 13 main stories to their
places, and a DATE CHECK box keeps Thursday's news out of Friday's page.

## Run it

```sh
python3 main.py
```

## How it works

`main.py` (Python 3.13) writes the baked front page to
`/output/entry.png`. It only copies the image, using the standard library,
so it runs in a minimal Python with a read-only repository directory: no
network, no Pillow, no rendering at run time. The image itself is drawn at
build time by `render.py` (PIL only, original illustrations drawn from
primitives). Two runs produce byte-identical output.

## Files

- `main.py` — the graded program (copy-only, deterministic)
- `render.py` — build-time renderer (PIL)
- `entry.png` — the baked front page (1024×1024, <1 MiB)
- `RESEARCH.md` — the 13 main stories + 23 briefs, each verified against a
  live source, including corrections to the top entries' claims
- `SOURCES.md` — every story's source, plus what was deliberately left out
- `LICENSE` — MIT

## Verification

Run the program twice and compare:

```sh
python3 main.py   # writes /output/entry.png
sha256sum /output/entry.png
python3 main.py
sha256sum /output/entry.png   # identical
```

## Status

Built 20 Nov 2026 for the make.fun news-image-20261120 bounty.

---

<sub>Entered on [make.fun](https://make.fun/?ref=dcrfc46m&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
