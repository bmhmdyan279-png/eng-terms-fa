"""Tests for the Persian morphology engine (scripts/persian_text.py).

Two kinds of test live here:

* **behavioural** — the rules do what the docs say (plural, comparative,
  broken plural, verb paradigm, compound split, typo tolerance).
* **invariants** — properties that must hold for *every* string in the dataset.
  These are what make the engine safe to trust: a headword is never mangled,
  stemming is idempotent, the folded form of a string is always indexed, and
  Python's ``casefold`` agrees with JavaScript's ``toLowerCase`` (otherwise the
  browser stemmer could not be a faithful mirror).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from build_pages import load_all_terms, load_meta  # noqa: E402
from persian_text import (  # noqa: E402
    BROKEN_PLURALS,
    CONJUGATIONS,
    STEM_TO_VERB,
    ZWNJ,
    build_lexicon,
    build_protected,
    content_tokens,
    fold,
    index_forms,
    normalize,
    orthography_warnings,
    root,
    root_family,
    split_compound,
    stem,
    suggest,
    tokenize,
)

RECORDS = [record for _, record in load_all_terms()]
LEXICON = build_lexicon(RECORDS)
PROTECTED = build_protected(RECORDS)


# --------------------------------------------------------------------------- #
# normalization
# --------------------------------------------------------------------------- #

class TestNormalize:
    def test_arabic_yeh_and_kaf_become_persian(self):
        assert normalize("كتاب") == "کتاب"
        assert normalize("مقاومت") == "مقاومت"

    def test_diacritics_and_tatweel_removed(self):
        assert normalize("مـقاومَـت") == "مقاومت"
        # أ folds to a bare alef (standard Arabic search normalization);
        # آ is a distinct Persian letter and must survive.
        assert normalize("رَأسِيّ") == "راسی"
        assert normalize("آب") == "آب"

    def test_digits_unified_to_ascii(self):
        assert normalize("۱۱۰ درجه") == "110 درجه"
        assert normalize("١٢٣") == "123"

    def test_heh_hamza_folded(self):
        assert normalize("خانهٔ من") == "خانه من"

    def test_half_space_is_preserved(self):
        # ZWNJ is meaningful in Persian; tokenize() decides what to do with it
        assert normalize("آب‌بندی") == "آب‌بندی"
        assert ZWNJ in normalize("آب‌بندی")

    def test_fold_drops_half_space_and_case(self):
        assert fold("آب‌بندی") == "آببندی"
        assert fold("Self-Consolidating") == "self-consolidating"

    def test_empty_and_none_are_safe(self):
        assert normalize("") == ""
        assert normalize(None) == ""
        assert fold(None) == ""


# --------------------------------------------------------------------------- #
# tokenization
# --------------------------------------------------------------------------- #

class TestTokenize:
    def test_compound_yields_whole_then_parts(self):
        tokens = tokenize("آب‌بندی")
        assert tokens[0] == "آب‌بندی"
        assert "آب" in tokens and "بندی" in tokens
        assert "آببندی" in tokens  # the de-spaced form is indexed too

    def test_persian_comma_is_a_separator(self):
        """Regression: «،» lives inside \\u0600-\\u06ff and used to be glued on."""
        tokens = tokenize("ساختمان، سپس پی")
        assert "ساختمان" in tokens
        assert not any("،" in token for token in tokens)

    def test_latin_hyphenated_terms_split(self):
        tokens = tokenize("self-consolidating concrete")
        assert "self-consolidating" in tokens
        assert "self" in tokens and "consolidating" in tokens

    def test_stopwords_and_digits_filtered_by_content_tokens(self):
        assert content_tokens("و یا که ۱۱۰ بتن") == ["بتن"]

    def test_tokens_are_deduplicated_in_order(self):
        assert tokenize("بتن بتن") == ["بتن"]


# --------------------------------------------------------------------------- #
# stemming
# --------------------------------------------------------------------------- #

class TestStem:
    @pytest.mark.parametrize(
        "word,expected",
        [
            ("آجرها", "آجر"),
            ("آجرهایمان", "آجر"),
            ("میلگردها", "میلگرد"),
            ("بزرگتر", "بزرگ"),
            ("بزرگترین", "بزرگ"),
        ],
    )
    def test_safe_suffixes(self, word, expected):
        assert stem(word, LEXICON, PROTECTED) == expected

    @pytest.mark.parametrize(
        "word,expected",
        [
            ("مشخصات", "مشخصه"),       # broken plural, not مشخص + ات
            ("آزمایشات", "آزمایش"),
            ("تجهیزات", "تجهیز"),
        ],
    )
    def test_arabic_broken_plurals(self, word, expected):
        assert stem(word, LEXICON, PROTECTED) == expected

    def test_ambiguous_suffix_needs_a_known_remainder(self):
        """«اندام» must not lose «ام»: «اندا» is not a word."""
        assert stem("اندام", LEXICON, PROTECTED) == "اندام"

    def test_is_idempotent(self):
        for word in ("آجرهایمان", "مشخصات", "می‌شود", "ناشاقولی", "آب‌بندی"):
            once = stem(word, LEXICON, PROTECTED)
            assert stem(once, LEXICON, PROTECTED) == once

    def test_short_words_are_never_over_reduced(self):
        for word in ("ماه", "راه", "چاه", "بهتر", "بستر"):
            assert len(stem(word, LEXICON, PROTECTED)) >= 2


class TestRoot:
    @pytest.mark.parametrize(
        "word,expected",
        [
            ("بندی", "بند"),          # present stem of بستن
            ("می‌شود", "شد"),          # verbal prefix + conjugation
            # «شاقولی» is itself a headword in the data, so the negative form
            # reduces to the headword, not further to «شاقول».
            ("ناشاقولی", "شاقولی"),
            ("مشخصات", "مشخصه"),
            ("آجرهایمان", "آجر"),
            ("خاکبرداری", "خاکبرداری"),  # compound: kept whole, parts are separate
        ],
    )
    def test_roots(self, word, expected):
        assert root(word, LEXICON, PROTECTED) == expected

    def test_verb_family_is_reachable(self):
        assert root_family("می‌شود", LEXICON, PROTECTED) == "شدن"
        assert root_family("شود", LEXICON, PROTECTED) == "شدن"

    def test_conjugations_cover_both_stems(self):
        assert CONJUGATIONS["شود"][0] == "شدن"
        assert CONJUGATIONS["بند"][0] == "بستن"
        assert STEM_TO_VERB["بند"] == "بستن"

    def test_is_idempotent(self):
        for word in ("می‌شود", "بندی", "ناشاقولی"):
            once = root(word, LEXICON, PROTECTED)
            assert root(once, LEXICON, PROTECTED) == once


class TestCompoundSplitting:
    @pytest.mark.parametrize(
        "word,head",
        [
            ("آجرکاری", "آجر"),
            ("بندکشی", "بند"),
            ("خاکبرداری", "خاک"),
            ("نماسازی", "نما"),
            ("سنگفرش", "سنگ"),
            ("پشتبند", "پشت"),
            ("زیرسازی", "زیر"),
        ],
    )
    def test_real_compounds_split(self, word, head):
        parts = split_compound(word, LEXICON, PROTECTED)
        assert parts and parts[0] == head, f"{word} → {parts}"

    @pytest.mark.parametrize("word", ["تیرچه", "میلگرد", "سرگرد", "سیمان", "پلیت", "درباره"])
    def test_non_compounds_stay_whole(self, word):
        assert split_compound(word, LEXICON, PROTECTED) == []

    def test_half_spaced_and_unspaced_forms_both_resolve(self):
        # tokenize() splits the half-spaced form; split_compound() covers the
        # same word when a user types it without the half-space.
        assert "بتن" in tokenize("بتن‌ریزی")
        assert split_compound("بتنریزی", LEXICON, PROTECTED) == ["بتن", "ریزی"]
        assert split_compound("بتن‌ریزی", LEXICON, PROTECTED) == ["بتن", "ریزی"]


# --------------------------------------------------------------------------- #
# dataset invariants — these are what make the engine trustworthy
# --------------------------------------------------------------------------- #

class TestDatasetInvariants:
    def test_every_headword_is_a_fixpoint(self):
        """A dictionary headword must survive stemming untouched.

        Without this, «سیمان» would reduce to «سیم» + «ان» and «رومی» to «روم» +
        «ی», inventing root families that do not exist.
        """
        bad = []
        for record in RECORDS:
            for token in tokenize(record["term_fa"]):
                if fold(token) not in PROTECTED:
                    continue
                if root(token, LEXICON, PROTECTED) != token.replace(ZWNJ, ""):
                    bad.append((record["term_fa"], token, root(token, LEXICON, PROTECTED)))
        assert not bad, f"headwords reduced: {bad}"

    def test_broken_plural_map_is_minimal(self):
        """Only genuine reductions: no self-maps, no «ها» plurals."""
        for plural, singular in BROKEN_PLURALS.items():
            if plural == singular:
                # allowed once, and only when documented as its own lemma
                assert plural == "مصالح", f"{plural} maps to itself"
                continue
            assert not plural.endswith("ها"), f"{plural} is a regular plural"

    def test_index_forms_always_contains_the_folded_input(self):
        """Whatever the morphology does, a search for the term itself must hit."""
        for record in RECORDS:
            for field in ("term_fa", "definition_fa", "etymology_fa"):
                value = str(record.get(field) or "")
                if not value.strip():
                    continue
                forms = index_forms(value, LEXICON, PROTECTED)
                for token in tokenize(value):
                    assert fold(token) in forms, f"{field} of {record['id']}: {token}"

    def test_casefold_and_lower_agree_everywhere(self):
        """The JS mirror uses toLowerCase(); Python uses casefold().

        If the two ever disagreed on a character in the data or in the parity
        corpus, the browser and the build would index different keys. This test
        makes that impossible.
        """
        strings = []
        for record in RECORDS:
            strings.extend(str(v) for v in record.values() if isinstance(v, str))
            for field in ("synonyms", "search_aliases", "usage_examples"):
                strings.extend(str(v) for v in record.get(field) or [])
        for value in LEXICON | PROTECTED:
            strings.append(value)
        offenders = [s for s in strings if s.casefold() != s.lower()]
        assert not offenders, f"casefold != lower for: {offenders[:5]}"

    def test_derived_forms_land_on_the_headword_and_stop(self):
        """Regression: reduction used to continue *past* a headword.

        «سیمانی» must reach «سیمان» — and then stop. A second round took the
        headword down to «سیم» + «ان», which put a cementitious adjective into
        the wire family and invented a root that does not exist.
        """
        cases = {
            "سیمانی": "سیمان",
            "بتنی": "بتن",
            "آجری": "آجر",
            "میلگردهایمان": "میلگرد",
        }
        for word, expected in cases.items():
            assert stem(word, LEXICON, PROTECTED) == expected, word
            assert root(word, LEXICON, PROTECTED) == expected, word

    def test_no_headword_shares_a_family_with_an_unrelated_word(self):
        """The concrete false families this rule prevents."""
        from build_search_index import build_index

        index = build_index(RECORDS, load_meta(), LEXICON, PROTECTED)
        assert "siman" not in index["roots"].get("سیم", [])
        assert "semicircular-arch" not in index["roots"].get("روم", [])

    def test_lexicon_and_protected_sets_are_folded(self):
        for word in LEXICON | PROTECTED:
            assert fold(word) == word


# --------------------------------------------------------------------------- #
# fuzzy matching
# --------------------------------------------------------------------------- #

class TestSuggest:
    def test_one_edit_away_is_suggested(self):
        vocab = ["آجر", "بتن", "سیمان"]
        assert "آجر" in suggest("اجر", vocab, max_distance=1)

    def test_prefix_is_preferred_over_edit_distance(self):
        vocab = ["آجرکاری", "آجر"]
        suggestions = suggest("آجرکا", vocab, max_distance=2)
        assert suggestions and suggestions[0] == "آجرکاری"

    def test_no_suggestion_for_an_exact_hit(self):
        assert suggest("آجر", ["آجر"], max_distance=1) == []

    def test_empty_input_is_safe(self):
        assert suggest("", ["آجر"]) == []


# --------------------------------------------------------------------------- #
# orthography lint
# --------------------------------------------------------------------------- #

class TestOrthography:
    def test_arabic_letters_in_persian_text_are_flagged(self):
        assert orthography_warnings("حصاركشی")
        assert orthography_warnings("درابزين")

    def test_glued_verbal_prefix_with_a_space_is_flagged(self):
        assert orthography_warnings("می شود")
        assert orthography_warnings("نمی شود")

    def test_real_words_starting_with_mi_are_not_flagged(self):
        """Regression: «میلگرد» and «میزان» used to look like glued «می»."""
        assert not orthography_warnings("میلگرد و میزان")

    def test_plural_with_a_full_space_is_flagged(self):
        assert orthography_warnings("آجر ها")

    def test_legitimate_compounds_are_not_flagged(self):
        """Regression: «راهکار» and «شاهکار» used to look like glued «ها»."""
        assert not orthography_warnings("راهکار و شاهکار و پناهگاه")

    def test_persian_digits_are_house_style(self):
        assert not orthography_warnings("در دمای ۱۱۰ درجه")

    def test_arabic_indic_digits_are_flagged(self):
        assert orthography_warnings("در دمای ١١٠ درجه")

    def test_sparse_vowel_marks_are_scholarship_not_errors(self):
        """A dictionary marks pronunciation: «تاوَن»، «فارسی بُر»، «کاملاً»."""
        assert not orthography_warnings("تاوَن و فارسی بُر و کاملاً")

    def test_dense_vowel_marks_mean_pasted_arabic(self):
        assert orthography_warnings("اِصْتِکاکُ المُفْرِطِ")

    def test_etymology_fields_allow_full_vocalization(self):
        assert not orthography_warnings("اِصْتِکاکُ المُفْرِطِ", allow_diacritics=True)

    def test_foreign_script_allowed_when_quoting_an_equivalent(self):
        assert not orthography_warnings("«درابزين» معادل عربی است", allow_foreign_script=True)

    def test_double_space_and_edges_are_flagged(self):
        assert orthography_warnings("بتن  مسلح")
        assert orthography_warnings(" بتن")
