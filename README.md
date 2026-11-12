<p align="center">
  <img src="assets/banner.svg" alt="tzmeet animated terminal demo" width="800">
</p>

<h1 align="center">tzmeet</h1>

<p align="center">
  Find the best meeting time across time zones.<br>
  <b>One file. Zero dependencies. Works offline.</b>
</p>

---

## Quick start

No install needed. Download the single file and run it:

```bash
curl -O https://raw.githubusercontent.com/ERROR404DTIR/tzmeet/main/tzmeet.py
python tzmeet.py Tehran London "New York"
```

Requires Python 3.9+ (standard library only).
On Windows, if you see a "no time zone database" message, run `pip install tzdata` once.

## Two modes

**1. Planner.** A 24-hour grid in every zone. The first zone is the reference.
`*` marks work hours and `>>` marks hours when everyone is working:

```bash
python tzmeet.py Tehran London "New York"
python tzmeet.py Berlin Sydney --date 2026-12-01 --work 8-17
```

**2. Convert.** What time is it everywhere when it's 14:00 in the first zone?

```bash
python tzmeet.py Tehran London Tokyo --at 14:00
```

## Options

| Option | Meaning |
|---|---|
| `--at HH:MM` | Convert a time in the first zone to all the others |
| `--date YYYY-MM-DD` | Plan for a specific day (daylight saving is handled correctly) |
| `--work 9-18` | Define work hours (default 9-18) |

Zones can be plain city names (`Tokyo`, `New York`) or full IANA names (`America/New_York`).
Half-hour zones such as Tehran (UTC+3:30) and India (UTC+5:30) are handled properly.
Set `NO_COLOR=1` to turn off colors.
