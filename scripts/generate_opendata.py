#!/usr/bin/env python3
"""Generate the Open Data bundle under docs/data/open/.

The project licenses its content CC BY-SA 4.0, which makes it *legally* open.
This script makes it open in the sense that actually matters for reuse: the
whole dictionary is published in interoperable, machine-actionable formats that
a third party can load without scraping HTML.

Outputs
-------
``terms.ndjson``
    One JSON object per line — streamable, diff-friendly, ideal for pipelines.
``terms.jsonld``
    schema.org ``Dataset`` + ``DefinedTermSet`` + one ``DefinedTerm`` per entry,
    with ``distribution`` pointing at every other file in the bundle. This is
    the same payload embedded in the home page for crawler discovery.
``terms.ttl``
    SKOS/RDF (Turtle): a ``skos:ConceptScheme`` with one ``skos:Concept`` per
    term, multilingual ``skos:prefLabel``/``skos:altLabel`` with language tags,
    ``skos:definition``, ``skos:historyNote`` (etymology), ``skos:related``,
    ``dct:subject`` (domains) and ``dct:bibliographicCitation`` (sources).
``datapackage.json``
    Frictionless Data descriptor for ``terms.csv`` — typed schema, licenses,
    sources, contributors.
``README.md``
    A human-readable manifest of the bundle, written next to the data so that
    whoever downloads the folder knows what they hold and how to cite it.

Everything is derived from data/terms/*.yaml — the single source of truth — and
from data/standards.yaml for citation metadata.

Usage:
    python scripts/generate_opendata.py [--out DIR]
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime, timezone
from pathlib import Path

from build_pages import ROOT, SITE_URL, load_all_terms, load_meta
from standards import load_registry

DEFAULT_OUT = ROOT / "docs" / "data" / "open"

DATA_VERSION = "0.2"
SOFTWARE_VERSION = "1.1.0"
LICENSE_CONTENT = "https://creativecommons.org/licenses/by-sa/4.0/"
LICENSE_CODE = "https://opensource.org/licenses/MIT"
REPO_URL = "https://github.com/bmhmdyan279-png/eng-terms-fa"
PUBLISHER = "eng-terms-fa Project"
MAINTAINER = "bmhmdyan279-png"

SCHEME_IRI = f"{SITE_URL}#termset"
DOMAIN_SCHEME_IRI = f"{SITE_URL}#domains"
DATASET_IRI = f"{SITE_URL}#dataset"

#: SKOS language tags per column.
LANGUAGE_OF = {"fa": "term_fa", "en": "term_en", "fr": "term_fr", "de": "term_de", "ar": "term_ar"}

ORIGIN_FA = {
    "fa": "فارسی", "ar": "عربی", "tr": "ترکی", "fr": "فرانسوی", "en": "انگلیسی",
    "de": "آلمانی", "la": "لاتین", "el": "یونانی", "ru": "روسی", "es": "اسپانیایی",
    "it": "ایتالیایی", "hy": "ارمنی", "mn": "مغولی", "other": "سایر",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return date.today().isoformat()


def concept_iri(slug: str) -> str:
    return f"{SITE_URL}terms/{slug}/#concept"


def domain_iri(domain: str) -> str:
    return f"{SITE_URL}#domain-{domain}"


# --------------------------------------------------------------------------- #
# public record
# --------------------------------------------------------------------------- #

def open_record(record: dict, registry: dict) -> dict:
    """The full public view of one term, including every reviewed field."""
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

    out = {
        "id": record["id"],
        "slug": record["slug"],
        "url": f"{SITE_URL}terms/{record['slug']}/",
        "term_fa": record.get("term_fa"),
        "term_en": record.get("term_en"),
        "term_fr": record.get("term_fr"),
        "term_de": record.get("term_de"),
        "term_ar": record.get("term_ar"),
        "pos": record.get("pos"),
        "domain": record.get("domain") or [],
        "definition_fa": record.get("definition_fa"),
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
        "references": references,
        "related_terms": record.get("related_terms") or [],
        "status": record.get("status", "draft"),
        "review_level": record.get("review_level"),
        "reviewed_by": record.get("reviewed_by"),
        "reviewed_at": record.get("reviewed_at"),
    }
    return {k: v for k, v in out.items() if v not in (None, "", [], {})}


# --------------------------------------------------------------------------- #
# NDJSON
# --------------------------------------------------------------------------- #

def write_ndjson(records: list[dict], out_dir: Path) -> Path:
    path = out_dir / "terms.ndjson"
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False) + "\n")
    return path


# --------------------------------------------------------------------------- #
# JSON-LD (schema.org)
# --------------------------------------------------------------------------- #

def defined_term_jsonld(record: dict) -> dict:
    alternate = [record["term_en"]] if record.get("term_en") else []
    alternate += [r["term"] for r in _alternate_names(record)]
    payload = {
        "@type": "DefinedTerm",
        "@id": concept_iri(record["slug"]),
        "name": record.get("term_fa"),
        "alternateName": alternate,
        "termCode": record["slug"],
        "url": record["url"],
        "description": record.get("definition_fa"),
        "inLanguage": "fa",
        "about": [domain_iri(d) for d in record.get("domain") or []],
    }
    if record.get("etymology_fa"):
        payload["citation"] = record["etymology_fa"]
    if record.get("usage_examples"):
        payload["exampleOfWork"] = record["usage_examples"]
    if record.get("status"):
        payload["creativeWorkStatus"] = record["status"]
    return {k: v for k, v in payload.items() if v}


def _alternate_names(record: dict) -> list[dict]:
    """Extra labels as {term, language} pairs (kept out of schema.org output)."""
    out = []
    for lang, field in (("fr", "term_fr"), ("de", "term_de"), ("ar", "term_ar")):
        if record.get(field):
            out.append({"term": record[field], "language": lang})
    for synonym in record.get("synonyms") or []:
        out.append({"term": synonym, "language": "fa"})
    for alias in record.get("search_aliases") or []:
        out.append({"term": alias, "language": "fa"})
    return out


def dataset_jsonld(records: list[dict], meta: dict) -> dict:
    generated = now_iso()
    distributions = [
        {
            "@type": "DataDownload",
            "encodingFormat": fmt,
            "contentUrl": f"{SITE_URL}data/open/{name}",
            "name": name,
        }
        for fmt, name in (
            ("application/x-ndjson", "terms.ndjson"),
            ("application/ld+json", "terms.jsonld"),
            ("text/turtle", "terms.ttl"),
            ("application/json", "datapackage.json"),
            ("text/csv", "terms.csv"),
        )
    ]
    return {
        "@context": {
            "@vocab": "https://schema.org/",
            "schema": "https://schema.org/",
            "dct": "http://purl.org/dc/terms/",
        },
        "@graph": [
            {
                "@type": "schema:Dataset",
                "@id": DATASET_IRI,
                "schema:name": "فرهنگ واژگان تخصصی مهندسی",
                "schema:alternateName": "Persian Engineering Terminology Dictionary",
                "schema:description": (
                    "A Persian-first multilingual (FA/EN/FR/DE/AR) terminology dataset for "
                    "civil engineering, concrete technology, building construction and mechanics, "
                    "with etymology, roots, definitions, usage examples and verified citations."
                ),
                "schema:url": SITE_URL,
                "schema:version": DATA_VERSION,
                "schema:dateModified": generated,
                "schema:datePublished": "2026-09-03",
                "schema:inLanguage": ["fa", "en", "fr", "de", "ar"],
                "schema:license": LICENSE_CONTENT,
                "schema:isAccessibleForFree": True,
                "schema:keywords": [
                    "terminology", "civil engineering", "concrete", "construction",
                    "Persian", "واژه‌شناسی", "مهندسی عمران", "بتن",
                ],
                "schema:creator": {
                    "@type": "schema:Organization",
                    "schema:name": PUBLISHER,
                    "schema:url": REPO_URL,
                },
                "schema:maintainer": {
                    "@type": "schema:Person",
                    "schema:name": MAINTAINER,
                    "schema:url": REPO_URL,
                },
                "schema:distribution": distributions,
                "schema:variableMeasured": [
                    "term_fa", "term_en", "term_fr", "term_de", "term_ar",
                    "definition_fa", "etymology_fa", "root_fa", "references",
                ],
                "schema:measurementTechnique": "SKOS / schema.org DefinedTerm",
            },
            {
                "@type": "schema:DefinedTermSet",
                "@id": SCHEME_IRI,
                "schema:name": meta.get("project", "فرهنگ واژگان تخصصی مهندسی"),
                "schema:url": SITE_URL,
                "schema:version": DATA_VERSION,
                "schema:inLanguage": ["fa", "en", "fr", "de", "ar"],
                "schema:license": LICENSE_CONTENT,
                "schema:hasDefinedTerm": [defined_term_jsonld(r) for r in records],
            },
        ],
    }


def write_jsonld(payload: dict, out_dir: Path) -> Path:
    path = out_dir / "terms.jsonld"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# SKOS / Turtle
# --------------------------------------------------------------------------- #

def ttl_iri(iri: str) -> str:
    return f"<{iri}>"


def ttl_literal(text: str, lang: str | None = None) -> str:
    """A Turtle literal with the escapes the grammar requires."""
    body = str(text)
    body = body.replace("\\", "\\\\").replace('"', '\\"')
    body = body.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    body = "".join(c for c in body if ord(c) >= 0x20 or c in "\t")
    return f'"""{body}"""@{lang}' if lang else f'"""{body}"""'


PREFIXES = """@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix cc:    <http://creativecommons.org/ns#> .
@prefix vann:  <http://purl.org/vocab/vann/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix schema: <https://schema.org/> .
@prefix terms: <{site}terms/> .
@prefix root:  <{site}> .
"""


def write_turtle(records: list[dict], meta: dict, out_dir: Path) -> Path:
    registry = load_registry()
    lines = [
        PREFIXES.format(site=SITE_URL),
        f"# فرهنگ واژگان تخصصی مهندسی — SKOS/RDF",
        f"# generated {now_iso()} from data/terms/*.yaml (single source of truth)",
        f"# license: CC BY-SA 4.0 <{LICENSE_CONTENT}>",
        "",
        f"{ttl_iri(SCHEME_IRI)} a skos:ConceptScheme ;",
        f"    dct:title {ttl_literal('فرهنگ واژگان تخصصی مهندسی', 'fa')} ;",
        f"    dct:alternative {ttl_literal('Persian Engineering Terminology Dictionary', 'en')} ;",
        f"    dct:publisher {ttl_literal(PUBLISHER)} ;",
        f"    dct:license {ttl_iri(LICENSE_CONTENT)} ;",
        f"    dct:modified {ttl_literal(today())}^^xsd:date ;",
        f"    owl:versionInfo {ttl_literal(DATA_VERSION)} ;",
        f"    vann:changes {ttl_iri(REPO_URL + '/blob/main/CHANGELOG.md')} ;",
        f"    skos:hasTopConcept ",
    ]

    top = [r for r in records if r.get("domain")]
    lines[-1] += ", ".join(ttl_iri(concept_iri(r["slug"])) for r in top[:5]) + " ."
    lines.append("")

    # domain concepts
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in meta.get("domains", [])}
    lines += [
        f"{ttl_iri(DOMAIN_SCHEME_IRI)} a skos:ConceptScheme ;",
        f"    dct:title {ttl_literal('حوزه‌های مهندسی این فرهنگ', 'fa')} ;",
        f"    dct:description {ttl_literal('Engineering domains used to classify the terms', 'en')} ;",
        f"    dct:license {ttl_iri(LICENSE_CONTENT)} .",
        "",
    ]
    for domain_id, title in domain_titles.items():
        count = sum(1 for r in records if domain_id in (r.get("domain") or []))
        lines += [
            f"{ttl_iri(domain_iri(domain_id))} a skos:Concept ;",
            f"    skos:inScheme {ttl_iri(DOMAIN_SCHEME_IRI)} ;",
            f"    skos:prefLabel {ttl_literal(title, 'fa')} ;",
            f"    skos:notation {ttl_literal(domain_id)} ;",
            f"    rdfs:comment {ttl_literal(f'{count} term(s) in this domain', 'en')} .",
            "",
        ]

    for record in records:
        iri = concept_iri(record["slug"])
        block = [f"{ttl_iri(iri)} a skos:Concept ;",
                 f"    skos:inScheme {ttl_iri(SCHEME_IRI)} ;",
                 f"    skos:topConceptOf {ttl_iri(SCHEME_IRI)} ;",
                 f"    skos:prefLabel {ttl_literal(record.get('term_fa'), 'fa')} ;"]

        alt_labels = []
        for lang, field in LANGUAGE_OF.items():
            value = record.get(field)
            if lang == "fa" or not value:
                continue
            alt_labels.append(ttl_literal(value, lang))
        for synonym in (record.get("synonyms") or []) + (record.get("search_aliases") or []):
            alt_labels.append(ttl_literal(synonym, "fa"))
        if alt_labels:
            block.append("    skos:altLabel " + ", ".join(alt_labels) + " ;")

        if record.get("definition_fa"):
            block.append(f"    skos:definition {ttl_literal(record['definition_fa'], 'fa')} ;")
        for antonym in record.get("antonyms") or []:
            block.append(f"    skos:scopeNote {ttl_literal('متضاد: ' + antonym, 'fa')} ;")
        if record.get("etymology_fa"):
            block.append(f"    skos:historyNote {ttl_literal(record['etymology_fa'], 'fa')} ;")
        if record.get("root_fa"):
            note = "ریشهٔ فارسی: " + str(record["root_fa"])
            if record.get("root_ar"):
                note += " • ریشهٔ عربی: " + str(record["root_ar"])
            if record.get("origin_lang"):
                note += " • زبان مبدأ: " + ORIGIN_FA.get(record["origin_lang"], record["origin_lang"])
            block.append(f"    skos:note {ttl_literal(note, 'fa')} ;")
        if record.get("plural_fa"):
            block.append(f"    skos:note {ttl_literal('جمع: ' + record['plural_fa'], 'fa')} ;")
        if record.get("abbrev_en"):
            block.append(f"    skos:note {ttl_literal('abbreviation: ' + record['abbrev_en'], 'en')} ;")
        for example in record.get("usage_examples") or []:
            block.append(f"    skos:example {ttl_literal(example, 'fa')} ;")
        for lang, note in (record.get("translation_notes") or {}).items():
            block.append(f"    skos:editorialNote {ttl_literal(f'[{lang}] {note}', 'fa')} ;")

        related = [r for r in record.get("related_terms") or [] if r != record["slug"]]
        if related:
            by_slug = {r["slug"]: r for r in records}
            iris = [ttl_iri(concept_iri(x)) for x in related if x in by_slug]
            if iris:
                block.append("    skos:related " + ", ".join(iris) + " ;")

        for domain in record.get("domain") or []:
            block.append(f"    dct:subject {ttl_iri(domain_iri(domain))} ;")

        for ref in record.get("references") or []:
            entry = registry.get(str(ref.get("code") or "").strip()) or {}
            citation = str(ref.get("code") or "")
            if entry.get("title") and entry["title"] != citation:
                citation += f" — {entry['title']}"
            if entry.get("org"):
                citation += f" ({entry['org']})"
            block.append(f"    dct:bibliographicCitation {ttl_literal(citation)} ;")
            if entry.get("url"):
                block.append(f"    rdfs:seeAlso {ttl_iri(entry['url'])} ;")

        block.append(f"    skos:notation {ttl_literal(record['slug'])} ;")
        block.append(f"    dct:identifier {ttl_literal(record['id'])} ;")
        block.append(f"    schema:creativeWorkStatus {ttl_literal(record.get('status', 'draft'))} ;")
        if record.get("reviewed_at"):
            block.append(f"    dct:date {ttl_literal(record['reviewed_at'])}^^xsd:date ;")
        if record.get("reviewed_by"):
            block.append(
                f"    dct:contributor {ttl_literal(record['reviewed_by'])} ;"
            )
        block[-1] = block[-1][:-1].rstrip() + " ."
        lines += block + [""]

    path = out_dir / "terms.ttl"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# CSV (open-data flavour: every field, one row per term)
# --------------------------------------------------------------------------- #

CSV_FIELDS = [
    "id", "slug", "term_fa", "term_en", "term_fr", "term_de", "term_ar", "pos",
    "domain", "status", "review_level", "reviewed_by", "reviewed_at",
    "definition_fa", "synonyms", "antonyms", "search_aliases", "usage_examples",
    "root_fa", "root_ar", "etymology_fa", "origin_lang", "plural_fa", "abbrev_en",
    "references", "related_terms", "url",
]


def write_csv(records: list[dict], out_dir: Path) -> Path:
    path = out_dir / "terms.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for record in records:
            row = dict(record)
            row["domain"] = "|".join(record.get("domain") or [])
            for field in ("synonyms", "antonyms", "search_aliases", "usage_examples", "related_terms"):
                row[field] = "|".join(str(v) for v in record.get(field) or [])
            row["references"] = "|".join(
                str(ref.get("code")) for ref in record.get("references") or []
            )
            writer.writerow(row)
    return path


# --------------------------------------------------------------------------- #
# Frictionless Data descriptor
# --------------------------------------------------------------------------- #

def datapackage(records: list[dict]) -> dict:
    fields = [
        {"name": "id", "type": "string", "constraints": {"required": True, "unique": True}},
        {"name": "slug", "type": "string", "constraints": {"required": True, "unique": True}},
        {"name": "term_fa", "type": "string", "constraints": {"required": True}},
        {"name": "term_en", "type": "string", "constraints": {"required": True}},
        {"name": "term_fr", "type": "string"},
        {"name": "term_de", "type": "string"},
        {"name": "term_ar", "type": "string"},
        {"name": "pos", "type": "string", "constraints": {"enum": ["noun", "verb", "adjective", "phrase"]}},
        {"name": "domain", "type": "string", "description": "pipe-separated domain ids"},
        {"name": "status", "type": "string", "constraints": {"enum": ["draft", "reviewed", "published"]}},
        {"name": "review_level", "type": "string",
         "constraints": {"enum": ["ai-assisted", "expert", "committee"]}},
        {"name": "reviewed_by", "type": "string"},
        {"name": "reviewed_at", "type": "date"},
        {"name": "definition_fa", "type": "string"},
        {"name": "synonyms", "type": "string"},
        {"name": "antonyms", "type": "string"},
        {"name": "search_aliases", "type": "string"},
        {"name": "usage_examples", "type": "string"},
        {"name": "root_fa", "type": "string"},
        {"name": "root_ar", "type": "string"},
        {"name": "etymology_fa", "type": "string"},
        {"name": "origin_lang", "type": "string"},
        {"name": "plural_fa", "type": "string"},
        {"name": "abbrev_en", "type": "string"},
        {"name": "references", "type": "string", "description": "pipe-separated registry codes"},
        {"name": "related_terms", "type": "string"},
        {"name": "url", "type": "string", "format": "uri"},
    ]
    return {
        "name": "persian-engineering-terminology",
        "title": "فرهنگ واژگان تخصصی مهندسی",
        "description": (
            "Persian-first multilingual engineering terminology (FA/EN/FR/DE/AR) for civil "
            "engineering, concrete technology, building construction and mechanics."
        ),
        "homepage": SITE_URL,
        "version": DATA_VERSION,
        "created": "2026-09-03",
        "modified": today(),
        "licenses": [
            {"name": "CC-BY-SA-4.0", "path": LICENSE_CONTENT, "title": "Creative Commons Attribution-ShareAlike 4.0"},
        ],
        "sources": [
            {"title": "Repository", "path": REPO_URL},
            {"title": "Source registry", "path": f"{REPO_URL}/blob/main/data/standards.yaml"},
        ],
        "contributors": [
            {"title": MAINTAINER, "role": "maintainer"},
            {"title": "Qwen (AI-assisted review)", "role": "contributor",
             "comment": "model-assisted content review; no human specialist sign-off yet"},
        ],
        "keywords": ["terminology", "persian", "civil-engineering", "concrete", "construction", "skos"],
        "image": f"{SITE_URL}assets/icons/icon-512.png",
        "resources": [
            {
                "name": "terms",
                "path": "terms.csv",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8-sig",
                "dialect": {"delimiter": ",", "lineTerminator": "\n", "header": True},
                "schema": {"fields": fields, "primaryKey": "id"},
            },
            {
                "name": "terms-ndjson",
                "path": "terms.ndjson",
                "format": "ndjson",
                "mediatype": "application/x-ndjson",
                "encoding": "utf-8",
                "schema": {"fields": fields, "primaryKey": "id"},
            },
            {
                "name": "terms-skos",
                "path": "terms.ttl",
                "format": "turtle",
                "mediatype": "text/turtle",
                "encoding": "utf-8",
            },
            {
                "name": "terms-jsonld",
                "path": "terms.jsonld",
                "format": "jsonld",
                "mediatype": "application/ld+json",
                "encoding": "utf-8",
            },
        ],
        "stats": {
            "term_count": len(records),
            "languages": ["fa", "en", "fr", "de", "ar"],
            "reviewed": sum(1 for r in records if r.get("status") in ("reviewed", "published")),
            "generated_at": now_iso(),
        },
    }


def write_readme(records: list[dict], out_dir: Path) -> Path:
    registry = load_registry()
    cited = sorted({
        str(ref.get("code")) for r in records for ref in (r.get("references") or [])
        if isinstance(ref, dict) and ref.get("code")
    })
    reviewed = sum(1 for r in records if r.get("status") in ("reviewed", "published"))
    lines = [
        "# بستهٔ دادهٔ باز — فرهنگ واژگان تخصصی مهندسی",
        "",
        f"- **نسخهٔ داده:** {DATA_VERSION}  •  **تولید:** {now_iso()}",
        f"- **مدخل‌ها:** {len(records)}  •  **بازبینی‌شده:** {reviewed}  •  **پیش‌نویس:** {len(records) - reviewed}",
        f"- **زبان‌ها:** fa (اصلی)، en (الزامی)، fr، de، ar",
        f"- **مجوز محتوا:** [CC BY-SA 4.0]({LICENSE_CONTENT})  •  **مجوز کد:** [MIT]({LICENSE_CODE})",
        "",
        "## فایل‌ها",
        "",
        "| فایل | قالب | کاربرد |",
        "|---|---|---|",
        "| `terms.ndjson` | NDJSON | بارگذاری خط‌به‌خط در پایپ‌لاین داده |",
        "| `terms.jsonld` | JSON-LD | schema.org Dataset + DefinedTermSet |",
        "| `terms.ttl` | Turtle (SKOS) | گراف دانش، قابل بارگذاری در هر triple store |",
        "| `terms.csv` | CSV (UTF-8 BOM) | اکسل/پانداس؛ فهرست جداکنندهٔ چندمقداری `|` است |",
        "| `datapackage.json` | Frictionless Data | توصیف‌کنندهٔ نوع‌دار مجموعه داده |",
        "",
        "## صداقت دربارهٔ وضعیت بازبینی",
        "",
        "همهٔ مدخل‌ها `status: reviewed` و `review_level: ai-assisted` هستند، یعنی بازبینی",
        "داده‌محور با دروازه‌های خودکار انجام شده ولی **تأیید متخصص انسانی را ندارند**.",
        "اسکیمای داده اجازه نمی‌دهد `status: published` بدون `review_level: expert` ثبت شود.",
        "ترجمه‌های FR/DE/AR که راستی‌آزمایی نشده‌اند `null` مانده‌اند؛ فهرست آن‌ها در",
        "`translation_gaps.csv` ریشهٔ مخزن است.",
        "",
        "## منابع مورد استناد در داده‌ها",
        "",
        f"{len(cited)} منبع از رجیستری {len(registry)}-تایی `data/standards.yaml`:",
        "",
    ]
    for code in cited:
        entry = registry.get(code) or {}
        org = f" — {entry['org']}" if entry.get("org") else ""
        title = f": {entry['title']}" if entry.get("title") and entry["title"] != code else ""
        lines.append(f"- `{code}`{org}{title}")
    lines += [
        "",
        "## استناد",
        "",
        "```bibtex",
        "@dataset{eng_terms_fa_2026,",
        f"  author       = {{{MAINTAINER}}},",
        "  title        = {فرهنگ واژگان تخصصی مهندسی (Persian Engineering Terminology Dictionary)},",
        f"  organization = {{{PUBLISHER}}},",
        "  year         = {2026},",
        f"  version      = {{{DATA_VERSION}}},",
        f"  url          = {{{SITE_URL}}},",
        "  license      = {CC BY-SA 4.0}",
        "}",
        "```",
        "",
    ]
    path = out_dir / "README.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #

def generate(out_dir: Path = DEFAULT_OUT) -> dict:
    records = [record for _, record in load_all_terms()]
    meta = load_meta()
    registry = load_registry()
    opened = [open_record(record, registry) for record in records]

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "ndjson": write_ndjson(opened, out_dir),
        "jsonld": write_jsonld(dataset_jsonld(opened, meta), out_dir),
        "ttl": write_turtle(opened, meta, out_dir),
        "csv": write_csv(opened, out_dir),
        "datapackage": None,
        "readme": write_readme(opened, out_dir),
    }
    package = datapackage(opened)
    package_path = out_dir / "datapackage.json"
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["datapackage"] = package_path

    return {"records": len(opened), "paths": paths, "package": package}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    result = generate(Path(args.out))
    total = sum(p.stat().st_size for p in result["paths"].values())
    print(
        f"✅ open data bundle: {result['records']} terms → {args.out} "
        f"({total // 1024} KiB in {len(result['paths'])} files)"
    )


if __name__ == "__main__":
    main()
