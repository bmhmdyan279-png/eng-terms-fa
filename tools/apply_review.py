#!/usr/bin/env python3
"""Apply the curated content review to data/terms/*.yaml.

Why a separate patch file instead of hand-editing YAML?
    * 132 records × ~10 fields cannot be edited by hand without drift.
    * The patch is reviewable as one document, and re-running it is a no-op.
    * The serializer is verified to be a **byte-exact round-trip**: applying an
      empty patch reproduces the committed files character for character, so a
      diff always shows content decisions and never formatting noise.

House style preserved:
    * the leading comment block of each shard,
    * `schema: term-v1` then `terms:`,
    * block sequences indented at the parent level,
    * `key:` (bare) for null instead of `key: null`,
    * a fixed, stable field order so diffs stay readable.

Usage:
    python tools/apply_review.py            # write changes
    python tools/apply_review.py --check    # exit 1 if files would change
    python tools/apply_review.py --dry-run  # print a summary, write nothing
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

DATA_DIR = ROOT / "data" / "terms"

from review_data import REVIEW  # noqa: E402

# Batch modules extend REVIEW in place; importing them is enough.
# Sorted so that batches are applied in a deterministic order.
_BATCH_DIR = Path(__file__).resolve().parent
for _batch in sorted(_BATCH_DIR.glob("review_batch*.py")):
    __import__(_batch.stem)

#: Field order of a serialized record. Unknown keys (if the schema ever grows
#: again) are appended in a stable sorted order at the end, never dropped.
FIELD_ORDER = (
    "id",
    "term_fa",
    "term_en",
    "term_fr",
    "term_de",
    "term_ar",
    "pos",
    "domain",
    "definition_fa",
    "synonyms",
    "antonyms",
    "search_aliases",
    "usage_examples",
    "root_fa",
    "root_ar",
    "etymology_fa",
    "origin_lang",
    "plural_fa",
    "abbrev_en",
    "references",
    "related_terms",
    "status",
    "review_level",
    "reviewed_by",
    "reviewed_at",
    "translation_notes",
    "slug",
)

#: Cap on related_terms in the *data*. Deliberately generous: the graph must be
#: complete and mutual, while how many chips a page shows is a presentation
#: decision taken in scripts/build_pages.py (MAX_RENDERED_RELATED).
MAX_RELATED_TERMS = 16


def symmetrize_related(terms: list[dict]) -> tuple[int, int]:
    """Make every related_terms link mutual (graph consistency pass).

    ``validate_content.py`` requires mutuality: a one-way link means either a
    missing relation or a wrong one. Author-specified links always win; the
    back-links that close the graph are appended in sorted order and the result
    is capped at MAX_RELATED_TERMS. The cap is verified never to bite — if it
    ever would, this function raises instead of silently breaking mutuality.
    """
    by_id = {record["id"]: record for record in terms}
    authored = {record["id"]: list(record.get("related_terms") or []) for record in terms}
    closed = {term_id: list(links) for term_id, links in authored.items()}
    added = 0

    for term_id, links in authored.items():
        for other in links:
            if other not in by_id or other == term_id or term_id in closed[other]:
                continue
            closed[other].append(term_id)
            added += 1

    max_degree = max((len(links) for links in closed.values()), default=0)
    if max_degree > MAX_RELATED_TERMS:
        raise SystemExit(
            f"symmetrize_related: degree {max_degree} exceeds MAX_RELATED_TERMS "
            f"({MAX_RELATED_TERMS}); raise the cap rather than break mutuality"
        )

    for term_id, links in closed.items():
        keep = list(dict.fromkeys(link for link in links if link in by_id and link != term_id))
        keep.sort(key=lambda item: (item not in authored[term_id], item))
        by_id[term_id]["related_terms"] = keep[:MAX_RELATED_TERMS]
    return added, max_degree


#: Keys whose value is dropped entirely when the patch sets them to None
#: (keeps the YAML free of `field: null` noise for optional fields).
DROPPABLE = {
    "term_fr", "term_de", "term_ar", "root_ar", "root_fa", "etymology_fa",
    "origin_lang", "plural_fa", "abbrev_en", "translation_notes",
    "review_level", "reviewed_by", "reviewed_at",
}

NULLABLE_KEEP = {"term_fr", "term_de", "term_ar"}


def header_of(text: str) -> str:
    """Leading comment/blank lines of a shard (everything before `schema:`)."""
    lines = []
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            lines.append(line)
        else:
            break
    return "\n".join(lines).rstrip("\n") + ("\n" if lines else "")


def order_record(record: dict) -> dict:
    ordered = {}
    for key in FIELD_ORDER:
        if key in record:
            ordered[key] = record[key]
    for key in sorted(k for k in record if k not in FIELD_ORDER):
        ordered[key] = record[key]
    return ordered


def dump_shard(header: str, doc: dict) -> str:
    """Serialize a shard in the project's house style."""
    body = yaml.dump(
        doc,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=10**6,
        indent=2,
    )
    # house style: a bare `key:` means null (never `key: null`)
    lines = []
    for line in body.splitlines():
        if line.endswith(": null"):
            line = line[: -len(" null")]
        lines.append(line)
    return header + "\n".join(lines) + "\n"


