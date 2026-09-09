# CHANGELOG

فرمت این فایل بر پایهٔ [Keep a Changelog](https://keepachangelog.com/fa/1.1.0/) و نسخه‌بندی بر پایهٔ [Semantic Versioning](https://semver.org/) است.

> سیاست پروژه: **هر ادعایی در README باید در CI قابل اثبات باشد.** اگر قابلیتی پیاده نیست، ادعا نمی‌شود.

## [Unreleased]

پاسخ به بازبینی‌های امنیتی/محتوایی سپتامبر ۲۰۲۶ (هشت نقد مستقل). تمرکز: «توقف آسیب» محتوایی + سخت‌سازی کد؛ بدون قابلیت بزرگ جدید.

### Security
- **رفع XSS در `build_pages.py`**: همهٔ مقادیر داده‌ای (term_fa/en/fr/de/ar، تعریف، منابع، واژه‌های مرتبط، domain، pos) پیش از رندر `html.escape` می‌شوند — پیش‌تر فقط `render_index()` escape داشت و `render_pages()` نداشت (ناهمسانی بحرانی)
- مقدارهای frontmatter با نقل‌قول JSON/YAML ایمن نوشته می‌شوند
- **CSP meta tag** در `docs/overrides/main.html` (بدون منبع خارجی؛ فونت‌ها و Pagefind هم‌origin)
- `unlink()` فایل‌های قدیمی با مدیریت `OSError` (بیلد در صورت قفل بودن فایل نمی‌میرد)
- حذف بی‌صدای `related_terms` نامعتبر حالا WARNING ثبت می‌کند (لایهٔ دوم دفاع پس از دروازهٔ اعتبارسنجی)
- `SECURITY.md` جدید: گزارش محرمانهٔ آسیب‌پذیری + دامنهٔ حملهٔ سایت ایستا

### Data — «توقف آسیب» ترجمه‌ها (policy: ترجمهٔ بازبینی‌نشده = null)
- **پاکسازی کامل `construction.yaml`**: ۵۰ معادل انگلیسی غلطِ ماشینی اصلاح شد (Contact him→bonding tool, Ginger→pre-wetted brick, Sailor→sealer, Countries→mortar bucket, the vault→rebar spacer, John is plastered→gypsum-coated iron, Jan Panah→parapet, Orlip→overlap, …)
- ۲۳۲ فیلد FR/DE/AR: فاجعه‌های ماشینی («Eau chinoise»، «Ne pas briquer»، «Cornichon F»، «Pagode»، «potier/Töpfer»، «sont perdus»، …) یا با معادل تخصصیِ قابل دفاع جایگزین شدند (mortier de jointoiement/Fugenmörtel، boutisse، cintreuse en F، naissance de voûte/Bogenansatz، poutre en béton/Betonbalken، …) یا `null` شدند
- ۹۸ تعریف تک‌واژه‌ای/مترادفی به تعریف فنی واقعی بازنویسی شد — **هشدارهای کیفیت تعریف از ۸۹ به ۰ رسید**
- رکورد تکراری «زیگزال» (غلط تایپی «زیگزاگ») ادغام و حذف شد
- **`mechanical.yaml` از ۱ به ۱۵ واژه رسید** (نیرو، اصطکاک، شتاب، جرم، سرعت، اینرسی، تکانه، مرکز ثقل، لنگر خمشی، برش، خستگی، مدول الاستیسیته، کرنش، وزن) با ترجمهٔ ۴ زبانهٔ استاندارد — همه `draft`
- `validate_data.py`: افزودن parapet/force/fatigue به فهرست مجاز هم‌ریشه‌ها

### Quality gates
- **`audit_translations.py` بازنویسی شد: اکنون هر ۴ زبان را می‌سنجد** (پیش‌تر فقط term_en با ۴ عبارت ممنوعه بود و «Cornichon F» را نمی‌دید!) — قوانین: عبارات ممنوعهٔ چندزبانه (بازگشت فاجعه‌های ۲۰۲۶-۰۹ را می‌گیرد)، جمله‌مانندی (ضمیر/فعل کمکی)، حرف تعریف ابتدا، بودجهٔ تعداد واژه per-language، کپی یکسان FR/DE/AR، نویسهٔ لاتین در term_ar
- CI: گام `audit_translations.py --strict` در هر دو workflow
- CI: گام «صفحات فهرست به‌روز هستند» (`git diff --exit-code`) — drift غیرممکن شد
- `translation_alerts.csv` با ستون‌های language/value بازتولید شد (اکنون ۰ هشدار)

### Single Source of Truth
- `docs/construction-terms.md` و `docs/book-vocab.md` **اکنون در هر بیلد از داده تولید می‌شوند** (`render_list_pages`) — نسخهٔ دستی با «آب‌بندی»×۳ و «اسکوپ»×۲ و لینک‌های مرده حذف شد
- `scripts/fix_old_links.py` حذف شد (کارش با تولید خودکار جایگزین شد)

### UX / A11y
- **وضعیت فیلترهای فهرست در URL ذخیره می‌شود** (`?domain=…&status=…&langs=…&sort=…`) — نمای فیلترشده قابل اشتراک و بازگشت است
- `aria-live="polite"` روی شمارندهٔ نتایج فیلتر
- `prefers-reduced-motion` از قبل وجود داشت (بدون تغییر)

### Docs / Honesty
- README: تفکیک صریح **نسخهٔ زیرساخت 1.0.0** از **نسخهٔ داده 0.1**؛ بخش «کیفیت داده‌ها» از ادعای مطلق (✅ تمام واژگان…) به «هدف کیفی + وضعیت فعلی شفاف» تبدیل شد
- README: «ترجمهٔ تمام ۴ زبان الزامی است» حذف شد — اکنون هم‌راستا با اسکما و CONTRIBUTING: فقط `term_en` الزامی؛ FR/DE/AR فقط در صورت بازبینی انسانی، وگرنه `null`
- `citation.md`: جای‌گیرندهٔ جعلی DOI (`10.5281/zenodo.XXXXXXX`) حذف شد؛ نسخهٔ مورد استناد به «نسخهٔ داده 0.1» اصلاح شد
- خروجی PDF غنی‌تر شد: ترجمه‌های غیرnull، دامنه/نوع واژه/وضعیت و منابع برای هر مدخل

### Tests
- ۳۲ → **۴۴ تست**: رگرسیون XSS، تولید صفحات فهرست از داده، تطابق نسخهٔ کامیت‌شده با خروجی مولد، و سوئیت کامل audit (فاجعه‌های معروف باید flag شوند؛ دادهٔ فعلی باید صفر هشدار باشد)

### عمداً تغییر نکرد (تصمیم‌های مستند)
- آستانهٔ Lighthouse روی ۷۵ ماند (دو منتقد خواهان ۹۰+ بودند؛ پیش از بالا بردن باید علت score پایین ریشه‌یابی شود — issue پیشنهادی)
- slugها تغییر نکردند (`the-vault`, `contact-him`, …) — سیاست تغییرناپذیری خودِ پروژه اجازه نمی‌دهد؛ معادل‌ها و تعریف‌ها اصلاح شدند و صفحهٔ هر واژه برچسب «پیش‌نویس» دارد
- `id == slug` حفظ شد (تفکیک identity از URL موضوع schema-v2 است)

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
