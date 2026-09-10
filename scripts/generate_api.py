#!/usr/bin/env python3
"""Generate the static JSON API under docs/data/api/.

Files:
    data/api/terms.json           every term (public view)
    data/api/terms/{slug}.json    a single term
    data/api/categories.json      domains with per-domain counts
    data/api/stats.json           collection statistics

The output lives in docs/data/ (git-ignored) and is copied into the
deployed site by MkDocs, so the API is served from GitHub Pages at
<data/api/...> with zero server code.

Usage:
    python scripts/generate_api.py [--out DIR]
"""

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from build_pages import ROOT, SITE_URL, load_all_terms, load_meta
from standards import load_registry

DEFAULT_OUT = ROOT / "docs" / "data" / "api"

STATUS_PUBLIC = {"draft": "draft", "reviewed": "reviewed", "published": "published"}


def public_view(record, registry=None) -> dict:
    """The public shape of one term.

    References are enriched from data/standards.yaml so an API consumer never
    has to resolve a bare code by hand — the registry stays the single source
    of truth for issuing body, title and URL.
    """
    registry = registry if registry is not None else load_registry()
    references = []
    for ref in record.get("references") or []:
        if not isinstance(ref, dict):
            continue
        entry = registry.get(str(ref.get("code") or "").strip()) or {}
        item = {
            "type": ref.get("type") or entry.get("type"),
            "code": ref.get("code"),
            "title": entry.get("title"),
            "org": ref.get("org") or entry.get("org"),
            "edition": ref.get("edition") or entry.get("edition"),
            "url": ref.get("url") or entry.get("url"),
            "section": ref.get("section"),
            "note": ref.get("note"),
        }
        references.append({k: v for k, v in item.items() if v})

    return {
        "id": record["id"],
        "term_fa": record["term_fa"],
        "term_en": record.get("term_en") or "",
        "term_fr": record.get("term_fr"),
        "term_de": record.get("term_de"),
        "term_ar": record.get("term_ar"),
        "pos": record.get("pos"),
        "domain": record.get("domain") or [],
        "definition_fa": record.get("definition_fa") or "",
        "synonyms": record.get("synonyms") or [],
        "antonyms": record.get("antonyms") or [],
        "search_aliases": record.get("search_aliases") or [],
        "usage_examples": record.get("usage_examples") or [],
        "root_fa": record.get("root_fa"),
        "root_ar": record.get("root_ar"),
        "etymology_fa": record.get("etymology_fa"),
        "origin_lang": record.get("origin_lang"),
        "plural_fa": record.get("plural_fa"),
        "abbrev_en": record.get("abbrev_en"),
        "translation_notes": record.get("translation_notes") or {},
        "status": STATUS_PUBLIC.get(record.get("status", "draft"), "draft"),
        "review_level": record.get("review_level"),
        "reviewed_by": record.get("reviewed_by"),
        "reviewed_at": record.get("reviewed_at"),
        "references": references,
        "related_terms": record.get("related_terms") or [],
        "slug": record["slug"],
        "url": f"{SITE_URL}terms/{record['slug']}/",
    }


def build_stats(terms, meta) -> dict:
    reviewed = sum(1 for t in terms if t.get("status") in ("reviewed", "published"))
    per_domain = {}
    for term in terms:
        for domain in term.get("domain") or []:
            per_domain[domain] = per_domain.get(domain, 0) + 1
    complete = sum(
        1 for t in terms
        if all(str(t.get(f) or "").strip() for f in ("term_fr", "term_de", "term_ar"))
    )
    reviewed_by_level = {}
    for term in terms:
        if term.get("status") in ("reviewed", "published"):
            key = term.get("review_level") or "unspecified"
            reviewed_by_level[key] = reviewed_by_level.get(key, 0) + 1
    return {
        "project": "فرهنگ واژگان تخصصی مهندسی",
        "version": "v0.2",
        "review_levels": reviewed_by_level,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_terms": len(terms),
        "languages": ["fa", "en", "fr", "de", "ar"],
        "reviewed_terms": reviewed,
        "draft_terms": len(terms) - reviewed,
        "fully_translated_terms": complete,
        "domains": per_domain,
        "site_url": SITE_URL,
        "license_content": "CC BY-SA 4.0",
        "license_code": "MIT",
        "open_data": f"{SITE_URL}data/open/",
        "honesty_note": (
            "reviewed entries are ai-assisted unless review_level says otherwise; "
            "unverified translations stay null"
        ),
    }


def build_categories(terms, meta) -> list:
    counts = {}
    for term in terms:
        for domain in term.get("domain") or []:
            counts[domain] = counts.get(domain, 0) + 1
    categories = []
    for domain in meta.get("domains", []):
        categories.append(
            {
                "id": domain["id"],
                "title_fa": domain.get("title_fa", domain["id"]),
                "count": counts.get(domain["id"], 0),
            }
        )
    return categories


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def generate_api(out_dir: Path = DEFAULT_OUT) -> dict:
    records = load_all_terms()
    meta = load_meta()
    terms = [public_view(record) for _, record in records]

    # Remove only what this script owns. The directory is shared with
    # build_search_index.py (search-index.json), and rmtree'ing it made the
    # build order load-bearing: whichever script ran last silently deleted the
    # other's output.
    if out_dir.exists():
        for stale in ("terms.json", "categories.json", "stats.json"):
            (out_dir / stale).unlink(missing_ok=True)
        single = out_dir / "terms"
        if single.exists():
            shutil.rmtree(single)

    write_json(out_dir / "terms.json", {"terms": terms, "count": len(terms)})

    single_dir = out_dir / "terms"
    for term in terms:
        write_json(single_dir / f"{term['slug']}.json", term)

    write_json(out_dir / "categories.json", {"categories": build_categories([r for _, r in records], meta)})
    write_json(out_dir / "stats.json", build_stats([r for _, r in records], meta))

    return {"terms": len(terms), "files": 3 + len(terms)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="output directory")
    args = parser.parse_args()
    result = generate_api(Path(args.out))
    print(f"✅ API generated: {result['terms']} terms, {result['files']} JSON files")


if __name__ == "__main__":
    main()
