# راهنمای مشارکت

از این‌که می‌خواهید این فرهنگ را بهتر کنید سپاسگزاریم! 🙏
این پروژه **داده‌محور** است: همهٔ واژه‌ها در `data/terms/*.yaml` زندگی می‌کنند و سایت/API/خروجی‌ها از همان‌ها ساخته می‌شوند. بنابراین مشارکت محتوایی یعنی ویرایش YAML — بدون نیاز به دانش وب.

## نردبان مشارکت

هر سطح که راحتی کافی است؛ هیچ مشارکتی کوچک نیست.

### 🟢 سطح ۱ — آسان (بدون YAML)
- گزارش ترجمهٔ اشتباه یا تایپو با قالب **translation-fix**
- پیشنهاد واژهٔ جدید با قالب **term-suggestion**
- بهبود مستندات (همین فایل، README، about)

### 🟡 سطح ۲ — متوسط (YAML پایه)
- افزودن واژه با `term_fa` + `term_en` + `definition_fa` (زبان‌های دیگر اختیاری)
- افزودن `synonyms` یا `related_terms` به مدخل‌های موجود

### 🔴 سطح ۳ — دشوار (محتوای مرجع)
- مدخل کامل با ارجاع به منبعِ ثبت‌شده در `data/standards.yaml` و ترجمه‌های بازبینی‌شده
- بازبینی تخصصی یک مدخل و ارتقای آن به `review_level: expert` + `status: published`
  (این تنها راهی است که یک مدخل «منتشرشده» می‌شود — بازبینی ماشینی هرگز به آن نمی‌رسد)

### 🟣 سطح ۴ — پرارزش‌ترین کارِ باقی‌مانده
فهرست `translation_gaps.csv` دقیقاً می‌گوید کدام معادل FR/DE/AR تهی یا توصیفی است.
اگر به یکی از این زبان‌ها تسلط تخصصی دارید، پرکردن هر سطر از آن فهرست، واقعی‌ترین
مشارکت ممکن در این پروژه است.

## راه‌اندازی محلی

```bash
git clone https://github.com/bmhmdyan279-png/eng-terms-fa.git
cd eng-terms-fa
pip install -r requirements.txt
# تولید همهٔ مصنوعات از داده‌ها (ترتیب مهم است)
python scripts/build_pages.py            # صفحات واژه‌ها و فهرست‌ها
python scripts/generate_stem_data.py     # جدول‌های صرفی برای موتور جستجوی مرورگر
python scripts/build_search_index.py     # نمایهٔ جستجوی ریشه‌محور
python scripts/generate_api.py           # API استاتیک
python scripts/generate_opendata.py      # بستهٔ دادهٔ باز
mkdocs serve                             # http://localhost:8000

# دروازه‌های کیفیت (همان‌هایی که CI اجرا می‌کند)
python scripts/validate_data.py
python scripts/validate_content.py
node tools/check_stemmer_parity.js
pytest tests/
```

## فرمت دقیق یک مدخل (schema: term-v1, rev.2)

