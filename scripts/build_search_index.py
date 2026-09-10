#!/usr/bin/env python3
"""Build the Persian-aware search index and the stemmer parity fixture.

Outputs
-------
``docs/data/api/search-index.json``
    Compact, offline-friendly index consumed by ``docs/assets/js/persian-search.js``.
    Every searchable surface form of every record is pre-computed here with
    :mod:`persian_text`, so the browser never has to guess about morphology.

``tests/fixtures/stemming-golden.json``
    A golden corpus of query strings with the forms/stems/roots this engine
    produces. ``tools/check_stemmer_parity.js`` runs the JavaScript mirror over
    the same corpus and CI fails if the two disagree — the browser and the
    build can never drift apart silently.

Why a generated index instead of Pagefind alone?
    Pagefind tokenizes on whitespace and knows nothing about the Persian
    half-space, «ها» plural, یای نسبت, Arabic broken plurals or verb stems.
    «آجرکاری» was unfindable by a query for «آجر». This index fixes that while
    Pagefind keeps serving full-text search over the prose pages.

Usage:
    python scripts/build_search_index.py [--out DIR] [--fixture PATH]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from build_pages import ROOT, load_all_terms, load_meta, normalize_persian
from persian_text import (
    CONJUGATIONS,
    build_lexicon,
    build_protected,
    content_tokens,
    fold,
    index_forms,
    normalize_latin,
    normalize,
    record_roots,
    root,
    root_family,
    split_compound,
    stem,
    tokenize,
)

DEFAULT_OUT = ROOT / "docs" / "data" / "api"
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "stemming-golden.json"

INDEX_VERSION = "1.0.0"
ALGORITHM = "persian-root-v1"

#: field key → (record fields, boost, index_whole_string).
#: Keep the keys and boosts in sync with FIELD_BOOST in
#: docs/assets/js/persian-search.js — tools/check_stemmer_parity.js checks it.
#: `index_whole_string` is False for prose fields: storing an entire definition
#: as a single "form" would bloat the index without ever matching a query.
FIELDS = {
    "t": (("term_fa", "plural_fa"), 10.0, True),
    "a": (("synonyms", "search_aliases", "antonyms"), 8.0, True),
    "e": (("term_en", "term_fr", "term_de", "term_ar", "abbrev_en"), 6.0, True),
    "r": (("root_fa", "root_ar", "etymology_fa"), 5.0, True),
    "n": (("domain",), 2.0, True),
    "d": (("definition_fa", "usage_examples"), 1.0, False),
}

#: Strings fed to the parity fixture. They must cover every rule of the engine:
#: half-space, plural, یای نسبت, broken plural, verbal prefix, compound split,
#: typo tolerance, Latin text, digits, stopwords, empty input.
GOLDEN_CORPUS = [
    "آب‌بندی", "آب بندی", "آببندی", "آجرها", "آجرهایمان", "آجرکاری",
    "بندکشی", "بندی", "خاکبرداری", "بتن‌ریزی", "آرماتوربندی", "میلگرد",
    "تیرچه", "سرگرد", "مشخصات", "مقاومت", "ناشاقولی", "شاقولی",
    "می‌شود", "نمی‌شود", "شده‌اند", "گرفتند", "بستن", "بند",
    "جان‌پناه", "پشت‌بند", "کله‌راسته", "سنگ‌دانه", "سیمان", "سیمانی",
    "بتن مسلح", "بتن مسلح‌ها", "روانی بتن", "اسلامپ", "ویبره",
    "دیوار حائل", "حائل", "گچ‌کاری", "نماسازی", "زیرسازی", "سنگفرش",
    "خستگی", "خسته", "لنگر خمشی", "مدول الاستیسیته", "کرنش", "تنش",
    "sealing", "rebar", "Self-Consolidating", "ACI 318-19", "۱۱۰ درجه",
    "", "   ", "و یا که", "پل", "چاه کور", "چاه", "کور",
    "آجر چارگوش", "آجر چهارگوش", "خرک", "اسکوپ", "تخماق", "دج",
    "ریشه", "هم‌ریشه", "واژهٔ روز", "خانهٔ من", "کتاب‌ها", "دیگری",
]


def _values(record: dict, fields: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    for field in fields:
        value = record.get(field)
        if value is None:
            continue
        if isinstance(value, str):
            if value.strip():
                out.append(value)
        elif isinstance(value, list):
            out.extend(str(v) for v in value if v is not None and str(v).strip())
        elif isinstance(value, dict):
            out.extend(str(v) for v in value.values() if v is not None and str(v).strip())
    return out


def _forms_for(value: str, key: str, whole: bool, lexicon: set[str], protected: set[str]) -> list[str]:
    if key == "e":  # latin columns: fold case, keep words
        return index_forms(normalize_latin(value), lexicon, protected)
    if whole:
        return index_forms(value, lexicon, protected)
    # prose: index the reduced forms of each content token only. Stopwords and
    # the full sentence never become forms — the raw text stays in "d" for
    # substring fallback and highlighting.
    out: list[str] = []
    for token in content_tokens(value):
        for form in index_forms(token, lexicon, protected):
            if form not in out:
                out.append(form)
    return out


def term_forms(record: dict, lexicon: set[str], protected: set[str]) -> dict[str, list[str]]:
    """Pre-computed search forms per field, most specific first."""
    forms: dict[str, list[str]] = {}
    for key, (fields, _boost, whole) in FIELDS.items():
        seen: list[str] = []
        pool: set[str] = set()
        for value in _values(record, fields):
            for form in _forms_for(value, key, whole, lexicon, protected):
                if form not in pool:
                    pool.add(form)
                    seen.append(form)
        forms[key] = seen
    return forms


def term_roots(record: dict, lexicon: set[str], protected: set[str]) -> list[str]:
    """Delegate to the shared implementation (single source of truth)."""
    return record_roots(record, lexicon, protected)


def build_index(records: list[dict], meta: dict, lexicon: set[str], protected: set[str]) -> dict:
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in meta.get("domains", [])}
    entries = []
    roots_map: dict[str, list[str]] = {}

    for record in records:
        slug = record["slug"]
        definition = normalize(record.get("definition_fa") or "")
        entry = {
            "s": slug,
            "fa": normalize_persian(record.get("term_fa") or ""),
            "en": (record.get("term_en") or "").strip(),
            "d": definition[:220],
            "dom": record.get("domain") or [],
            "st": record.get("status", "draft"),
            "rl": record.get("review_level", "ai-assisted") if record.get("status") != "draft" else None,
            "r": term_roots(record, lexicon, protected),
            "f": term_forms(record, lexicon, protected),
        }
        for code in entry["dom"]:
            title = domain_titles.get(code)
            if title:
                entry["f"].setdefault("n", [])
                for form in index_forms(title, lexicon, protected):
                    if form not in entry["f"]["n"]:
                        entry["f"]["n"].append(form)
        entries.append(entry)
        for item in entry["r"]:
            roots_map.setdefault(item, [])
            if slug not in roots_map[item]:
                roots_map[item].append(slug)

    return {
        "version": INDEX_VERSION,
        "algorithm": ALGORITHM,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fields": {key: boost for key, (_fields, boost, _whole) in FIELDS.items()},
        "lexicon_size": len(lexicon),
        "count": len(entries),
        "terms": entries,
        "roots": roots_map,
        # The browser stemmer needs the same guard-rail lexicon the build used.
        # Sorted for a stable diff; ~30 KiB raw, ~8 KiB gzipped — cheap enough
        # to precache, which keeps search working offline (PWA promise).
        "lexicon": sorted(lexicon),
        # Headwords are lexicalized units and must survive stemming untouched.
        "protected": sorted(protected),
    }


def build_fixture(records: list[dict], lexicon: set[str], protected: set[str]) -> dict:
    """Golden output of the Python engine over GOLDEN_CORPUS."""
    cases = []
    for text in GOLDEN_CORPUS:
        cases.append(
            {
                "input": text,
                "normalize": normalize(text),
                "fold": fold(text),
                "tokenize": tokenize(text),
                "content_tokens": content_tokens(text),
                "stem": [stem(t, lexicon, protected) for t in tokenize(text)],
                "root": [root(t, lexicon, protected) for t in tokenize(text)],
                "forms": index_forms(text, lexicon, protected),
            }
        )
    return {
        "algorithm": ALGORITHM,
        "note": "Generated by scripts/build_search_index.py — do not edit by hand. "
                "tools/check_stemmer_parity.js asserts the JS mirror reproduces it.",
        "lexicon_size": len(lexicon),
        "cases": cases,
    }


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE))
    args = parser.parse_args()

    records = [record for _, record in load_all_terms()]
    meta = load_meta()
    lexicon = build_lexicon(records)
    protected = build_protected(records)

    index = build_index(records, meta, lexicon, protected)
    fixture = build_fixture(records, lexicon, protected)

    write_json(Path(args.out) / "search-index.json", index)
    write_json(Path(args.fixture), fixture)

    forms = sum(len(f) for entry in index["terms"] for f in entry["f"].values())
    print(
        f"✅ search index: {index['count']} terms, {len(index['roots'])} roots, "
        f"{forms} indexed forms, lexicon {len(lexicon)} words, "
        f"{len(protected)} protected headwords "
        f"({(Path(args.out) / 'search-index.json').stat().st_size // 1024} KiB)"
    )
    print(f"✅ parity fixture: {len(fixture['cases'])} cases → {args.fixture}")


if __name__ == "__main__":
    main()
