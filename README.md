# 🏗️ دیکشنری تخصصی مهندسی
[![GitHub release](https://img.shields.io/github/v/release/bmhmdyan279-png/eng-terms-fa)](https://github.com/bmhmdyan279-png/eng-terms-fa/releases)
## 📖 دربارهٔ پروژه

این پروژه یک **دیکشنری تخصصی مهندسی** با تمرکز بر واژگان فنی و علمی در حوزه‌های **عمران، مکانیک، معماری و فناوری بتن** است.

## Current Status (نسخهٔ زیرساخت 1.1.0 — نسخهٔ داده 0.2؛ بازبینی داده‌محور انجام شده)

> **دو نسخه را اشتباه نگیرید:** `1.1.0` نسخهٔ *نرم‌افزار/زیرساخت* است (معماری داده،
> موتور ریشه‌یابی، دادهٔ باز، CI)؛ `0.2` نسخهٔ *محتوا/داده* است.
>
> **صداقت دربارهٔ «بازبینی»:** هر ۱۳۲ مدخل از `draft` خارج شده‌اند و
> `status: reviewed` دارند، ولی `review_level: ai-assisted` است — یعنی بازبینی
> داده‌محور با دروازه‌های خودکار، **بدون تأیید متخصص انسانی**. اسکیمای داده اجازه
> نمی‌دهد مدخلی بدون `review_level: expert` به `published` برسد، پس این وضعیت
> قابل جعل نیست. هر مدخل، بازبین و سطح بازبینی خودش را در صفحهٔ خودش نشان می‌دهد.

- ✅ Data-driven architecture (YAML → MkDocs)
- ✅ CI/CD pipeline با ۵ دروازهٔ کیفیت + توازی پایتون/جاوااسکریپت
- ✅ Content review: ۱۳۲/۱۳۲ مدخل (تعریف، ریشه‌شناسی، مترادف، نمونهٔ کاربرد، استناد راستی‌آزمایی‌شده)
- ✅ **جستجوی ریشه‌محور فارسی** — نیم‌فاصله، جمع، یای نسبت، صفت تفضیلی، شکل فعل، جمع مکسر عربی، واژهٔ مرکب، تحمل غلط تایپی
- ✅ **دادهٔ باز** — NDJSON، SKOS/RDF (Turtle)، JSON-LD (schema.org)، CSV، Frictionless datapackage
- ⚠️  ترجمه‌های FR/DE/AR: ۹۹٪/۹۷٪/۹۷٪ پوشش؛ ۱۸ مورد تهی یا توصیفی در `translation_gaps.csv` گزارش می‌شود
- ⚠️  بازبینی انسانی متخصص هنوز انجام نشده (`review_level: expert` صفر مدخل)
- 🚧 Pagefind همچنان برای جستجوی متن کامل صفحه‌ها فعال است

### ویژگی‌ها

- 🔍 **جستجوی ریشه‌محور فارسی** — «آجرکاری»، «آجرها» و «آجر» یک خانواده‌اند؛ «بندکشی» و «آب‌بندی» با ریشهٔ «بند» پیدا می‌شوند؛ «می‌شود» به «شد»/«شدن» می‌رسد؛ «مشخصات» به «مشخصه». آفلاین و بدون سرور.
- 🧬 **ریشه‌شناسی و ساخت‌واژه** — هر مدخل `root_fa`، `etymology_fa`، `origin_lang` و (برای وام‌واژه‌ها) `root_ar` دارد؛ صفحهٔ هر واژه «هم‌ریشه‌ها» را نشان می‌دهد.
- 📚 **استناد راستی‌آزمایی‌شده** — هر `references[].code` باید در `data/standards.yaml` باشد و بگوید *چگونه* از مدخل پشتیبانی می‌کند؛ استناد ساختگی بیلد را می‌شکند.
- 📦 **دادهٔ باز واقعی** — علاوه بر API، خروجی SKOS/RDF و JSON-LD و NDJSON و datapackage منتشر می‌شود (CC BY-SA 4.0).
- 🌐 **نسخهٔ وب PWA** – قابل نصب، کارکرد آفلاین (نمایهٔ جستجو هم پیش‌حافظه می‌شود)
- 🌍 **معادل‌های چندزبانه**: انگلیسی (الزامی)، فرانسوی، آلمانی و عربی — ترجمهٔ راستی‌آزمایی‌نشده `null` می‌ماند و ترجمهٔ توصیفی با `translation_notes` علامت می‌خورد.
- ✅ **اعتبارسنجی خودکار** – JSON Schema، یکتایی شناسه‌ها، تغییرناپذیری URLها، لنتر نگارش فارسی، تقارن گراف واژه‌ها
- 📅 **واژهٔ روز** – چرخش قطعی روزانه
- 🤝 **مشارکت آسان** – فرم پیشنهاد واژه + راهنمای YAML

### کیفیت داده‌ها

**دروازه‌های خودکار** (در هر بیلد CI — هر ادعا باید در CI اثبات شود):

| دروازه | چه چیزی را ثابت می‌کند |
|---|---|
| `scripts/validate_data.py` | اسکما، یکتایی id/slug، یکپارچگی `related_terms`، تغییرناپذیری slugها نسبت به `origin/main`، ترجمهٔ تنبل، placeholder |
| `scripts/validate_content.py` | **ارجاع‌ها در رجیستری وجود دارند و `note` دارند**؛ `reviewed` بدون بازبین/تاریخ/سطح ممکن نیست؛ `published` بدون بازبینی انسانی ممکن نیست؛ `reviewed_by` نمی‌تواند دروغ بگوید؛ تعریف ≥۸۰ نویسه و غیرتکراری؛ نگارش فارسی؛ نمونهٔ کاربرد باید خودِ واژه را داشته باشد؛ گراف دوطرفه؛ هم‌پوشانی مترادف‌ها مستند باشد |
| `scripts/audit_translations.py --strict` | دودِ تست ترجمه در ۴ زبان: عبارات ممنوعهٔ ماشینی، جمله‌مانندی، حرف تعریف ابتدا، کپی یکسان FR/DE/AR، نویسهٔ لاتین در عربی |
| `tools/check_stemmer_parity.js` | موتور ریشه‌یابی پایتون و جاوااسکریپت روی ۷۱ نمونه (۴۹۷ مقایسه) **یکسان** خروجی می‌دهند |
| `pytest tests/` | ۵۰۵ آزمون: اسکما، XSS، تناظر صفحات تولیدشده، نامتغیرهای موتور صرفی، گراف SKOS، JSON-LD، دروازهٔ محتوا |
| `git diff --exit-code` | صفحات فهرست، جدول‌های صرفی JS، فیکسچر طلایی، `translation_alerts.csv` و `translation_gaps.csv` همه به‌روزند |

**سیاست محتوا** (بدون تغییر):

- 🎯 تعریف تخصصی: ≥۸۰ نویسه پس از خروج از `draft` (میانگین فعلی ۱۳۶، بیشینه ۳۶۱)
- 🎯 `term_en` الزامی و کوچک‌نویس (مگر سرواژه/نام خاص)
- 🎯 FR/DE/AR: یا راستی‌آزمایی‌شده، یا `null`. معادل توصیفی باید در `translation_notes` اعلام شود
- 🎯 هر ارجاع از رجیستری `data/standards.yaml` با وضعیت راستی‌آزمایی (`confirmed`/`declared`)

> ⚠️ در همین بازبینی، «استاندارد ملی ایران شماره ۶۶۴» که به *بتن* ارجاع شده بود
> در هیچ فهرستی از استانداردهای INSO یافت نشد؛ از رجیستری حذف و ارجاع‌های بتن به
> `ACI 116R`، `ASTM C125` و «آیین‌نامه بتن ایران (آبا)» منتقل شد.

## 🚀 اجرای محلی

### پیش‌نیازها

- Python 3.10+
- Node.js 18+ (برای Pagefind و آزمون توازی موتور ریشه‌یابی)
- Git

### راه‌اندازی سریع

```bash
git clone https://github.com/bmhmdyan279-png/eng-terms-fa.git
cd eng-terms-fa

pip install -r requirements.txt          # اجرای سایت
pip install -r requirements-dev.txt      # + rdflib برای آزمون‌های RDF

# تولید همهٔ مصنوعات از داده‌ها (به همین ترتیب)
python scripts/build_pages.py            # صفحات واژه‌ها و فهرست‌ها
python scripts/generate_stem_data.py     # جدول‌های صرفی برای جاوااسکریپت
python scripts/build_search_index.py     # نمایهٔ جستجوی ریشه‌محور + فیکسچر طلایی
python scripts/generate_api.py           # API استاتیک JSON
python scripts/generate_opendata.py      # بستهٔ دادهٔ باز (SKOS/JSON-LD/NDJSON/…)

mkdocs serve                             # http://localhost:8000
```

### دروازه‌های کیفیت

```bash
python scripts/validate_data.py          # اسکما، یکتایی، تغییرناپذیری slug
python scripts/validate_content.py       # استناد، صداقت بازبینی، نگارش، گراف
python scripts/audit_translations.py     # دودِ تست ترجمه (با --strict سخت‌گیرانه)
node tools/check_stemmer_parity.js       # توازی پایتون ⇄ جاوااسکریپت
node tools/search_probe.js آجرکاری بند rebar   # کاوش کیفیت رتبه‌بندی
pytest tests/
```

### ویرایش دسته‌جمعی محتوا

بازبینی محتوایی در `tools/review_batch*.py` به‌صورت وصله‌های خوانا نگهداری می‌شود و
`tools/apply_review.py` آن‌ها را روی YAML اعمال می‌کند (با سریال‌سازِ بایت‌به‌بایت
پایدار و گذرِ «دوطرفه‌سازی گراف واژه‌ها»):

```bash
python tools/apply_review.py --dry-run   # چه چیزی تغییر می‌کند؟
python tools/apply_review.py             # اعمال
python tools/apply_review.py --check     # در CI: داده با وصله‌ها هم‌خوان است؟
```

## 📂 ساختار پروژه

```
eng-terms-fa/
├── .github/workflows/          # CI (۵ دروازه + توازی + Lighthouse) و Deploy
├── data/
│   ├── standards.yaml          # ✦ رجیستری منابع راستی‌آزمایی‌شده (تنها منبع مجاز استناد)
│   └── terms/                  # داده‌های ماژولار (هر فایل یک حوزه)
│       ├── _meta.yaml          # فراداده: دامنه‌ها، فایل‌ها، نسخهٔ داده
│       ├── concrete.yaml       # بتن، سیمان و سازه‌های بتنی
│       ├── construction.yaml   # اصطلاحات ساختمانی و کارگاهی
│       ├── academy.yaml        # واژگان مصوب فرهنگستان
│       └── mechanical.yaml     # واژگان مکانیک
├── docs/
│   ├── assets/js/
│   │   ├── persian-stem-data.js   # ✦ تولیدشده از پایتون (جدول‌های صرفی)
│   │   ├── persian-stem.js        # ✦ آینهٔ الگوریتم ریشه‌یابی در مرورگر
│   │   └── persian-search.js      # ✦ رابط جستجوی آنی، آفلاین، بی‌XSS
│   ├── data.md                 # ✦ مستند دادهٔ باز و API
│   └── terms/                  # صفحات واژگان (تولید خودکار؛ در گیت نیست)
├── schemas/term-v1.schema.json # اسکیمای مدخل (rev.2: ریشه، ریشه‌شناسی، سطح بازبینی)
├── scripts/
│   ├── persian_text.py         # ✦ موتور نرمال‌سازی/ریشه‌یابی فارسی
│   ├── build_search_index.py   # ✦ نمایهٔ جستجو + فیکسچر طلایی توازی
│   ├── generate_stem_data.py   # ✦ صدور جدول‌های صرفی به JS
│   ├── generate_opendata.py    # ✦ NDJSON / SKOS-Turtle / JSON-LD / CSV / datapackage
│   ├── validate_content.py     # ✦ دروازهٔ کیفیت علمی محتوا
│   ├── standards.py            # ✦ بارگذار رجیستری منابع
│   ├── build_pages.py          # تولید صفحات + اعتبارسنجی اسکما
│   ├── validate_data.py        # دروازهٔ کیفیت داده
│   ├── audit_translations.py   # پایش ترجمه‌ها
│   ├── generate_api.py         # API استاتیک JSON
│   ├── generate_exports.py     # Anki / CSV / PDF
│   ├── mkdocs_hooks.py         # آمار زنده، واژهٔ روز، JSON-LD مجموعه‌داده
│   └── totd.py                 # واژهٔ روز
├── tools/
│   ├── apply_review.py         # ✦ اعمال وصله‌های بازبینی روی YAML (بایت‌پایدار)
│   ├── review_data.py          # ✦ تصمیم‌های محتوایی بازبینی
│   ├── review_batch*.py        # ✦ دسته‌های بازبینی
│   ├── check_stemmer_parity.js # ✦ اثبات توازی پایتون ⇄ JS
│   └── search_probe.js         # ✦ کاوش کیفیت رتبه‌بندی
├── tests/                      # ۵۰۵ آزمون
├── CITATION.cff                # ✦ استناد ماشین‌خوان
├── translation_gaps.csv        # ✦ فهرست زندهٔ ترجمه‌های تهی/توصیفی
└── requirements{,-dev}.txt
```

✦ = افزودهٔ این نسخه

## ✍️ نحوهٔ افزودن واژهٔ جدید

۱. فایل موضوعی مناسب را در `data/terms/` باز کنید (مثلاً `construction.yaml`).

۲. یک واژهٔ جدید به این شکل اضافه کنید (باید با `schemas/term-v1.schema.json` سازگار باشد):

```yaml
- id: slug-unique
  term_fa: واژهٔ فارسی
  term_en: english word          # کوچک‌نویس؛ مگر سرواژه یا نام خاص
  term_fr: null                  # ترجمهٔ راستی‌آزمایی‌نشده = null («نداریم» بهتر از «غلط» است)
  term_de: null
  term_ar: null
  pos: noun                      # noun | verb | adjective | phrase
  domain: [construction]         # فقط دامنه‌های data/terms/_meta.yaml
  definition_fa: >-
    تعریف تخصصی و دقیق؛ پس از خروج از draft باید دست‌کم ۸۰ نویسه باشد
    و نباید کپی تعریف مدخل دیگری باشد.
  synonyms: [واژهٔ هم‌معنی]      # معادل‌های معنایی (به ریشه‌ها و جستجو می‌روند)
  search_aliases: [وام‌واژهٔ رایج] # شکل‌های نوشتاری/گفتاری که کاربر تایپ می‌کند
  usage_examples:
    - جمله‌ای که خودِ واژه در آن به کار رفته باشد (دروازهٔ CI بررسی می‌کند).
  root_fa: ریشهٔ فارسی           # مثلاً «بند» برای آب‌بندی و بندکشی
  root_ar: null                  # ریشهٔ عربی برای وام‌واژه‌ها (مثل «ق-و-م»)
  etymology_fa: >-
    ریشه‌شناسی: زبان مبدأ، ساخت‌واژه، تاریخ وام‌گیری.
  origin_lang: fa                # fa | ar | tr | fr | en | de | la | el | …
  plural_fa: واژه‌ها
  references:
    - type: standard             # standard | book | other
      code: ACI 318-19           # ✦ باید در data/standards.yaml باشد
      note: >-                   # ✦ الزامی: این منبع چگونه از مدخل پشتیبانی می‌کند؟
        تعریف با دامنهٔ کاربرد این استاندارد هم‌خوان است.
  related_terms: [slug-واژه-مرتبط]  # فقط شناسهٔ واژه‌های موجود؛ پیوند باید دوطرفه باشد
  status: reviewed               # draft | reviewed | published
  review_level: ai-assisted      # ai-assisted | expert | committee
  reviewed_by: نام بازبین        # برای بازبینی ماشینی باید صریح بگوید AI
  reviewed_at: 2026-09-10
  translation_notes:             # فقط وقتی معادل «توصیفی» است، نه سرِواژهٔ مصوب
    de: معادل توصیفی؛ سرِواژهٔ مصوب آلمانی راستی‌آزمایی نشد.
  slug: slug-unique              # باید با id یکسان و یکتا و تغییرناپذیر باشد
```

> ⚠️ `status: published` تنها با `review_level: expert` یا `committee` ممکن است —
> این قید هم در اسکیمای JSON Schema و هم در `validate_content.py` اعمال می‌شود.

۳. داده‌ها را اعتبارسنجی کنید (اسکما، یکتایی، تغییرناپذیری slug، ترجمه‌ها):

```bash
python scripts/validate_data.py
```

۴. صفحات را بازسازی کنید:

```bash
python scripts/build_pages.py
```

۵. تغییرات را کامیت و پوش کنید.

۶. GitHub Actions به‌صورت خودکار اعتبارسنجی، تست و به‌روزرسانی سایت را انجام می‌دهد.

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم!

**الزامات مشارکت:**
- تعاریف باید **تخصصی و دقیق** باشند — حداقل ۵۰ نویسه (دروازهٔ CI) و در حالت ایده‌آل ۲-۳ خط
- `term_en` **الزامی** است؛ `term_fr` / `term_de` / `term_ar` فقط در صورت **بازبینی انسانی** پر شوند — ترجمهٔ بازبینی‌نشده باید `null` بماند
- عبارت «برابر مصوب فرهنگستان» به‌تنهایی جای تعریف را نمی‌گیرد (ذکر منبع کنار تعریف کامل بلامانع است)
- **ارجاع به استانداردها** (ACI، ASTM، DIN، استانداردهای ملی) ترجیح داده می‌شود

### راه‌های مشارکت

- [فرم پیشنهاد واژه](https://bmhmdyan279-png.github.io/eng-terms-fa/contribute-form/)
- [راهنمای مشارکت](CONTRIBUTING.md)
- [کد رفتار](CODE_OF_CONDUCT.md)

## 📦 دادهٔ باز، API و خروجی‌ها

مستند کامل در [صفحهٔ دادهٔ باز](https://bmhmdyan279-png.github.io/eng-terms-fa/data/) است.

**بستهٔ دادهٔ باز (`data/open/` روی سایت):**

| فایل | قالب | کاربرد |
|---|---|---|
| `terms.ndjson` | NDJSON | بارگذاری خط‌به‌خط در پایپ‌لاین داده |
| `terms.ttl` | Turtle (SKOS) | گراف دانش؛ قابل بارگذاری در هر triple store |
| `terms.jsonld` | JSON-LD | schema.org `Dataset` + `DefinedTermSet` + ۱۳۲ `DefinedTerm` |
| `terms.csv` | CSV | اکسل/پانداس |
| `datapackage.json` | Frictionless Data | توصیف‌کنندهٔ نوع‌دار مجموعه |

**API (JSON):** `data/api/terms.json`، `data/api/terms/{slug}.json`،
`data/api/categories.json`، `data/api/stats.json` و نمایهٔ جستجو
`data/api/search-index.json`.

**دانلود (`/downloads/` روی سایت):** `anki.apkg`، `terms.csv`، `terms.pdf`،
`open-data.zip`، `skos.ttl`، `terms.ndjson`، `translation_gaps.csv`.

**استناد:** [صفحهٔ ارجاع](docs/citation.md) و `CITATION.cff` در ریشهٔ مخزن
(BibTeX / APA / MLA).

## 📜 مجوز

- **کد:** MIT License (LICENSE-CODE.md)
- **محتوا (واژگان):** Creative Commons BY-SA 4.0 (LICENSE-CONTENT.md)

---
**توسعه‌دهنده:** [bmhmdyan279-png](https://github.com/bmhmdyan279-png)

**📧 تماس:** برای سوالات فنی یا پیشنهادات همکاری، Issue باز کنید.
