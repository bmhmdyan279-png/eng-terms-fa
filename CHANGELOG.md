# CHANGELOG

فرمت این فایل بر پایهٔ [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/) و نسخه‌بندی بر پایهٔ [Semantic Versioning](https://semver.org/) است.

> سیاست پروژه: **هر ادعایی در README باید در CI قابل اثبات باشد.** اگر قابلیتی پیاده نیست، ادعا نمی‌شود.

## [1.0.0] — 2026-09-03

نخستین انتشار عمومی — «انتشار زیرساخت». زیرساخت داده، کیفیت و استقرار به سطح مرجع رسید؛ بازبینی تخصصی محتوا به‌صورت شفاف در جریان است (همهٔ مدخل‌ها `status: draft`).

### Added
- **مدل دادهٔ ماژولار**: شکافتن `data/terms.yaml` به `data/terms/{concrete,construction,academy,mechanical}.yaml` + `_meta.yaml` (دامنه‌ها و فهرست فایل‌ها)
- **اسکیمای رسمی**: `schemas/term-v1.schema.json` با فیلدهای الزامی `id, term_fa, term_en, pos, domain, definition_fa, status, slug` و `additionalProperties: false`
- **دروازهٔ کیفیت**: `scripts/validate_data.py` — اعتبارسنجی اسکما، یکتایی id/slug، یکپارچگی `related_terms`، **تغییرناپذیری slug** نسبت به baseline (بدون auto-fix)، ترجمه‌های تنبل (کپی term_en)، مقادیر placeholder؛ exit 1 روی هر خطا
- **پایش ترجمه**: `scripts/audit_translations.py` + `translation_alerts.csv` (قوانین طول/تعداد کلمه/عبارات ممنوعهٔ ترجمهٔ ماشینی)
- **CI سخت‌گیرانه**: `.github/workflows/ci.yml` — validate → pytest → build → `mkdocs build --strict` → Pagefind → خروجی‌ها → Lighthouse (حداقل ۹۰) → pre-commit؛ گام‌های validate/export به `deploy.yml` هم اضافه شد
- **جستجوی واقعی Pagefind**: ایندکس در CI (`npx pagefind --site site/`)، `search-init.js` با رابط فارسی و محدودسازی ایندکس به محتوا (`data-pagefind-body`)
- **صفحهٔ فرود جدید**: Hero، آمار زنده (تزریق در بیلد)، دکمه‌های CTA، **واژهٔ روز** با چرخش قطعی روزانهٔ سمت کلاینت (`totd.js` + `scripts/totd.py`)
- **فیلترهای فهرست واژگان**: دامنه / وضعیت / دسترس‌پذیری ترجمه + مرتب‌سازی locale-aware فارسی و انگلیسی (`Intl.Collator`)
- **SEO**: JSON-LD `DefinedTerm` برای هر واژه، Open Graph / Twitter Cards (`docs/overrides/main.html`)، `sitemap.xml` با `lastmod/changefreq/priority`، `robots.txt`
- **دسترس‌پذیری**: کنتراست WCAG AA (با تست)، استایل فوکوس، برچسب‌های `lang` برای معادل‌های خارجی، ARIA برای جستجو، `dir=rtl` روی سند
- **PWA واقعی**: `manifest.webmanifest` (آیکن‌های ۱۹۲/۵۱۲/maskable تولیدشده با PIL)، `sw.js` با استراتژی Cache-First، اسکریپت ثبت SW
- **API استاتیک**: `data/api/{terms.json, terms/{slug}.json, categories.json, stats.json}` تولیدشده در CI
- **خروجی‌های چندقالبی**: `scripts/generate_exports.py` — `anki.apkg`، `terms.csv` (با BOM)، `terms.pdf` (فونت وزیرمتن subset‌شده در `tools/fonts/`)
- **سیستم استناد**: `docs/citation.md` — BibTeX/APA/MLA + جای‌گیرندهٔ DOI + راهنمای نسخه/تاریخ
- **مستندات جامعه**: CONTRIBUTING کامل با نردبان مشارکت (آسان/متوسط/دشوار)، CODE_OF_CONDUCT (سازگاری با Contributor Covenant 2.1)، قالب‌های Issue (term-suggestion / bug-report / translation-fix)، قالب PR، بازنویسی صادقانهٔ `docs/about.md`
- **هویت بصری**: تصویر Social preview (1280×640) و آیکن‌های برنامه

### Changed
- ۱۳ ترجمهٔ فاجعه‌بار ماشینی با معادل‌های قابل دفاع جایگزین شد: corner brick، header brick، F-bar bender، embedded steel، pointing mortar، bullnose brick، lime bloom، three-quarter brick، concrete beam، tamper، springing، masonry course، semicircular arch؛ ترجمه‌های FR/DE مشکوک/کپی‌شده `null` شدند
- README با واقعیت هم‌تراز شد؛ ادعاهای PWA/Pagefind/اعتبارسنجی تنها **پس از** پیاده‌سازیِ قابل اثبات در CI بازگشتند
- `LICENSE` به متن کامل MIT (با نام دارنده) ارتقا یافت
- لینک‌های ۹۷ صفحهٔ فهرست legacy به شناسه‌های جدید وصل شد

### Fixed
- لینک شکستهٔ `Eng-dict` در `docs/contribute.md` و ایمیل جعلی در `docs/contribute-form.md`
- ۴۰۴های دسته‌جمعی صفحات واژگان (اسلاگ‌های transliteration قدیمی)
- `mkdocs build --strict` بدون هیچ هشدار/خطا

### Removed
- `data/terms.yaml` تک‌فایلی (جایگزین با شارد‌ها؛ تاریخچه در گیت محفوظ است)
- لودر جعلی `docs/assets/js/pagefind.js` و تنظیم مردهٔ قالب‌ها
- `LICENSE.md` اضافه (منبع سردرگمی؛ `LICENSE` + `LICENSE-CODE/CONTENT.md` کافی‌اند)

### Known limitations (شفاف)
- هر ۱۱۹ مدخل `status: draft` است؛ بازبینی تخصصی در جریان است
- ۸۸ تعریف کوتاه‌تر از ۵۰ کاراکتر — در `draft` هشدار است و با ارتقای وضعیت، خطای سخت می‌شود
- بخشی از FR/DE/AR هنوز بازبینی نشده‌اند (برچسب‌گذاری و null‌سازی تدریجی در نقشهٔ راه)
- Pagefind برای فارسی stemming ندارد (جستجوی تطبیق دقیق)

## [0.1.0] — 2026-08-07

نمونهٔ اولیهٔ عمومی.

### Added
- خط لولهٔ داده‌محور: YAML → `build_pages.py` → Markdown → MkDocs Material (RTL + Vazirmatn) → GitHub Pages
- گردش کار استقرار خودکار با مجوزهای صحیح Pages
- مجموعهٔ اولیهٔ ۱۱۹ واژه (فناوری بتن، اصطلاحات ساختمانی، واژگان مصوب فرهنگستان، بذر مکانیک)
- `normalize_persian` (یکسان‌سازی ی/ک عربی) + نخستین تست واحد
- مجوز دوگانهٔ MIT (کد) / CC BY-SA 4.0 (محتوا)
