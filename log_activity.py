#!/usr/bin/env python3
"""
log_activity.py — append one entry to activity_log.json without hand-editing JSON.

Local usage:
    python3 log_activity.py kc7
    python3 log_activity.py letsdefend 2 "SOC101 alert triage"

Also works via env vars PLATFORM / COUNT / NOTE (used by the
"Log activity" GitHub Action, so you can log from the GitHub mobile app).
"""

import json
import os
import sys
import datetime
from pathlib import Path

PATH = Path(__file__).parent / "activity_log.json"
VALID_PLATFORMS = ("kc7", "letsdefend")


def main():
    if len(sys.argv) > 1:
        platform = sys.argv[1].strip().lower()
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        note = " ".join(sys.argv[3:]).strip()
    else:
        platform = os.environ.get("PLATFORM", "").strip().lower()
        count = int(os.environ.get("COUNT") or 1)
        note = os.environ.get("NOTE", "").strip()

    if platform not in VALID_PLATFORMS:
        sys.exit(f"Unknown platform: {platform!r} (expected one of {VALID_PLATFORMS})")

    entry = {
        "date": datetime.date.today().isoformat(),
        "platform": platform,
        "count": count,
    }
    if note:
        entry["note"] = note

    data = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else []
    data.append(entry)
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Logged: {entry}")


if __name__ == "__main__":
    main()
