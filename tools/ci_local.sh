#!/usr/bin/env bash
# اجرای محلیِ همهٔ دروازه‌های CI، به همان ترتیب.
#
#   bash tools/ci_local.sh           # همهٔ گام‌ها
#   bash tools/ci_local.sh --fast    # بدون بیلد سایت و Lighthouse
#
# اگر این اسکریپت سبز باشد، CI هم سبز خواهد بود (به‌جز Lighthouse که به
# مرورگر بی‌سر نیاز دارد).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY="${PYTHON:-python3}"
[ -x ".venv/bin/python" ] && PY=".venv/bin/python"

FAST=0
[ "${1:-}" = "--fast" ] && FAST=1

step() { printf '\n\033[1;36m▶ %s\033[0m\n' "$1"; }
ok()   { printf '\033[1;32m  ✓ %s\033[0m\n' "$1"; }

step "۱) دروازه‌های داده و محتوا"
$PY scripts/validate_data.py
$PY scripts/validate_content.py
$PY scripts/audit_translations.py --strict
ok "داده، محتوا و ترجمه‌ها"

step "۲) تولید مصنوعات از داده‌ها"
$PY scripts/build_pages.py
$PY scripts/generate_stem_data.py
$PY scripts/build_search_index.py
$PY scripts/generate_api.py
$PY scripts/generate_opendata.py
ok "مصنوعات"

step "۳) آزمون‌ها"
$PY -m pytest tests/ -q
ok "آزمون‌ها"

step "۴) توازی موتور ریشه‌یابی (پایتون ⇄ جاوااسکریپت)"
if command -v node >/dev/null 2>&1; then
  node tools/check_stemmer_parity.js
else
  echo "  ⚠ node پیدا نشد — گام توازی رد شد"
fi

step "۵) تازگی مصنوعات تولیدشده (همان git diffهای CI)"
git diff --exit-code \
  docs/construction-terms.md docs/book-vocab.md \
  docs/assets/js/persian-stem-data.js \
  tests/fixtures/stemming-golden.json \
  translation_alerts.csv translation_gaps.csv
ok "هیچ مصنوعی کهنه نیست"

if [ "$FAST" = "1" ]; then
  printf '\n\033[1;32m✅ ci_local (--fast) سبز است\033[0m\n'
  exit 0
fi

step "۶) بیلد سخت‌گیرانهٔ سایت"
$PY -m mkdocs build --strict
for required in site/data/api/search-index.json site/data/open/terms.ttl \
                site/data/open/terms.ndjson site/data/open/datapackage.json; do
  test -s "$required" || { echo "  ✗ $required ساخته نشد"; exit 1; }
done
ok "سایت و بستهٔ داده در site/ حاضرند"

printf '\n\033[1;32m✅ ci_local سبز است\033[0m\n'
printf '   باقی‌مانده فقط در CI: Pagefind، Lighthouse و pre-commit\n'
