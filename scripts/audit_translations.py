#!/usr/bin/env python3
"""Translation smoke test for the sharded data files (data/terms/*.yaml).

This is a *smoke test*, not a proof of translation quality: it catches the
obvious machine-translation disasters (literal sentence fragments,
wrong-domain words, transliterations), it cannot judge whether a plausible
equivalent is the right specialist term.

Rules (per language):
  * ``term_en`` must never be empty; FR/DE/AR may be null — an unverified
    translation MUST stay null (see schemas/term-v1.schema.json).
  * a value may not exceed a per-language word budget (sentence-like values
    are machine-translation artifacts); pure punctuation tokens ("/", "-")
    do not count.
  * a value may not start with an article ("the vault", "le puits",
    "der Brunnen") — headwords are bare terms. Arabic keeps its definite
    article, which is standard for terminology.
  * a value may not contain personal pronouns or conjugated auxiliaries
    ("Contact him", "John is plastered", "Ne sois pas une brique").
  * a value may not contain a known forbidden word/phrase — the blacklist
    is seeded with the disasters found in the 2026-09 translation audit
    («Cornichon F», «Eau chinoise», «Pagode», «sont perdus», ...).
  * FR/DE/AR must not all be identical (copy-paste "translation"), and a
    Latin-script value must not sit in term_ar (or vice versa).

Results are written to ``translation_alerts.csv`` in the repository root.

Usage:
    python scripts/audit_translations.py            # report only (always exit 0)
    python scripts/audit_translations.py --strict   # exit 1 when any alert exists
"""

import argparse
import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"
OUTPUT_FILE = ROOT / "translation_alerts.csv"

CSV_FIELDS = ["term_fa", "language", "value", "domain", "slug", "source_file", "reasons"]

# language code -> (field, max words)
LANGS = {
    "en": ("term_en", 3),
    "fr": ("term_fr", 4),
    "de": ("term_de", 3),
    "ar": ("term_ar", 4),
}

MIN_EN_LENGTH = 3

LEADING_ARTICLE = {
    "en": re.compile(r"^(a|an|the)\b", re.I),
    "fr": re.compile(r"^(le|la|les|un|une|du|des|au|aux|l')\b", re.I),
    "de": re.compile(r"^(der|die|das|ein|eine|einen|einem|einer)\b", re.I),
}

PRONOUN_OR_AUXILIARY = {
    "en": re.compile(r"\b(him|her|you|your|he|she|they|them|is|are|am|was|were|be|not|no)\b", re.I),
    "fr": re.compile(r"\b(vous|votre|tu|ton|ta|il|elle|est|sont|êtes|sois|soit|ne|pas)\b", re.I),
    "de": re.compile(r"\b(sie|du|er|ist|sind|war|waren|sein|ihre|ihr|nicht|kein|keine)\b", re.I),
}

# Words/phrases observed in the machine-translation disasters of the old
# construction.yaml. Kept as a regression net: if they ever come back, the
# audit must scream. Matched case-insensitively on word boundaries.
FORBIDDEN = {
    "en": [
        "contact him", "john", "ginger", "sailor", "countries", "pickle",
        "chinese", "do not", "don't", "pagoda", "potter", "the vault",
        "shriveled", "overwhelmed", "reasoning", "clavicle", "cornichon",
        "töpfer", 
    ],
    "fr": [
        "ne pas", "ne sois", "cornichon", "pagode", "potier", "sont perdus",
        "eau chinoise", "contactez", "oreiller", "éperon", "clavicule",
        "toxique", "gingembre", "marin", "tremble", "embarquement", "mûr",
        "ambiance", "pays", "soins", "quatre heures",
    ],
    "de": [
        "sei kein", "nicht mauern", "pickle", "pagode", "töpfer",
        "sind verloren", "chinesisches wasser", "kissen", "sporn",
        "schlüsselbeinband", "giftig", "ingwer", "seemann", "länder",
        "espe", "steifer kopf", "überwältigt", "radkasten", "quartal",
        "pflege", "anhänger", "atmosphäre", "verdammt",
    ],
    "ar": [
        "لا لبنة", "لا تكن", "مخلل", "باغودا", "الخزاف", "ضائعة", "قلادة",
        "مغرفة", "سامة", "زنجبيل", "بحار", "بلدان", "الترقوة",
        "ذابل", "القبو", "أعمى جيدا", "عجلة جيدا", "دي جي", "أسبن",
        "تيزون", "أورليب", "جون", "اتصل به", "لتجول", "الصعود", "رعاية",
        "خلف الذراع", "حزام الترقوة", "يتوهم", "سهم الفهرس", "الخاص بك",
        "مجصص", "آرو", "مسلل",
    ],
}