def merge(record: dict, patch: dict) -> dict:
    out = dict(record)
    for key, value in patch.items():
        if value is None and key in DROPPABLE and key not in NULLABLE_KEEP:
            out.pop(key, None)
            continue
        out[key] = value
    return out


def apply(check: bool = False, dry_run: bool = False) -> int:
    changed_files = 0
    patched_records = 0
    unknown_ids = set(REVIEW)

    shards: dict[str, dict] = {}
    for path in sorted(DATA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        original = path.read_text(encoding="utf-8")
        doc = yaml.safe_load(original)
        if not isinstance(doc, dict) or not isinstance(doc.get("terms"), list):
            print(f"ERROR: {path.name}: not a term shard", file=sys.stderr)
            return 2

        touched = False
        new_terms = []
        for record in doc["terms"]:
            patch = REVIEW.get(record.get("id"))
            if patch is None:
                new_terms.append(order_record(record))
                continue
            unknown_ids.discard(record.get("id"))
            merged = merge(record, patch)
            if merged != record:
                touched = True
                patched_records += 1
            new_terms.append(order_record(merged))

        # Graph consistency is a property of the whole shard *and* its
        # cross-shard links, so it is applied below across all shards.
        shards[path.name] = {"doc": doc, "header": header_of(original),
                             "original": original, "terms": new_terms}
    # --- graph consistency across every shard, then serialize ---------------
    all_terms = [record for shard in shards.values() for record in shard["terms"]]
    added_links, max_degree = symmetrize_related(all_terms)

    for name, shard in shards.items():
        path = DATA_DIR / name
        new_doc = {"schema": shard["doc"].get("schema", "term-v1"), "terms": shard["terms"]}
        rendered = dump_shard(shard["header"], new_doc)

        if rendered != shard["original"]:
            changed_files += 1
            if not check and not dry_run:
                path.write_text(rendered, encoding="utf-8")
            print(f"{'would rewrite' if dry_run or check else 'rewrote'} {name}")
    if added_links:
        print(f"{added_links} back-link(s) added; max related_terms degree {max_degree}")

    if unknown_ids:
        print(
            f"ERROR: review patch references unknown ids: {sorted(unknown_ids)}",
            file=sys.stderr,
        )
        return 2

    print(f"{patched_records} record(s) patched across {changed_files} file(s)")
    if check and changed_files:
        print("✗ data files are out of date — run: python tools/apply_review.py", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 when files would change")
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    args = parser.parse_args()
    sys.exit(apply(check=args.check, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
