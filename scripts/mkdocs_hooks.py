"""MkDocs hooks for the engineering dictionary.

1. Live stats: the home page contains markers
   (<!--stats:start--><!--stats:end-->) that are filled at render time
   with numbers computed from data/terms/*.yaml — always current, never
   stale in the source file.

2. Pagefind scoping: every page's content is wrapped in a
   <div data-pagefind-body> so the search index only covers real
   content, not the repeated navigation chrome.
"""

import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import totd as _totd  # noqa: E402

STATS_SLOT = '<div id="live-stats"></div>'
TOTD_SLOT = '<div id="totd-slot"></div>'

LANGUAGE_COUNT = 5  # FA, EN, FR, DE, AR

_cache = None


def _fa_digits(number: int) -> str:
    return str(number).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def _load_terms():
    global _cache
    if _cache is None:
        terms = []
        for path in sorted(DATA_DIR.glob("*.yaml")):
            if path.name.startswith("_"):
                continue
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            terms.extend(doc.get("terms") or [])
        _cache = terms
    return _cache


def compute_stats(terms) -> dict:
    reviewed = sum(1 for t in terms if t.get("status") in ("reviewed", "published"))
    return {
        "total": len(terms),
        "languages": LANGUAGE_COUNT,
        "reviewed": reviewed,
        "draft": len(terms) - reviewed,
    }


def render_totd_html(terms, day=None) -> str:
    """Render the deterministic term-of-the-day card for `day`."""
    import html as _html

    if not terms:
        return '<div id="totd"></div>'
    index = _totd.pick_index(len(terms), day)
    term = terms[index]
    fa = _html.escape(str(term.get("term_fa", "")))
    en = _html.escape(str(term.get("term_en", "")))
    slug = _html.escape(str(term.get("slug", "")))
    definition = str(term.get("definition_fa", "")).strip()
    if len(definition) > 140:
        definition = definition[:140] + "…"
    definition = _html.escape(definition)
    card = (
        '<div class="totd-card">\n'
        '  <span class="totd-label">واژهٔ روز</span>\n'
        f'  <a class="totd-term" href="terms/{slug}/">{fa}</a>\n'
        f'  <span class="totd-en" dir="ltr" lang="en">{en}</span>\n'
        f'  <p class="totd-def">{definition}</p>\n'
        "</div>"
    )
    payload = [
        [
            str(t.get("slug", "")),
            str(t.get("term_fa", "")),
            str(t.get("term_en", "")),
            str(t.get("definition_fa", ""))[:140],
        ]
        for t in terms
    ]
    import json as _json

    data_script = (
        '<script id="totd-data" type="application/json">'
        + _json.dumps(payload, ensure_ascii=False)
        + "</script>"
    )
    return f'<div id="totd">{card}</div>\n{data_script}'


def render_stats_html(terms) -> str:
    stats = compute_stats(terms)
    return (
        '<div class="live-stats">\n'
        f'  <span class="stat"><b>{_fa_digits(stats["total"])}</b> واژه</span>\n'
        f'  <span class="stat"><b>{_fa_digits(stats["languages"])}</b> زبان</span>\n'
        f'  <span class="stat"><b>{_fa_digits(stats["reviewed"])}</b> بازبینی‌شده</span>\n'
        f'  <span class="stat"><b>{_fa_digits(stats["draft"])}</b> پیش‌نویس در حال بازبینی</span>\n'
        "</div>"
    )


def on_page_content(html, page, config, files):
    # NOTE: HTML comments are re-ordered by the markdown renderer, so we use
    # stable <div> slots in index.md instead of comment markers.
    if page.file.src_path == "index.md":
        terms = _load_terms()
        html = html.replace(STATS_SLOT, render_stats_html(terms))
        html = html.replace(TOTD_SLOT, render_totd_html(terms))
    return f'<div data-pagefind-body>{html}</div>'


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def collect_pages(site_dir: Path) -> list:
    """Return (path, priority, changefreq) for every directory-style page."""
    pages = []
    for html_file in sorted(site_dir.rglob("index.html")):
        rel = html_file.relative_to(site_dir)
        path = rel.parent.as_posix()
        if path == ".":
            pages.append(("", "1.0", "weekly"))
        elif path.startswith("terms"):
            pages.append((path + "/", "0.8", "weekly"))
        else:
            pages.append((path + "/", "0.6", "monthly"))
    return pages


def write_sitemap(site_dir: Path, site_url: str) -> Path:
    """Generate sitemap.xml with <lastmod> (file mtime) and <changefreq>."""
    from datetime import datetime, timezone

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for path, priority, changefreq in collect_pages(site_dir):
        html_file = site_dir / path / "index.html"
        if not html_file.exists():
            continue
        lastmod = datetime.fromtimestamp(html_file.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        loc = site_url + path
        if not loc.endswith("/"):
            loc += "/"
        lines.append(
            "  <url>\n"
            f"    <loc>{_xml_escape(loc)}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    lines.append("</urlset>")
    sitemap_path = site_dir / "sitemap.xml"
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sitemap_path


def on_post_build(config, **kwargs):
    site_dir = Path(config["site_dir"])
    site_url = (config.get("site_url") or "").rstrip("/") + "/"
    sitemap = write_sitemap(site_dir, site_url)
    print(f"sitemap.xml written with {len(collect_pages(site_dir))} urls")
