import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from build_pages import load_all_terms, load_meta, render_index
from mkdocs_hooks import STATS_MARKERS, compute_stats, render_stats_html

REPO = Path(__file__).parent.parent


def test_rendered_index_has_faceted_filters():
    records = load_all_terms()
    html = render_index(records, load_meta())
    assert 'id="filter-domain"' in html
    assert 'id="filter-status"' in html
    assert 'id="filter-langs"' in html
    assert 'id="filter-sort"' in html
    assert 'id="terms-list"' in html
    assert html.count('class="term-row"') == len(records)


def test_every_index_row_carries_filter_metadata():
    records = load_all_terms()
    html = render_index(records, load_meta())
    for attr in ('data-domain', 'data-status', 'data-langs', 'data-fa', 'data-en'):
        assert html.count(attr) == len(records), f"missing {attr} on some rows"


def test_stats_match_real_data():
    records = load_all_terms()
    stats = compute_stats([record for _, record in records])
    assert stats["total"] == len(records)
    assert stats["languages"] == 5
    assert stats["reviewed"] >= 0
    assert stats["draft"] == stats["total"] - stats["reviewed"]


def test_homepage_has_stats_markers():
    homepage = (REPO / "docs" / "index.md").read_text(encoding="utf-8")
    assert STATS_MARKERS.search(homepage), "stats markers missing from docs/index.md"


def test_stats_markers_are_replaced_at_render():
    records = load_all_terms()
    fake_html = "<p>before</p><!--stats:start--><!--stats:end--><p>after</p>"
    rendered = STATS_MARKERS.sub(render_stats_html([r for _, r in records]), fake_html)
    assert "live-stats" in rendered
    assert "stats:start" not in rendered
