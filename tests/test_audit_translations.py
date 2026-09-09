import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from audit_translations import audit_records, find_problems, load_terms


class TestFindProblems:
    """The audit must catch the machine-translation disasters of 2026-09."""

    def test_flags_sentence_fragments(self):
        assert find_problems("en", "Contact him")
        assert find_problems("en", "John is plastered")
        assert find_problems("fr", "Ne pas briquer")
        assert find_problems("fr", "Ne sois pas une brique")
        assert find_problems("de", "Kontaktieren Sie ihn")

    def test_flags_wrong_domain_words(self):
        assert find_problems("fr", "Cornichon F")
        assert find_problems("de", "Pickle F")
        assert find_problems("fr", "Pagode")
        assert find_problems("de", "Pagode")
        assert find_problems("en", "Ginger")
        assert find_problems("en", "Sailor")
        assert find_problems("en", "Countries")
        assert find_problems("fr", "Eau chinoise")
        assert find_problems("de", "Chinesisches Wasser")
        assert find_problems("fr", "sont perdus")
        assert find_problems("de", "sind verloren")

    def test_flags_leading_articles(self):
        assert find_problems("en", "the vault")
        assert find_problems("en", "a ball")
        assert find_problems("fr", "le coffre-fort")
        assert find_problems("de", "der Tresor")

    def test_flags_too_long_values(self):
        assert find_problems("en", "this is a whole sentence not a term")

    def test_clean_values_pass(self):
        clean = [
            ("en", "rebar spacer"),
            ("en", "parapet"),
            ("fr", "mortier de jointoiement"),
            ("fr", "arc en plein cintre"),
            ("de", "Fugenmörtel"),
            ("de", "Brüstung"),
            ("ar", "مونة اللحامات"),
            ("ar", "وسادة ارتكاز"),
        ]
        for lang, value in clean:
            assert find_problems(lang, value) == [], f"{lang}:{value}"

    def test_null_is_valid_for_optional_languages(self):
        assert find_problems("fr", None) == []
        assert find_problems("de", None) == []
        assert find_problems("ar", None) == []
        assert find_problems("en", None)  # EN is required


class TestAuditRecords:
    def test_copy_paste_translation_detected(self):
        record = {
            "term_fa": "آلوئک", "slug": "x", "domain": [],
            "term_en": "Aloy", "term_fr": "Aloy", "term_de": "Aloy", "term_ar": "Aloy",
        }
        alerts = audit_records([record])
        assert any("identical" in a["reasons"] for a in alerts)

    def test_arabic_script_checked(self):
        record = {"term_fa": "x", "slug": "x", "domain": [], "term_en": "ok",
                  "term_fr": None, "term_de": None, "term_ar": "متن لاتین Latin"}
        alerts = audit_records([record])
        assert any("Latin characters" in a["reasons"] for a in alerts)

    def test_current_data_passes_audit(self):
        """The committed dataset must be alert-free (CI gate: --strict)."""
        assert audit_records(load_terms()) == []
