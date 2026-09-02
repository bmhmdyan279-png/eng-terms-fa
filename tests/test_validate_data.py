import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from validate_data import (
    check_definition_lengths,
    check_lazy_translations,
    check_placeholder_values,
    check_slug_immutability,
)


def test_lazy_translation_is_detected():
    records = [("x.yaml", {"term_fa": "آجر", "term_en": "brick", "term_fr": "Brick"})]
    errors = check_lazy_translations(records)
    assert len(errors) == 1
    assert "term_fr" in errors[0]


def test_genuine_translation_passes():
    records = [("x.yaml", {"term_en": "brick", "term_fr": "brique", "term_de": "Ziegel", "term_ar": "طوب"})]
    assert check_lazy_translations(records) == []


def test_international_cognates_are_allowed():
    records = [("x.yaml", {"term_en": "asphalt", "term_de": "Asphalt"})]
    assert check_lazy_translations(records) == []


def test_placeholder_values_are_detected():
    records = [
        (
            "x.yaml",
            {
                "term_fa": "واژه",
                "definition_fa": "TODO",
                "references": [{"type": "book", "code": "placeholder"}],
            },
        )
    ]
    errors = check_placeholder_values(records)
    assert len(errors) == 2


def test_placeholder_scan_ignores_real_content():
    records = [("x.yaml", {"term_fa": "واژه", "definition_fa": "تعریف واقعی و کامل"})]
    assert check_placeholder_values(records) == []


def test_definition_length_blocks_reviewed_terms():
    records = [
        ("x.yaml", {"definition_fa": "کوتاه", "status": "reviewed"}),
        ("x.yaml", {"definition_fa": "کوتاه", "status": "draft"}),
        ("x.yaml", {"definition_fa": "الف" * 60, "status": "reviewed"}),
    ]
    errors, warnings = check_definition_lengths(records)
    assert len(errors) == 1 and "reviewed" in errors[0]
    assert len(warnings) == 1 and "draft" in warnings[0]


def test_slug_immutability_detects_a_change():
    baseline = [{"term_fa": "بتن", "slug": "beton"}]
    current = [{"id": "betun", "term_fa": "بتن", "slug": "betun"}]
    errors = check_slug_immutability(baseline, current)
    assert len(errors) == 1
    assert "immutable" in errors[0]


def test_slug_immutability_matches_by_id_first():
    baseline = [{"id": "beton", "term_fa": "بتن", "slug": "beton"}]
    current = [{"id": "beton", "term_fa": "بتن (اصلاح‌شده)", "slug": "beton"}]
    assert check_slug_immutability(baseline, current) == []


def test_slug_immutability_allows_new_terms():
    baseline = [{"term_fa": "بتن", "slug": "beton"}]
    current = [
        {"id": "beton", "term_fa": "بتن", "slug": "beton"},
        {"id": "new-term", "term_fa": "واژه جدید", "slug": "new-term"},
    ]
    assert check_slug_immutability(baseline, current) == []
