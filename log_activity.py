#!/usr/bin/env python3
"""
log_activity.py — append one entry to activity_log.json without hand-editing JSON.

Local usage (defaults to today if --date is omitted):
    python3 log_activity.py kc7 25 "Questions answered in DNS investigation"
    python3 log_activity.py letsdefend 2 "SOC101 alert triage"
    python3 log_activity.py kc7 1 "backfilled case" --date 2026-08-01

Also works via env vars PLATFORM / COUNT / NOTE / DATE (used by the
"Log activity" GitHub Action, so you can log from the GitHub mobile app —
leave the Action's "date" input blank to use today, or fill it in to log
a past day).
"""

import json
import os
import sys
import datetime
from pathlib import Path

PATH = Path(__file__).parent / "activity_log.json"
VALID_PLATFORMS = ("kc7", "letsdefend")


def extract_date_flag(argv):
    """Pull --date VALUE or --date=VALUE out of argv, wherever it appears."""
    date_val = None
    remaining = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--date" and i + 1 < len(argv):
            date_val = argv[i + 1]
            i += 2
            continue
        if arg.startswith("--date="):
            date_val = arg.split("=", 1)[1]
            i += 1
            continue
        remaining.append(arg)
        i += 1
    return date_val, remaining


def main():
    date_str, argv = extract_date_flag(sys.argv[1:])

    if argv:
        platform = argv[0].strip().lower()
        count = int(argv[1]) if len(argv) > 1 else 1
        note = " ".join(argv[2:]).strip()
    else:
        platform = os.environ.get("PLATFORM", "").strip().lower()
        count = int(os.environ.get("COUNT") or 1)
        note = os.environ.get("NOTE", "").strip()
        if date_str is None:
            date_str = os.environ.get("DATE", "").strip() or None

    if platform not in VALID_PLATFORMS:
        sys.exit(f"Unknown platform: {platform!r} (expected one of {VALID_PLATFORMS})")
    if count <= 0:
        sys.exit("Count must be a positive whole number")

    if date_str:
        try:
            date_obj = datetime.date.fromisoformat(date_str)
        except ValueError:
            sys.exit(f"Invalid date: {date_str!r} (expected YYYY-MM-DD)")
    else:
        date_obj = datetime.date.today()

    entry = {"date": date_obj.isoformat(), "platform": platform, "count": count}
    if note:
        entry["note"] = note

    data = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else []
    data.append(entry)
    data.sort(key=lambda e: e.get("date", ""))  # keep the file readable when backfilling
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    unit = "questions" if platform == "kc7" else "cases"
    print(f"Logged: {entry} ({count} {unit})")


if __name__ == "__main__":
    main()
