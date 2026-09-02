import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from build_pages import load_all_terms
from generate_api import build_categories, build_stats, generate_api, public_view
from generate_exports import write_csv, CSV_FIELDS
from totd import pick_index

REPO = Path(__file__).parent.parent


def test_public_view_shape():
    records = load_all_terms()
    view = public_view(records[0][1])
    for key in ("id", "term_fa", "term_en", "pos", "domain", "definition_fa", "status", "slug", "url"):
        assert key in view
    assert view["url"].startswith("https://")


def test_generate_api_creates_all_files(tmp_path):
    records = load_all_terms()
    result = generate_api(tmp_path)
    assert (tmp_path / "terms.json").exists()
    assert (tmp_path / "categories.json").exists()
    assert (tmp_path / "stats.json").exists()
    assert (tmp_path / "terms").is_dir()
    assert len(list((tmp_path / "terms").glob("*.json"))) == result["terms"]
    data = json.loads((tmp_path / "terms.json").read_text(encoding="utf-8"))
    assert data["count"] == len(records)


def test_api_stats_consistency():
    records = [r for _, r in load_all_terms()]
    stats = build_stats(records, {"domains": []})
    assert stats["total_terms"] == len(records)
    assert stats["reviewed_terms"] + stats["draft_terms"] == stats["total_terms"]


def test_categories_counts_sum():
    records = [r for _, r in load_all_terms()]
    meta = {"domains": [{"id": "construction"}, {"id": "concrete"}]}
    cats = build_categories(records, meta)
    assert all("count" in c for c in cats)


def test_csv_has_all_columns(tmp_path):
    records = [r for _, r in load_all_terms()]
    path = write_csv(records, tmp_path)
    content = path.read_text(encoding="utf-8-sig")
    header = content.splitlines()[0]
    for col in CSV_FIELDS:
        assert col in header


def test_exports_produce_valid_files(tmp_path):
    import sys as _sys
    _sys.path.insert(0, str(REPO / 'scripts'))
    from generate_exports import generate_exports
    result = generate_exports(tmp_path)
    assert result["csv"].exists()
    assert result["anki"].read_bytes()[:2] == b"PK"  # apkg is a zip
    assert result["pdf"].read_bytes()[:5] == b"%PDF-"


def test_totd_is_deterministic_and_in_range():
    count = len(load_all_terms())
    day = date(2026, 9, 3)
    a = pick_index(count, day)
    b = pick_index(count, day)
    assert a == b
    assert 0 <= a < count


def test_citation_contains_all_formats():
    text = (REPO / "docs" / "citation.md").read_text(encoding="utf-8")
    assert "BibTeX" in text
    assert "APA" in text
    assert "MLA" in text
    assert "DOI" in text
    assert "author" in text