```yaml
- id: corner-brick                # یکتا، پایدار، برابر با slug
  term_fa: آجر نبشی
  term_en: corner brick           # کوچک‌نویس مگر سرواژه/نام خاص
  term_fr: brique d'angle         # ترجمهٔ راستی‌آزمایی‌شده
  term_de: Eckstein
  term_ar: null                   # ترجمهٔ راستی‌آزمایی‌نشده = null (نه ترجمهٔ ماشینی!)
  pos: noun                       # noun | verb | adjective | phrase
  domain: [construction]          # فقط دامنه‌های data/terms/_meta.yaml
  definition_fa: >-
    آجری که برای ساختن نبش (زاویهٔ خارجی) دیوار به کار می‌رود تا رج‌ها در
    زاویه به‌درستی به یکدیگر پیوند بخورند؛ معمولاً با چرخاندن یا برش آجر کامل
    در محل نصب می‌شود. (پس از خروج از draft: دست‌کم ۸۰ نویسه)
  synonyms: [آجر کنج]             # معادل معنایی → به ریشه‌ها و جستجو می‌رود
  search_aliases: [آجر گوشه]      # شکل نوشتاری/گفتاری که کاربر تایپ می‌کند
  usage_examples:
    - نبش دیوار با آجر نبشی چیده شد تا راستای رج‌ها نشکند.   # باید خودِ واژه را داشته باشد
  root_fa: آجر
  etymology_fa: >-
    «نبش» در اصطلاح بنایی زاویهٔ خارجی دیوار است و در برابر «کنج»
    (زاویهٔ داخلی) قرار دارد.
  origin_lang: fa                 # fa | ar | tr | fr | en | de | la | el | …
  references:                     # فقط منابعِ data/standards.yaml
    - type: standard
      code: مبحث هشتم مقررات ملی ساختمان
      note: ضوابط آجرچینی و پیوستگی رج‌ها با تعریف این واژه هم‌خوان است.
  related_terms: [header-brick]   # فقط idهای موجود؛ پیوند باید دوطرفه باشد
  status: reviewed                # draft | reviewed | published
  review_level: ai-assisted       # ai-assisted | expert | committee
  reviewed_by: Qwen (بازبینی دستیار هوشمند)
  reviewed_at: 2026-09-10
  slug: corner-brick              # تغییرناپذیر؛ URL پایدار است
```

اگر معادلی را می‌نویسید که **سرِواژهٔ مصوب آن زبان نیست** و توصیفی ساخته شده،
باید اعلامش کنید — وگرنه دروازهٔ محتوا آن را می‌گیرد:

```yaml
  translation_notes:
    de: معادل توصیفی؛ سرِواژهٔ مصوب آلمانی برای این اصطلاح راستی‌آزمایی نشد.
```

## دروازه‌های کیفیت (چه چیزی CI را قرمز می‌کند؟)

### `python scripts/validate_data.py` — داده درست است؟

1. انطباق کامل با `schemas/term-v1.schema.json` (فیلدهای الزامی، الگوی slug، enumها،
   و قیدِ «`published` فقط با `review_level: expert|committee`»)
2. یکتایی `id` و `slug` در همهٔ شارد‌ها
3. `related_terms` فقط به `id` موجود ارجاع دهد
4. **تغییرناپذیری slug** نسبت به شاخهٔ پایه (URL دارایی است)
5. تعریف زیر ۵۰ نویسه برای `reviewed/published` خطا و برای `draft` هشدار
6. ترجمهٔ FR/DE/AR عیناً برابر `term_en` نباشد (نشانهٔ ترجمه تنبل)
7. هیچ فیلدی `TODO`/`placeholder` نباشد

### `python scripts/validate_content.py` — محتوا قابل دفاع است؟

1. هر `references[].code` در `data/standards.yaml` باشد **و** `note` داشته باشد
   (استناد ساختگی یا بی‌توضیح = شکست بیلد)
2. `status != draft` ⇒ `reviewed_by` + `reviewed_at` + `review_level`؛ تاریخ معتبر و غیرآینده
3. **صداقت انتساب**: `review_level: ai-assisted` نمی‌تواند `reviewed_by` با عنوان
   انسانی (مهندس/دکتر/استاد/professor…) داشته باشد
4. تعریف بازبینی‌شده ≥ ۸۰ نویسه، غیرتکراری، و صرفاً بازگویی سرمدخل نباشد
5. لنتر نگارش فارسی روی همهٔ متن‌های authored (ی/ک عربی، «می » با فاصلهٔ کامل،
   «کتاب ها»، ارقام عربی، فاصلهٔ دوبل). اعراب‌گذاری *پراکنده* مجاز است چون فرهنگ
   باید تلفظ را نشان دهد («تاوَن»، «فارسی بُر»)، ولی اعراب *انبوه* نشانهٔ متن عربیِ
   جای‌گذاری‌شده است
6. هر `usage_example` باید خودِ واژه یا یکی از مترادف‌هایش را داشته باشد
7. گراف `related_terms` دوطرفه و بدون خودارجاع؛ مترادفی که سرمدخل مدخل دیگری است
   باید با پیوند دوطرفه مستند شود
