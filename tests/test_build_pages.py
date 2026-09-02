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
