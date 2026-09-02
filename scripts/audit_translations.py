#!/usr/bin/env python3
"""Audit machine-translated English equivalents in data/terms.yaml.

Flags suspicious ``term_en`` values that look like raw machine translation:

* shorter than 3 characters or longer than 3 words
* containing known forbidden phrases (literal word-for-word translations)

Results are written to ``translation_alerts.csv`` in the repository root.

Usage:
    python scripts/audit_translations.py            # report only (always exit 0)
    python scripts/audit_translations.py --strict   # exit 1 when any alert exists
"""

import argparse
import csv
import sys
from pathlib import Path

import yaml

MIN_TERM_LENGTH = 3
MAX_WORD_COUNT = 3

# Phrases that appear when a machine translates Persian word-for-word
# (e.g. «نبشی» -> "do not brick", «نره» -> "don't be a brick",
#  «آچار» -> "pickle", «چین» -> "chinese").
FORBIDDEN_PHRASES = (
    "do not",
    "don't be",
    "pickle",
    "chinese",
)

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "terms.yaml"
OUTPUT_FILE = ROOT / "translation_alerts.csv"

CSV_FIELDS = ["term_fa", "term_en", "category", "slug", "reasons"]


def find_problems(term_en):
    """Return the list of problems for a term_en value (empty = clean)."""
    text = (term_en or "").strip()
    if not text:
        return ["empty term_en"]

    problems = []

    if len(text) < MIN_TERM_LENGTH:
        problems.append(f"too short ({len(text)} < {MIN_TERM_LENGTH} chars)")

    word_count = len(text.split())
    if word_count > MAX_WORD_COUNT:
        problems.append(f"too long ({word_count} > {MAX_WORD_COUNT} words)")

    lowered = text.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            problems.append(f"forbidden phrase: '{phrase}'")

    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with code 1 if any term is flagged",
    )
    args = parser.parse_args()

    if not DATA_FILE.exists():
        print(f"error: data file not found: {DATA_FILE}", file=sys.stderr)
        return 2

    with open(DATA_FILE, encoding="utf-8") as f:
        terms = yaml.safe_load(f) or []

    alerts = []
    for index, term in enumerate(terms, start=1):
        problems = find_problems(term.get("term_en"))
        if problems:
            alerts.append(
                {
                    "term_fa": term.get("term_fa") or f"<entry #{index}>",
                    "term_en": (term.get("term_en") or "").strip(),
                    "category": term.get("category", ""),
                    "slug": term.get("slug", ""),
                    "reasons": "; ".join(problems),
                }
            )

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(alerts)

    print(f"Audited {len(terms)} terms against term_en quality rules")
    print(
        f"Rules: min length {MIN_TERM_LENGTH} chars, max {MAX_WORD_COUNT} words, "
        f"forbidden phrases: {', '.join(FORBIDDEN_PHRASES)}"
    )
    print(f"{len(alerts)} alert(s) written to {OUTPUT_FILE}")
    for row in alerts:
        print(f"  WARNING: {row['term_fa']} | {row['term_en']} | {row['reasons']}")

    if alerts and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
