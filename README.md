# makefun-news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/Alfatih15/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/Alfatih15/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

**The World Today** — one image summing up the world news of Wednesday 18 November 2026, drawn entirely in code: a newspaper front page with a masthead, the date banner, and six story panels.

Stories covered: the APEC summit opening in Shenzhen (Trump–Xi–Putin trilateral set for Thursday 19 Nov), Trump in Manila for Quad talks and Canada–China trade deals, Ukraine striking the Kerch Bridge for a second day, Iranian drones targeting a US radar in Bahrain (intercepted), North Korea's ballistic missile launch, UK sanctions on eight Israeli settlement firms with the Gaza truce near collapse, Cyclone Akvan nearing India, and MS Dhoni retiring from the IPL.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png — 1024x1024 PNG, byte-identical on every run
```

## How it works

`main.py` is pure Python 3.13 standard library (no network, no PIL, no fonts on disk). It defines a 5x7 bitmap font in code, draws the whole front page with simple vector pictograms (globe, plane, bridge, drone, missile, scales, cyclone), and encodes the PNG itself with `zlib` + `struct`. Every pixel comes from code in this repository — no pre-made image is embedded or copied.

---

<sub>Entered on [make.fun](https://make.fun/?ref=hjff56h1&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
