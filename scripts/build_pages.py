#!/usr/bin/env python3
"""Build the term pages (docs/terms/*.md) from the sharded YAML data.

Data layout:
    data/terms/_meta.yaml      collection metadata (domains, files)
    data/terms/*.yaml          term records, one file per subject area

Every record is validated against schemas/term-v1.schema.json plus
cross-record rules (unique id/slug, referential integrity of
related_terms, known domains). ANY invalid record fails the build.

Definitions shorter than DEFINITION_TARGET_LENGTH characters are
reported as warnings (content review is still in progress) but do not
fail the build.
"""

import json
import sys
import unicodedata
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"
META_FILE = DATA_DIR / "_meta.yaml"
SCHEMA_FILE = ROOT / "schemas" / "term-v1.schema.json"
DOCS_TERMS_DIR = ROOT / "docs" / "terms"

DEFINITION_TARGET_LENGTH = 50

SITE_URL = "https://bmhmdyan279-png.github.io/eng-terms-fa/"
TERM_SET_NAME = "فرهنگ واژگان تخصصی مهندسی"

POS_FA = {"noun": "اسم", "verb": "فعل", "adjective": "صفت", "phrase": "عبارت"}
REF_TYPE_FA = {"standard": "استاندارد", "book": "کتاب", "other": "سایر"}
STATUS_FA = {"draft": "پیش‌نویس", "reviewed": "بازبینی‌شده", "published": "منتشرشده"}


def normalize_persian(text: str) -> str:
    if not text:
        return ""
    text = text.replace("ي", "ی").replace("ك", "ک")
    return unicodedata.normalize("NFKC", text)


def render_jsonld(record) -> str:
    """Build a schema.org DefinedTerm JSON-LD block for a term page."""
    import json as _json

    definition = str(record.get("definition_fa") or "").strip()
    payload = {
        "@context": "https://schema.org",
        "@type": "DefinedTerm",
        "name": normalize_persian(record["term_fa"]),
        "alternateName": str(record.get("term_en") or "").strip(),
        "termCode": record["slug"],
        "inDefinedTermSet": {
            "@type": "DefinedTermSet",
            "name": TERM_SET_NAME,
            "url": SITE_URL,
        },
        "description": definition,
        "inLanguage": ["fa", "en"],
        "url": f"{SITE_URL}terms/{record['slug']}/",
    }
    body = _json.dumps(payload, ensure_ascii=False, indent=2)
    body = body.replace("</", "<\\/")  # never allow </script> injection
    return f'<script type="application/ld+json">\n{body}\n</script>\n'


def fail(message: str):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def load_meta() -> dict:
    if not META_FILE.exists():
        fail(f"metadata file not found: {META_FILE}")
    meta = yaml.safe_load(META_FILE.read_text(encoding="utf-8"))
    if not isinstance(meta, dict) or not isinstance(meta.get("domains"), list):
        fail(f"{META_FILE} is malformed (expected a 'domains' list)")
    return meta


def load_all_terms():
    """Return a list of (source_file_name, record) tuples from all shards."""
    if not DATA_DIR.exists():
        fail(f"data directory not found: {DATA_DIR}")
    records = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or doc.get("schema") != "term-v1":
            fail(f"{path.name}: missing or unsupported top-level 'schema: term-v1'")
        terms = doc.get("terms")
        if not isinstance(terms, list):
            fail(f"{path.name}: missing 'terms' list")
        for index, record in enumerate(terms):
            if not isinstance(record, dict):
                fail(f"{path.name}: entry #{index + 1} is not a mapping")
            records.append((path.name, record))
    if not records:
        fail("no term records found in data/terms/")
    return records


