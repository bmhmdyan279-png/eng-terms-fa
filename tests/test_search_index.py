"""Tests for the generated search index and the stemmer parity artefacts.

The search contract these tests lock down:

* a query for a headword always finds that headword (whatever the morphology did),
* a query for a synonym or a search alias finds the entry too,
* the half-space, the full space and the joined spelling behave identically,
* root families are real (every slug in ``roots`` exists),
* the JS data module is byte-fresh against the Python tables, and
* the golden fixture is byte-fresh against the current engine output.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from build_pages import load_all_terms, load_meta  # noqa: E402
from build_search_index import (  # noqa: E402
    ALGORITHM,
    FIELDS,
    GOLDEN_CORPUS,
    INDEX_VERSION,
    build_fixture,
    build_index,
)
from persian_text import build_lexicon, build_protected, fold  # noqa: E402

RECORDS = [record for _, record in load_all_terms()]
LEXICON = build_lexicon(RECORDS)
PROTECTED = build_protected(RECORDS)
INDEX = build_index(RECORDS, load_meta(), LEXICON, PROTECTED)
BY_SLUG = {entry["s"]: entry for entry in INDEX["terms"]}


# --------------------------------------------------------------------------- #
# index shape
# --------------------------------------------------------------------------- #

class TestIndexShape:
    def test_header_metadata(self):
        assert INDEX["version"] == INDEX_VERSION
        assert INDEX["algorithm"] == ALGORITHM
        assert INDEX["count"] == len(RECORDS) == len(INDEX["terms"])
        assert INDEX["generated_at"].endswith("Z")

    def test_every_field_has_a_boost(self):
        assert set(INDEX["fields"]) == set(FIELDS)
        for key, boost in INDEX["fields"].items():
            assert boost > 0, key
        # the headword must outweigh prose, or ranking is meaningless
        assert INDEX["fields"]["t"] > INDEX["fields"]["d"]
        assert INDEX["fields"]["a"] > INDEX["fields"]["d"]

    def test_every_entry_has_the_required_keys(self):
        for entry in INDEX["terms"]:
            for key in ("s", "fa", "en", "dom", "st", "r", "f"):
                assert key in entry, f"{entry.get('s')} lacks {key}"
            assert entry["s"] in {r["slug"] for r in RECORDS}
            assert set(entry["f"]) <= set(FIELDS)

    def test_lexicon_and_protected_are_shipped_for_the_browser(self):
        assert INDEX["lexicon_size"] == len(INDEX["lexicon"]) == len(LEXICON)
        assert set(INDEX["protected"]) == set(PROTECTED)
        # the browser stemmer needs folded keys — the client compares fold()
        for word in INDEX["lexicon"] + INDEX["protected"]:
            assert fold(word) == word

    def test_prose_definitions_are_not_indexed_as_one_form(self):
        """A whole sentence as a single "form" would bloat the index forever."""
        for entry in INDEX["terms"]:
            for form in entry["f"].get("d", []):
                assert len(form) <= 40, f"{entry['s']}: sentence-sized form indexed"

    def test_headword_fields_keep_the_compact_full_form(self):
        entry = BY_SLUG["sealing"]
        assert "آب بندی" in entry["f"]["t"]
        assert "آببندی" in entry["f"]["t"]  # space-free variant


# --------------------------------------------------------------------------- #
# the search contract
# --------------------------------------------------------------------------- #

def _forms_of(slug, field="t"):
    return BY_SLUG[slug]["f"].get(field, [])


class TestSearchContract:
    @pytest.mark.parametrize("record", RECORDS, ids=lambda r: r["slug"])
    def test_headword_is_always_findable_by_itself(self, record):
        """fold(term_fa) and every token of it must be in the headword field."""
        forms = _forms_of(record["slug"])
        folded_full = fold(record["term_fa"])
        assert folded_full in forms or folded_full.replace(" ", "") in forms
        for token in record["term_fa"].replace("\u200c", " ").split():
            if len(token) >= 2:
                assert fold(token) in forms or any(
                    f.startswith(fold(token)) for f in forms
                ), f"{record['slug']}: token {token} not indexed"

    @pytest.mark.parametrize("record", RECORDS, ids=lambda r: r["slug"])
    def test_synonyms_and_aliases_are_indexed(self, record):
        expected = list(record.get("synonyms") or []) + list(record.get("search_aliases") or [])
        if not expected:
            pytest.skip("no synonyms or aliases")
        forms = set(_forms_of(record["slug"], "a"))
        for value in expected:
            assert fold(value) in forms, f"{record['slug']}: {value} missing from aliases"

    def test_multilingual_columns_are_searchable(self):
        assert "rebar" in _forms_of("armator", "e")
        assert "sealing" in _forms_of("sealing", "e")
        assert "étanchéité" in _forms_of("sealing", "e")

    def test_half_space_and_space_queries_are_equivalent(self):
        """«آب‌بندی»، «آب بندی» and «آببندی» must hit the same entry."""
        for query in ("آب بندی", "آببندی", "آب‌بندی".replace("\u200c", ""), "آب‌بندی"):
            folded = fold(query)
            assert any(folded == f or folded.replace(" ", "") == f for f in _forms_of("sealing"))

    def test_root_families_are_real(self):
        slugs = {r["slug"] for r in RECORDS}
        for root_value, members in INDEX["roots"].items():
            assert len(root_value) >= 2
            for slug in members:
                assert slug in slugs, f"root {root_value} points at unknown slug {slug}"
            assert len(members) == len(set(members))

    def test_known_root_family_groups_the_brick_terms(self):
        family = set(INDEX["roots"].get("آجر", []))
        assert {"square-brick", "corner-brick", "header-brick", "broken-brick"} <= family

    def test_known_root_family_groups_the_band_terms(self):
        """«بند» must gather آب‌بندی، بند آجر، بند کلوکی، پشت بند و سیم آرماتوربندی."""
        family = set(INDEX["roots"].get("بند", []))
        assert {"sealing", "brick-block", "clavicle-strap", "back-strap"} <= family

    def test_loanwords_are_not_split_into_false_families(self):
        """Regression: «سیمان» used to join the «سیم» family, «رومی» the «روم» one."""
        assert "siman" not in INDEX["roots"].get("سیم", [])
        assert "siman" in INDEX["roots"].get("سیمان", [])
        assert "semicircular-arch" not in INDEX["roots"].get("روم", [])
        assert "semicircular-arch" in INDEX["roots"].get("رومی", [])

    def test_site_jargon_aliases_resolve(self):
        """«ویبره» is what people type; the headword is «لرزاننده»."""
        assert "ویبره" in _forms_of("vibrator", "a")
        assert "کالیبراسیون" in _forms_of("calibration", "a")
        assert "میلگرد" in _forms_of("armator", "a")


# --------------------------------------------------------------------------- #
# freshness of the committed artefacts
# --------------------------------------------------------------------------- #

class TestGeneratedArtefactsAreFresh:
    def test_committed_fixture_matches_the_engine(self):
        path = REPO / "tests" / "fixtures" / "stemming-golden.json"
        assert path.exists(), "run: python scripts/build_search_index.py"
        committed = json.loads(path.read_text(encoding="utf-8"))
        fresh = build_fixture(RECORDS, LEXICON, PROTECTED)
        assert committed["algorithm"] == fresh["algorithm"]
        assert [c["input"] for c in committed["cases"]] == [c["input"] for c in fresh["cases"]]
        for old, new in zip(committed["cases"], fresh["cases"]):
            for key in ("normalize", "fold", "tokenize", "content_tokens", "stem", "root", "forms"):
                assert old[key] == new[key], f"fixture drifted on {old['input']!r}.{key}"

    def test_fixture_covers_every_morphological_rule(self):
        corpus = " ".join(GOLDEN_CORPUS)
        assert "\u200c" in corpus, "no half-space case"
        assert "ها" in corpus, "no plural case"
        assert "مشخصات" in corpus, "no broken-plural case"
        assert "می‌شود" in corpus, "no verbal-prefix case"
        assert "آجرکاری" in corpus, "no compound-split case"
        assert any(c.isascii() for c in corpus), "no Latin case"

    def test_committed_stem_data_matches_the_python_tables(self):
        """docs/assets/js/persian-stem-data.js must not drift from Python.

        The file is generated, committed and checked here — the browser stemmer
        reads its affix tables from this file, so drift would silently change
        search behaviour without any Python test noticing.
        """
        import generate_stem_data

        path = REPO / "docs" / "assets" / "js" / "persian-stem-data.js"
        assert path.exists(), "run: python scripts/generate_stem_data.py"
        committed = path.read_text(encoding="utf-8")
        assert generate_stem_data.render() == committed, (
            "persian-stem-data.js is stale — run: python scripts/generate_stem_data.py"
        )

    def test_index_build_is_deterministic(self):
        """Same data in ⇒ byte-identical index out (except the timestamp).

        `docs/data/` is generated and git-ignored, so there is nothing to diff
        against; what matters is that two runs never disagree, because the
        browser index and the pages must describe the same morphology.
        """
        first = build_index(RECORDS, load_meta(), LEXICON, PROTECTED)
        second = build_index(RECORDS, load_meta(), LEXICON, PROTECTED)
        first.pop("generated_at")
        second.pop("generated_at")
        assert first == second

    def test_fixture_is_reproducible_byte_for_byte(self):
        import json as _json

        a = build_fixture(RECORDS, LEXICON, PROTECTED)
        b = build_fixture(RECORDS, LEXICON, PROTECTED)
        assert _json.dumps(a, ensure_ascii=False, sort_keys=True) == \
               _json.dumps(b, ensure_ascii=False, sort_keys=True)
