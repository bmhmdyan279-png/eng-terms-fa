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
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "terms"

STATS_MARKERS = re.compile(r"<!--\s*stats:start\s*-->.*?<!--\s*stats:end\s*-->", re.DOTALL)

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
    if page.file.src_path == "index.md":
        stats_html = render_stats_html(_load_terms())
        html = STATS_MARKERS.sub(stats_html, html)
    return f'<div data-pagefind-body>{html}</div>'
