# 📦 دادهٔ باز و API

همهٔ محتوای این فرهنگ تحت مجوز **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**
و همهٔ کدها تحت مجوز **MIT** منتشر می‌شود. این صفحه فهرست کامل قالب‌های
ماشین‌خوان، نحوهٔ بارگذاری و شیوهٔ استناد را توضیح می‌دهد.

!!! important "داده از یک منبع حقیقت تولید می‌شود"
    هیچ‌یک از فایل‌های زیر دستی نوشته نمی‌شوند. همه از `data/terms/*.yaml`
    (واژه‌ها) و `data/standards.yaml` (منابع) در هر بیلد CI تولید می‌شوند، پس
    هرگز با هم ناهمخوان نمی‌شوند.

## بستهٔ دادهٔ باز { #bundle }

| فایل | قالب | اندازهٔ تقریبی | کاربرد |
|---|---|---|---|
| [`data/open/terms.ndjson`](data/open/terms.ndjson) | NDJSON | ~۳۰۰ کیلوبایت | بارگذاری خط‌به‌خط در پایپ‌لاین داده |
| [`data/open/terms.jsonld`](data/open/terms.jsonld) | JSON-LD (schema.org) | ~۲۰۰ کیلوبایت | `Dataset` + `DefinedTermSet` + ۱۳۲ `DefinedTerm` |
| [`data/open/terms.ttl`](data/open/terms.ttl) | Turtle (SKOS/RDF) | ~۳۶۰ کیلوبایت | گراف دانش؛ قابل بارگذاری در هر triple store |
| [`data/open/terms.csv`](data/open/terms.csv) | CSV (UTF-8 BOM) | ~۱۵۰ کیلوبایت | اکسل/پانداس؛ جداکنندهٔ چندمقداری `\|` |
| [`data/open/datapackage.json`](data/open/datapackage.json) | Frictionless Data | ~۹ کیلوبایت | توصیف‌کنندهٔ نوع‌دار مجموعهٔ داده |
| [`data/open/README.md`](data/open/README.md) | Markdown | — | شناسنامهٔ بسته + منابع مورد استناد |

### بارگذاری سریع

```python
# NDJSON — کم‌مصرف‌ترین راه برای خواندن کل مجموعه
import json, urllib.request

url = "https://bmhmdyan279-png.github.io/eng-terms-fa/data/open/terms.ndjson"
with urllib.request.urlopen(url) as response:
    terms = [json.loads(line) for line in response if line.strip()]
print(len(terms), terms[0]["term_fa"])
```

```python
# SKOS/RDF با rdflib
from rdflib import Graph, Namespace
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

graph = Graph()
graph.parse("terms.ttl", format="turtle")
for concept in graph.subjects(None, None):
    pass
print(len(graph), "triples")
```

```bash
# خط فرمان: همهٔ واژه‌هایی که ریشهٔ «بند» دارند
jq -c 'select(.root_fa == "بند") | {term_fa, term_en}' terms.ndjson
```

### نگاشت SKOS

| فیلد داده | خاصیت SKOS |
|---|---|
| `term_fa` | `skos:prefLabel@fa` |
| `term_en/fr/de/ar` | `skos:altLabel@en/fr/de/ar` |
| `synonyms`, `search_aliases` | `skos:altLabel@fa` |
| `definition_fa` | `skos:definition@fa` |
| `etymology_fa` | `skos:historyNote@fa` |
| `root_fa`، `root_ar`، `origin_lang`، `plural_fa` | `skos:note@fa` |
| `usage_examples` | `skos:example@fa` |
| `antonyms` | `skos:scopeNote@fa` |
| `translation_notes` | `skos:editorialNote@fa` |
| `related_terms` | `skos:related` |
| `domain` | `dct:subject` (به مفهوم حوزه) |
| `references` | `dct:bibliographicCitation` + `rdfs:seeAlso` |
| `slug` / `id` | `skos:notation` / `dct:identifier` |
| `status` | `schema:creativeWorkStatus` |
| `reviewed_at` / `reviewed_by` | `dct:date` / `dct:contributor` |

هر واژه یک IRI پایدار دارد: `…/terms/{slug}/#concept` و هر حوزه
`…/#domain-{id}`. چون slugها تغییرناپذیرند، این IRIها هم تغییرناپذیرند.

## API { #api }

API ایستا است (بدون سرور) و از همان داده تولید می‌شود:

