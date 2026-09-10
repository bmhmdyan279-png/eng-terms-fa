#!/usr/bin/env python3
"""Scientific-content gate for the terminology data.

``validate_data.py`` proves the data is *well formed*. This script proves the
data is *defensible*: that citations resolve to real sources, that reviewed
entries really were reviewed by somebody named, that definitions are not
copy-paste, that Persian orthography is exemplary (a dictionary teaches
spelling), and that the term graph is consistent.

Checks
------
1.  Every ``references[].code`` exists in ``data/standards.yaml`` and carries a
    ``note`` explaining how it supports the entry. A citation without a
    verifiable source is a build blocker — this is the gate that makes
    fabricated references impossible.
2.  ``status != draft`` requires ``reviewed_by`` + ``reviewed_at`` +
    ``review_level``. ``published`` additionally requires an expert or
    committee review level (also enforced by the JSON Schema).
3.  Attribution honesty: ``reviewed_by`` may not claim to be a human when
    ``review_level`` is ``ai-assisted``.
4.  Definition quality: >= DEFINITION_REVIEWED_LENGTH characters once the entry
    leaves draft, not identical to another entry's definition, not a bare
    restatement of the headword.
5.  Persian orthography lint on every authored string (Arabic ی/ک، اعراب،
    «می» چسبیده، فاصلهٔ دوبل، ارقام عربی). Persian digits are house style and
    are allowed; Arabic-Indic digits are not.
6.  ``usage_examples`` must actually use the term (or one of its tokens or
    synonyms) — catches copy-pasted examples.
7.  Graph consistency: no self-references, and every link is mutual.
8.  Overlap discipline: a synonym that equals another entry's headword must be
    documented by a mutual ``related_terms`` link.
9.  ``term_en`` is a headword, not a title: lowercase unless it is an acronym.
10. ``translation_notes`` must only reference languages that have a value, and
    every descriptive translation must have one.

Outputs
-------
* console report with coverage statistics
* ``translation_gaps.csv`` — every missing or descriptive translation, with the
  reason, so a human FR/DE/AR maintainer has a work list

Exit codes: 0 = clean, 1 = at least one error.

Usage:
    python scripts/validate_content.py [--baseline REF] [--gaps-csv PATH]
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

from build_pages import ROOT, load_all_terms, load_meta
from persian_text import (
    ARABIC_DIGITS,
    ARABIC_KAF,
    ARABIC_YEH,
    HARAKAT,
    TEH_MARBUTA,
    ZWNJ,
    fold,
    orthography_warnings,
    tokenize,
)
from standards import load_registry

GAPS_CSV = ROOT / "translation_gaps.csv"
GAPS_FIELDS = ["slug", "term_fa", "language", "state", "value", "reason", "source_file"]

#: Definitions must clear a higher bar once an entry leaves draft.
DEFINITION_REVIEWED_LENGTH = 80

#: Persian-language fields that carry authored prose.
#: Fields where Arabic harakat are legitimate scholarship, not a typo.
DIACRITIC_OK_FIELDS = ("etymology_fa", "root_fa", "root_ar")
PROSE_FIELDS = ("term_fa", "definition_fa", "root_fa", "etymology_fa", "plural_fa")
LIST_PROSE_FIELDS = ("synonyms", "antonyms", "search_aliases", "usage_examples")

LANG_FIELDS = {"fr": "term_fr", "de": "term_de", "ar": "term_ar"}
LANG_FA = {"fr": "فرانسوی", "de": "آلمانی", "ar": "عربی"}

#: A note may also explain the English column, so `en` is a valid note key even
#: though it is not a translation gap (term_en is mandatory).
NOTE_LANGS = ("en", "fr", "de", "ar")

ACRONYM_RE = re.compile(r"^[A-Z0-9][A-Z0-9 .\-/]*$")


def label(source: str, record: dict) -> str:
    return f"{source}::{record.get('id') or record.get('term_fa') or '?'}"


# --------------------------------------------------------------------------- #
# 1. citations
# --------------------------------------------------------------------------- #

def check_references(records, registry):
    errors, warnings = [], []
    for source, record in records:
        lab = label(source, record)
        for index, ref in enumerate(record.get("references") or []):
            if not isinstance(ref, dict):
                errors.append(f"{lab}: references[{index}] is not a mapping")
                continue
            code = str(ref.get("code") or "").strip()
            if not code:
                errors.append(f"{lab}: references[{index}] has no code")
                continue
            if code not in registry:
                errors.append(
                    f"{lab}: reference '{code}' is not in data/standards.yaml — "
                    f"an unverifiable citation cannot ship"
                )
                continue
            entry = registry[code]
            if ref.get("type") and ref["type"] != entry.get("type"):
                errors.append(
                    f"{lab}: reference '{code}' is typed '{ref['type']}' here but "
                    f"'{entry.get('type')}' in the registry"
                )
            if not str(ref.get("note") or "").strip():
                errors.append(
                    f"{lab}: reference '{code}' has no 'note' — every citation must say "
                    f"how it supports the entry"
                )
            for key in ("org", "title", "url"):
                if ref.get(key) and entry.get(key) and ref[key] != entry[key]:
                    warnings.append(
                        f"{lab}: reference '{code}' overrides '{key}'; the registry is the source of truth"
                    )
    return errors, warnings


# --------------------------------------------------------------------------- #
# 2-3. review integrity & attribution honesty
# --------------------------------------------------------------------------- #

#: Words that would make an AI-assisted review look like a human sign-off.
HUMAN_CLAIM_RE = re.compile(
    r"\b(professor|dr\.?|engineer|مهندس|دکتر|استاد|کارشناس|متخصص)\b", re.IGNORECASE
)


def check_review(records, today=None):
    errors = []
    today = today or date.today()
    for source, record in records:
        lab = label(source, record)
        status = record.get("status", "draft")
        if status == "draft":
            continue
        reviewer = str(record.get("reviewed_by") or "").strip()
        reviewed_at = str(record.get("reviewed_at") or "").strip()
        level = record.get("review_level", "ai-assisted")

        if not reviewer:
            errors.append(f"{lab}: status '{status}' requires 'reviewed_by'")
        if not reviewed_at:
            errors.append(f"{lab}: status '{status}' requires 'reviewed_at'")
        else:
            try:
                parsed = date.fromisoformat(reviewed_at)
            except ValueError:
                errors.append(f"{lab}: reviewed_at '{reviewed_at}' is not a valid ISO date")
            else:
                if parsed > today:
                    errors.append(f"{lab}: reviewed_at '{reviewed_at}' is in the future")
        if level == "ai-assisted" and HUMAN_CLAIM_RE.search(reviewer):
            errors.append(
                f"{lab}: review_level is 'ai-assisted' but reviewed_by claims a human "
                f"credential ('{reviewer}') — attribution must stay honest"
            )
        if level not in ("expert", "committee") and status == "published":
            errors.append(f"{lab}: status 'published' requires review_level expert or committee")
        if level == "ai-assisted" and not re.search(r"ai|هوشمند|مدل|ربات", reviewer, re.IGNORECASE):
            errors.append(
                f"{lab}: review_level 'ai-assisted' requires reviewed_by to say so "
                f"(got '{reviewer}')"
            )
    return errors


# --------------------------------------------------------------------------- #
# 4. definition quality
# --------------------------------------------------------------------------- #

def check_definitions(records):
    errors, warnings = [], []
    seen: dict[str, str] = {}
    for source, record in records:
        lab = label(source, record)
        definition = unicodedata.normalize("NFKC", str(record.get("definition_fa") or "")).strip()
        status = record.get("status", "draft")
        required = DEFINITION_REVIEWED_LENGTH if status != "draft" else 50
        if len(definition) < required:
            message = f"{lab}: definition_fa has {len(definition)} chars (minimum {required} for '{status}')"
            (errors if status != "draft" else warnings).append(message)

        key = fold(re.sub(r"\s+", " ", definition))
        if key in seen:
            errors.append(f"{lab}: definition_fa is identical to {seen[key]} — copy-paste definition")
        else:
            seen[key] = lab

        headword = fold(record.get("term_fa") or "")
        if key and key.rstrip(".، ") == headword:
            errors.append(f"{lab}: definition_fa merely restates the headword")
    return errors, warnings


# --------------------------------------------------------------------------- #
# 5. Persian orthography
# --------------------------------------------------------------------------- #

def check_orthography(records):
    errors = []
    for source, record in records:
        lab = label(source, record)
        for field in PROSE_FIELDS:
            value = record.get(field)
            if isinstance(value, str):
                for problem in orthography_warnings(
                    value, allow_diacritics=field in DIACRITIC_OK_FIELDS
                ):
                    errors.append(f"{lab}: {field}: {problem}")
        for field in LIST_PROSE_FIELDS:
            for item in record.get(field) or []:
                if isinstance(item, str):
                    for problem in orthography_warnings(item):
                        errors.append(f"{lab}: {field}: '{item[:40]}': {problem}")
        for index, ref in enumerate(record.get("references") or []):
            note = ref.get("note") if isinstance(ref, dict) else None
            if isinstance(note, str):
                for problem in orthography_warnings(note):
                    errors.append(f"{lab}: references[{index}].note: {problem}")
    return errors


# --------------------------------------------------------------------------- #
# 6. usage examples must use the term
# --------------------------------------------------------------------------- #

def check_examples(records):
    errors = []
    for source, record in records:
        lab = label(source, record)
        allowed = {fold(record.get("term_fa") or "")}
        for field in ("synonyms", "search_aliases"):
            for item in record.get(field) or []:
                allowed.add(fold(str(item)))
        # every token of the headword counts: «آب‌بندی» appears as «آب‌بندی» or «بندکشی»
        for token in tokenize(record.get("term_fa") or ""):
            allowed.add(fold(token))
            allowed.add(fold(token.replace(ZWNJ, "")))
        allowed = {a for a in allowed if len(a) >= 2}

        for example in record.get("usage_examples") or []:
            folded = fold(str(example))
            if not any(word in folded for word in allowed):
                errors.append(
                    f"{lab}: usage_example does not contain the term or any of its "
                    f"synonyms: '{str(example)[:60]}…'"
                )
    return errors


# --------------------------------------------------------------------------- #
# 7-8. graph consistency & synonym overlap
# --------------------------------------------------------------------------- #

def check_graph(records):
    errors = []
    related = {record["id"]: set(record.get("related_terms") or []) for _, record in records}
    headwords = {fold(record.get("term_fa") or ""): record["id"] for _, record in records}

    for term_id, links in related.items():
        if term_id in links:
            errors.append(f"{term_id}: related_terms contains itself")
        for other in links:
            if other not in related:
                errors.append(f"{term_id}: related_terms references unknown id '{other}'")
                continue
            if term_id not in related[other]:
                errors.append(f"{term_id}: link to '{other}' is not mutual")

    for source, record in records:
        term_id = record["id"]
        for field in ("synonyms", "search_aliases"):
            for item in record.get(field) or []:
                owner = headwords.get(fold(str(item)))
                if not owner or owner == term_id:
                    continue
                if term_id in related.get(owner, set()) and owner in related.get(term_id, set()):
                    continue  # documented overlap: the two entries reference each other
                errors.append(
                    f"{term_id}: {field} '{item}' is the headword of '{owner}' but the two "
                    f"entries do not reference each other — undocumented duplicate"
                )
    return errors


# --------------------------------------------------------------------------- #
# 9. English headword style
# --------------------------------------------------------------------------- #

def check_english_style(records):
    warnings = []
    for source, record in records:
        term_en = str(record.get("term_en") or "").strip()
        if not term_en or ACRONYM_RE.match(term_en):
            continue
        first = term_en.split()[0]
        if re.match(r"^[A-Z](?:-[A-Za-z0-9]+)?$", first):
            continue  # letter designation: "F-bar bender", "T-section"
        if first[:1].isupper() and not first.isupper():
            warnings.append(
                f"{label(source, record)}: term_en '{term_en}' starts with a capital — "
                f"headwords are lowercase unless they are proper nouns or acronyms"
            )
    return warnings


# --------------------------------------------------------------------------- #
# 10. translations + gap report
# --------------------------------------------------------------------------- #

def check_translations(records):
    errors, warnings = [], []
    for source, record in records:
        lab = label(source, record)
        notes = record.get("translation_notes") or {}
        if not isinstance(notes, dict):
            errors.append(f"{lab}: translation_notes must be a mapping")
            notes = {}
        for lang, note_text in notes.items():
            if lang not in NOTE_LANGS:
                errors.append(f"{lab}: translation_notes has an unknown language '{lang}'")
                continue
            for problem in orthography_warnings(
                str(note_text), allow_diacritics=True, allow_foreign_script=True
            ):
                errors.append(f"{lab}: translation_notes.{lang}: {problem}")
            if lang == "en":
                continue
            if not str(record.get(LANG_FIELDS[lang]) or "").strip():
                errors.append(
                    f"{lab}: translation_notes.{lang} exists but term_{lang} is empty — "
                    f"an unverified translation must stay null *and* leave no note"
                )
        if str(record.get("root_ar") or "").strip() and record.get("origin_lang") not in ("ar", "fa"):
            warnings.append(
                f"{lab}: root_ar is set but origin_lang is '{record.get('origin_lang')}'"
            )
    return errors, warnings


def collect_translation_gaps(records):
    """Every missing or descriptive translation, with a reason."""
    rows = []
    for source, record in records:
        notes = record.get("translation_notes") or {}
        for lang, field in LANG_FIELDS.items():
            value = str(record.get(field) or "").strip()
            if not value:
                rows.append(
                    {
                        "slug": record.get("slug", ""),
                        "term_fa": record.get("term_fa", ""),
                        "language": lang,
                        "state": "missing",
                        "value": "",
                        "reason": (
                            "عمداً تهی: معادل راستی‌آزمایی‌شده‌ای در این زبان یافت نشد "
                            "(سیاست «نداریم بهتر از غلط است»)"
                        ),
                        "source_file": source,
                    }
                )
            elif notes.get(lang):
                rows.append(
                    {
                        "slug": record.get("slug", ""),
                        "term_fa": record.get("term_fa", ""),
                        "language": lang,
                        "state": "descriptive",
                        "value": value,
                        "reason": notes[lang],
                        "source_file": source,
                    }
                )
    return rows


def write_gaps_csv(rows, path=GAPS_CSV):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=GAPS_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #

def coverage_report(records):
    terms = [record for _, record in records]
    total = len(terms)
    lines = [f"validate_content: {total} records"]

    status = Counter(record.get("status", "draft") for record in terms)
    levels = Counter(record.get("review_level") for record in terms if record.get("status") != "draft")
    lines.append(f"  status        : {dict(status)}")
    if levels:
        lines.append(f"  review levels : {dict(levels)}")

    def coverage(field):
        count = sum(
            1 for record in terms
            if (record.get(field) or (None if not isinstance(record.get(field), list) else record.get(field)))
            and str(record.get(field)).strip() not in ("", "None", "[]")
        )
        return f"{count}/{total} ({100 * count // max(total, 1)}%)"

    for field in ("term_fr", "term_de", "term_ar", "synonyms", "usage_examples",
                  "references", "related_terms", "root_fa", "etymology_fa",
                  "origin_lang", "search_aliases", "plural_fa", "root_ar"):
        lines.append(f"  {field:<14}: {coverage(field)}")

    lengths = [len(str(record.get("definition_fa") or "")) for record in terms]
    if lengths:
        ordered = sorted(lengths)
        lines.append(
            f"  definition    : min {ordered[0]} / median {ordered[len(ordered) // 2]} / max {ordered[-1]} chars"
        )

    registry = load_registry()
    cited = {
        ref["code"]
        for record in terms
        for ref in (record.get("references") or [])
        if isinstance(ref, dict) and ref.get("code")
    }
    lines.append(f"  citations     : {len(cited)} distinct sources from a registry of {len(registry)}")
    unused = sorted(set(registry) - cited)
    if unused:
        lines.append(f"  uncited sources: {len(unused)} (registry entries no term points at)")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gaps-csv", default=str(GAPS_CSV))
    args = parser.parse_args()

    load_meta()
    records = load_all_terms()
    registry = load_registry()

    errors: list[str] = []
    warnings: list[str] = []

    for check_errors, check_warnings in (
        check_references(records, registry),
        check_definitions(records),
        check_translations(records),
    ):
        errors.extend(check_errors)
        warnings.extend(check_warnings)

    errors.extend(check_review(records))
    errors.extend(check_orthography(records))
    errors.extend(check_examples(records))
    errors.extend(check_graph(records))
    warnings.extend(check_english_style(records))

    gaps = collect_translation_gaps(records)
    write_gaps_csv(gaps, Path(args.gaps_csv))

    print(coverage_report(records))
    print(f"  translation report: {len(gaps)} row(s) → {args.gaps_csv}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(f"\n✗ content validation FAILED: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"\n✓ content validation passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
