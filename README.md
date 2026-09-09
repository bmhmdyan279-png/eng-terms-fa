# 🏗️ دیکشنری تخصصی مهندسی
[![GitHub release](https://img.shields.io/github/v/release/bmhmdyan279-png/eng-terms-fa)](https://github.com/bmhmdyan279-png/eng-terms-fa/releases)
## 📖 دربارهٔ پروژه

این پروژه یک **دیکشنری تخصصی مهندسی** با تمرکز بر واژگان فنی و علمی در حوزه‌های **عمران، مکانیک، معماری و فناوری بتن** است.

## Current Status (نسخهٔ زیرساخت 1.0.0 — نسخهٔ داده 0.1؛ بازبینی محتوا در جریان)

> **دو نسخه را اشتباه نگیرید:** `1.0.0` نسخهٔ *نرم‌افزار/زیرساخت* است (معماری داده، CI، PWA، API)؛
> `0.1` نسخهٔ *محتوا/داده* است — همهٔ مدخل‌ها هنوز `status: draft` هستند و بازبینی تخصصی
> واژه‌به‌واژه در جریان است. وضعیت هر مدخل در صفحهٔ همان واژه نمایش داده می‌شود.

- ✅ Data-driven architecture (YAML → MkDocs)
- ✅ CI/CD pipeline
- ⚠️  Content review in progress (0 reviewed entries so far)
- ⚠️  Translation quality check ongoing (unverified FR/DE/AR stay `null`)
- 🚧 Search: Pagefind indexed in CI (no Persian stemming yet)

### ویژگی‌ها

- 🌐 **نسخهٔ وب PWA** – قابل نصب روی گوشی، کارکرد آفلاین
- 📱 **واکنش‌گرا (Responsive)** – بهینه برای موبایل و تبلت
- 🔍 **جستجوی پیشرفته** – با نمایهٔ Pagefind که در هر بیلد CI ساخته می‌شود
- 🌍 **معادل‌های چندزبانه**: انگلیسی (الزامی)، فرانسوی، آلمانی و عربی (فقط بازبینی‌شده‌ها نمایش داده می‌شوند؛ بقیه `null`)
- 📚 **اتصال به منابع تخصصی** – شامل واژگان کتاب «آزمایشات فناوری بتن»
- ✅ **اعتبارسنجی خودکار داده‌ها** – اسکیمای JSON Schema، یکتایی شناسه‌ها و تغییرناپذیری URLها در هر بیلد
- 📦 **API و خروجی چندقالبی** – JSON عمومی + CSV، Anki و PDF برای دانلود
- 📅 **واژهٔ روز** – چرخش قطعی روزانه در صفحهٔ اصلی
- 🤝 **مشارکت آسان** – فرم پیشنهاد واژه (فنی و غیرفنی)

### کیفیت داده‌ها

**هدف کیفی** (برای مدخل‌هایی که به `reviewed` ارتقا می‌یابند):

- 🎯 **تعاریف تخصصی و دقیق** — حداقل ۵۰ نویسه (دروازهٔ CI) و در حالت ایده‌آل ۲-۳ خط با جزئیات فنی
- 🎯 **معادل انگلیسی معتبر** — برای هر مدخل الزامی است
- 🎯 **معادل FR/DE/AR فقط در صورت بازبینی انسانی** — ترجمهٔ بازبینی‌نشده `null` می‌ماند؛ «نداریم» بهتر از «غلط» است
- 🎯 **ارجاع به استانداردها** (ACI، ASTM، استانداردهای ملی ایران)

**وضعیت فعلی** (شفاف): همهٔ مدخل‌ها `draft` هستند؛ آمار زندهٔ صفحهٔ اصلی تعداد
مدخل‌های بازبینی‌شده را نشان می‌دهد.

**دروازه‌های خودکار** (در هر بیلد CI):

- ✅ `scripts/validate_data.py` — بررسی اسکما، یکتایی id/slug، یکپارچگی `related_terms`، تغییرناپذیری slugها، ترجمهٔ تنبل و مقادیر placeholder؛ روی هر رکورد نامعتبر شکست می‌خورد
- ✅ `scripts/audit_translations.py --strict` — دودِ تست ترجمه در هر ۴ زبان: عبارات ممنوعهٔ ترجمهٔ ماشینی، جمله‌مانند بودن، حرف تعریف ابتدا، کپی یکسان FR/DE/AR

## 🚀 اجرای محلی

### پیش‌نیازها

- Python 3.10+
<!-- موقتاً حذف شد — وابستگی به Pagefind که هنوز فعال نیست:
- Node.js 18+ (برای Pagefind)
-->
- Git

### راه‌اندازی سریع

```bash
# کلون پروژه
git clone https://github.com/bmhmdyan279-png/eng-terms-fa.git
cd eng-terms-fa

# نصب وابستگی‌ها
pip install -r requirements.txt

# تولید صفحات از داده‌ها
python scripts/build_pages.py

# اجرای محلی
mkdocs serve
```

حالا مرورگر را روی `http://localhost:8000` باز کنید.

برای تست جستجوی Pagefind به‌صورت محلی (اختیاری — در سایت مستقرشده خودکار است):

```bash
mkdocs build
npx pagefind --site site/   # نیازمند Node.js
```

## 📂 ساختار پروژه

```
eng-terms-fa/
├── .github/workflows/        # CI/CD (خودکار)
├── data/
│   └── terms/                # داده‌های ماژولار (هر فایل یک حوزه)
│       ├── _meta.yaml        # فراداده: دامنه‌ها و فایل‌های موضوعی
│       ├── concrete.yaml     # بتن، سیمان و سازه‌های بتنی
│       ├── construction.yaml # اصطلاحات ساختمانی و کارگاهی
│       ├── academy.yaml      # واژگان مصوب فرهنگستان
│       └── mechanical.yaml   # واژگان مکانیک
├── docs/                     # سایت MkDocs
│   ├── assets/               # CSS, JS
│   └── terms/                # صفحات واژگان (تولید خودکار؛ در گیت نگهداری نمی‌شود)
├── schemas/
│   └── term-v1.schema.json   # اسکیمای هر مدخل (بیلد روی رکورد نامعتبر شکست می‌خورد)
├── scripts/
│   ├── build_pages.py        # تولید صفحات + اعتبارسنجی اسکما
│   ├── validate_data.py      # دروازهٔ کیفیت داده‌ها (در CI اجرا می‌شود)
│   ├── audit_translations.py # پایش کیفیت ترجمه‌های انگلیسی
│   ├── generate_api.py       # خروجی JSON API (در CI اجرا می‌شود)
│   ├── generate_exports.py   # خروجی Anki/CSV/PDF
│   ├── totd.py               # واژهٔ روز (انتخاب قطعی بر اساس تاریخ)
│   ├── cleanup_terms.py      # پاکسازی داده‌ها
│   └── fix_old_links.py      # اصلاح لینک‌های قدیمی
├── tests/                    # تست‌های واحد
├── mkdocs.yml                # تنظیمات اصلی
└── requirements.txt          # وابستگی‌های پایتون
```

## ✍️ نحوهٔ افزودن واژهٔ جدید

۱. فایل موضوعی مناسب را در `data/terms/` باز کنید (مثلاً `construction.yaml`).

۲. یک واژهٔ جدید به این شکل اضافه کنید (باید با `schemas/term-v1.schema.json` سازگار باشد):

```yaml
- id: slug-unique
  term_fa: واژهٔ فارسی
  term_en: English Word
  term_fr: null            # ترجمهٔ بازبینی‌نشده = null («نداریم» بهتر از «غلط» است)
  term_de: null
  term_ar: null
  pos: noun                # یکی از: noun | verb | adjective | phrase
  domain: [construction]   # باید در فهرست دامنه‌های data/terms/_meta.yaml باشد
  definition_fa: |
    تعریف تخصصی و دقیق واژه با جزئیات فنی.
    حداقل ۵۰ نویسه (دروازهٔ CI)؛ هدف: ۲-۳ خط شامل کاربردهای مهندسی.
    عبارت «برابر مصوب فرهنگستان» جای تعریف را نمی‌گیرد؛ ذکر منبع در
    کنار تعریف کامل بلامانع است.
  references:
    - type: standard       # یکی از: standard | book | other
      code: ACI 318-19
  related_terms:           # فقط شناسهٔ واژه‌های موجود (نه متن آزاد)
    - slug-واژه-مرتبط
  status: draft            # draft | reviewed | published
  slug: slug-unique        # باید با id یکسان و یکتا باشد
```

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

## 📦 API و خروجی‌ها

در هر استقرار، CI یک API استاتیک و خروجی‌های قابل دانلود تولید می‌کند:

**API (JSON):**
- `data/api/terms.json` — همهٔ واژه‌ها
- `data/api/terms/{slug}.json` — یک واژه
- `data/api/categories.json` — دامنه‌ها با شمارش
- `data/api/stats.json` — آمار زندهٔ مجموعه

**دانلود (`/downloads/` روی سایت):**
- `anki.apkg` — جعبهٔ فلش‌کارت Anki
- `terms.csv` — جدول Excel (با BOM برای نمایش صحیح فارسی)
- `terms.pdf` — نسخهٔ چاپی (فونت وزیرمتن)

**استناد:** برای ارجاع علمی (BibTeX / APA / MLA) صفحهٔ [ارجاع](docs/citation.md) را ببینید.

## 📜 مجوز

- **کد:** MIT License (LICENSE-CODE.md)
- **محتوا (واژگان):** Creative Commons BY-SA 4.0 (LICENSE-CONTENT.md)

---
**توسعه‌دهنده:** [bmhmdyan279-png](https://github.com/bmhmdyan279-png)

**📧 تماس:** برای سوالات فنی یا پیشنهادات همکاری، Issue باز کنید.