8. `term_en` بزرگ‌نویس نباشد مگر سرواژه یا نام‌گذاری حرفی (`F-bar bender`)
9. `translation_notes` فقط روی زبانی که مقدار دارد

### بقیهٔ دروازه‌ها

- `scripts/audit_translations.py --strict` — دودِ تست ترجمه در ۴ زبان
- `node tools/check_stemmer_parity.js` — موتور ریشه‌یابی پایتون و مرورگر باید
  روی ۷۱ نمونه (۴۹۷ مقایسه) یکسان باشند
- `pytest tests/` — ۴۸۱ آزمون
- `git diff --exit-code` روی صفحات فهرست، `persian-stem-data.js`، فیکسچر طلایی،
  `translation_alerts.csv` و `translation_gaps.csv` — یعنی هیچ مصنوع تولیدی
  نمی‌تواند کهنه بماند

## دروازه‌های کیفیت (چه چیزی CI را قرمز می‌کند؟)

`python scripts/validate_data.py` این‌ها را بررسی و روی هر خطا **fail** می‌شود:

1. انطباق کامل با `schemas/term-v1.schema.json` (فیلدهای الزامی، الگوی slug، enumها)
2. یکتایی `id` و `slug` در همهٔ شارد‌ها
3. `related_terms` فقط به `id` موجود ارجاع دهد
4. **تغییرناپذیری slug**: slugی که روی شاخهٔ پایه وجود دارد قابل تغییر نیست (URL منبع است)
5. تعریف زیر ۵۰ کاراکتر برای وضعیت `reviewed/published` (در `draft` هشدار است)
6. ترجمهٔ FR/DE/AR عیناً برابر `term_en` نباشد (نشانهٔ ترجمه تنبل)
7. هیچ فیلدی `TODO`/`placeholder` نباشد

هشدارها (که fail نمی‌کنند) در خروجی CI ثبت می‌شوند؛ `translation_alerts.csv` نیز ترجمه‌های انگلیسی مشکوک را پرچم می‌زند.

## فرایند بازبینی (Review)

```
پیشنهاد (Issue/فرم)
  → PR با status: draft → CI سبز → بازبینی نگهدارنده
  → بازبینی داده‌محور (review_level: ai-assisted) → status: reviewed
  → بازبینی متخصص انسانی (review_level: expert + reviewed_by واقعی)
  → status: published        ← تنها با تأیید انسانی ممکن است
```

- **کاربر هرگز مستقیم دادهٔ منتشرشده را تغییر نمی‌دهد**؛ همه‌چیز از PR و CI می‌گذرد.
- ترجمه‌ای که بازبینی نشده را **وارد نکنید**؛ فیلد را حذف/`null` بگذارید. «نداریم» بهتر از «غلط» است.
- برای هر زبان، اولویت با منبع مکتوب (استاندارد، فرهنگ مصوب، کتاب مرجع) است نه مترجم ماشینی.

## سبک نوشتار تعریف

- حداقل ۲ جمله و ۵۰ کاراکتر؛ مفهوم، نه ترجمهٔ لفظی
- کاربرد مهندسی و دامنهٔ اعتبار را بگویید («در فناوری بتن…»، «در اجرای ساختمان…»)
- از «برابر مصوب فرهنگستان» به‌عنوان متن تعریف خودداری کنید (در صورت نیاز، در `references` به مصوبه ارجاع دهید)
- ارجاع‌ها را تا جای ممکن با `type/code/edition` کامل کنید

## قرارداد کامیت و PR

- کامیت‌ها کوچک و تک‌منظوره، با [Conventional Commits](https://www.conventionalcommits.org/):
  `feat(concrete): add slump test`، `fix(translation): correct header brick`، `docs: ...`
- هر PR باید: CI سبز + توضیح منبع داده + فهرست تغییرات دستی باشد.
- با مشارکت، مجوزهای پروژه (MIT برای کد، CC BY-SA 4.0 برای محتوا) را می‌پذیرید.

## رفتار جامعه

مطابق [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — احترام متقابل، نقد داده نه افراد.

سوالی دارید؟ [Issue باز کنید](https://github.com/bmhmdyan279-png/eng-terms-fa/issues).
