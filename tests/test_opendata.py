"""Tests for the Open Data bundle (scripts/generate_opendata.py).

The claim on the docs page is: *the whole dictionary is published in
interoperable, machine-actionable formats*. These tests make that claim
checkable instead of decorative:

* NDJSON streams, one record per line, with the required fields
* the Turtle parses as RDF and forms a coherent SKOS graph (every concept has
  a prefLabel and a scheme, no dangling ``skos:related``, domains in their own
  scheme so they can never be mistaken for terms)
* the JSON-LD parses and carries a Dataset + DefinedTermSet + one DefinedTerm
  per entry + a DataDownload per bundle file
* ``datapackage.json`` describes exactly the CSV that ships next to it
* the bundle README cites every source the data actually uses

rdflib is a dev dependency (requirements-dev.txt). Without it the RDF checks
skip rather than silently pass — CI always installs it.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from build_pages import load_all_terms  # noqa: E402
from generate_opendata import (  # noqa: E402
    CSV_FIELDS,
    DATASET_IRI,
    DOMAIN_SCHEME_IRI,
    SCHEME_IRI,
    concept_iri,
    datapackage,
    dataset_jsonld,
    domain_iri,
    generate,
    open_record,
    ttl_literal,
)
from standards import load_registry  # noqa: E402

try:
    from rdflib import Graph, Namespace, RDF, URIRef

    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    DCT = Namespace("http://purl.org/dc/terms/")
    SCHEMA = Namespace("https://schema.org/")
    HAS_RDFLIB = True
except ImportError:  # pragma: no cover
    HAS_RDFLIB = False

RECORDS = [record for _, record in load_all_terms()]
REGISTRY = load_registry()


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    """Generate a fresh bundle once per module (never trust a stale artefact)."""
    out = tmp_path_factory.mktemp("open")
    result = generate(out)
    return out, result


# --------------------------------------------------------------------------- #
# NDJSON
# --------------------------------------------------------------------------- #

class TestNdjson:
    def test_one_json_object_per_line(self, bundle):
        out, result = bundle
        lines = (out / "terms.ndjson").read_text(encoding="utf-8").splitlines()
        assert len(lines) == result["records"] == len(RECORDS)
        for line in lines:
            json.loads(line)  # must not raise

    def test_required_fields_present_in_every_line(self, bundle):
        out, _ = bundle
        for line in (out / "terms.ndjson").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            for key in ("id", "slug", "term_fa", "term_en", "definition_fa", "status", "url"):
                assert record.get(key), f"{record.get('id')} lacks {key}"
            assert record["url"].endswith(f"/terms/{record['slug']}/")

    def test_review_metadata_is_honest(self, bundle):
        out, _ = bundle
        for line in (out / "terms.ndjson").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("status") == "reviewed":
                assert record.get("reviewed_by"), record["id"]
                assert record.get("reviewed_at"), record["id"]
                assert record.get("review_level") in ("ai-assisted", "expert", "committee")
            if record.get("status") == "published":
                assert record.get("review_level") in ("expert", "committee")

    def test_every_cited_source_resolves_in_the_registry(self, bundle):
        out, _ = bundle
        for line in (out / "terms.ndjson").read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            for ref in record.get("references") or []:
                assert ref["code"] in REGISTRY, f"{record['id']}: unknown source {ref['code']}"
                assert ref.get("note"), f"{record['id']}: citation without a note"
                assert ref.get("org"), f"{record['id']}: citation without an issuing body"


# --------------------------------------------------------------------------- #
# CSV + datapackage
# --------------------------------------------------------------------------- #

class TestCsvAndDatapackage:
    def test_csv_header_matches_the_descriptor(self, bundle):
        out, _ = bundle
        header = (out / "terms.csv").read_text(encoding="utf-8-sig").splitlines()[0]
        assert header.split(",") == CSV_FIELDS

    def test_csv_has_one_row_per_term(self, bundle):
        out, result = bundle
        with open(out / "terms.csv", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) == result["records"]
        assert len({row["id"] for row in rows}) == len(rows)

    def test_datapackage_describes_the_shipped_resources(self, bundle):
        out, _ = bundle
        package = json.loads((out / "datapackage.json").read_text(encoding="utf-8"))
        assert package["name"] == "persian-engineering-terminology"
        assert package["licenses"][0]["name"] == "CC-BY-SA-4.0"
        assert package["stats"]["term_count"] == len(RECORDS)
        for resource in package["resources"]:
            assert (out / resource["path"]).exists(), f"declared but missing: {resource['path']}"
        described = {f["name"] for f in package["resources"][0]["schema"]["fields"]}
        assert described == set(CSV_FIELDS)

    def test_datapackage_declares_the_ai_assisted_contributor(self):
        """The descriptor must not imply a human review that never happened."""
        package = datapackage([open_record(r, REGISTRY) for r in RECORDS])
        contributors = " ".join(str(c) for c in package["contributors"])
        assert "AI-assisted" in contributors or "ai-assisted" in contributors

    def test_open_record_drops_empty_optional_fields(self):
        record = open_record({"id": "x", "slug": "x", "term_fa": "واژه",
                              "term_en": "term", "definition_fa": "تعریف",
                              "domain": [], "references": []}, REGISTRY)
        assert "root_fa" not in record
        assert "term_fr" not in record
        assert record["id"] == "x"


# --------------------------------------------------------------------------- #
# RDF (SKOS) — parsed, not eyeballed
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def skos_graph(bundle):
    if not HAS_RDFLIB:
        pytest.skip("rdflib not installed (requirements-dev.txt)")
    out, _ = bundle
    graph = Graph()
    graph.parse(out / "terms.ttl", format="turtle")
    return graph


@pytest.fixture(scope="module")
def jsonld_graph(bundle):
    if not HAS_RDFLIB:
        pytest.skip("rdflib not installed (requirements-dev.txt)")
    out, _ = bundle
    payload = json.loads((out / "terms.jsonld").read_text(encoding="utf-8"))
    graph = Graph()
    graph.parse(data=json.dumps(payload), format="json-ld")
    return graph


@pytest.mark.skipif(not HAS_RDFLIB, reason="rdflib not installed (requirements-dev.txt)")
class TestTurtle:
    def test_parses_and_has_two_schemes(self, skos_graph):
        schemes = {str(x) for x in skos_graph.subjects(RDF.type, SKOS.ConceptScheme)}
        assert schemes == {SCHEME_IRI, DOMAIN_SCHEME_IRI}, "terms + domains must be separate schemes"

    def test_one_concept_per_term_plus_one_per_domain(self, skos_graph):
        from build_pages import load_meta

        meta = load_meta()
        concepts = set(skos_graph.subjects(RDF.type, SKOS.Concept))
        assert len(concepts) == len(RECORDS) + len(meta["domains"])

    def test_every_term_concept_has_a_preflabel_and_a_scheme(self, skos_graph):
        for record in RECORDS:
            iri = URIRef(concept_iri(record["slug"]))
            assert list(skos_graph.objects(iri, SKOS.prefLabel)), record["slug"]
            assert SCHEME_IRI in {str(x) for x in skos_graph.objects(iri, SKOS.inScheme)}

    def test_domain_concepts_live_in_their_own_scheme(self, skos_graph):
        from build_pages import load_meta

        for domain in load_meta()["domains"]:
            iri = URIRef(domain_iri(domain["id"]))
            schemes = {str(x) for x in skos_graph.objects(iri, SKOS.inScheme)}
            assert DOMAIN_SCHEME_IRI in schemes, f"{domain['id']} not in the domain scheme"
            assert SCHEME_IRI not in schemes, "a domain must never look like a term"

    def test_no_dangling_related_links(self, skos_graph):
        concepts = set(skos_graph.subjects(RDF.type, SKOS.Concept))
        for subject, obj in skos_graph.subject_objects(SKOS.related):
            assert obj in concepts, f"dangling skos:related → {obj}"

    def test_related_links_are_mutual_in_the_graph(self, skos_graph):
        pairs = {(str(s), str(o)) for s, o in skos_graph.subject_objects(SKOS.related)}
        assert pairs == {(o, s) for s, o in pairs}, "skos:related must be symmetric"

    def test_definitions_and_etymologies_are_language_tagged(self, skos_graph):
        definitions = list(skos_graph.objects(None, SKOS.definition))
        assert len(definitions) == len(RECORDS)
        assert all(str(literal.language) == "fa" for literal in definitions)
        history = list(skos_graph.objects(None, SKOS.historyNote))
        assert history, "etymology must reach the graph as skos:historyNote"

    def test_multilingual_labels_carry_their_language(self, skos_graph):
        tags = {str(literal.language) for literal in skos_graph.objects(None, SKOS.altLabel)}
        assert {"en", "fr", "de", "ar", "fa"} <= tags

    def test_citations_are_present(self, skos_graph):
        citations = list(skos_graph.objects(None, DCT.bibliographicCitation))
        assert len(citations) >= len(RECORDS)

    def test_review_status_is_machine_readable(self, skos_graph):
        statuses = {str(literal) for literal in skos_graph.objects(None, SCHEMA.creativeWorkStatus)}
        assert statuses <= {"draft", "reviewed", "published"}
        assert "reviewed" in statuses


class TestTurtleEscaping:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ('has "quotes"', '"""has \\"quotes\\""""'),
            ("line\nbreak", '"""line\\nbreak"""'),
            ("back\\slash", '"""back\\\\slash"""'),
        ],
    )
    def test_literals_are_escaped(self, text, expected):
        assert ttl_literal(text).startswith(expected)

    def test_language_tag_is_appended(self):
        assert ttl_literal("بتن", "fa").endswith('@fa')


# --------------------------------------------------------------------------- #
# JSON-LD
# --------------------------------------------------------------------------- #

@pytest.mark.skipif(not HAS_RDFLIB, reason="rdflib not installed (requirements-dev.txt)")
class TestJsonLd:
    def test_dataset_and_termset_are_declared(self, jsonld_graph):
        assert list(jsonld_graph.subjects(RDF.type, SCHEMA.Dataset))
        assert list(jsonld_graph.subjects(RDF.type, SCHEMA.DefinedTermSet))

    def test_one_defined_term_per_entry(self, jsonld_graph):
        terms = set(jsonld_graph.subjects(RDF.type, SCHEMA.DefinedTerm))
        assert len(terms) == len(RECORDS)

    def test_every_bundle_file_is_a_download(self, jsonld_graph):
        downloads = set(jsonld_graph.objects(None, SCHEMA.contentUrl))
        assert len(downloads) == 5
        assert any(str(url).endswith("terms.ttl") for url in downloads)
        assert any(str(url).endswith("terms.ndjson") for url in downloads)

    def test_license_and_version_are_declared(self, jsonld_graph):
        licenses = {str(x) for x in jsonld_graph.objects(None, SCHEMA.license)}
        assert any("creativecommons.org/licenses/by-sa/4.0" in url for url in licenses)
        versions = {str(x) for x in jsonld_graph.objects(None, SCHEMA.version)}
        assert versions, "the dataset must declare a version"

    def test_context_uses_the_full_schema_vocabulary(self):
        """A bare prefix context silently drops every un-prefixed property."""
        from build_pages import load_meta

        payload = dataset_jsonld([open_record(r, REGISTRY) for r in RECORDS], load_meta())
        assert payload["@context"].get("@vocab") == "https://schema.org/"
        assert payload["@graph"][0]["@id"] == DATASET_IRI


# --------------------------------------------------------------------------- #
# bundle README
# --------------------------------------------------------------------------- #

class TestBundleReadme:
    def test_readme_lists_every_cited_source(self, bundle):
        out, _ = bundle
        readme = (out / "README.md").read_text(encoding="utf-8")
        cited = {
            str(ref.get("code"))
            for record in RECORDS
            for ref in (record.get("references") or [])
            if isinstance(ref, dict) and ref.get("code")
        }
        missing = sorted(code for code in cited if code not in readme)
        assert not missing, f"README does not document: {missing}"

    def test_readme_states_the_review_status_honestly(self, bundle):
        out, _ = bundle
        readme = (out / "README.md").read_text(encoding="utf-8")
        assert "ai-assisted" in readme
        assert "تأیید متخصص انسانی" in readme
        assert "CC BY-SA 4.0" in readme
