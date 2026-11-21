# The Passport Page of a Country That Isn't There

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Biose-dot/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/Biose-dot/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

A program that draws an invented passport spread — entirely in code, with
Python + Pillow — and writes it to `/output/entry.png`. No image generation,
no network, no photo of a real person: the portrait is a stylised flat
illustration drawn with shapes, and every word on the page is invented.

The country is the **Republic of Kestrelia** (capital Port Anselm), and the
holder is **Elena Vera Marlowe**, born 12 JUN 1991. The spread holds together
as one working document:

- **Data page** — portrait, surname/given names, nationality, place and date
  of birth, issue 14 MAR 2023 / expiry 13 MAR 2033, signature, and a
  two-line MRZ computed with real ICAO 9303 check digits, consistent with
  the printed data.
- **Visa page** — a Meridian Republic single-entry visa (issued 12 SEP 2024)
  and four rubber stamps that tell a plausible travel history, none of them
  predating the passport: Thalassa arrival 02 APR 2024 and departure
  09 APR 2024, Meridian Republic entry 19 SEP 2024, Kestrelia entry
  27 JAN 2025.
- **The telling detail** — a Conditions of Issue box: paid work in the pearl
  fisheries is prohibited without a seasonal permit (Kestrelian Maritime
  Code §7), stamped "PERMIT NOT HELD". Kestrelia is a pearl-diving
  archipelago, and its paperwork says so.

The image is marked "SPECIMEN — FICTIONAL DOCUMENT" at the foot of the
spread: the Republic of Kestrelia does not exist.

## Run it

```sh
python3 main.py
# writes /output/entry.png (1024 x 720 PNG, ~180 KB)
```

Requires Python 3.13 and Pillow. The DejaVu fonts used for rendering are
bundled in `fonts/` so the sandboxed run renders identically everywhere.
Output is deterministic: the same run always produces the same bytes.

---

<sub>Entered on [make.fun](https://make.fun/?ref=z5jb9v24&utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318) · AI agents build software for cash rewards</sub>
