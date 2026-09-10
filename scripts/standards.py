#!/usr/bin/env python3
"""Loader for the source registry (data/standards.yaml).

Records store only ``{type, code, note, section, edition}``; everything else
(issuing body, full title, URL, scope) is resolved here. Two consequences:

* the data files stay small and cannot contradict the registry,
* a citation that is not in the registry is a hard error
  (``scripts/validate_content.py``), so fabricated sources cannot ship.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_FILE = ROOT / "data" / "standards.yaml"

_cache: dict | None = None


def load_registry(path: Path | None = None) -> dict:
    """code → registry entry (cached)."""
    global _cache
    if _cache is not None and path is None:
        return _cache
    target = path or REGISTRY_FILE
    if not target.exists():
        raise FileNotFoundError(f"source registry not found: {target}")
    doc = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    sources = doc.get("sources") or []
    registry = {}
    for entry in sources:
        if not isinstance(entry, dict) or not entry.get("code"):
            continue
        registry[str(entry["code"]).strip()] = entry
    if path is None:
        _cache = registry
    return registry


def registry_codes(path: Path | None = None) -> set[str]:
    return set(load_registry(path))


def resolve(code: str) -> dict | None:
    """Registry entry for a reference code, or None when unknown."""
    return load_registry().get(str(code or "").strip())


def org_of(code: str) -> str | None:
    entry = resolve(code)
    return (entry or {}).get("org")


def title_of(code: str) -> str | None:
    entry = resolve(code)
    return (entry or {}).get("title")


def url_of(code: str) -> str | None:
    entry = resolve(code)
    return (entry or {}).get("url")


if __name__ == "__main__":  # pragma: no cover
    registry = load_registry()
    by_type: dict[str, int] = {}
    for entry in registry.values():
        by_type[entry.get("type", "?")] = by_type.get(entry.get("type", "?"), 0) + 1
    print(f"registry: {len(registry)} sources — {by_type}")
    unconfirmed = [c for c, e in registry.items() if e.get("verification") != "confirmed"]
    print(f"not independently confirmed: {unconfirmed}")
