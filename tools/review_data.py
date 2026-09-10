"""Curated content review — the single place where editorial decisions live.

Each key is a term id; each value is a partial record that tools/apply_review.py
merges over the committed YAML. ``None`` deletes an optional field.

Editorial rules applied here (and enforced by scripts/validate_content.py)
--------------------------------------------------------------------------
1.  **Honest attribution.** Every entry promoted out of draft carries
    ``review_level: ai-assisted`` and a ``reviewed_by`` that says so. The schema
    forbids ``status: published`` without an expert/committee review level, so
    this pass can never masquerade as human sign-off.
2.  **Verifiable citations only.** Every ``references[].code`` must exist in
    ``data/standards.yaml``, and each reference carries a ``note`` saying *how*
    it supports the entry. An unverifiable citation is a build error.
3.  **Translations: verified or null.** FR/DE/AR are filled only where a
    defensible equivalent exists; anything descriptive is declared in
    ``translation_notes`` instead of pretending to be an attested headword.
4.  **Roots are real.** ``root_fa``/``root_ar`` are filled only when the
    morphology is certain; ``search_aliases`` carry the loanword/site forms that
    practitioners actually type (ویبره، کالیبراسیون، بچینگ…).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

#: Reviewer attribution — deliberately explicit that no human signed off.
REVIEWED_BY = "Qwen (بازبینی دستیار هوشمند)"
REVIEWED_AT = "2026-09-10"
REVIEW_LEVEL = "ai-assisted"

#: How a source supports an entry. Keeping this short and uniform is what makes
#: the citation honest: we claim scope alignment, not a verbatim quotation.
N_SCOPE = "تعریف با دامنهٔ کاربرد این منبع هم‌خوان است؛ ارجاع به معنای نقل مستقیم متن آن نیست."
N_TERM = "منبع واژه‌شناسی و تعریف هنجاری این اصطلاح."
N_ACADEMY = "منبع معادل فارسی مصوب فرهنگستان."
N_BOOK = "واژه و روش آزمایش از این منبع برداشت شده است."
N_CODE = "ضوابط اجرایی و واژگان این مبحث با تعریف هم‌خوان است."


def ref(code: str, note: str = N_SCOPE, section: str | None = None) -> dict:
    """Build a reference, taking its ``type`` from the registry.

    Deriving the type instead of spelling it out is what keeps
    ``validate_content.py`` able to prove every citation resolves: a mismatch
    between the record and the registry becomes impossible by construction.
    """
    from standards import load_registry

    entry = load_registry().get(str(code).strip()) or {}
    out = {"type": entry.get("type") or "standard", "code": code, "note": note}
    if section:
        out["section"] = section
    return out


#: Backwards-compatible aliases; both resolve the type from the registry.
def std(code: str, note: str = N_SCOPE, section: str | None = None) -> dict:
    return ref(code, note, section)


def bk(code: str, note: str = N_BOOK) -> dict:
    return ref(code, note)


def rev(**fields) -> dict:
    """Mark an entry as reviewed with honest, machine-checkable attribution."""
    out = dict(fields)
    out.setdefault("status", "reviewed")
    out.setdefault("review_level", REVIEW_LEVEL)
    out.setdefault("reviewed_by", REVIEWED_BY)
    out.setdefault("reviewed_at", REVIEWED_AT)
    return out


REVIEW: dict[str, dict] = {
    # ======================================================================
    # concrete.yaml — هستهٔ فناوری بتن
    # ======================================================================
    "beton": rev(
        definition_fa=(
            "مصالح ساختمانیِ سنگ‌مصنوعی که از اختلاط سنگدانهٔ ریز و درشت، سیمان هیدرولیک، آب و در "
            "صورت نیاز افزودنی به دست می‌آید. مقاومت فشاری آن بالا و مقاومت کششی‌اش ناچیز است، "
            "به‌همین دلیل معمولاً با آرماتور ترکیب می‌شود. سخت شدن بتن نتیجهٔ واکنش هیدراتاسیون "
            "سیمان است نه خشک شدن؛ از این رو عمل‌آوری مرطوب و پیوسته نقش تعیین‌کننده در دستیابی به "
            "مقاومت طراحی و دوام دارد."
        ),
        synonyms=["سنگ مصنوعی"],
        search_aliases=["بتون", "کانکریت"],
        usage_examples=[
            "مقاومت فشاری مشخصهٔ بتن این پروژه C30 و ردهٔ در معرضی آن XA2 در نظر گرفته شد.",
            "بتن تازه باید پیش از آغاز گیرش، متراکم و بلافاصله عمل‌آوری شود.",
        ],
        root_fa="بتن",
        etymology_fa=(
            "وام‌واژه از فرانسوی béton که خود از لاتین bitumen (قیر، مادهٔ چسباننده) گرفته شده است؛ "
            "در فارسی گاه به اشتباه «بتون» نوشته یا گفته می‌شود."
        ),
        origin_lang="fr",
        plural_fa="بتن‌ها",
        references=[
            std("ACI 116R", N_TERM),
            std("ASTM C125", N_TERM),
            std("آیین‌نامه بتن ایران (آبا)", N_CODE),
            std("EN 206", N_SCOPE),
            bk("نویل — خواص بتن"),
        ],
        related_terms=["siman", "armator", "gravel", "silt", "cement-matrix"],
    ),
    "siman": rev(
        definition_fa=(
            "مادهٔ چسبانندهٔ هیدرولیکی که عمدتاً از پختن ترکیب سنگ آهک و خاک رس (کلینکر) و آسیاب "
            "آن همراه با مقدار تنظیم‌شده‌ای گچ به دست می‌آید؛ گچ زمان گیرش را کنترل می‌کند. "
            "در ترکیب با آب، خمیر سیمان طی واکنش هیدراتاسیون سخت می‌شود و برخلاف چسب‌های معمولی "
            "حتی در زیر آب هم به گیرش و کسب مقاومت ادامه می‌دهد."
        ),
        search_aliases=["سیمنت", "سیمان پرتلند"],
        usage_examples=[
            "نسبت آب به سیمان مهم‌ترین عامل مقاومت و دوام بتن است.",
            "سیمان کیسه‌ای باید روی پالت، دور از رطوبت و حداکثر تا مدت مجاز انبار شود.",
        ],
        root_fa="سیمان",
        etymology_fa=(
            "وام‌واژه از انگلیسی cement یا فرانسوی ciment، هر دو از لاتین caementum به معنای سنگ "
            "خردشده. نام «سیمان پرتلند» از شباهت رنگ بتن سخت‌شده با سنگ پرتلند انگلستان گرفته شده است."
        ),
        origin_lang="en",
        references=[
            std("استاندارد ملی ایران ۳۸۹", N_TERM),
            std("ASTM C150", N_TERM),
            std("ISO 679", N_SCOPE),
            std("ACI 116R", N_TERM),
        ],
        related_terms=["beton", "stone-cement", "cement-matrix", "batching"],
    ),
    "armator": rev(
        definition_fa=(
            "فولاد تقویتی — به شکل میلگرد، خاموت، خرک یا مش — که درون بتن جای می‌گیرد تا مقاومت کششی "
            "و برشی عضو را تأمین کند، زیرا بتن در کشش رفتاری شکننده و ضعیف دارد. آرماتور همچنین "
            "عرض ترک را کنترل می‌کند و نیرو را میان اجزای سازه منتقل می‌سازد. پوشش بتن روی آرماتور "
            "نقش محافظت در برابر خوردگی را دارد و کمینهٔ آن در آیین‌نامه تعیین شده است."
        ),
        synonyms=["فولاد تقویتی", "میلگرد"],
        search_aliases=["میلگردها", "آرماتوربندی", "تسلیح"],
        usage_examples=[
            "طول وصلهٔ پوششی آرماتور باید دست‌کم برابر مقدار محاسبه‌شده در آیین‌نامه باشد.",
            "پیش از بتن‌ریزی، زنگ‌زدگی سست آرماتور تمیز و فاصلهٔ آن از قالب با خرک کنترل شود.",
        ],
        root_fa="آرماتور",
        etymology_fa=(
            "وام‌واژه از فرانسوی armature به معنای زره و سازوبرگ؛ در فارسی هم به خود میلگرد و هم به "
            "عمل آرماتوربندی اطلاق می‌شود. معادل انگلیسی rebar کوتاه‌شدهٔ reinforcing bar است."
        ),
        origin_lang="fr",
        plural_fa="آرماتورها",
        references=[
            std("مبحث نهم مقررات ملی ساختمان", N_CODE),
            std("ACI 318-19", N_SCOPE),
            std("آیین‌نامه بتن ایران (آبا)", N_CODE),
            std("ACI 222R", N_SCOPE),
        ],
        related_terms=["beton", "orlip", "the-vault", "wire-reinforcement", "f-bar-bender", "a-basket", "pin"],
    ),

    # ======================================================================
    # mechanical.yaml — بذر واژگان مکانیک
    # ======================================================================
    "gashtavar": rev(
        definition_fa=(
            "کمیتی برداری که تمایل یک نیرو به چرخاندن جسم حول یک محور یا نقطه را می‌سنجد و برابر است "
            "با حاصل‌ضرب خارجی بردار مکان (از محور تا نقطهٔ اثر نیرو) در بردار نیرو؛ اندازهٔ آن "
            "حاصل‌ضرب نیرو در بازوی عمودی آن است و یکای آن در دستگاه بین‌المللی نیوتن‌متر است."
        ),
        synonyms=["لنگر پیچشی", "ممان پیچش"],
        root_fa="گشت",
        etymology_fa=(
            "ساختهٔ فرهنگستان از «گشت» (چرخش) و پسوند «ـاور»؛ در متون فنی قدیمی‌تر «لنگر پیچشی» یا "
            "وام‌واژهٔ «تورک» (torque) به کار می‌رفت."
        ),
        origin_lang="fa",
        references=[std("هیبی — مکانیک مهندسی", N_TERM), std("مبحث دهم مقررات ملی ساختمان", N_CODE)],
        related_terms=["force", "bending-moment", "shear"],
    ),
    "force": rev(
        definition_fa=(
            "کمیتی برداری که موجب تغییر حرکت، تغییر شکل یا ایجاد شتاب در جسم می‌شود و با قانون دوم "
            "نیوتن (F=ma) تعریف عملیاتی می‌یابد؛ یکای آن در دستگاه بین‌المللی نیوتن است. در مهندسی "
            "ساختمان، بارهای مرده، زنده، باد و زلزله به‌صورت نیرو یا لنگر بر اعضا اثر می‌کنند."
        ),
        synonyms=["قوه"],
        root_fa="نیرو",
        etymology_fa="فارسی اصیل به معنای توان و زور؛ در متون قدیمی‌تر معادل عربی «قوه» رایج بود.",
        origin_lang="fa",
        plural_fa="نیروها",
        references=[std("هیبی — مکانیک مهندسی", N_TERM), std("مبحث ششم مقررات ملی ساختمان", N_CODE)],
        related_terms=["acceleration", "mass", "tension", "bending-moment", "gashtavar"],
    ),
    "friction": rev(
        definition_fa=(
            "نیروی مقاومتی که در سطح تماس دو جسم و در برابر حرکت نسبی آن‌ها ایجاد می‌شود؛ به جنس و "
            "زبری سطح‌ها و نیروی عمودی وارد بر آن‌ها بستگی دارد و با ضریب اصطکاک بیان می‌شود. در "
            "مهندسی خاک، بخشی از مقاومت برشی و ظرفیت باربری پی از اصطکاک جانبی خاک تأمین می‌شود."
        ),
        synonyms=["سایش"],
        root_fa="اصطکاک",
        etymology_fa="وام‌واژهٔ عربی از باب افتعال به معنای ساییده‌شدن دو چیز بر یکدیگر.",
        origin_lang="ar",
        references=[std("هیبی — مکانیک مهندسی", N_TERM), std("مبحث هفتم مقررات ملی ساختمان", N_CODE)],
        related_terms=["force", "weight", "tension"],
    ),
    "acceleration": rev(
        definition_fa=(
            "نرخ تغییرات سرعت نسبت به زمان؛ کمیتی برداری با یکای متر بر مجذور ثانیه. در دینامیک "
            "سازه‌ها شتاب مبنای محاسبهٔ نیروی زلزله است و معمولاً به‌صورت بخشی از شتاب گرانش (g) "
            "بیان می‌شود."
        ),
        root_fa="شتاب",
        etymology_fa="فارسی اصیل؛ معادل مصوب فرهنگستان برای acceleration که در متون قدیمی‌تر «تعجیل» خوانده می‌شد.",
        origin_lang="fa",
        plural_fa="شتاب‌ها",
        references=[std("هیبی — مکانیک مهندسی", N_TERM), std("مبحث ششم مقررات ملی ساختمان", N_CODE)],
        related_terms=["force", "velocity", "inertia", "mass"],
    ),
    "mass": rev(
        definition_fa=(
            "مقدار مادهٔ تشکیل‌دهندهٔ یک جسم و معیار مقاومت آن در برابر شتاب‌گیری؛ یکای آن کیلوگرم "
            "است. جرم خاصیتی ذاتی و مستقل از مکان است، در حالی که وزن نیرویی وابسته به میدان گرانش "
            "است — تفاوتی که در زبان روزمره اغلب نادیده گرفته می‌شود."
        ),
        antonyms=["بی‌وزنی"],
        root_fa="جرم",
        root_ar="ج-ر-م",
        etymology_fa="وام‌واژهٔ عربی به معنای جسم و تن؛ در فارسی روزمره به‌اشتباه به‌جای «وزن» به کار می‌رود.",
        origin_lang="ar",
        plural_fa="جرم‌ها",
        references=[std("هیبی — مکانیک مهندسی", N_TERM)],
        related_terms=["weight", "inertia", "momentum", "center-of-gravity"],
    ),
    "velocity": rev(
        definition_fa=(
            "نرخ جابه‌جایی جسم نسبت به زمان؛ کمیتی برداری با یکای متر بر ثانیه که به اندازهٔ آن "
            "«تندی» گفته می‌شود. در مکانیک سیال‌ها و پمپاژ بتن، سرعت جریان بر افت فشار و خطر "
            "جداشدگی دانه‌ها اثر مستقیم دارد."
        ),
        synonyms=["تندی"],
        root_fa="سرعت",
        root_ar="س-ر-ع",
        etymology_fa="وام‌واژهٔ عربی؛ در متون فنی میان «سرعت» (برداری) و «تندی» (اسکالر) تمایز گذاشته می‌شود.",
        origin_lang="ar",
        plural_fa="سرعت‌ها",
        references=[std("هیبی — مکانیک مهندسی", N_TERM)],
        related_terms=["acceleration", "momentum"],
    ),
    "inertia": rev(
        definition_fa=(
            "خاصیت مقاومت جسم در برابر تغییر وضعیت سکون یا حرکت یکنواخت خود؛ هرچه جرم جسم بیشتر "
            "باشد اینرسی آن بیشتر است. در تحلیل لرزه‌ای، نیروی زلزله از شتاب‌دادن به جرم (لختی) "
            "سازه پدید می‌آید."
        ),
        synonyms=["لختی", "قصور ذاتی"],
        root_fa="اینرسی",
        etymology_fa=(
            "وام‌واژه از لاتین inertia (بی‌حرکتی)؛ معادل مصوب فرهنگستان «لَختی» است و در متن‌های "
            "قدیمی‌تر «قصور ذاتی» به کار می‌رفته است."
        ),
        origin_lang="la",
        references=[std("هیبی — مکانیک مهندسی", N_TERM)],
        related_terms=["mass", "acceleration"],
    ),
    "momentum": rev(
        definition_fa=(
            "حاصل‌ضرب جرم جسم در سرعت آن؛ کمیتی برداری که در تحلیل برخوردها و بارهای ضربه‌ای پایسته "
            "می‌ماند. یکای آن کیلوگرم‌متر بر ثانیه است و تغییر آن نسبت به زمان برابر با نیروی "
            "برآیند وارد بر جسم است."
        ),
        synonyms=["اندازهٔ حرکت", "کمیت حرکت"],
        root_fa="تکانه",
        etymology_fa="«تکانه» معادل مصوب فرهنگستان است؛ پیش از آن «اندازهٔ حرکت» و وام‌واژهٔ «ممنتوم» رایج بود.",
        origin_lang="fa",
        references=[std("هیبی — مکانیک مهندسی", N_TERM)],
        related_terms=["mass", "velocity", "force"],
    ),
    "center-of-gravity": rev(
        definition_fa=(
            "نقطه‌ای که برآیند نیروهای وزن اجزای جسم در آن متمرکز فرض می‌شود؛ در اجسام همگن و "
            "متقارن بر مرکز هندسی منطبق است. موقعیت آن نسبت به سطح اتکا، پایداری سازه و تجهیزاتی "
            "مانند جرثقیل و قالب را تعیین می‌کند."
        ),
        synonyms=["گرانیگاه", "نقطهٔ ثقل"],
        root_fa="ثقل",
        root_ar="ث-ق-ل",
        etymology_fa="«ثقل» وام‌واژهٔ عربی به معنای سنگینی است؛ معادل فارسی مصوب فرهنگستان «گرانیگاه» است.",
        origin_lang="ar",
        references=[std("هیبی — مکانیک مهندسی", N_TERM)],
        related_terms=["mass", "weight", "pendant"],
    ),
    "bending-moment": rev(
        definition_fa=(
            "اثر چرخشی نیروهای داخلی یک مقطع در برابر خمش؛ برابر با حاصل‌ضرب نیرو در فاصلهٔ عمودی آن "
            "تا مقطع است و یکای آن نیوتن‌متر است. نمودار لنگر خمشی در تیرها محل بحرانی طراحی را "
            "مشخص می‌کند و در بتن مسلح، آرماتور کششی برای مقابله با آن جای می‌گیرد."
        ),
        synonyms=["ممان خمشی", "لنگر خمش"],
        abbrev_en="M",
        root_fa="لنگر",
        etymology_fa=(
            "«لنگر» در فارسی فنی برای moment به کار می‌رود؛ «لنگر خمشی» معادل bending moment است و "
            "«ممان خمشی» نیز رایج است. با «لنگر» به معنای anchor هم‌شکل ولی متفاوت است."
        ),
        origin_lang="fa",
        references=[
            std("بیِر و جانستون — مقاومت مصالح", N_TERM),
            std("مبحث نهم مقررات ملی ساختمان", N_CODE),
        ],
        related_terms=["shear", "gashtavar", "tension", "strain", "bending", "concrete-beam"],
    ),
    "shear": rev(
        definition_fa=(
            "تنش یا نیرویی موازی با سطح مقطع که تمایل به بریدن یا لغزاندن لایه‌های جسم نسبت به "
            "یکدیگر دارد. در تیرهای بتنی با خاموت و در دیوارهای برشی با جان عضو مهار می‌شود و معمولاً "
            "شکست آن ترد و بدون اخطار قبلی است، پس در طراحی مقدم بر خمش کنترل می‌شود."
        ),
        synonyms=["تنش برشی"],
        root_fa="برش",
        etymology_fa="اسم مصدر از «بریدن»؛ در مقاومت مصالح برای shear و در کارگاه برای عمل برش فولاد به کار می‌رود.",
        origin_lang="fa",
        references=[
            std("بیِر و جانستون — مقاومت مصالح", N_TERM),
            std("مبحث نهم مقررات ملی ساختمان", N_CODE),
        ],
        related_terms=["bending-moment", "tension", "zigzag", "gashtavar"],
    ),
    "fatigue": rev(
        definition_fa=(
            "کاهش تدریجی مقاومت ماده زیر بارهای تکراری و متناوبی که هر یک از حد مقاومت ایستا کمترند؛ "
            "شکست خستگی معمولاً از یک عیب ریز یا تمرکز تنش آغاز می‌شود و با رشد ترک پیش می‌رود. "
            "عامل اصلی شکست در ماشین‌آلات، پل‌ها و سازه‌های تحت بار چرخه‌ای است."
        ),
        synonyms=["کلال", "خستگی مصالح"],
        root_fa="خستگی",
        etymology_fa="فارسی اصیل؛ معادل عربی آن «کَلال» است که در متن‌های تخصصی هم دیده می‌شود.",
        origin_lang="fa",
        references=[
            std("بیِر و جانستون — مقاومت مصالح", N_TERM),
            std("EN 1992-1-1", N_SCOPE),
        ],
        related_terms=["tension", "bending-moment", "strain"],
    ),
    "modulus-of-elasticity": rev(
        definition_fa=(
            "نسبت تنش به کرنش در ناحیهٔ کشسان ماده و معیار سختی آن؛ برای فولاد ساختمانی حدود "
            "۲۰۰ گیگاپاسکال و برای بتن معمولی حدود ۲۵ تا ۳۰ گیگاپاسکال است. مدول الاستیسیتهٔ بتن به "
            "مقاومت فشاری، نوع سنگدانه و سن بتن بستگی دارد و با آزمون بارگذاری ایستا اندازه‌گیری می‌شود."
        ),
        synonyms=["مدول یانگ", "مدول ارتجاعی", "مدول کشسانی"],
        abbrev_en="E",
        root_fa="الاستیسیته",
        etymology_fa=(
            "«الاستیسیته» وام‌واژه از فرانسوی élasticité است؛ معادل مصوب فرهنگستان «کشسانی» است، پس "
            "«مدول الاستیسیته» = «مدول کشسانی» = «مدول یانگ»."
        ),
        origin_lang="fr",
        references=[
            std("بیِر و جانستون — مقاومت مصالح", N_TERM),
            std("ASTM C469", N_SCOPE),
            bk("نویل — خواص بتن"),
        ],
        related_terms=["strain", "elasticity", "tension", "bending-moment"],
    ),
    "strain": rev(
        definition_fa=(
            "تغییر شکل نسبی جسم نسبت به ابعاد اولیهٔ آن تحت اثر تنش؛ کمیتی بی‌بعد که در ناحیهٔ کشسان "
            "با تنش نسبت مستقیم دارد (قانون هوک). کرنش کششی باعث طویل‌شدن و کرنش فشاری باعث کوتاهش "
            "الیاف می‌شود و در بتن، کرنش جمع‌شدگی و خزش نیز بدون بار خارجی پدید می‌آید."
        ),
        synonyms=["تغییرشکل نسبی", "کرنش نسبی"],
        antonyms=["تنش"],
        root_fa="کرنش",
        etymology_fa=(
            "«کرنش» در برابر «تنش» (stress) ساخته شده است: تنش نیرو بر واحد سطح است و کرنش تغییر "
            "طول نسبی و بی‌بعد."
        ),
        origin_lang="fa",
        references=[
            std("بیِر و جانستون — مقاومت مصالح", N_TERM),
            std("ASTM C469", N_SCOPE),
            std("ASTM C157", N_SCOPE),
        ],
        related_terms=["modulus-of-elasticity", "tension", "elasticity", "bending"],
    ),
    "weight": rev(
        definition_fa=(
            "نیروی وارد بر جسم از سوی میدان گرانش؛ حاصل‌ضرب جرم در شتاب گرانش است و یکای آن نیوتن "
            "است. در ساختمان، «وزن مرده» شامل وزن اعضای سازه‌ای و پوشش‌ها و «وزن زنده» شامل بارهای "
            "متحرک بهره‌برداری می‌شود."
        ),
        synonyms=["سنگینی"],
        antonyms=["بی‌وزنی", "سبکی"],
        root_fa="وزن",
        root_ar="و-ز-ن",
        etymology_fa=(
            "وام‌واژهٔ عربی از ریشهٔ «و-ز-ن» (سنجیدن)؛ در فارسی هم برای جرم و هم برای وزن به کار "
            "می‌رود، ولی در مکانیک این دو متفاوت‌اند."
        ),
        origin_lang="ar",
        references=[std("هیبی — مکانیک مهندسی", N_TERM), std("مبحث ششم مقررات ملی ساختمان", N_CODE)],
        related_terms=["mass", "center-of-gravity", "force"],
    ),

    # ======================================================================
    # academy.yaml — واژه‌های مصوب فرهنگستان (کتاب آزمایشات فناوری بتن)
    # ======================================================================
    "digital": rev(
        term_en="digital",
        synonyms=["دیجیتالی", "عددی"],
        search_aliases=["دیجیتال"],
        usage_examples=["دماسنج دیجیتال نمونه‌ها را در بازهٔ عمل‌آوری به‌صورت پیوسته ثبت می‌کند."],
        root_fa="رقم",
        root_ar="ر-ق-م",
        etymology_fa=(
            "واژه‌ای فارسی بر پایهٔ «رقم» (نشانه، عدد) — که خود وام‌واژه‌ای عربی از ریشهٔ «ر-ق-م» "
            "است — و معادل مصوب فرهنگستان برای digital؛ وام‌واژهٔ «دیجیتال» از numérique/digital در "
            "گفتار کارگاهی رایج‌تر است."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY)],
        related_terms=["calibration", "control", "protocol"],
    ),
    "oven": rev(
        term_en="oven",
        synonyms=["کورهٔ خشک‌کن", "فرن"],
        search_aliases=["اون", "فر آزمایشگاهی", "کوره"],
        usage_examples=["نمونه‌های سنگدانه تا رسیدن به وزن ثابت در تاوَن ۱۱۰ درجهٔ سانتی‌گراد خشک می‌شوند."],
        root_fa="تاوَن",
        etymology_fa=(
            "«تاوَن» معادل مصوب فرهنگستان برای oven است و در فارسی به کوره/اجاق پخت نان هم گفته "
            "می‌شود؛ در آزمایشگاه فناوری بتن به کورهٔ خشک‌کن با کنترل دقیق دما اطلاق می‌گردد."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY)],
        related_terms=["calibration", "pycnometer", "protocol"],
    ),
    "mesh-sieve-size": rev(
        term_en="mesh / sieve size",
        synonyms=["شمارهٔ الک", "اندازهٔ الک"],
        search_aliases=["مش", "الک", "غربال", "سایز الک", "دانه‌بندی"],
        usage_examples=["دانه‌بندی سنگدانه با مجموعه‌ای از الک‌های استاندارد و گزارش درصد عبوری انجام می‌شود."],
        root_fa="غربال",
        etymology_fa=(
            "«غربال» وام‌واژه‌ای کهن به معنای الک است؛ «اندازهٔ غربالی» معادل مصوب فرهنگستان برای "
            "mesh/sieve size است و به گشادگی چشمهٔ الک اشاره دارد."
        ),
        origin_lang="fa",
        plural_fa="اندازه‌های غربالی",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY),
            std("ASTM C136", N_SCOPE),
            std("ASTM C33", N_SCOPE),
        ],
        related_terms=["gravel", "silt", "cumin", "blockage"],
    ),
    "calibration": rev(
        term_en="calibration",
        synonyms=["کالیبراسیون", "درجه‌بندی"],
        search_aliases=["کالیبره", "کالیبره کردن"],
        usage_examples=["دستگاه فشار بتن باید در بازه‌های زمانی تعیین‌شده با نمونهٔ مرجع واسنجیده شود."],
        root_fa="سنجیدن",
        etymology_fa=(
            "«واسنجیدن» معادل مصوب فرهنگستان برای calibration است؛ وام‌واژهٔ «کالیبراسیون» از "
            "فرانسوی calibration در کارگاه و آزمایشگاه رایج‌تر است."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY)],
        related_terms=["control", "tolerance", "oven"],
    ),
    "depot": rev(
        term_en="depot",
        synonyms=["انبار مصالح"],
        search_aliases=["دپو", "انبار"],
        usage_examples=["آمادگاه سنگدانه باید طوری پوشیده شود که رطوبت آن در بازهٔ مصرف تغییر نکند."],
        root_fa="آماد",
        etymology_fa=(
            "«آمادگاه» از «آماد» (آمادگی) و پسوند مکان «ـگاه» ساخته شده و معادل مصوب فرهنگستان برای "
            "depot است؛ وام‌واژهٔ «دپو» از فرانسوی dépôt در کارگاه‌ها رایج است."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY)],
        related_terms=["batching", "control", "gravel"],
    ),
    "jig-jigging": rev(
        term_en="jig / jigging",
        synonyms=["جیک‌جیک", "میله‌کوبی"],
        search_aliases=["جیگ", "جیگینگ", "تراکم دستی"],
        usage_examples=["متراکم‌سازی نمونهٔ بتن در قالب با سیخ‌کوبی یا جیک روی میز لرزان انجام می‌شود."],
        root_fa="جیک",
        etymology_fa=(
            "«جیک» صورت فارسی‌شدهٔ jig است و به عمل کوبیدن و متناوب لرزاندن برای خروج هوای محبوس "
            "گفته می‌شود؛ در متون فارسی «میله‌کوبی» و «سیخ‌زدن» هم به کار می‌رود."
        ),
        origin_lang="en",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), std("ASTM C192", N_SCOPE)],
        related_terms=["vibrator", "frequency", "tamper", "to-pump"],
    ),
    "cement-matrix": rev(
        term_en="cement paste / matrix",
        synonyms=["ماتریس سیمانی", "خمیر سیمان"],
        search_aliases=["آژند سیمانی", "ماتریس"],
        usage_examples=["کیفیت آژند سیمانی، به‌ویژه نسبت آب به سیمان، دوام بتن را تعیین می‌کند."],
        root_fa="آژند",
        etymology_fa=(
            "«آژند» واژه‌ای فارسی به معنای پیوند و لایهٔ پرکننده است که فرهنگستان آن را برای "
            "matrix/cement paste برگزیده؛ در متون مهندسی «ماتریس» و «خمیر سیمان» نیز رایج است."
        ),
        origin_lang="fa",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY),
            std("ACI 116R", N_TERM),
        ],
        related_terms=["siman", "beton", "sealing"],
    ),
    "control": rev(
        term_en="control",
        synonyms=["کنترل", "واپایی"],
        search_aliases=["کنترل کیفیت", "QC"],
        usage_examples=[
            "واپایش کیفیت بتن تازه شامل اسلامپ، دما و هوای بتن پیش از تخلیه در قالب است.",
        ],
        root_fa="پاییدن",
        etymology_fa=(
            "«واپایش» معادل مصوب فرهنگستان برای control است، از «پاییدن» (نگاه داشتن و نگریستن)؛ "
            "وام‌واژهٔ «کنترل» از فرانسوی contrôle در متون اجرایی غالب است."
        ),
        origin_lang="fa",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY),
            std("ACI 301", N_SCOPE),
        ],
        related_terms=["tolerance", "calibration", "protocol", "batch"],
    ),
    "protocol": rev(
        term_en="protocol",
        synonyms=["شیوه‌نامهٔ آزمایش"],
        search_aliases=["پروتکل"],
        usage_examples=["تشریفات آزمون مقاومت فشاری، سرعت بارگذاری و ابعاد آزمونه را تعیین می‌کند."],
        root_fa="تشریفات",
        etymology_fa=(
            "«تشریفات» معادل مصوب فرهنگستان برای protocol در معنای آیین‌اجرایی است؛ وام‌واژهٔ "
            "«پروتکل» از فرانسوی protocole در متون آزمایشگاهی رایج‌تر است."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), std("ASTM C192", N_SCOPE)],
        related_terms=["control", "calibration", "tolerance", "batch"],
    ),
    "batch": rev(
        term_en="batch",
        synonyms=["دستهٔ بتن", "پیمانه"],
        search_aliases=["بچ"],
        usage_examples=["برای هر ۵۰ متر مکعب بتن یا هر دسته، دست‌کم یک مجموعه آزمونه گرفته می‌شود."],
        root_fa="دسته",
        etymology_fa=(
            "«دسته» معادل مصوب فرهنگستان برای batch است؛ در کارگاه وام‌واژهٔ «بچ» و ترکیب «بچینگ» "
            "(batching plant) رایج است."
        ),
        origin_lang="fa",
        plural_fa="دسته‌ها",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            std("ASTM C94", N_SCOPE),
            std("ACI 304R", N_SCOPE),
        ],
        related_terms=["batching", "control", "tolerance", "depot"],
    ),
    "batching": rev(
        term_en="batching",
        synonyms=["پیمانه‌گیری", "توزین مصالح"],
        search_aliases=["بچینگ", "بچینگ پلانت", "کارخانهٔ بتن"],
        usage_examples=["در بچینگ، مصالح بر پایهٔ وزن توزین می‌شوند، نه حجم؛ تلورانس توزین در استاندارد تعیین شده است."],
        root_fa="مخلوط",
        etymology_fa=(
            "«مخلوط‌ساز» معادل مصوب فرهنگستان برای batching است؛ در گفتار اجرایی «بچینگ» و «بچینگ "
            "پلانت» به کار می‌رود."
        ),
        origin_lang="fa",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            std("ACI 211.1", N_SCOPE),
            std("ACI 304R", N_SCOPE),
            std("ASTM C94", N_SCOPE),
        ],
        related_terms=["batch", "siman", "depot", "tolerance"],
    ),
    "tolerance": rev(
        term_en="tolerance",
        synonyms=["رواداری", "حد مجاز انحراف"],
        search_aliases=["تلورانس", "تلرانس"],
        usage_examples=["رواداری افت اسلامپ در تحویل بتن و رواداری ابعاد قالب باید در مشخصات ذکر شود."],
        root_fa="رواداری",
        etymology_fa=(
            "«رواداری» معادل مصوب فرهنگستان برای tolerance است؛ «تحمل» و وام‌واژهٔ «تلورانس» نیز در "
            "متون اجرایی دیده می‌شود."
        ),
        origin_lang="fa",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            std("ACI 301", N_SCOPE),
            std("ASTM C94", N_SCOPE),
        ],
        related_terms=["control", "batch", "calibration", "drop"],
    ),
    "frequency": rev(
        term_en="frequency",
        synonyms=["فرکانس", "بسامد نوسان"],
        search_aliases=["فرکانس"],
        usage_examples=["بسامد ویبرهٔ داخلی معمولاً در بازهٔ ۱۰۰ تا ۱۵۰ هرتز انتخاب می‌شود."],
        root_fa="بسامد",
        etymology_fa=(
            "«بسامد» معادل مصوب فرهنگستان برای frequency است (از «بس» + «آمدن» = بسامدِ آمد و شد)؛ "
            "وام‌واژهٔ «فرکانس» در گفتار مهندسی رایج‌تر است."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), std("ACI 309R", N_SCOPE)],
        related_terms=["vibrator", "jig-jigging", "tamper"],
    ),
    "vibrator": rev(
        term_en="vibrator",
        synonyms=["لرزانندهٔ بتن"],
        search_aliases=["ویبره", "ویبراتور", "ویبراتو", "شیلنگ ویبره"],
        usage_examples=[
            "ویبره باید عمودی در بتن فرو برود و تا خروج حباب‌های هوا و برق‌افتادن سطح ادامه یابد.",
            "ویبره‌زدن بیش از حد باعث جداشدگی دانه‌ها و تجمع شیرهٔ سیمان در سطح می‌شود.",
        ],
        root_fa="لرز",
        etymology_fa=(
            "«لرزاننده» معادل مصوب فرهنگستان برای vibrator است (از «لرزیدن»)؛ در کارگاه وام‌واژهٔ "
            "«ویبره» و «ویبراتور» از فرانسوی vibreur غالب است."
        ),
        origin_lang="fa",
        references=[
            bk("کتاب آزمایشات فناوری بتن", N_BOOK),
            std("ACI 309R", N_TERM),
            std("ASTM C192", N_SCOPE),
        ],
        related_terms=["frequency", "jig-jigging", "tamper", "to-pump"],
    ),
    "gallery": rev(
        term_en="gallery",
        synonyms=["راهروی بازرسی"],
        search_aliases=["گالری"],
        usage_examples=["در بدنهٔ سد، تالارها برای زهکشی آب نفوذی و نصب تجهیزات پایش به کار می‌روند."],
        root_fa="تالار",
        etymology_fa=(
            "«تالار» واژه‌ای فارسی به معنای تالار و راهروی سرپوشیده است که فرهنگستان آن را برای gallery "
            "برگزیده؛ وام‌واژهٔ «گالری» در متون سدسازی نیز دیده می‌شود."
        ),
        origin_lang="fa",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), bk("فرهنگ واژه‌های مصوب فرهنگستان", N_ACADEMY)],
        related_terms=["the-well", "sealing", "shell"],
    ),
    "pycnometer": rev(
        term_en="pycnometer",
        synonyms=["چگالی‌سنج"],
        search_aliases=["پیکومتر", "پیکونومتر", "بالن چگالی"],
        usage_examples=["وزن مخصوص سنگدانهٔ ریز با بطری چگالی و بر پایهٔ ASTM C128 تعیین می‌شود."],
        root_fa="چگالی",
        etymology_fa=(
            "«بطری چگالی» معادل مصوب فرهنگستان برای pycnometer است؛ این واژه از یونانی pyknos "
            "(چگال، فشرده) و metron (سنجش) ساخته شده است."
        ),
        origin_lang="el",
        references=[bk("کتاب آزمایشات فناوری بتن", N_BOOK), std("ASTM C128", N_SCOPE), std("ASTM C127", N_SCOPE)],
        related_terms=["oven", "gravel", "silt"],
    ),
}
