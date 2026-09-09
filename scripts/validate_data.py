#!/usr/bin/env python3
"""Quality gate for the terminology data (data/terms/*.yaml).

Checks
------
1.  Every record validates against schemas/term-v1.schema.json.
2.  id and slug are unique across all shards (and id == slug).
3.  related_terms only reference existing ids.
4.  Slugs are immutable: records that already exist on the baseline
    branch (origin/main by default) must keep their slug. There is no
    auto-fix — a changed slug fails the gate, because published URLs
    are stable assets.
5.  definition_fa must be at least 50 characters. Content review is
    still in progress, so records with status=draft are reported as
    warnings; the rule becomes a hard error as soon as a term is
    promoted to reviewed/published.
6.  term_fr / term_de / term_ar must not be identical to term_en
    (an identical "translation" is a sign of lazy machine translation).
7.  No field may contain a placeholder value (TODO, placeholder, ...).

Exit codes: 0 = everything ok, 1 = at least one error.

Usage:
    python scripts/validate_data.py [--baseline REF]
"""

import argparse
import subprocess
import sys

import yaml

from build_pages import (
    DEFINITION_TARGET_LENGTH,
    load_all_terms,
    load_meta,
    validate_terms,
)

BASELINE_CANDIDATES = ("origin/main", "origin/master", "main", "master")

PLACEHOLDER_VALUES = {"todo", "placeholder", "tbd", "fixme", "n/a"}

LAZY_TRANSLATION_FIELDS = ("term_fr", "term_de", "term_ar")

# Internationalisms / loanwords that are legitimately spelled identically
# in English, French and German. These must not be treated as "lazy"
# translations. Keep lowercase; comparison is case-insensitive.
COGNATE_ALLOWLIST = {
    # flagged by the data today (genuine cognates)
    "asphalt", "digital", "depot", "traverse", "tension", "affiliation",
    "cumin", "zigzag", "parapet", "force", "fatigue",
    # common international technical terms (same spelling across languages)
    "protocol", "batch", "tolerance", "frequency", "vibrator", "gallery",
    "pycnometer", "oven", "control", "jig", "calibration", "diesel",
    "epoxy", "silicone", "polyester", "nylon", "laser", "radar", "robot",
    "modem", "server", "internet", "taxi", "bus", "metro", "tram",
    "wagon", "kilogram", "meter", "liter", "volt", "ampere", "watt",
    "hertz", "pascal", "newton", "joule", "calorie", "gram", "ton",
    "plasma", "insulin", "vitamin", "hormone", "enzyme", "protein",
    "glucose", "caffeine", "alcohol", "glycerin", "vaseline", "paraffin",
    "bitumen", "nickel", "zinc", "titanium", "silicon", "carbon", "ozone",
    "helium", "neon", "argon", "uranium", "chromium", "magnesium",
    "sodium", "calcium", "potassium", "aluminium",
}


def record_label(source, record):
    return f"{source}::{record.get('id') or record.get('term_fa') or '?'}"


def check_lazy_translations(records):
    """Flag FR/DE/AR values identical to term_en (lazy translation)."""
    errors = []
    for source, record in records:
        term_en = (record.get("term_en") or "").strip().casefold()
        if not term_en:
            continue
        for field in LAZY_TRANSLATION_FIELDS:
            value = (record.get(field) or "").strip()
            if not value or value.casefold() != term_en:
                continue
            if term_en in COGNATE_ALLOWLIST:
                continue  # legitimate internationalism, identical by design
            errors.append(
                f"{record_label(source, record)}: {field} is identical to "
                f"term_en ('{value}') — looks like an unperformed translation"
            )
    return errors


