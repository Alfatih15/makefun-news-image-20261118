# BUILD_LOG.md — news-image-20261118

## What was built
`main.py` (Python 3.13, stdlib only) draws a 1024x1024 newspaper front page
for Wednesday 18 November 2026 and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`:
masthead "THE WORLD TODAY", navy date banner "WEDNESDAY 18 NOVEMBER 2026",
a lead APEC/Shenzhen story with a globe pictogram, four grid stories
(Manila/Quad, Kerch Bridge, Iran drones in Bahrain, North Korea missile),
and a bottom strip (UK sanctions / Gaza truce; Cyclone Akvan / Dhoni IPL
retirement). Text is rendered with a 5x7 bitmap font defined in code;
the PNG is encoded by hand (zlib + struct, filter 0). No network, no
embedded image bytes, nothing copied from the kit starter.

## Verification
- `mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py` run twice:
  both runs wrote 20,931 bytes, sha256
  `84dc19ccffa63cfe2c5dedc58f93dc8109a8342296083fbbae899b445417eb55`
  (identical — deterministic).
- PNG signature valid, dimensions 1024x1024, size 20,931 bytes (limit 1 MiB).
- Rendered image viewed directly: masthead, date banner and all six
  panels legible; no text overflow, no garbled text.
- First render had a defect: the bottom-strip headlines at scale 3
  overflowed their panels and collided with the footer. Fixed by adding
  an `hscale` parameter to `panel()` and rendering the bottom strip at
  scale 2, plus denser arc steps and solid globe dots; re-rendered and
  re-verified (sha256 above is the fixed version).

## Authorship
All code written with file write/edit tools in this session (which began
after the competition opened, 2026-11-18T00:00:00Z). `main.py` was written
in full, then revised in a second edit pass. No shell heredoc/cat/cp/sed
was used to write code, and no kit starter file was copied.