def validate_terms(records, meta):
    """Validate every record; return (errors, warnings)."""
    errors, warnings = [], []

    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    known_domains = {d["id"] for d in meta["domains"] if isinstance(d, dict) and "id" in d}

    seen_ids, seen_slugs = {}, {}
    for source, record in records:
        label = f"{source}::{record.get('id') or record.get('term_fa') or '?'}"

        for err in validator.iter_errors(record):
            errors.append(f"{label}: schema: {'/'.join(str(p) for p in err.path) or '<root>'}: {err.message}")

        rid, slug = record.get("id"), record.get("slug")
        if rid:
            if rid in seen_ids:
                errors.append(f"{label}: duplicate id '{rid}' (also in {seen_ids[rid]})")
            seen_ids[rid] = source
        if slug:
            if slug in seen_slugs:
                errors.append(f"{label}: duplicate slug '{slug}' (also in {seen_slugs[slug]})")
            seen_slugs[slug] = source
            if rid and slug != rid:
                errors.append(f"{label}: slug '{slug}' must equal id '{rid}' (stable URLs)")

        for domain in record.get("domain") or []:
            if domain not in known_domains:
                errors.append(f"{label}: unknown domain '{domain}' (not in _meta.yaml)")

        definition = (record.get("definition_fa") or "").strip()
        if len(definition) < DEFINITION_TARGET_LENGTH:
            warnings.append(f"{label}: definition_fa has {len(definition)} chars (target >= {DEFINITION_TARGET_LENGTH})")

    for source, record in records:
        label = f"{source}::{record.get('id') or '?'}"
        for related in record.get("related_terms") or []:
            if related not in seen_ids:
                errors.append(f"{label}: related_terms references unknown id '{related}'")

    return errors, warnings


def render_pages(records, meta):
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in meta["domains"]}
    terms = [record for _, record in records]
    slug_to_term_fa = {t["slug"]: normalize_persian(t["term_fa"]) for t in terms}

    DOCS_TERMS_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in DOCS_TERMS_DIR.glob("*.md"):
        old_file.unlink()

    for record in terms:
        term_fa = normalize_persian(record["term_fa"])
        slug = record["slug"]
        term_en = str(record.get("term_en") or "—").strip() or "—"
        term_fr = str(record.get("term_fr") or "—").strip() or "—"
        term_de = str(record.get("term_de") or "—").strip() or "—"
        term_ar = str(record.get("term_ar") or "—").strip() or "—"
        definition = str(record.get("definition_fa") or "").strip() or "تعریفی ثبت نشده است."
        domains = [domain_titles.get(d, d) for d in record.get("domain") or []] or ["عمومی"]
        pos_fa = POS_FA.get(record.get("pos"), record.get("pos"))
        status = record.get("status", "draft")
        references = record.get("references") or []
        related = record.get("related_terms") or []

        page = (
            f"---\ntitle: {term_fa}\n"
            f"description: تعریف و معادل‌های واژه {term_fa}\n"
            f"slug: {slug}\n---\n\n# {term_fa}\n"
        )

        page += render_jsonld(record)

        if status == "draft":
            page += '\n!!! warning "وضعیت: پیش‌نویس"\n    این مدخل هنوز بازبینی تخصصی نشده است.\n'
        elif status == "reviewed":
            reviewer = record.get("reviewed_by") or ""
            page += f'\n!!! success "وضعیت: بازبینی‌شده"\n    بازبینی تخصصی انجام شده است.{(" — " + reviewer) if reviewer else ""}\n'
        elif status == "published":
            page += '\n!!! success "وضعیت: منتشرشده"\n'

        book_refs = [r for r in references if isinstance(r, dict) and r.get("type") == "book" and "آزمایشات فناوری بتن" in str(r.get("code", ""))]
        if book_refs:
            page += '\n!!! note "از کتاب آزمایشات فناوری بتن"\n    این واژه در کتاب آزمایشات فناوری بتن آورده شده است.\n'

        page += f"""
<div class="term-card">
## معادل‌های واژه
| زبان | معادل |
|------|-------|
| **انگلیسی** | <span dir="ltr" lang="en">{term_en}</span> |
| **فرانسوی** | <span dir="ltr" lang="fr">{term_fr}</span> |
| **آلمانی** | <span dir="ltr" lang="de">{term_de}</span> |
| **عربی** | <span dir="rtl" lang="ar">{term_ar}</span> |
</div>
## تعریف
{definition}
## دسته‌بندی
**{"، ".join(domains)}** • نوع واژه: {pos_fa}
"""

        page += "\n## منابع\n"
        if references:
            for ref in references:
                if isinstance(ref, dict):
                    kind = REF_TYPE_FA.get(ref.get("type"), "سایر")
                    edition = f"، ویرایش {ref['edition']}" if ref.get("edition") else ""
                    page += f"- {ref.get('code', '—')} ({kind}{edition})\n"
                else:
                    page += f"- {ref}\n"
        else:
            page += "منبعی ثبت نشده است.\n"

        page += '\n## واژه‌های مرتبط\n<div class="related-terms">\n'
        valid_related = [
            f'<a href="./{rid}.md">{slug_to_term_fa[rid]}</a>'
            for rid in related
            if rid in slug_to_term_fa
        ]
        page += ("\n".join(valid_related) + "\n" if valid_related else "واژه مرتبطی ثبت نشده است.\n")
        page += "\n</div>\n\n---\n\nبازگشت به فهرست\n"

        (DOCS_TERMS_DIR / f"{slug}.md").write_text(page, encoding="utf-8")

    (DOCS_TERMS_DIR / "index.md").write_text(render_index(records, meta), encoding="utf-8")