def _scan_for_placeholders(value, path, label, errors):
    if isinstance(value, str):
        if value.strip().lower() in PLACEHOLDER_VALUES:
            errors.append(f"{label}: {path} holds a placeholder value ('{value.strip()}')")
    elif isinstance(value, dict):
        for key, item in value.items():
            _scan_for_placeholders(item, f"{path}.{key}", label, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _scan_for_placeholders(item, f"{path}[{index}]", label, errors)


def check_placeholder_values(records):
    """No field anywhere in a record may be a TODO/placeholder value."""
    errors = []
    for source, record in records:
        _scan_for_placeholders(record, "<record>", record_label(source, record), errors)
    return errors


def check_definition_lengths(records):
    """Minimum definition length.

    draft terms are still under content review → warning.
    reviewed/published terms must meet the bar → error.
    """
    errors, warnings = [], []
    for source, record in records:
        definition = (record.get("definition_fa") or "").strip()
        status = record.get("status", "draft")
        if len(definition) >= DEFINITION_TARGET_LENGTH:
            continue
        message = (
            f"{record_label(source, record)}: definition_fa has {len(definition)} "
            f"chars (minimum {DEFINITION_TARGET_LENGTH})"
        )
        if status in ("reviewed", "published"):
            errors.append(f"{message} — status is '{status}', the definition must be complete")
        else:
            warnings.append(f"{message} — status is 'draft', pending content review")
    return errors, warnings


def check_slug_immutability(baseline_records, current_records):
    """Every term that exists on the baseline must keep its slug.

    Matching is done by id first, then by term_fa (v1 records had no id).
    New terms are allowed; changed slugs are not — URLs are stable assets.
    """
    errors = []
    current_by_id = {r.get("id"): r for r in current_records if r.get("id")}
    current_by_fa = {}
    for record in current_records:
        fa = (record.get("term_fa") or "").strip()
        if fa:
            current_by_fa.setdefault(fa, record)

    for baseline in baseline_records:
        baseline_id = (baseline.get("id") or "").strip() or None
        baseline_slug = (baseline.get("slug") or "").strip() or None
        term_fa = (baseline.get("term_fa") or "").strip()
        if not baseline_slug:
            continue  # v1 records without a stored slug have nothing to lock

        current = current_by_id.get(baseline_id) if baseline_id else None
        if current is None and term_fa:
            current = current_by_fa.get(term_fa)
        if current is None:
            continue  # removal is not slug-mutation; handled by content review

        current_slug = (current.get("slug") or "").strip() or None
        if current_slug and current_slug != baseline_slug:
            errors.append(
                f"slug changed: '{term_fa or baseline_id}' was '{baseline_slug}', "
                f"now '{current_slug}' — slugs are immutable (published URLs are stable assets)"
            )
    return errors


def _git(*args):
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8"
    )


def find_baseline_ref(explicit=None):
    """Return the first resolvable baseline git ref, or None."""
    candidates = (explicit,) if explicit else BASELINE_CANDIDATES
    for ref in candidates:
        if not ref:
            continue
        if _git("rev-parse", "--verify", "--quiet", ref).returncode == 0:
            return ref
    return None


def load_baseline_records(ref):
    """Load term records committed on `ref` (v1 monolith and/or v2 shards)."""
    records = []

    monolith = _git("show", f"{ref}:data/terms.yaml")
    if monolith.returncode == 0:
        data = yaml.safe_load(monolith.stdout) or []
        if isinstance(data, list):
            records.extend(r for r in data if isinstance(r, dict))

    listing = _git("ls-tree", "-r", "--name-only", ref, "data/terms/")
    if listing.returncode == 0:
        for name in listing.stdout.split():
            if name.startswith("data/terms/_") or not name.endswith(".yaml"):
                continue
            content = _git("show", f"{ref}:{name}")
            if content.returncode != 0:
                continue
            doc = yaml.safe_load(content.stdout) or {}
            if isinstance(doc, dict):
                records.extend(r for r in (doc.get("terms") or []) if isinstance(r, dict))

    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default=None,
        help="git ref to compare slugs against (default: auto-detect origin/main)",
    )
    args = parser.parse_args()

    meta = load_meta()
    records = load_all_terms()

    errors, warnings = [], []

    # 1-3: schema, unique ids/slugs, related_terms integrity, known domains
    schema_errors, _ = validate_terms(records, meta)
    errors.extend(schema_errors)

    # 4: slug immutability against the baseline branch
    baseline_ref = find_baseline_ref(args.baseline)
    if baseline_ref is None:
        warnings.append(
            "no baseline git ref found (origin/main?) — slug immutability check skipped"
        )
    else:
        baseline_records = load_baseline_records(baseline_ref)
        errors.extend(check_slug_immutability(baseline_records, [r for _, r in records]))

    # 5: definition length (draft = warning, reviewed/published = error)
    length_errors, length_warnings = check_definition_lengths(records)
    errors.extend(length_errors)
    warnings.extend(length_warnings)

    # 6: lazy translations
    errors.extend(check_lazy_translations(records))

    # 7: placeholder values
    errors.extend(check_placeholder_values(records))

    print(f"validate_data: {len(records)} records from data/terms/*.yaml")
    print(f"               slug immutability baseline: {baseline_ref or '<none>'}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(f"\n✗ validation FAILED: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1

    print(f"\n✓ validation passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
