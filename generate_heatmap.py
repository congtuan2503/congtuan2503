#!/usr/bin/env python3
"""
generate_heatmap.py

Builds a GitHub-contributions-style SVG heatmap from activity_log.json.

Why this exists:
KC7 (kc7cyber.com) and LetsDefend don't expose a public API or embeddable
badge, so their activity can't be pulled automatically. This script instead
reads a small JSON log that YOU update by hand, and turns it into a heatmap +
stats block that you
embed in your GitHub profile README (image, not live data).

Usage:
    python3 generate_heatmap.py

Reads:  activity_log.json
Writes: assets/activity_heatmap.svg
"""

import json
import datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent
LOG_FILE = ROOT / "activity_log.json"
OUT_FILE = ROOT / "assets" / "activity_heatmap.svg"

# ---- theme -----------------------------------------------------------
CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT_PAD = 28
TOP_PAD = 54
BOTTOM_PAD = 60

# Calm anime-blue palette: vivid enough on GitHub's dark background without
# the visual fatigue of a neon glow.
LEVEL_COLORS = ["#161b22", "#172554", "#1e40af", "#2563eb", "#60a5fa"]
EMPTY_COLOR = "#161b22"
TEXT_COLOR = "#e2e8f0"
MUTED_COLOR = "#94a3b8"

# Heatmap intensity is a comparable learning-effort score, not a raw count.
# A KC7 case averages 70 questions and is treated as the effort of 4
# LetsDefend cases.
KC7_QUESTIONS_PER_CASE = 70
LETSDEFEND_CASES_PER_KC7_CASE = 4
EFFORT_PER_KC7_QUESTION = LETSDEFEND_CASES_PER_KC7_CASE / KC7_QUESTIONS_PER_CASE

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}  # Mon=0..Sun=6, sparse labels


def load_log():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def level_for(count, max_count):
    if count <= 0:
        return 0
    if max_count <= 1:
        return 4 if count > 0 else 0
    # 4 buckets above zero, scaled to the max day in the log
    ratio = count / max_count
    if ratio <= 0.25:
        return 1
    if ratio <= 0.5:
        return 2
    if ratio <= 0.75:
        return 3
    return 4


def effort_for(platform, count):
    """Return effort in LetsDefend-case equivalents."""
    if platform == "kc7":
        return count * EFFORT_PER_KC7_QUESTION
    if platform == "letsdefend":
        return count
    return count


def format_number(value):
    """Format counts cleanly, keeping a single decimal only when needed."""
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def compute_streaks(day_counts, end_date):
    """Current streak (consecutive days up to end_date, or the last active
    day if today has nothing logged yet) and longest streak in the window."""
    all_days = sorted(day_counts.keys())
    if not all_days:
        return 0, 0

    longest = cur_run = 0
    prev = None
    for d in all_days:
        if prev is not None and (d - prev).days == 1:
            cur_run += 1
        else:
            cur_run = 1
        longest = max(longest, cur_run)
        prev = d

    # current streak: walk backwards from end_date (or last logged day)
    anchor = end_date if end_date in day_counts else all_days[-1]
    current = 0
    d = anchor
    active = set(day_counts.keys())
    while d in active:
        current += 1
        d -= datetime.timedelta(days=1)
    return current, longest


