"""Sanity checks on the repository's own configuration files.

These are cheap tests for expensive mistakes: a malformed Issue-template YAML
silently disables the form on GitHub, a broken workflow means CI never runs, and
a stale `not_in_nav` turns into a build warning that `--strict` escalates to an
error. One of these actually happened while adding the expert-review template
(an unquoted «review_level: expert» in `name:` broke YAML parsing).
"""

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

WORKFLOWS = sorted((REPO / ".github" / "workflows").glob("*.yml"))
TEMPLATES = sorted((REPO / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))


class TestYamlConfig:
    @pytest.mark.parametrize("path", WORKFLOWS + TEMPLATES + [
        REPO / ".pre-commit-config.yaml",
        REPO / "data" / "standards.yaml",
        REPO / "data" / "terms" / "_meta.yaml",
        *sorted((REPO / "data" / "terms").glob("*.yaml")),
    ], ids=lambda p: p.name)
    def test_parses(self, path):
        assert path.exists(), path
        yaml.unsafe_load(path.read_text(encoding="utf-8"))

    def test_mkdocs_config_parses(self):
        """mkdocs.yml uses Material's !!python/name tags, so it needs the unsafe loader."""
        config = yaml.unsafe_load((REPO / "mkdocs.yml").read_text(encoding="utf-8"))
        assert config["theme"]["language"] == "fa"
        assert config["theme"]["direction"] == "rtl"

    def test_every_nav_entry_exists(self):
        config = yaml.unsafe_load((REPO / "mkdocs.yml").read_text(encoding="utf-8"))
        docs = REPO / "docs"
        for item in config["nav"]:
            for title, target in item.items():
                assert (docs / target).exists(), f"nav «{title}» → missing {target}"

    def test_generated_and_data_paths_are_out_of_nav(self):
        config = yaml.unsafe_load((REPO / "mkdocs.yml").read_text(encoding="utf-8"))
        not_in_nav = config.get("not_in_nav", "")
        assert "terms/*.md" in not_in_nav
        assert "data/open/README.md" in not_in_nav

    def test_search_scripts_are_loaded_in_dependency_order(self):
        """The stemmer must load before the UI that uses it."""
        config = yaml.unsafe_load((REPO / "mkdocs.yml").read_text(encoding="utf-8"))
        scripts = config["extra_javascript"]
        order = [s for s in scripts if "persian" in s]
        assert order == [
            "assets/js/persian-stem-data.js",
            "assets/js/persian-stem.js",
            "assets/js/persian-search.js",
        ]
        for script in scripts:
            assert (REPO / "docs" / script).exists(), f"missing {script}"


class TestIssueTemplates:
    def test_expert_review_template_exists_and_is_honest(self):
        """The roadmap's next step is human sign-off; there must be a way to ask for it."""
        path = REPO / ".github" / "ISSUE_TEMPLATE" / "expert-review.yml"
        assert path.exists()
        body = path.read_text(encoding="utf-8")
        data = yaml.unsafe_load(body)
        ids = {field.get("id") for field in data["body"] if isinstance(field, dict)}
        assert {"slug", "verdict", "credential", "correction"} <= ids
        # the template must tell contributors that anonymity keeps the entry ai-assisted
        assert "ai-assisted" in body

    def test_term_suggestion_asks_for_search_aliases(self):
        body = (REPO / ".github" / "ISSUE_TEMPLATE" / "term-suggestion.yml").read_text(encoding="utf-8")
        data = yaml.unsafe_load(body)
        ids = {field.get("id") for field in data["body"] if isinstance(field, dict)}
        assert "synonyms" in ids and "source" in ids


class TestJsonConfig:
    def test_schema_is_valid_draft_2020_12(self):
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO / "schemas" / "term-v1.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)

    def test_schema_forbids_fake_human_sign_off(self):
        """`published` without an expert/committee review level must not validate."""
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO / "schemas" / "term-v1.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        record = {
            "id": "x", "slug": "x", "term_fa": "واژه", "term_en": "term",
            "pos": "noun", "domain": ["construction"],
            "definition_fa": "تعریفی که به اندازهٔ کافی بلند باشد.",
            "status": "published", "review_level": "ai-assisted",
        }
        assert not validator.is_valid(record)
        record["review_level"] = "expert"
        assert validator.is_valid(record)

    def test_schema_is_additive_for_rev1_records(self):
        """A rev.1 record (no etymology, no review level) must still validate."""
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO / "schemas" / "term-v1.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        legacy = {
            "id": "legacy", "slug": "legacy", "term_fa": "واژه", "term_en": "term",
            "pos": "noun", "domain": ["construction"], "definition_fa": "تعریف",
            "status": "draft",
        }
        assert validator.is_valid(legacy)

    def test_manifest_is_valid_json(self):
        manifest = json.loads((REPO / "docs" / "manifest.webmanifest").read_text(encoding="utf-8"))
        assert manifest["name"]