| مسیر | محتوا |
|---|---|
| `data/api/terms.json` | همهٔ واژه‌ها + تعداد |
| `data/api/terms/{slug}.json` | یک واژه |
| `data/api/categories.json` | حوزه‌ها با شمارش هر حوزه |
| `data/api/stats.json` | آمار مجموعه، مجوز، زمان تولید |
| `data/api/search-index.json` | نمایهٔ جستجوی ریشه‌محور (واژه‌ها، ریشه‌ها، واژگان محافظت‌شده) |

```bash
curl -s .../data/api/terms/sealing.json | jq '.term_fa, .root_fa, .references[0].code'
```

!!! note "CORS و مصرف در مرورگر"
    سایت روی GitHub Pages است و سروری در کار نیست؛ درخواست‌ها هم‌origin اند.
    برای مصرف از دامنهٔ دیگر، فایل‌ها را با `fetch` از همین نشانی‌ها بخوانید
    یا بستهٔ داده را دانلود کنید (مجوز CC BY-SA اجازهٔ بازتوزیع می‌دهد).

## دانلودهای آماده { #downloads }

خروجی‌های قابل دانلود در سایت در نشانی `downloads/` قرار می‌گیرند
(در GitHub Actions ساخته می‌شوند و در مخزن نیستند):

- `terms.csv` — صفحهٔ گسترده
- `anki.apkg` — دستهٔ فلش‌کارت Anki
- `terms.pdf` — نسخهٔ چاپی با فونت وزیرمتن

## جستجوی ریشه‌محور { #root-search }

نمایهٔ `search-index.json` با `scripts/build_search_index.py` ساخته می‌شود و
موتور آن (`docs/assets/js/persian-stem.js`) نیم‌فاصله، جمع، یای نسبت، صفت
تفضیلی، شکل فعل، جمع‌های مکسر عربی و واژه‌های مرکب را می‌شناسد:

- «آجرکاری»، «آجرها» و «آجر» یک خانواده‌اند
- «بندکشی» و «آب‌بندی» با ریشهٔ «بند» پیدا می‌شوند
- «می‌شود» به «شد» و «شدن» می‌رسد
- «مشخصات» به «مشخصه» می‌رسد
- سرمدخل‌ها هرگز کوتاه نمی‌شوند («سیمان» ≠ «سیم» + «ان»)

همین الگوریتم در پایتون و جاوااسکریپت پیاده شده و `tools/check_stemmer_parity.js`
در CI اثبات می‌کند که خروجی دو پیاده‌سازی روی ۷۱ نمونهٔ آزمون (۴۹۷ مقایسه)
یکسان است.

## شکاف‌های ترجمه { #gaps }

فهرست زندهٔ ترجمه‌های تهی یا توصیفی در
[`translation_gaps.csv`](https://github.com/bmhmdyan279-png/eng-terms-fa/blob/main/translation_gaps.csv)
است. سیاست پروژه: **«نداریم» بهتر از «غلط» است** — ترجمهٔ راستی‌آزمایی‌نشده
`null` می‌ماند و ترجمهٔ توصیفی حتماً با `translation_notes` علامت می‌خورد تا
خواننده بداند با سرِواژهٔ مصوب روبه‌رو نیست.

## منابع و رجیستری استناد { #sources }

هر `references[].code` در داده‌ها باید در
[`data/standards.yaml`](https://github.com/bmhmdyan279-png/eng-terms-fa/blob/main/data/standards.yaml)
وجود داشته باشد؛ در غیر این صورت بیلد می‌شکند. این رجیستری وضعیت
راستی‌آزمایی هر منبع را هم نگه می‌دارد (`confirmed` یا `declared`) و اجازه
نمی‌دهد استنادِ ساختگی منتشر شود.

!!! warning "یک ارجاع نامعتبر پیدا و حذف شد"
    نسخهٔ پیشین داده، «استاندارد ملی ایران شماره ۶۶۴» را برای *بتن* استناد
    کرده بود. این شماره در هیچ فهرستی از استانداردهای سازمان ملی استاندارد
    یافت نشد، پس از رجیستری حذف و ارجاع‌های بتن به `ACI 116R`، `ASTM C125` و
    «آیین‌نامه بتن ایران (آبا)» منتقل شد.

## استناد { #cite }

برای استناد علمی به این مجموعه، [صفحهٔ ارجاع](citation.md) را ببینید
(BibTeX / APA / MLA) و `CITATION.cff` را در ریشهٔ مخزن.