ARABIC_RE = re.compile(r"[\u0600-\u06ff]")
LATIN_RE = re.compile(r"[A-Za-z]")


def _words(value: str):
    """Tokens that count towards the word budget (punctuation-only dropped)."""
    return [t for t in value.split() if any(c.isalnum() for c in t)]


def find_problems(lang: str, value):
    """Return the list of problems for one language value (empty = clean)."""
    if value is None:
        # null is the *correct* state for an unverified translation
        return [] if lang != "en" else ["empty term_en (required)"]

    text = str(value).strip()
    if not text:
        return ["empty term_en (required)"] if lang == "en" else []

    problems = []
    lowered = text.lower()

    if lang == "en" and len(text) < MIN_EN_LENGTH:
        problems.append(f"too short ({len(text)} < {MIN_EN_LENGTH} chars)")

    max_words = LANGS[lang][1]
    words = _words(text)
    if len(words) > max_words:
        problems.append(f"too long ({len(words)} > {max_words} words) — looks like a sentence")

    article = LEADING_ARTICLE.get(lang)
    if article and article.search(text):
        problems.append("starts with an article — headwords are bare terms")

    pronoun = PRONOUN_OR_AUXILIARY.get(lang)
    if pronoun and pronoun.search(text):
        problems.append("contains a pronoun/auxiliary — looks like a sentence, not a term")

    for phrase in FORBIDDEN.get(lang, []):
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", lowered):
            problems.append(f"forbidden machine-translation artifact: '{phrase}'")

    if lang == "ar" and LATIN_RE.search(text):
        problems.append("Latin characters in term_ar")
    if lang in ("en", "fr", "de") and ARABIC_RE.search(text):
        problems.append(f"Arabic characters in term_{lang}")

    return problems


def audit_records(terms):
    """Audit loaded term records; return the list of alert dicts."""
    alerts = []
    for index, term in enumerate(terms, start=1):
        term_fa = term.get("term_fa") or f"<entry #{index}>"
        base = {
            "term_fa": term_fa,
            "domain": ", ".join(term.get("domain") or []) if isinstance(term.get("domain"), list) else str(term.get("domain") or ""),
            "slug": term.get("slug", ""),
            "source_file": term.get("_source_file", ""),
        }

        values = {}
        for lang, (field, _) in LANGS.items():
            value = term.get(field)
            values[lang] = value
            for problem in find_problems(lang, value):
                alerts.append({**base, "language": lang, "value": "" if value is None else str(value), "reasons": problem})

        # copy-paste "translation": FR/DE/AR all identical
        triple = [str(values[l]).strip().casefold() for l in ("fr", "de", "ar") if values[l] not in (None, "")]
        if len(triple) == 3 and len(set(triple)) == 1:
            alerts.append({**base, "language": "fr+de+ar", "value": str(values["fr"]),
                           "reasons": "FR, DE and AR are all identical — copy-paste translation"})

    return alerts


def load_terms():
    if not DATA_DIR.exists():
        print(f"error: data directory not found: {DATA_DIR}", file=sys.stderr)
        sys.exit(2)
    terms = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for record in doc.get("terms") or []:
            record["_source_file"] = path.name
            terms.append(record)
    return terms


def write_csv(alerts, output_file=OUTPUT_FILE):
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(alerts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit with code 1 if any term is flagged")
    parser.add_argument("--out", default=str(OUTPUT_FILE), help="alert CSV output path")
    args = parser.parse_args()

    terms = load_terms()
    alerts = audit_records(terms)
    write_csv(alerts, Path(args.out))

    print(f"Audited {len(terms)} terms × {len(LANGS)} languages (translation smoke test)")
    print(f"{len(alerts)} alert(s) written to {args.out}")
    for row in alerts:
        print(f"  WARNING: {row['term_fa']} [{row['language']}] {row['value']!r} — {row['reasons']}")

    if alerts and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
