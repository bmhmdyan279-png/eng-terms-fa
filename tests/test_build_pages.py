import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from build_pages import normalize_persian, load_all_terms, load_meta, validate_terms


def test_normalize():
    assert normalize_persian('كتاب') == 'کتاب'


def test_all_records_pass_schema_validation():
    """Every committed record must satisfy term-v1.schema.json and the
    cross-record rules (unique ids/slugs, valid related_terms, known domains)."""
    records = load_all_terms()
    assert records, "no term records found"
    errors, _ = validate_terms(records, load_meta())
    assert errors == [], "\n".join(errors)


def test_ids_and_slugs_are_unique_and_stable():
    records = load_all_terms()
    ids = [record.get("id") for _, record in records]
    slugs = [record.get("slug") for _, record in records]
    assert len(ids) == len(set(ids)), "duplicate ids found"
    assert len(slugs) == len(set(slugs)), "duplicate slugs found"
    assert ids == slugs, "id and slug must be identical (stable URLs)"


def test_render_pages_escapes_html(tmp_path, monkeypatch):
    """Regression test: hostile YAML must never reach the page as raw HTML."""
    import build_pages

    monkeypatch.setattr(build_pages, "DOCS_TERMS_DIR", tmp_path)
    evil = {
        "id": "evil",
        "slug": "evil",
        "term_fa": "بد",
        "term_en": "<script>alert(1)</script>",
        "term_fr": '"><img src=x onerror=alert(2)>',
        "term_de": None,
        "term_ar": None,
        "pos": "noun",
        "domain": ["construction"],
        "definition_fa": "<b>raw</b> & \"quoted\"",
        "status": "draft",
        "references": [{"type": "standard", "code": "<i>ACI</i>"}],
        "related_terms": [],
    }
    meta = {"domains": [{"id": "construction", "title_fa": "ساختمان"}]}
    build_pages.render_pages([("construction.yaml", evil)], meta)

    page = (tmp_path / "evil.md").read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;alert(1)" in page
    assert "<b>raw</b>" not in page          # escaped everywhere, JSON-LD included
    assert "<img src=x" not in page
    assert "<i>ACI</i>" not in page

    # frontmatter must stay parseable YAML even with quoted values
    import yaml as _yaml
    front = page.split("---")[1]
    data = _yaml.safe_load(front)
    assert data["title"] == "بد"
    assert data["slug"] == "evil"


def test_list_pages_are_generated_from_data(tmp_path, monkeypatch):
    """construction-terms.md / book-vocab.md must be derived from the YAML."""
    import re
    import build_pages

    construction = tmp_path / "construction-terms.md"
    book = tmp_path / "book-vocab.md"
    monkeypatch.setattr(build_pages, "CONSTRUCTION_LIST_FILE", construction)
    monkeypatch.setattr(build_pages, "BOOK_VOCAB_FILE", book)

    records = load_all_terms()
    build_pages.render_list_pages(records, load_meta())

    content = construction.read_text(encoding="utf-8")
    # no duplicate headwords any more (آب بندی used to appear 3 times)
    assert content.count("**[آب بندی]") == 1
    # every link resolves to a real term slug
    slugs = {record["slug"] for _, record in records}
    for link in re.findall(r"\(terms/([^)]+)\.md\)", content):
        if link == "index":
            continue  # legitimate pointer to the generated term index
        assert link in slugs, f"dead link: terms/{link}.md"

    book_content = book.read_text(encoding="utf-8")
    assert "رقمی" in book_content
    for link in re.findall(r"\(terms/([^)]+)\.md\)", book_content):
        assert link in slugs


def test_committed_list_pages_match_generated_output(tmp_path, monkeypatch):
    """The committed copies must not drift from the data (CI enforces this too).

    Renders into tmp_path and *compares* against the committed files — it must
    never rewrite them, otherwise the CI git-diff gate would be defeated.
    """
    import build_pages

    real_c = build_pages.CONSTRUCTION_LIST_FILE
    real_b = build_pages.BOOK_VOCAB_FILE
    tmp_c = tmp_path / "construction-terms.md"
    tmp_b = tmp_path / "book-vocab.md"
    monkeypatch.setattr(build_pages, "CONSTRUCTION_LIST_FILE", tmp_c)
    monkeypatch.setattr(build_pages, "BOOK_VOCAB_FILE", tmp_b)

    build_pages.render_list_pages(load_all_terms(), load_meta())

    assert tmp_c.read_text(encoding="utf-8") == real_c.read_text(encoding="utf-8"), \
        "docs/construction-terms.md is stale — run scripts/build_pages.py"
    assert tmp_b.read_text(encoding="utf-8") == real_b.read_text(encoding="utf-8"), \
        "docs/book-vocab.md is stale — run scripts/build_pages.py"
