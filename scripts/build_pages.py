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
from html import escape as html_escape
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from persian_text import (  # noqa: E402
    build_lexicon,
    build_protected,
    normalize as persian_normalize,
    record_roots,
)
from standards import resolve as resolve_source  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"
META_FILE = DATA_DIR / "_meta.yaml"
SCHEMA_FILE = ROOT / "schemas" / "term-v1.schema.json"
DOCS_TERMS_DIR = ROOT / "docs" / "terms"

# Legacy list pages — regenerated from the data on every build so they can
# never drift away from the single source of truth (data/terms/*.yaml).
CONSTRUCTION_LIST_FILE = ROOT / "docs" / "construction-terms.md"
BOOK_VOCAB_FILE = ROOT / "docs" / "book-vocab.md"
BOOK_SOURCE_FILE = "academy.yaml"
GENERATED_BANNER = (
    "<!-- این صفحه به‌صورت خودکار از data/terms/*.yaml توسط scripts/build_pages.py "
    "تولید می‌شود — آن را دستی ویرایش نکنید. -->"
)

DEFINITION_TARGET_LENGTH = 50

SITE_URL = "https://bmhmdyan279-png.github.io/eng-terms-fa/"
TERM_SET_NAME = "فرهنگ واژگان تخصصی مهندسی"

POS_FA = {"noun": "اسم", "verb": "فعل", "adjective": "صفت", "phrase": "عبارت"}
REF_TYPE_FA = {"standard": "استاندارد", "book": "کتاب", "other": "سایر"}
STATUS_FA = {"draft": "پیش‌نویس", "reviewed": "بازبینی‌شده", "published": "منتشرشده"}
REVIEW_LEVEL_FA = {
    "ai-assisted": "بازبینی دستیار هوشمند (بدون تأیید متخصص انسانی)",
    "expert": "بازبینی متخصص",
    "committee": "کمیتهٔ واژه‌گزینی",
}
ORIGIN_FA = {
    "fa": "فارسی", "ar": "عربی", "tr": "ترکی", "fr": "فرانسوی", "en": "انگلیسی",
    "de": "آلمانی", "la": "لاتین", "el": "یونانی", "ru": "روسی", "es": "اسپانیایی",
    "it": "ایتالیایی", "hy": "ارمنی", "mn": "مغولی", "other": "سایر",
}

#: How many same-root neighbours a term page lists at most.
MAX_ROOT_NEIGHBOURS = 8

#: How many related-term chips a page renders. The data graph stays complete and
#: mutual; showing fifteen chips on one page is noise, not information.
MAX_RENDERED_RELATED = 10


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


def _esc(value) -> str:
    """HTML-escape any value interpolated into a generated page.

    Every field that originates from the YAML data MUST pass through this
    before it reaches the Markdown/HTML output — a malicious pull request
    must never be able to inject raw markup or <script> tags.
    """
    return html_escape(str(value), quote=True)


def _yaml_str(value) -> str:
    """Render a value as a safely quoted YAML/JSON scalar for frontmatter."""
    return json.dumps(str(value), ensure_ascii=False)


def build_root_index(terms, lexicon=None, protected=None):
    """root (folded) → [slugs]. Powers the «هم‌ریشه‌ها» panel on every page."""
    if lexicon is None:
        lexicon = build_lexicon(terms)
    if protected is None:
        protected = build_protected(terms)
    index = {}
    for record in terms:
        for root in record_roots(record, lexicon, protected):
            index.setdefault(root, [])
            if record["slug"] not in index[root]:
                index[root].append(record["slug"])
    return index


def root_neighbours(record, root_index, lexicon=None, protected=None, limit=MAX_ROOT_NEIGHBOURS):
    """(root, [other slugs]) pairs for one record, richest root first.

    The lexicon MUST be the same one the index was built with: without it the
    guarded suffix rules cannot reduce «بندی» to «بند» and the panel would show
    a weaker root family than the search actually uses.
    """
    from persian_text import fold, root as persian_root

    candidates = record_roots(record, lexicon, protected)
    candidate_set = {fold(item) for item in candidates}
    # «بندی» reduces to «بند»; listing both would repeat the same family.
    out = []
    for item in candidates:
        deeper = fold(persian_root(item, lexicon, protected))
        if deeper != fold(item) and deeper in candidate_set:
            continue
        slugs = [slug for slug in root_index.get(item, []) if slug != record["slug"]]
        if slugs:
            out.append((item, slugs[:limit]))
    out.sort(key=lambda pair: len(pair[1]), reverse=True)
    return out[:3]


