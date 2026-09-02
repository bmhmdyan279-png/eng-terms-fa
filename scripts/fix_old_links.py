#!/usr/bin/env python3
"""Relink legacy list pages (docs/book-vocab.md, docs/construction-terms.md)
to the current term ids.

Links have the form ``[متن فارسی](terms/slug.md)``. When the target slug no
longer exists among the current ids, the Persian link text is resolved
against the data (data/terms/*.yaml) and the link is rewritten to the
current id. Unresolvable links are reported and fail the script — nothing
is silently degraded.

Usage:
    python scripts/fix_old_links.py
"""

import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"
TARGET_FILES = [ROOT / "docs" / "book-vocab.md", ROOT / "docs" / "construction-terms.md"]

LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(terms/([^)]+\.md)\)")


def normalize_persian(text: str) -> str:
    if not text:
        return ""
    text = text.replace("ي", "ی").replace("ك", "ک")
    return unicodedata.normalize("NFKC", text)


def load_terms():
    terms = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        terms.extend(doc.get("terms") or [])
    return terms


def main():
    terms = load_terms()
    if not terms:
        print(f"error: no terms found in {DATA_DIR}", file=sys.stderr)
        return 2

    current_ids = {t["id"] for t in terms if "id" in t}
    by_term_fa = {}
    for term in terms:
        key = normalize_persian((term.get("term_fa") or "").strip())
        if key:
            by_term_fa.setdefault(key, term)

    total_kept = total_relinked = 0
    unresolved = []

    for target_file in TARGET_FILES:
        if not target_file.exists():
            print(f"warning: {target_file} not found, skipping")
            continue

        text = target_file.read_text(encoding="utf-8")
        kept = relinked = 0

        def replace(match):
            nonlocal kept, relinked
            link_text, filename = match.group(1), match.group(2)
            slug = filename[:-3]
            if slug in current_ids:
                kept += 1
                return match.group(0)
            term = by_term_fa.get(normalize_persian(link_text.strip()))
            if term:
                relinked += 1
                return f"[{link_text}](terms/{term['id']}.md)"
            unresolved.append((target_file.name, link_text, filename))
            return match.group(0)

        new_text = LINK_PATTERN.sub(replace, text)
        if new_text != text:
            target_file.write_text(new_text, encoding="utf-8")
            print(f"✅ {target_file.name}: {relinked} link(s) relinked, {kept} already valid")
        else:
            print(f"ℹ️ {target_file.name}: no changes needed ({kept} links valid)")
        total_kept += kept
        total_relinked += relinked

    print(f"\nsummary: {total_kept} valid, {total_relinked} relinked, {len(unresolved)} unresolved")
    if unresolved:
        for file_name, link_text, filename in unresolved:
            print(f"  ✗ {file_name}: [{link_text}](terms/{filename}) matches no current term", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
