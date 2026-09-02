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
- مدخل کامل با ارجاع به استاندارد/کتاب و ترجمه‌های بازبینی‌شده
- بازبینی تخصصی یک مدخل (`status: reviewed` + `reviewed_by` + `reviewed_at`)

## راه‌اندازی محلی

```bash
git clone https://github.com/bmhmdyan279-png/eng-terms-fa.git
cd eng-terms-fa
pip install -r requirements.txt
python scripts/build_pages.py        # تولید صفحات از داده‌ها
python scripts/generate_api.py       # (اختیاری) API محلی
mkdocs serve                         # http://localhost:8000
```

## فرمت دقیق یک مدخل (schema: term-v1)

```yaml
- id: corner-brick                # یکتا، پایدار، برابر با slug
  term_fa: آجر نبشی
  term_en: corner brick
  term_fr: null                   # ترجمهٔ بازبینی‌نشده = null (نه ترجمهٔ ماشینی!)
  term_de: null
  term_ar: null
  pos: noun                       # noun | verb | adjective | phrase
  domain: [construction]          # فقط دامنه‌های data/terms/_meta.yaml
  definition_fa: |
    آجری که برای ساختن نبش و گوشهٔ دیوار به کار می‌رود؛
    معمولاً با چرخاندن یا برش آجر کامل در محل نصب می‌شود.
    (حداقل ۵۰ کاراکتر؛ تخصصی، بدون عبارت «برابر مصوب فرهنگستان»)
  references:                     # اختیاری اما برای مدخل مرجع الزامی
    - type: standard              # standard | book | other
      code: مبحث پنجم مقررات ملی ساختمان
  related_terms: [header-brick]   # فقط idهای موجود
  status: draft                   # draft | reviewed | published
  slug: corner-brick              # تغییرناپذیر؛ URL پایدار است
```

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
پیشنهاد (Issue/فرم) → PR با status: draft → CI سبز → بازبینی نگهدارنده
→ (برای مرجع شدن) بازبینی متخصص + reviewed_by/reviewed_at → status: reviewed
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
