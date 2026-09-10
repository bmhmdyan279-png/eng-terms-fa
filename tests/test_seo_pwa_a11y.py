import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from build_pages import render_jsonld
from mkdocs_hooks import write_sitemap

REPO = Path(__file__).parent.parent


def _luminance(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [(c / 12.92) if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(fg, bg):
    l1, l2 = _luminance(fg), _luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def test_jsonld_defined_term_structure():
    record = {
        "term_fa": "بتن",
        "term_en": "concrete",
        "slug": "beton",
        "definition_fa": "مصالح ساختمانی مرکب از سیمان، آب و سنگدانه.",
    }
    block = render_jsonld(record)
    assert block.startswith('<script type="application/ld+json">')
    payload = json.loads(block.split('\n', 1)[1].rsplit('\n', 2)[0])
    assert payload["@context"] == "https://schema.org"
    assert payload["@type"] == "DefinedTerm"
    assert payload["name"] == "بتن"
    assert payload["alternateName"] == "concrete"
    assert payload["inLanguage"] == ["fa", "en"]
    assert payload["inDefinedTermSet"]["@type"] == "DefinedTermSet"
    assert payload["description"] == record["definition_fa"]


def test_jsonld_never_contains_closing_script_tag():
    record = {"term_fa": "x", "term_en": "y", "slug": "z", "definition_fa": "</script> injection"}
    assert "</script>" not in render_jsonld(record).split("ld+json\">", 1)[1].rsplit("</script>", 1)[0]


def test_pwa_manifest_is_valid():
    manifest = json.loads((REPO / "docs" / "manifest.webmanifest").read_text(encoding="utf-8"))
    for key in ("name", "short_name", "theme_color", "background_color", "display", "start_url"):
        assert manifest.get(key), key
    assert manifest["display"] == "standalone"
    sizes = {icon["sizes"] for icon in manifest["icons"]}
    assert "192x192" in sizes and "512x512" in sizes
    purposes = {icon.get("purpose") for icon in manifest["icons"]}
    assert "maskable" in purposes
    for icon in manifest["icons"]:
        assert (REPO / "docs" / icon["src"]).exists(), icon["src"]


def test_service_worker_is_cache_first():
    sw = (REPO / "docs" / "sw.js").read_text(encoding="utf-8")
    assert "caches.match" in sw
    assert "install" in sw and "activate" in sw and "fetch" in sw


def test_robots_points_to_sitemap():
    robots = (REPO / "docs" / "robots.txt").read_text(encoding="utf-8")
    assert "User-agent: *" in robots
    assert "sitemap.xml" in robots


def test_sitemap_has_lastmod_and_changefreq(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    terms = tmp_path / "terms"
    terms.mkdir()
    (terms / "index.html").write_text("<html></html>", encoding="utf-8")
    (terms / "beton").mkdir()
    (terms / "beton" / "index.html").write_text("<html></html>", encoding="utf-8")

    sitemap = write_sitemap(tmp_path, "https://example.org/")
    content = sitemap.read_text(encoding="utf-8")
    assert content.count("<url>") == 3
    assert "<lastmod>" in content and "<changefreq>" in content and "<priority>" in content
    assert "https://example.org/terms/beton/" in content
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    assert today in content


def test_status_badge_contrast_meets_wcag_aa():
    # (fg, effective bg) pairs mirrored from docs/assets/css/extra.css
    pairs = [
        ("#664d00", "#ffffff"),  # draft, light
        ("#1b5e20", "#ffffff"),  # reviewed, light
        ("#0d47a1", "#ffffff"),  # published, light
        ("#ffd75e", "#1e1e1e"),  # draft, dark
        ("#81c784", "#1e1e1e"),  # reviewed, dark
        ("#64b5f6", "#1e1e1e"),  # published, dark
        # جستجوی ریشه‌محور (.ps-badge-*) از همان پالت استفاده می‌کند
        ("#37474f", "#ffffff"),  # near-miss, light
        ("#cfd8dc", "#1e1e1e"),  # near-miss, dark
    ]
    for fg, bg in pairs:
        ratio = _contrast(fg, bg)
        assert ratio >= 4.5, f"{fg} on {bg} = {ratio:.2f} (< 4.5:1)"