def render_pages(records, meta):
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in meta["domains"]}
    terms = [record for _, record in records]
    slug_to_term_fa = {t["slug"]: normalize_persian(t["term_fa"]) for t in terms}
    lexicon = build_lexicon(terms)
    protected = build_protected(terms)
    root_index = build_root_index(terms, lexicon, protected)

    DOCS_TERMS_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in DOCS_TERMS_DIR.glob("*.md"):
        try:
            old_file.unlink()
        except OSError as exc:  # locked by an editor/antivirus: don't kill the build
            print(f"WARNING: could not remove stale page {old_file}: {exc}", file=sys.stderr)

    for record in terms:
        term_fa = normalize_persian(record["term_fa"])
        slug = record["slug"]
        term_en = _esc(str(record.get("term_en") or "—").strip() or "—")
        term_fr = _esc(str(record.get("term_fr") or "—").strip() or "—")
        term_de = _esc(str(record.get("term_de") or "—").strip() or "—")
        term_ar = _esc(str(record.get("term_ar") or "—").strip() or "—")
        definition = _esc(str(record.get("definition_fa") or "").strip() or "تعریفی ثبت نشده است.")
        domains = [_esc(domain_titles.get(d, d)) for d in record.get("domain") or []] or ["عمومی"]
        pos_fa = _esc(POS_FA.get(record.get("pos"), record.get("pos") or ""))
        status = record.get("status", "draft")
        references = record.get("references") or []
        related = record.get("related_terms") or []

        page = (
            f"---\ntitle: {_yaml_str(term_fa)}\n"
            f"description: {_yaml_str('تعریف و معادل‌های واژه ' + term_fa)}\n"
            f"slug: {_yaml_str(slug)}\n---\n\n# {_esc(term_fa)}\n"
        )

        page += render_jsonld(record)

        if status == "draft":
            page += '\n!!! warning "وضعیت: پیش‌نویس"\n    این مدخل هنوز بازبینی تخصصی نشده است.\n'
        elif status == "reviewed":
            reviewer = _esc(record.get("reviewed_by") or "")
            level = REVIEW_LEVEL_FA.get(record.get("review_level"), REVIEW_LEVEL_FA["ai-assisted"])
            reviewed_at = _esc(record.get("reviewed_at") or "")
            meta_bits = " • ".join(bit for bit in (level, reviewer, reviewed_at) if bit)
            page += (
                f'\n!!! success "وضعیت: بازبینی‌شده"\n'
                f'    بازبینی انجام شده است{(" — " + meta_bits) if meta_bits else ""}.\n'
            )
            if record.get("review_level", "ai-assisted") == "ai-assisted":
                page += (
                    "    هنوز تأیید متخصص انسانی را ندارد؛ اگر ایرادی می‌بینید "
                    "[گزارش کنید](../contribute.md).\n"
                )
        elif status == "published":
            page += '\n!!! success "وضعیت: منتشرشده (تأیید متخصص)"\n'

        book_refs = [r for r in references if isinstance(r, dict) and r.get("type") == "book" and "آزمایشات فناوری بتن" in str(r.get("code", ""))]
        if book_refs:
            page += '\n!!! note "از کتاب آزمایشات فناوری بتن"\n    این واژه در کتاب آزمایشات فناوری بتن آورده شده است.\n'

        translation_notes = record.get("translation_notes") or {}

        equivalents_rows = [
            ("انگلیسی", "en", term_en, "ltr"),
            ("فرانسوی", "fr", term_fr, "ltr"),
            ("آلمانی", "de", term_de, "ltr"),
            ("عربی", "ar", term_ar, "rtl"),
        ]
        equivalents = "\n".join(
            f"| **{label}** | <span dir=\"{direction}\" lang=\"{code}\">{value}</span>"
            + (f" <span class=\"translation-note\">{_esc(translation_notes[code])}</span>"
               if translation_notes.get(code) else "")
            + " |"
            for label, code, value, direction in equivalents_rows
        )

        page += f"""
<div class="term-card">
## معادل‌های واژه
| زبان | معادل |
|------|-------|
{equivalents}
</div>
## تعریف
{definition}
## دسته‌بندی
**{"، ".join(domains)}** • نوع واژه: {pos_fa}
"""

        # ---- ساخت‌واژه و ریشه‌شناسی (فقط وقتی داده‌ای وجود دارد) ----
        morphology = []
        if record.get("root_fa"):
            morphology.append(f"- **ریشهٔ فارسی:** {_esc(normalize_persian(record['root_fa']))}")
        if record.get("root_ar"):
            morphology.append(
                f'- **ریشهٔ عربی:** <span dir="rtl" lang="ar">{_esc(record["root_ar"])}</span>'
            )
        if record.get("origin_lang"):
            morphology.append(
                f"- **زبان مبدأ واژه:** {_esc(ORIGIN_FA.get(record['origin_lang'], record['origin_lang']))}"
            )
        if record.get("plural_fa"):
            morphology.append(f"- **جمع:** {_esc(normalize_persian(record['plural_fa']))}")
        if record.get("abbrev_en"):
            morphology.append(
                f'- **مخفف انگلیسی:** <span dir="ltr" lang="en">{_esc(record["abbrev_en"])}</span>'
            )
        neighbours = root_neighbours(record, root_index, lexicon, protected)
        if neighbours:
            chips = []
            for root_value, slugs in neighbours:
                links = "، ".join(
                    f'<a href="./{_esc(slug)}.md">{_esc(slug_to_term_fa.get(slug, slug))}</a>'
                    for slug in slugs
                )
                chips.append(f"    - «{_esc(normalize_persian(root_value))}»: {links}")
            morphology.append("- **هم‌ریشه‌ها در این فرهنگ:**\n" + "\n".join(chips))
        if record.get("etymology_fa"):
            morphology.append(f"- **ریشه‌شناسی:** {_esc(normalize_persian(record['etymology_fa']))}")
        if morphology:
            page += '\n<div class="term-morphology">\n## ساخت‌واژه و ریشه\n' + "\n".join(morphology) + "\n</div>\n"

        # ---- مترادف‌ها و متضادها ----
        synonyms = [normalize_persian(v) for v in (record.get("synonyms") or [])]
        antonyms = [normalize_persian(v) for v in (record.get("antonyms") or [])]
        aliases = [normalize_persian(v) for v in (record.get("search_aliases") or [])]
        if synonyms or antonyms or aliases:
            page += "\n## مترادف‌ها و متضادها\n"
            if synonyms:
                page += f"- **مترادف:** {_esc('، '.join(synonyms))}\n"
            if antonyms:
                page += f"- **متضاد:** {_esc('، '.join(antonyms))}\n"
            if aliases:
                page += f"- **شکل‌های نوشتاری دیگر:** {_esc('، '.join(aliases))}\n"

        # ---- نمونهٔ کاربرد ----
        examples = [normalize_persian(v) for v in (record.get("usage_examples") or [])]
        if examples:
            page += "\n## نمونهٔ کاربرد\n"
            for example in examples:
                page += f"> {_esc(example)}\n\n"

        page += "\n## منابع\n"
        if references:
            for ref in references:
                if isinstance(ref, dict):
                    code = str(ref.get("code") or "—")
                    # everything beyond the code comes from the registry, so the
                    # data files can never contradict it (and an unregistered
                    # citation fails validate_content.py).
                    source = resolve_source(code) or {}
                    kind = _esc(REF_TYPE_FA.get(ref.get("type") or source.get("type"), "سایر"))
                    bits = [kind]
                    org = ref.get("org") or source.get("org")
                    if org:
                        bits.append(_esc(org))
                    edition = ref.get("edition") or source.get("edition")
                    if edition:
                        bits.append(f"ویرایش {_esc(edition)}")
                    if ref.get("section"):
                        bits.append(f"بخش {_esc(ref['section'])}")
                    label = _esc(code)
                    full_title = source.get("title")
                    if full_title and full_title != code:
                        label += f" — {_esc(full_title)}"
                    url = str(ref.get("url") or source.get("url") or "").strip()
                    if url.lower().startswith(("http://", "https://")):
                        label = f'<a href="{_esc(url)}" rel="noopener">{label}</a>'
                    page += f"- {label} ({'، '.join(bits)})\n"
                    if ref.get("note"):
                        page += f"    - {_esc(persian_normalize(ref['note']))}\n"
                else:
                    page += f"- {_esc(ref)}\n"
        else:
            page += "منبعی ثبت نشده است.\n"

        page += '\n## واژه‌های مرتبط\n<div class="related-terms">\n'
        valid_related = []
        for rid in related[:MAX_RENDERED_RELATED]:
            if rid in slug_to_term_fa:
                valid_related.append(f'<a href="./{_esc(rid)}.md">{_esc(slug_to_term_fa[rid])}</a>')
            else:
                # validate_terms() already fails the build on unknown ids;
                # this warning is defence in depth so nothing is ever
                # dropped silently if the gate is bypassed.
                print(
                    f"WARNING: {slug}: related_terms references unknown id '{rid}' — link dropped",
                    file=sys.stderr,
                )
        page += ("\n".join(valid_related) + "\n" if valid_related else "واژه مرتبطی ثبت نشده است.\n")
        hidden = len(related) - len(valid_related)
        if hidden > 0:
            page += f"\nو {hidden} واژهٔ مرتبط دیگر…\n"
        page += "\n</div>\n\n---\n\nبازگشت به فهرست\n"

        (DOCS_TERMS_DIR / f"{slug}.md").write_text(page, encoding="utf-8")

    (DOCS_TERMS_DIR / "index.md").write_text(render_index(records, meta), encoding="utf-8")


