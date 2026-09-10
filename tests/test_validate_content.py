"""Tests for the scientific-content gate (scripts/validate_content.py).

A gate that nobody tests is a decoration. Each check gets a failing input that
must be caught and a passing input that must not be, plus one test asserting the
committed dataset satisfies every rule — the same pattern the translation audit
already uses.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from build_pages import load_all_terms  # noqa: E402
from standards import load_registry  # noqa: E402
from validate_content import (  # noqa: E402
    DEFINITION_REVIEWED_LENGTH,
    check_definitions,
    check_english_style,
    check_examples,
    check_graph,
    check_orthography,
    check_references,
    check_review,
    check_translations,
    collect_translation_gaps,
)

REGISTRY = load_registry()
RECORDS = load_all_terms()
ANY_CODE = next(iter(REGISTRY))
ANY_TYPE = REGISTRY[ANY_CODE]["type"]


def rec(**fields):
    """A minimal valid reviewed record, overridable per test."""
    base = {
        "id": "x",
        "slug": "x",
        "term_fa": "واژهٔ آزمایش",
        "term_en": "test term",
        "pos": "noun",
        "domain": ["construction"],
        "definition_fa": (
            "تعریفی که به اندازهٔ کافی بلند و فنی نوشته شده است تا از دروازهٔ کیفیت محتوای "
            "بازبینی‌شده عبور کند و نمونه‌ای از سطح مورد انتظار باشد."
        ),
        "status": "reviewed",
        "review_level": "ai-assisted",
        "reviewed_by": "Qwen (بازبینی دستیار هوشمند)",
        "reviewed_at": date.today().isoformat(),
        "references": [{"type": ANY_TYPE, "code": ANY_CODE, "note": "تعریف با دامنهٔ منبع هم‌خوان است."}],
    }
    base.update(fields)
    return base


# --------------------------------------------------------------------------- #
# 1. citations
# --------------------------------------------------------------------------- #

class TestCitations:
    def test_registered_source_with_a_note_passes(self):
        assert check_references([("x.yaml", rec())], REGISTRY) == ([], [])

    def test_unregistered_source_is_an_error(self):
        record = rec(references=[{"type": "standard", "code": "استاندارد ملی ایران ۶۶۴", "note": "x"}])
        errors, _ = check_references([("x.yaml", record)], REGISTRY)
        assert errors and "not in data/standards.yaml" in errors[0]

    def test_citation_without_a_note_is_an_error(self):
        record = rec(references=[{"type": ANY_TYPE, "code": ANY_CODE}])
        errors, _ = check_references([("x.yaml", record)], REGISTRY)
        assert errors and "no 'note'" in errors[0]

    def test_type_contradicting_the_registry_is_an_error(self):
        record = rec(references=[{"type": "book", "code": ANY_CODE, "note": "x"}])
        errors, _ = check_references([("x.yaml", record)], REGISTRY)
        if ANY_TYPE != "book":
            assert errors and "typed" in errors[0]

    def test_overriding_registry_metadata_is_only_a_warning(self):
        entry = REGISTRY[ANY_CODE]
        record = rec(references=[
            {"type": ANY_TYPE, "code": ANY_CODE, "note": "x", "org": entry.get("org", "") + " (دیگر"}
        ])
        errors, warnings = check_references([("x.yaml", record)], REGISTRY)
        assert not errors
        assert warnings and "source of truth" in warnings[0]

    def test_malformed_reference_is_an_error(self):
        errors, _ = check_references([("x.yaml", rec(references=["not-a-mapping"]))], REGISTRY)
        assert errors and "not a mapping" in errors[0]


# --------------------------------------------------------------------------- #
# 2-3. review integrity and attribution honesty
# --------------------------------------------------------------------------- #

class TestReviewIntegrity:
    def test_complete_review_metadata_passes(self):
        assert check_review([("x.yaml", rec())]) == []

    def test_draft_needs_no_review_metadata(self):
        record = rec(status="draft", reviewed_by=None, reviewed_at=None, review_level=None)
        assert check_review([("x.yaml", record)]) == []

    def test_reviewed_without_a_reviewer_is_an_error(self):
        errors = check_review([("x.yaml", rec(reviewed_by=None))])
        assert errors and "reviewed_by" in errors[0]

    def test_reviewed_without_a_date_is_an_error(self):
        errors = check_review([("x.yaml", rec(reviewed_at=None))])
        assert errors and "reviewed_at" in errors[0]

    def test_bad_date_format_is_an_error(self):
        errors = check_review([("x.yaml", rec(reviewed_at="10/09/2026"))])
        assert errors and "not a valid ISO date" in errors[0]

    def test_future_review_date_is_an_error(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        errors = check_review([("x.yaml", rec(reviewed_at=future))])
        assert errors and "future" in errors[0]

    def test_published_requires_human_sign_off(self):
        errors = check_review([("x.yaml", rec(status="published", review_level="ai-assisted"))])
        assert errors and "expert or committee" in errors[0]

    def test_published_with_an_expert_review_passes(self):
        record = rec(status="published", review_level="expert", reviewed_by="دکتر فلانی")
        assert check_review([("x.yaml", record)]) == []

    def test_ai_assisted_review_may_not_claim_a_human_credential(self):
        """The core honesty rule: no fake expert sign-off."""
        record = rec(reviewed_by="مهندس محمدی")
        errors = check_review([("x.yaml", record)])
        assert errors and "attribution must stay honest" in errors[0]

    def test_ai_assisted_review_must_say_so(self):
        errors = check_review([("x.yaml", rec(reviewed_by="some-anonymous-handle"))])
        assert errors and "requires reviewed_by to say so" in errors[0]


# --------------------------------------------------------------------------- #
# 4. definitions
# --------------------------------------------------------------------------- #

class TestDefinitions:
    def test_long_enough_definition_passes(self):
        assert check_definitions([("x.yaml", rec())]) == ([], [])

    def test_short_definition_blocks_a_reviewed_entry(self):
        record = rec(definition_fa="کوتاه")
        errors, warnings = check_definitions([("x.yaml", record)])
        assert errors and not warnings
        assert str(DEFINITION_REVIEWED_LENGTH) in errors[0]

    def test_short_definition_only_warns_for_a_draft(self):
        record = rec(status="draft", definition_fa="کوتاه")
        errors, warnings = check_definitions([("x.yaml", record)])
        assert not errors and warnings

    def test_copy_pasted_definition_is_an_error(self):
        text = "تعریف یکسان که در دو مدخل کپی شده است و باید گرفته شود."
        a = rec(id="a", slug="a", definition_fa=text)
        b = rec(id="b", slug="b", definition_fa=text)
        errors, _ = check_definitions([("x.yaml", a), ("y.yaml", b)])
        assert any("copy-paste" in e for e in errors), errors

    def test_definition_that_only_restates_the_headword_is_an_error(self):
        record = rec(term_fa="بتن", definition_fa="بتن.")
        errors, _ = check_definitions([("x.yaml", record)])
        assert any("restates the headword" in e for e in errors), errors


# --------------------------------------------------------------------------- #
# 5. orthography
# --------------------------------------------------------------------------- #

class TestOrthographyGate:
    def test_clean_record_passes(self):
        assert check_orthography([("x.yaml", rec())]) == []

    def test_arabic_kaf_in_the_headword_is_an_error(self):
        errors = check_orthography([("x.yaml", rec(term_fa="كتاب"))])
        assert errors and "term_fa" in errors[0]

    def test_glued_verbal_prefix_in_a_definition_is_an_error(self):
        errors = check_orthography([("x.yaml", rec(definition_fa="این کار می شود و تمام."))])
        assert errors and "می‌" in errors[0]

    def test_vocalized_etymology_is_allowed(self):
        record = rec(etymology_fa="از ریشهٔ اِصْتِکاکُ المُفْرِطِ در عربی، با آوایش دقیق.")
        assert check_orthography([("x.yaml", record)]) == []

    def test_pasted_arabic_in_a_definition_is_an_error(self):
        record = rec(definition_fa="اِصْتِکاکُ المُفْرِطِ بَینَ السَّطحَینِ یُؤَدّی اِلی الفَرْمَلَة")
        errors = check_orthography([("x.yaml", record)])
        assert errors and "definition_fa" in errors[0]

    def test_reference_notes_are_linted_too(self):
        record = rec(references=[{"type": ANY_TYPE, "code": ANY_CODE, "note": "یك یادداشت  عربی"}])
        errors = check_orthography([("x.yaml", record)])
        assert errors and "note" in errors[0]


# --------------------------------------------------------------------------- #
# 6. usage examples
# --------------------------------------------------------------------------- #

class TestUsageExamples:
    def test_example_using_the_headword_passes(self):
        record = rec(term_fa="آب‌بندی", usage_examples=["آب‌بندی بام پیش از کاشی‌کاری انجام شد."])
        assert check_examples([("x.yaml", record)]) == []

    def test_example_using_a_synonym_passes(self):
        record = rec(term_fa="لرزاننده", synonyms=["ویبره"],
                     usage_examples=["ویبره باید عمودی در بتن فرو رود."])
        assert check_examples([("x.yaml", record)]) == []

    def test_example_about_something_else_is_an_error(self):
        record = rec(term_fa="آرماتور", usage_examples=["هوا امروز بارانی بود."])
        errors = check_examples([("x.yaml", record)])
        assert errors and "does not contain the term" in errors[0]


# --------------------------------------------------------------------------- #
# 7-8. graph consistency
# --------------------------------------------------------------------------- #

class TestGraph:
    def test_mutual_links_pass(self):
        a = rec(id="a", slug="a", related_terms=["b"])
        b = rec(id="b", slug="b", related_terms=["a"])
        assert check_graph([("x.yaml", a), ("y.yaml", b)]) == []

    def test_self_reference_is_an_error(self):
        errors = check_graph([("x.yaml", rec(id="a", slug="a", related_terms=["a"]))])
        assert errors and "contains itself" in errors[0]

    def test_one_way_link_is_an_error(self):
        a = rec(id="a", slug="a", related_terms=["b"])
        b = rec(id="b", slug="b", related_terms=[])
        errors = check_graph([("x.yaml", a), ("y.yaml", b)])
        assert errors and "not mutual" in errors[0]

    def test_unknown_link_target_is_an_error(self):
        a = rec(id="a", slug="a", related_terms=["ghost"])
        errors = check_graph([("x.yaml", a)])
        assert errors and "unknown id" in errors[0]

    def test_synonym_matching_another_headword_needs_a_mutual_link(self):
        a = rec(id="a", slug="a", term_fa="میلگرد", synonyms=["آرماتور"], related_terms=[])
        b = rec(id="b", slug="b", term_fa="آرماتور", related_terms=[])
        errors = check_graph([("x.yaml", a), ("y.yaml", b)])
        assert errors and "undocumented duplicate" in errors[0]

    def test_documented_overlap_is_allowed(self):
        a = rec(id="a", slug="a", term_fa="پاکار", synonyms=["پاطاق"], related_terms=["b"])
        b = rec(id="b", slug="b", term_fa="پاطاق", related_terms=["a"])
        assert check_graph([("x.yaml", a), ("y.yaml", b)]) == []


# --------------------------------------------------------------------------- #
# 9-10. English style and translation notes
# --------------------------------------------------------------------------- #

class TestStyle:
    def test_lowercase_headword_passes(self):
        assert check_english_style([("x.yaml", rec(term_en="bearing pad"))]) == []

    def test_acronym_passes(self):
        assert check_english_style([("x.yaml", rec(term_en="RC"))]) == []

    def test_letter_designation_passes(self):
        """«F-bar bender» is not a title-cased headword."""
        assert check_english_style([("x.yaml", rec(term_en="F-bar bender"))]) == []

    def test_title_cased_headword_is_a_warning(self):
        warnings = check_english_style([("x.yaml", rec(term_en="Square brick"))])
        assert warnings and "lowercase" in warnings[0]


class TestTranslationNotes:
    def test_note_on_a_filled_column_passes(self):
        record = rec(term_fr="moise de coffrage", translation_notes={"fr": "معادل توصیفی است."})
        assert check_translations([("x.yaml", record)]) == ([], [])

    def test_note_on_an_empty_column_is_an_error(self):
        """Policy: unverified means null *and* silent — no note on a gap."""
        record = rec(term_fr=None, translation_notes={"fr": "معادل توصیفی است."})
        errors, _ = check_translations([("x.yaml", record)])
        assert errors and "must stay null" in errors[0]

    def test_unknown_language_key_is_an_error(self):
        record = rec(translation_notes={"es": "x"})
        errors, _ = check_translations([("x.yaml", record)])
        assert errors and "unknown language" in errors[0]

    def test_english_note_is_allowed(self):
        record = rec(translation_notes={"en": "waler معادل مصوب انگلیسی است."})
        assert check_translations([("x.yaml", record)]) == ([], [])

    def test_arabic_radical_on_a_non_arabic_origin_is_a_warning(self):
        record = rec(root_ar="ق-و-م", origin_lang="fr")
        _, warnings = check_translations([("x.yaml", record)])
        assert warnings and "origin_lang" in warnings[0]


# --------------------------------------------------------------------------- #
# gap report
# --------------------------------------------------------------------------- #

class TestGapReport:
    def test_missing_and_descriptive_translations_are_reported(self):
        a = rec(id="a", slug="a", term_fr=None, term_de=None, term_ar=None)
        b = rec(id="b", slug="b", term_fr="acier enrobé de plâtre",
                term_de="gipsummantelter Stahl", term_ar="حديد مكسو بالجبس",
                translation_notes={"fr": "معادل توصیفی است."})
        rows = collect_translation_gaps([("x.yaml", a), ("y.yaml", b)])
        missing = [r for r in rows if r["state"] == "missing"]
        descriptive = [r for r in rows if r["state"] == "descriptive"]
        assert len(missing) == 3
        assert len(descriptive) == 1 and descriptive[0]["value"] == "acier enrobé de plâtre"
        assert all(r["reason"] for r in rows)

    def test_a_complete_entry_produces_no_rows(self):
        record = rec(term_fr="x", term_de="y", term_ar="z")
        assert collect_translation_gaps([("x.yaml", record)]) == []


# --------------------------------------------------------------------------- #
# the committed dataset must satisfy every gate
# --------------------------------------------------------------------------- #

class TestCommittedDataset:
    def test_passes_every_content_gate(self):
        errors = []
        for check_errors, _ in (
            check_references(RECORDS, REGISTRY),
            check_definitions(RECORDS),
            check_translations(RECORDS),
        ):
            errors.extend(check_errors)
        errors.extend(check_review(RECORDS))
        errors.extend(check_orthography(RECORDS))
        errors.extend(check_examples(RECORDS))
        errors.extend(check_graph(RECORDS))
        assert not errors, "\n".join(errors[:10])

    def test_english_headword_style_is_clean(self):
        warnings = check_english_style(RECORDS)
        assert not warnings, "\n".join(warnings[:5])

    def test_every_entry_leaves_draft_with_attribution(self):
        for _, record in RECORDS:
            assert record["status"] in ("reviewed", "published"), record["id"]
            assert record.get("reviewed_by"), record["id"]
            assert record.get("reviewed_at"), record["id"]
            assert record.get("review_level"), record["id"]

    def test_no_entry_claims_human_sign_off(self):
        """Guards the honesty claim made in README/about/citation."""
        for _, record in RECORDS:
            if record.get("review_level") == "ai-assisted":
                assert "ai" in record["reviewed_by"].lower() or "هوشمند" in record["reviewed_by"]
            assert record["status"] != "published" or record.get("review_level") in ("expert", "committee")

    @pytest.mark.parametrize("field", ["root_fa", "etymology_fa", "origin_lang", "references"])
    def test_reviewed_fields_are_fully_populated(self, field):
        missing = [r["id"] for _, r in RECORDS if not r.get(field)]
        assert not missing, f"{field} missing for: {missing[:8]}"

    def test_translation_gaps_are_declared_not_hidden(self):
        rows = collect_translation_gaps(RECORDS)
        for row in rows:
            assert row["reason"], row
            if row["state"] == "descriptive":
                assert row["value"]