def render_index(records, meta):
    """Generate docs/terms/index.md with client-side faceted filters."""
    import html as _html

    terms = [record for _, record in records]
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in meta.get("domains", [])}
    domain_order = [d["id"] for d in meta.get("domains", [])]
    present_domains = [
        d for d in domain_order
        if any(d in (t.get("domain") or []) for t in terms)
    ]

    def esc(value):
        return _html.escape(str(value), quote=True)

    out = []
    out.append("---\ntitle: فهرست واژگان\ndescription: فهرست واژگان با فیلتر حوزه، وضعیت و ترجمه‌ها\n---\n")
    out.append("# فهرست واژگان")
    out.append("")
    out.append('<div class="term-filters" markdown="0">')
    out.append('  <div class="filter-group"><label for="filter-domain">حوزه:</label>'
               ' <select id="filter-domain"><option value="">همه</option>')
    for d in present_domains:
        out.append(f'    <option value="{esc(d)}">{esc(domain_titles.get(d, d))}</option>')
    out.append('  </select></div>')
    out.append('  <div class="filter-group"><label for="filter-status">وضعیت:</label>'
               ' <select id="filter-status"><option value="">همه</option>')
    for status, label in STATUS_FA.items():
        out.append(f'    <option value="{status}">{label}</option>')
    out.append('  </select></div>')
    out.append('  <div class="filter-group"><label for="filter-langs">دست‌کم دارای:</label>'
               ' <select id="filter-langs"><option value="">همهٔ زبان‌ها</option>'
               '<option value="en">انگلیسی</option>'
               '<option value="fr">فرانسوی</option>'
               '<option value="de">آلمانی</option>'
               '<option value="ar">عربی</option></select></div>')
    out.append('  <div class="filter-group"><label for="filter-sort">مرتب‌سازی:</label>'
               ' <select id="filter-sort"><option value="fa">فارسی (الفبایی)</option>'
               '<option value="en">انگلیسی (الفبایی)</option></select></div>')
    out.append('  <span id="terms-count" class="terms-count"></span>')
    out.append('</div>')
    out.append("")
    out.append('<ul id="terms-list" class="terms-list">')
    for record in sorted(terms, key=lambda t: normalize_persian(t["term_fa"])):
        fa = normalize_persian(record["term_fa"])
        en = str(record.get("term_en") or "").strip()
        status = record.get("status", "draft")
        status_label = STATUS_FA.get(status, status)
        domains = record.get("domain") or []
        langs = ["en"] if en else []
        for code in ("fr", "de", "ar"):
            if str(record.get(f"term_{code}") or "").strip():
                langs.append(code)
        domain_labels = "، ".join(domain_titles.get(d, d) for d in domains)
        out.append(
            '  <li class="term-row"'
            f' data-domain="{esc(" ".join(domains))}"'
            f' data-status="{esc(status)}"'
            f' data-langs="{esc(" ".join(langs))}"'
            f' data-fa="{esc(fa)}" data-en="{esc(en)}">'
            f'<a href="./{esc(record["slug"])}.md">{esc(fa)}</a>'
            f' <span class="term-en" dir="ltr" lang="en">{esc(en)}</span>'
            f' <span class="term-domain">{esc(domain_labels)}</span>'
            f' <span class="term-status term-status-{esc(status)}">{esc(status_label)}</span>'
            "</li>"
        )
    out.append("</ul>")
    return "\n".join(out) + "\n"


def main():
    meta = load_meta()
    records = load_all_terms()
    errors, warnings = validate_terms(records, meta)

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"\n✗ build aborted: {len(errors)} validation error(s) across {len(records)} records", file=sys.stderr)
        sys.exit(1)

    render_pages(records, meta)
    print(f"✅ {len(records)} صفحه تولید شد ({len(warnings)} هشدار کیفیت تعریف)")


if __name__ == "__main__":
    main()