def build_svg(entries):
    today = datetime.date.today()
    # Align the grid so it ends on the most recent Saturday and spans ~53 weeks
    end = today
    start = end - datetime.timedelta(days=370)
    start -= datetime.timedelta(days=(start.weekday() + 1) % 7)  # back to a Sunday

    day_effort = defaultdict(float)
    day_platform_counts = defaultdict(lambda: defaultdict(int))
    platform_totals = defaultdict(int)

    for e in entries:
        try:
            d = datetime.date.fromisoformat(e["date"])
        except (KeyError, ValueError):
            continue
        count = int(e.get("count", 1))
        if count <= 0:
            continue
        platform = str(e.get("platform", "other")).lower()
        day_effort[d] += effort_for(platform, count)
        day_platform_counts[d][platform] += count
        platform_totals[platform] += count

    max_effort = max(day_effort.values(), default=0)
    weeks = []
    d = start
    while d <= end:
        week = []
        for _ in range(7):
            week.append(d)
            d += datetime.timedelta(days=1)
        weeks.append(week)

    width = LEFT_PAD + len(weeks) * STEP + 10
    height = TOP_PAD + 7 * STEP + BOTTOM_PAD

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Segoe UI, Helvetica, Arial, sans-serif">'
    )
    svg.append(f'<rect width="{width}" height="{height}" fill="#0d1117" rx="10"/>')

    title = "SOC Training Activity \u2014 KC7 questions &amp; LetsDefend cases"
    svg.append(
        f'<text x="{LEFT_PAD}" y="18" fill="{TEXT_COLOR}" font-size="13" font-weight="600">{title}</text>'
    )
    svg.append(
        f'<text x="{LEFT_PAD}" y="32" fill="{MUTED_COLOR}" font-size="10">'
        f'Normalized effort: {KC7_QUESTIONS_PER_CASE} KC7 questions = {LETSDEFEND_CASES_PER_KC7_CASE} LetsDefend cases</text>'
    )

    # month labels
    last_month = None
    for wi, week in enumerate(weeks):
        first_day = week[0]
        if first_day.day <= 7 and first_day.month != last_month:
            x = LEFT_PAD + wi * STEP
            svg.append(
                f'<text x="{x}" y="{TOP_PAD - 6}" fill="{MUTED_COLOR}" font-size="10">'
                f'{MONTH_NAMES[first_day.month - 1]}</text>'
            )
            last_month = first_day.month

    # weekday labels
    for wd, label in WEEKDAY_LABELS.items():
        y = TOP_PAD + wd * STEP + CELL - 1
        svg.append(f'<text x="0" y="{y}" fill="{MUTED_COLOR}" font-size="9">{label}</text>')

    # cells
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day > end:
                continue
            x = LEFT_PAD + wi * STEP
            y = TOP_PAD + di * STEP
            effort = day_effort.get(day, 0)
            color = LEVEL_COLORS[level_for(effort, max_effort)] if effort else EMPTY_COLOR
            raw = day_platform_counts.get(day, {})
            if raw:
                details = []
                if raw.get("kc7"):
                    details.append(f"KC7: {raw['kc7']} questions")
                if raw.get("letsdefend"):
                    details.append(f"LetsDefend: {raw['letsdefend']} cases")
                for platform, count in sorted(raw.items()):
                    if platform not in {"kc7", "letsdefend"}:
                        details.append(f"{platform}: {count}")
                title_txt = f"{day.isoformat()}: {'; '.join(details)} ({format_number(effort)} effort)"
            else:
                title_txt = f"{day.isoformat()}: no activity"
            svg.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}"><title>{title_txt}</title></rect>'
            )

    # legend
    legend_y = height - 46
    svg.append(f'<text x="{LEFT_PAD}" y="{legend_y + 9}" fill="{MUTED_COLOR}" font-size="10">Less effort</text>')
    lx = LEFT_PAD + 32
    for lvl, color in enumerate(LEVEL_COLORS):
        svg.append(f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
        lx += STEP
    svg.append(f'<text x="{lx + 4}" y="{legend_y + 9}" fill="{MUTED_COLOR}" font-size="10">More effort</text>')

    # stats line
    current_streak, longest_streak = compute_streaks(day_effort, today)
    kc7_total = platform_totals.get("kc7", 0)
    ld_total = platform_totals.get("letsdefend", 0)
    total_effort = sum(day_effort.values())
    stats_txt = f"KC7: {kc7_total} questions   \u2022   LetsDefend: {ld_total} cases   \u2022   Total: {format_number(total_effort)} LD-case equivalent"
    streak_txt = f"current streak: {current_streak}d   \u2022   longest streak: {longest_streak}d"
    svg.append(f'<text x="{LEFT_PAD}" y="{height - 21}" fill="{TEXT_COLOR}" font-size="10">{stats_txt}</text>')
    svg.append(f'<text x="{LEFT_PAD}" y="{height - 7}" fill="{MUTED_COLOR}" font-size="10">{streak_txt}</text>')

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    entries = load_log()
    svg = build_svg(entries)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT_FILE} from {len(entries)} log entries.")


if __name__ == "__main__":
    main()
