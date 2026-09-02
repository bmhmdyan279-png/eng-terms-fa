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

DEFAULT_OUT = ROOT / "docs" / "data" / "api"

STATUS_PUBLIC = {"draft": "draft", "reviewed": "reviewed", "published": "published"}


def public_view(record) -> dict:
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
        "status": STATUS_PUBLIC.get(record.get("status", "draft"), "draft"),
        "references": record.get("references") or [],
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
    return {
        "project": "فرهنگ واژگان تخصصی مهندسی",
        "version": "v0.1",
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

    if out_dir.exists():
        shutil.rmtree(out_dir)

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
