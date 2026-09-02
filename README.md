# 🏗️ دیکشنری تخصصی مهندسی

## 📖 دربارهٔ پروژه

این پروژه یک **دیکشنری تخصصی مهندسی** با تمرکز بر واژگان فنی و علمی در حوزه‌های **عمران، مکانیک، معماری و فناوری بتن** است.

## Current Status (v0.1 - Work in Progress)
- ✅ Data-driven architecture (YAML → MkDocs)
- ✅ CI/CD pipeline
- ⚠️  Content review in progress
- ⚠️  Translation quality check ongoing
- 🚧 Search: MkDocs default (Pagefind coming soon)

### ویژگی‌ها

<!-- موقتاً غیرفعال شد — فایل `docs/manifest.webmanifest` وجود ندارد؛ ادعای PWA پس از پیاده‌سازی واقعی بازمی‌گردد:
- 🌐 **نسخهٔ وب PWA** – قابل نصب روی گوشی، کارکرد آفلاین
-->
- 📱 **واکنش‌گرا (Responsive)** – بهینه برای موبایل و تبلت
<!-- موقتاً غیرفعال شد — Pagefind در `mkdocs.yml` فعال نیست و ایندکس آن در CI ساخته نمی‌شود:
- 🔍 **جستجوی پیشرفتهٔ فارسی** – با پشتیبانی از Pagefind
-->
- 🌍 **معادل‌های چندزبانه**: انگلیسی، فرانسوی، آلمانی، عربی
- 📚 **اتصال به منابع تخصصی** – شامل واژگان کتاب «آزمایشات فناوری بتن»
<!-- موقتاً غیرفعال شد — فایل `scripts/validate_data.py` هنوز وجود ندارد:
- ✅ **اعتبارسنجی خودکار داده‌ها** – تضمین کیفیت و کامل بودن تعاریف
-->
- 🤝 **مشارکت آسان** – فرم پیشنهاد واژه (فنی و غیرفنی)

### کیفیت داده‌ها

تمام واژگان دارای:
- ✅ **تعاریف تخصصی و دقیق** (حداقل ۲-۳ خط با جزئیات فنی)
- ✅ **ترجمه کامل ۴ زبانه** (انگلیسی، فرانسوی، آلمانی، عربی)
- ✅ **ارجاعات به استانداردها** (ACI، ASTM، استانداردهای ملی ایران)
<!-- موقتاً غیرفعال شد — فایل `scripts/validate_data.py` وجود ندارد:
- ✅ **سیستم اعتبارسنجی خودکار** (`scripts/validate_data.py`) برای جلوگیری از ورود داده‌های بی‌کیفیت
-->

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

## 📂 ساختار پروژه

```
eng-terms-fa/
├── .github/workflows/    # CI/CD (خودکار)
├── data/
│   └── terms.yaml        # تمام واژگان در این فایل (YAML)
├── docs/                 # سایت MkDocs
│   ├── assets/           # CSS, JS
│   └── terms/            # صفحات واژگان (خودکار ساخته می‌شود)
├── scripts/
│   ├── build_pages.py    # تبدیل terms.yaml به Markdown
│   ├── cleanup_terms.py  # پاکسازی داده‌ها
│   └── fix_old_links.py  # اصلاح لینک‌های قدیمی
├── tests/                # تست‌های واحد
├── mkdocs.yml            # تنظیمات اصلی
└── requirements.txt      # وابستگی‌های پایتون
```

## ✍️ نحوهٔ افزودن واژهٔ جدید

۱. فایل `data/terms.yaml` را باز کنید.

۲. یک واژهٔ جدید به این شکل اضافه کنید:

```yaml
- term_fa: واژهٔ فارسی
  term_en: English Word
  term_fr: Mot français
  term_de: Deutsches Wort
  term_ar: کلمة عربیة
  category: دسته‌بندی (مثلاً: مصالح ساختمانی، سازه‌های بتنی، مکانیک)
  definition: |
    تعریف تخصصی و دقیق واژه با جزئیات فنی.
    باید حداقل ۲-۳ خط باشد و شامل کاربردهای مهندسی باشد.
    از عبارات عمومی مانند "برابر مصوب فرهنگستان" خودداری کنید.
  references:
    - استاندارد یا کتاب مرجع (مثلاً: ACI 318-19، ASTM C136)
    - منبع دوم (اختیاری)
  slug: slug-unique
  featured_book: true  # اگر در کتاب تخصصی شما وجود دارد
```

<!-- موقتاً حذف شد — اسکریپت `validate_data.py` وجود ندارد:
۳. اعتبارسنجی کنید:

```bash
python scripts/validate_data.py
```
-->

۳. صفحات را بازسازی کنید:

```bash
python scripts/build_pages.py
```

۴. تغییرات را کامیت و پوش کنید.

۵. GitHub Actions به‌صورت خودکار سایت را به‌روز می‌کند.

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم!

**الزامات مشارکت:**
- تعاریف باید **تخصصی، دقیق و حداقل ۲-۳ خط** باشند
- ترجمه **تمام ۴ زبان** (انگلیسی، فرانسوی، آلمانی، عربی) الزامی است
- از عبارات عمومی مانند "برابر مصوب فرهنگستان" خودداری کنید
- **ارجاع به استانداردها** (ACI، ASTM، DIN، استانداردهای ملی) ترجیح داده می‌شود

### راه‌های مشارکت

- [فرم پیشنهاد واژه](https://bmhmdyan279-png.github.io/eng-terms-fa/contribute-form/)
- [راهنمای مشارکت](CONTRIBUTING.md)
- [کد رفتار](CODE_OF_CONDUCT.md)

## 📜 مجوز

- **کد:** MIT License (LICENSE-CODE.md)
- **محتوا (واژگان):** Creative Commons BY-SA 4.0 (LICENSE-CONTENT.md)

---
**توسعه‌دهنده:** [bmhmdyan279-png](https://github.com/bmhmdyan279-png)

**📧 تماس:** برای سوالات فنی یا پیشنهادات همکاری، Issue باز کنید.
