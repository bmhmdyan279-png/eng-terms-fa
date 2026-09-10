# نقشهٔ کار — بازبینی محتوای علمی + ریشه‌یابی فارسی در جستجو + دادهٔ باز

> فایل کاری داخلی (در کامیت نهایی می‌ماند تا مسیر تصمیم‌ها مستند باشد).
> اصل حاکم، همان شعار پروژه است: **هر ادعا باید در CI اثبات شود**؛ «نداریم» بهتر از «غلط» است.

## وضعیت پایه (پیش از شروع)
- ۱۳۲ رکورد، همه `status: draft`، ۰ خطای اعتبارسنجی، ۰ هشدار ترجمه، ۴۴ تست سبز.
- شکاف ترجمه: FR=۹، DE=۱۳، AR=۹ تهی.
- `synonyms`/`antonyms`/`usage_examples` در **۰** رکورد؛ `references` در ۲۰؛ `related_terms` در ۱۶.
- جستجو: فقط Pagefind، بدون نرمال‌سازی یا ریشه‌یابی فارسی.

## فاز ۱ — مدل داده (افزودنی، سازگار با گذشته)
فیلدهای جدید اختیاری در `schemas/term-v1.schema.json`:
`root_fa`, `root_ar`, `etymology_fa`, `origin_lang`, `plural_fa`, `abbrev_en`,
`search_aliases`, `translation_notes`, `review_level`؛ و در `$defs/reference`:
`org`, `section`, `url`, `note`.

## فاز ۲ — ثبت منابع (Open Data provenance)
`data/standards.yaml`: رجیستری استانداردها/کتاب‌های **واقعی و قابل‌راستی‌آزمایی**.
دروازهٔ جدید: هر `references[].code` باید در رجیستری باشد یا با الگوی مجاز بخواند؛
ارجاع ناشناخته = خطا. این جلوی «استناد جعلی» را می‌گیرد.

## فاز ۳ — موتور ریشه‌یابی فارسی
`scripts/persian_text.py`: نرمال‌سازی (ی/ک، اعراب، ZWNJ، ارقام)، توکن‌سازی،
واژه‌های ایستا، واهشت (stemming) محافظه‌کار با **حفاظ واژگانی** (هیچ‌وقت به ناکلمه نمی‌رسد)،
شکستن جمع‌های عربی، ریشه‌یابی. خروجی: `docs/data/api/search-index.json` + فایل طلایی توازی.
`docs/assets/js/persian-stem.js` + `persian-search.js` (آفلاین، PWA) و
`tools/check_stemmer_parity.js` (توازی Python/JS در CI).

## فاز ۴ — بازبینی محتوای ۱۳۲ مدخل
تعریف دقیق‌تر، `synonyms`/`antonyms`/`usage_examples`/`related_terms` (دوطرفه)،
`references` از رجیستری، `root_fa`/`etymology_fa`/`origin_lang`/`plural_fa`،
پرکردن شکاف‌های ترجمه **فقط** برای معادل‌های قابل دفاع، و ارتقا به `reviewed`.

صداقت: `reviewed_by: "Qwen (AI-assisted review)"` + `review_level: ai-assisted`.
`published` فقط با `review_level: expert` (انسانی) ممکن است.

## فاز ۵ — خروجی‌های دادهٔ باز
`terms.ndjson`, `terms.jsonld` (schema.org Dataset + DefinedTermSet),
`terms.ttl` (SKOS/RDF)، `datapackage.json` (Frictionless)، `CITATION.cff`،
صفحهٔ `docs/data.md` و ستون‌های جدید در CSV/Anki/PDF.

## فاز ۶ — دروازه‌های کیفیت علمی
`scripts/validate_content.py`: reviewed ⇒ ارجاع + بازبین + تاریخ + تعریف ≥۸۰ نویسه؛
تشخیص تعریف تکراری/کپی‌شده؛ پایداری `related_terms`؛ لنتر نگارش فارسی
(نیم‌فاصله، ی/ک عربی، ارقام، «می‌شود»)؛ توازن ترجمه‌ها.

## فاز ۷ — مستندات، تست‌ها، CI
README/CHANGELOG/RELEASE_NOTES/about/citation/CONTRIBUTING به‌روز،
تست‌های جدید، گام‌های جدید CI، بازتولید همهٔ مصنوعات، کامیت.