def render_index(records, meta):
    """Generate docs/terms/index.md with client-side faceted filters."""
    import html as _html

    all_terms = [record for _, record in records]
    lexicon = build_lexicon(all_terms)
    protected = build_protected(all_terms)

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
    out.append('<div id="persian-search" data-persian-search dir="rtl" markdown="0"></div>')
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
    out.append('  <span id="terms-count" class="terms-count" aria-live="polite"></span>')
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
        roots = record_roots(record, lexicon, protected)
        out.append(
            '  <li class="term-row"'
            f' data-domain="{esc(" ".join(domains))}"'
            f' data-status="{esc(status)}"'
            f' data-langs="{esc(" ".join(langs))}"'
            f' data-roots="{esc(" ".join(roots))}"'
            f' data-fa="{esc(fa)}" data-en="{esc(en)}">'
            f'<a href="./{esc(record["slug"])}.md">{esc(fa)}</a>'
            f' <span class="term-en" dir="ltr" lang="en">{esc(en)}</span>'
            f' <span class="term-domain">{esc(domain_labels)}</span>'
            f' <span class="term-status term-status-{esc(status)}">{esc(status_label)}</span>'
            "</li>"
        )
    out.append("</ul>")
    return "\n".join(out) + "\n"


def _definition_teaser(record, limit=100):
    """First line of the definition, trimmed — for the generated list pages."""
    text = " ".join(str(record.get("definition_fa") or "").split())
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text or "—"


