#!/usr/bin/env python3
"""tzmeet - find the best meeting time across time zones.

One file, zero dependencies. Needs Python 3.9+.
(On Windows, if no time zone data is found, run once: pip install tzdata)

  python tzmeet.py Tehran London "New York"            # 24h planner, first zone is the reference
  python tzmeet.py Tehran London Tokyo --at 14:00      # convert 14:00 Tehran time everywhere
  python tzmeet.py Berlin Sydney --date 2026-12-01 --work 8-17
"""
import argparse
import os
import sys
from datetime import date, datetime, time

try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError:
    sys.exit("tzmeet needs Python 3.9 or newer.")

__version__ = "1.0.0"

USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ
if USE_COLOR and os.name == "nt":
    os.system("")  # enables ANSI colors in the Windows console


def paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def resolve(query, zones):
    if query in zones:
        return query
    key = query.lower().replace(" ", "_")
    exact = sorted(z for z in zones if z.lower().split("/")[-1] == key)
    if exact:
        return exact[0]
    partial = sorted(z for z in zones if key in z.lower())
    if partial:
        return partial[0]
    sys.exit(f"error: unknown time zone '{query}'. Try a city like 'Tokyo' or a name like 'Europe/Paris'.")


def short(zone):
    return zone.split("/")[-1].replace("_", " ")


def utc_label(dt):
    mins = int(dt.utcoffset().total_seconds() // 60)
    sign = "+" if mins >= 0 else "-"
    mins = abs(mins)
    return f"UTC{sign}{mins // 60}" + (f":{mins % 60:02d}" if mins % 60 else "")


def convert(zones, day, at):
    try:
        h, m = (int(x) for x in at.split(":"))
        src = datetime.combine(day, time(h, m), tzinfo=ZoneInfo(zones[0]))
    except ValueError:
        sys.exit("error: --at must look like HH:MM, e.g. 14:30")
    print(f"{day:%Y-%m-%d}  {at} in {short(zones[0])}\n")
    for z in zones:
        dt = src.astimezone(ZoneInfo(z))
        delta = (dt.date() - day).days
        tag = f" ({delta:+d}d)" if delta else ""
        print(f"{short(z):<18}{dt:%a %H:%M}{tag:<7}  {utc_label(dt)}")


def grid(zones, day, start, end):
    tzs = [ZoneInfo(z) for z in zones]
    print(f"Meeting planner for {day:%Y-%m-%d}  (reference: {short(zones[0])})")
    print(f"'*' = work hours ({start}:00-{end}:00), '>>' = everyone is working\n")
    print("   " + "  ".join(short(z)[:11].ljust(11) for z in zones))
    first = datetime.combine(day, time(12), tzinfo=tzs[0])
    print("   " + "  ".join(paint(utc_label(first.astimezone(t)).ljust(11), 90) for t in tzs))
    overlap = []
    for h in range(24):
        base = datetime.combine(day, time(h), tzinfo=tzs[0])
        cells, flags = [], []
        for t in tzs:
            dt = base.astimezone(t)
            working = start <= dt.hour + dt.minute / 60 < end
            delta = (dt.date() - day).days
            text = f"{dt:%H:%M}" + (f"{delta:+d}d" if delta else "")
            cells.append((f"{text:<9}{'*' if working else ' '} ", working))
            flags.append(working)
        everyone = all(flags)
        if everyone:
            overlap.append(f"{h:02d}:00")
        color = lambda w: "1;32" if everyone else ("0" if w else "90")
        marker = ">>" if everyone else "  "
        print(f"{marker} " + " ".join(paint(c, color(w)) for c, w in cells))
    print()
    if overlap:
        print(f"Everyone is working at ({short(zones[0])} time): {', '.join(overlap)}")
    else:
        print("No hour works for everyone. Try a wider --work range, e.g. --work 8-20")


def main():
    p = argparse.ArgumentParser(prog="tzmeet", description="Find the best meeting time across time zones.")
    p.add_argument("zones", nargs="+", help="cities or zone names, e.g. Tehran London 'New York' (first = reference)")
    p.add_argument("--date", help="date as YYYY-MM-DD (default: today in the first zone)")
    p.add_argument("--at", metavar="HH:MM", help="convert this time in the first zone to all others")
    p.add_argument("--work", default="9-18", help="work hours, e.g. 9-18 (default)")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args()

    known = available_timezones()
    if not known:
        sys.exit("error: no time zone database found. On Windows run: pip install tzdata")
    zones = [resolve(z, known) for z in a.zones]

    try:
        start, end = (int(x) for x in a.work.split("-"))
        day = date.fromisoformat(a.date) if a.date else datetime.now(ZoneInfo(zones[0])).date()
    except ValueError:
        sys.exit("error: use --work like 9-18 and --date like 2026-12-01")

    if a.at:
        convert(zones, day, a.at)
    else:
        grid(zones, day, start, end)


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
