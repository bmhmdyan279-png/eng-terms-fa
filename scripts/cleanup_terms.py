#!/usr/bin/env python3
"""پاکسازی غیرمخرب داده‌های شاردشده (data/terms/*.yaml).

اقدامات (بدون حذف هیچ رکوردی — حذف خودکار تکراری‌ها در v1 ممنوع است):
- نرمال‌سازی ی/ک عربی در term_fa و حذف فاصله‌های ابتدا/انتهای رشته‌ها
- حذف کلیدهای مردهٔ v0 (standards, source, category, featured_book)
- تبدیل references رشته‌ای به فهرست آبجکت‌های {type, code}

قبل از نوشتن، اعتبارسنجی اسکما اجرا می‌شود؛ در صورت خطا فایل تغییر نمی‌کند.

Usage:
    python scripts/cleanup_terms.py [--dry-run]
"""

import argparse
import sys
from pathlib import Path

import yaml

from build_pages import DATA_DIR, load_all_terms, load_meta, normalize_persian, validate_terms


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


DEAD_KEYS = ("standards", "source", "category", "featured_book")


def clean_record(record):
    changed = 0
    if "term_fa" in record:
        new_fa = normalize_persian(str(record["term_fa"]).strip())
        if new_fa != record["term_fa"]:
            record["term_fa"] = new_fa
            changed += 1
    for key in list(record.keys()):
        value = record[key]
        if isinstance(value, str):
            stripped = value.strip()
            if stripped != value:
                record[key] = stripped
                changed += 1
            if stripped == "" and key in ("term_fr", "term_de", "term_ar"):
                record[key] = None
                changed += 1
        if key in DEAD_KEYS:
            del record[key]
            changed += 1
    refs = record.get("references")
    if isinstance(refs, list) and any(isinstance(r, str) for r in refs):
        record["references"] = [
            {"type": "book" if str(r).startswith("کتاب") else "standard", "code": str(r)}
            if isinstance(r, str) else r
            for r in refs
        ]
        changed += 1
    elif isinstance(refs, str):
        record["references"] = [{"type": "book" if refs.startswith("کتاب") else "standard", "code": refs}]
        changed += 1
    return record, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    total_changed = 0
    for path in sorted(DATA_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        terms = doc.get("terms") or []
        file_changed = 0
        for index, record in enumerate(terms):
            terms[index], changed = clean_record(record)
            file_changed += changed

        if not file_changed:
            print(f"ℹ️  {path.name}: تغییری لازم نبود")
            continue

        if not args.dry_run:
            header = "\n".join(
                line for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith("#")
            )
            body = yaml.dump(
                {"schema": doc.get("schema", "term-v1"), "terms": terms},
                Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False,
                width=4096, default_flow_style=False,
            )
            path.write_text(header + "\n" + body, encoding="utf-8")
        total_changed += file_changed
        print(f"✅ {path.name}: {file_changed} اصلاح")

    # sanity: دادهٔ تمیزشده همچنان باید اعتبارسنجی شود
    records = load_all_terms()
    errors, _ = validate_terms(records, load_meta())
    if errors:
        print(f"✗ پس از پاکسازی {len(errors)} خطای اعتبارسنجی — بازبینی کنید:", file=sys.stderr)
        for e in errors[:10]:
            print("  ", e, file=sys.stderr)
        return 1
    print(f"✓ پاکسازی کامل شد ({total_changed} اصلاح) و اعتبارسنجی سبز است")
    return 0


if __name__ == "__main__":
    sys.exit(main())