def render_list_pages(records, meta):
    """Regenerate docs/construction-terms.md and docs/book-vocab.md.

    These pages used to be hand-maintained lists that drifted away from the
    data (duplicate entries, dead links). They are now derived from
    data/terms/*.yaml on every build — one single source of truth.
    """

    def entry(record):
        fa = _esc(normalize_persian(record["term_fa"]))
        slug = _esc(record["slug"])
        en = _esc(str(record.get("term_en") or "").strip())
        teaser = _esc(_definition_teaser(record))
        return f"- **[{fa}](terms/{slug}.md)** ({en}): {teaser}"

    construction = sorted(
        (r for _, r in records if "construction" in (r.get("domain") or [])),
        key=lambda r: normalize_persian(r["term_fa"]),
    )
    book = sorted(
        (r for source, r in records if source == BOOK_SOURCE_FILE),
        key=lambda r: normalize_persian(r["term_fa"]),
    )

    construction_page = (
        "# 🏗️ اصطلاحات ساختمانی\n\n"
        f"{GENERATED_BANNER}\n\n"
        "واژگان تخصصی و پرکاربرد در حوزهٔ ساختمان و اجرا.\n"
        "برای فیلتر بر پایهٔ حوزه، وضعیت و زبان‌ها به "
        "[فهرست واژگان](terms/index.md) بروید.\n\n"
        + "\n".join(entry(r) for r in construction)
        + "\n"
    )
    CONSTRUCTION_LIST_FILE.write_text(construction_page, encoding="utf-8")

    book_page = (
        "# 📖 واژگان اختصاصی کتاب آزمایشات فناوری بتن\n\n"
        f"{GENERATED_BANNER}\n\n"
        "واژگان مصوب فرهنگستان زبان و ادب فارسی که در کتاب «آزمایشات فناوری بتن» "
        "به کار رفته‌اند، همراه با تعریف تخصصی هر واژه.\n\n"
        + "\n".join(entry(r) for r in book)
        + "\n"
    )
    BOOK_VOCAB_FILE.write_text(book_page, encoding="utf-8")

    return len(construction), len(book)


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
    n_construction, n_book = render_list_pages(records, meta)
    print(
        f"✅ {len(records)} صفحه تولید شد ({len(warnings)} هشدار کیفیت تعریف) + "
        f"construction-terms.md ({n_construction}) و book-vocab.md ({n_book}) بازتولید شدند"
    )


if __name__ == "__main__":
    main()
