#!/usr/bin/env python3
"""واژهٔ روز — deterministic daily term pick.

The pick is seeded with the calendar date (YYYY-MM-DD), so every run on
the same day yields the same term, and the term rotates daily without
any stored state.

Usage:
    python scripts/totd.py             # today's term
    python scripts/totd.py --date 2026-09-03
"""

import argparse
import random
from datetime import date, datetime


def pick_index(count: int, day: date = None) -> int:
    day = day or date.today()
    return random.Random(day.isoformat()).randrange(count)


def main():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_pages import load_all_terms

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=None, help="ISO date, e.g. 2026-09-03")
    args = parser.parse_args()

    day = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else date.today()
    records = [record for _, record in load_all_terms()]
    if not records:
        raise SystemExit("no terms found")

    term = records[pick_index(len(records), day)]
    print(f"واژهٔ روز {day.isoformat()}:")
    print(f"  {term['term_fa']} — {term.get('term_en', '')}")
    print(f"  {term.get('definition_fa', '')}")
    print(f"  https://bmhmdyan279-png.github.io/eng-terms-fa/terms/{term['slug']}/")


if __name__ == "__main__":
    main()
