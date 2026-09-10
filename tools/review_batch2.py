"""Content review — batch 2: اصطلاحات ساختمانی و کارگاهی (بخش ۱ از ۲).

معنی‌شناسی این واژه‌ها در همین بازبینی با دو واژه‌نامهٔ صنفی راستی‌آزمایی شد
(رجیستری: «واژه‌نامهٔ اصطلاحات سنتی آجرکاری» و «واژه‌نامهٔ اصطلاحات کارگاهی
عمران»). هرجا متن داده با منبع نمی‌خواند، تعریف اصلاح شد و در etymology_fa
مستند گردید.
"""

from review_data import (
    N_ACADEMY,
    N_BOOK,
    N_CODE,
    N_SCOPE,
    N_TERM,
    REVIEW,
    bk,
    rev,
    std,
)

#: Reference bundles reused across masonry entries.
M8 = std("مبحث هشتم مقررات ملی ساختمان", N_CODE)
M9 = std("مبحث نهم مقررات ملی ساختمان", N_CODE)
M10 = std("مبحث دهم مقررات ملی ساختمان", N_CODE)
M7 = std("مبحث هفتم مقررات ملی ساختمان", N_CODE)
M5 = std("مبحث پنجم مقررات ملی ساختمان", N_SCOPE)
M6 = std("مبحث ششم مقررات ملی ساختمان", N_CODE)
M12 = std("مبحث دوازدهم مقررات ملی ساختمان", N_CODE)
M4 = std("مبحث چهارم مقررات ملی ساختمان", N_CODE)
BRICK = std("استاندارد ملی ایران ۷", N_SCOPE)
PUB55 = std("نشریه ۵۵", N_CODE)
ABA = std("آیین‌نامه بتن ایران (آبا)", N_CODE)
ACI318 = std("ACI 318-19", N_SCOPE)
EN_MASONRY = std("EN 1996-1-1", N_SCOPE)
EN_BRICK = std("EN 771-1", N_SCOPE)
TRAD = bk("واژه‌نامهٔ اصطلاحات سنتی آجرکاری", "منبع معنی‌شناسی این واژهٔ سنتی؛ مرجع هنجاری نیست.")
SITE = bk("واژه‌نامهٔ اصطلاحات کارگاهی عمران", "منبع اصطلاح کارگاهی؛ مرجع هنجاری نیست.")
MECH = bk("هیبی — مکانیک مهندسی", N_TERM)
STRENGTH = bk("بیِر و جانستون — مقاومت مصالح", N_TERM)

#: «معادل توصیفی» = معادلی که سرِواژهٔ راستی‌آزمایی‌شده در آن زبان ندارد و
#: به‌جای تهی‌گذاشتن، با شفافیت توصیف شده است. این note کنار همان ترجمه نمایش
#: داده می‌شود تا خواننده بداند با یک واژهٔ مصوب روبه‌رو نیست.
N_COINED = "معادل توصیفی؛ سرِواژهٔ مصوب این زبان برای این اصطلاح راستی‌آزمایی نشد."

BATCH = {
    # ------------------------------------------------------------------ آب و عایق
    "sealing": rev(
        definition_fa=(
            "عملیات جلوگیری از نفوذ آب یا رطوبت به درون سازه یا فضاهای داخلی ساختمان، که با استفاده "
            "از مواد عایق (نظیر قیر، ایزوگام و غشاهای پلیمری) و رعایت جزئیات اجرایی در نقاط حساس "
            "مانند پی، پشت‌بام و سرویس‌های بهداشتی انجام می‌شود. اجرای نادرست آن به زنگ‌زدگی "
            "آرماتور، رشد قارچ و کاهش عمر مفید سازه می‌انجامد."
        ),
        synonyms=["آب‌بندی", "عایق‌کاری رطوبتی"],
        search_aliases=["واترپروف", "ایزوگام", "قیرگونی"],
        usage_examples=[
            "آب‌بندی پشت‌بام با قیر و غشای پلیمری اجرا و سپس با آزمون غرقابی کنترل شد.",
            "در سرویس‌های بهداشتی، آب‌بندی کف پیش از کاشی‌کاری الزامی است.",
        ],
        root_fa="بند",
        etymology_fa=(
            "ترکیب «آب» و «بندی» از «بستن» (بن مضارع: بند)؛ در فارسی فنی به نفوذناپذیرکردن سطح "
            "گفته می‌شود. نوشتن آن با نیم‌فاصله (آب‌بندی) رایج‌تر است و هر دو شکل در جستجو "
            "یکسان‌اند."
        ),
        origin_lang="fa",
        plural_fa="آب‌بندی‌ها",
        references=[PUB55, std("ACI 201.2R", N_SCOPE), SITE],
        related_terms=["isolation", "isolated", "sailor", "cap", "cement-matrix", "blind-well"],
    ),
    "pointing-mortar": rev(
        term_en="pointing mortar",
        synonyms=["بندکشی", "دوغاب‌ریزی بند"],
        search_aliases=["آب‌چین"],
        usage_examples=[
            "بند آجرکاری با ملات ماسه و سیمان دوغاب‌ریزی شد تا سطح بند آب‌بند و یکنواخت گردد.",
        ],
        root_fa="چین",
        etymology_fa=(
            "«چین» از «چیدن». واژه‌نامهٔ اصطلاحات آجری «آب‌چین» را چنین تعریف می‌کند: «دوغاب‌ریزی "
            "آجرکاری‌ها با ملات ماسه و سیمان یا مانند آن». امروزه همین عملیات بیشتر «بندکشی» "
            "نامیده می‌شود."
        ),
        origin_lang="fa",
        references=[M8, BRICK, TRAD],
        related_terms=["sealing", "brick-block", "masonry-course", "clavicle-strap", "lime-bloom"],
    ),
    "isolation": rev(
        term_en="isolation",
        synonyms=["عایق‌بندی", "جداکردگی"],
        search_aliases=["ایزوله‌سازی"],
        usage_examples=[
            "ایزولاسیون حرارتی بام و دیوار خارجی، بار سرمایش و گرمایش ساختمان را کاهش می‌دهد.",
        ],
        root_fa="ایزوله",
        etymology_fa=(
            "وام‌واژه از فرانسوی isolation، از ایتالیایی isolare (جزیره کردن، از لاتین insula = "
            "جزیره)؛ معادل فارسی آن «عایق‌بندی» و «جداکردگی» است و سه نوع رطوبتی، حرارتی و صوتی دارد."
        ),
        origin_lang="fr",
        references=[PUB55, M5],
        related_terms=["isolated", "sealing", "sailor", "blind-well"],
    ),
    "isolated": rev(
        term_en="isolated",
        synonyms=["عایق‌شده", "جداشده"],
        antonyms=["پیوسته", "متصل"],
        root_fa="ایزوله",
        etymology_fa="صفت مفعولی از «ایزوله کردن»؛ برای عضو یا فضایی به کار می‌رود که با عایق از محیط اطراف جدا شده باشد.",
        origin_lang="fr",
        references=[PUB55, M5],
        related_terms=["isolation", "sealing", "exposure"],
    ),
    "sailor": rev(
        term_en="sealer",
        synonyms=["تثبیت‌کنندهٔ سطح", "مواد آب‌بند سطحی"],
        search_aliases=["سیلر"],
        usage_examples=[
            "پیش از رنگ‌آمیزی، یک لایه سیلر روی گچ اجرا شد تا جذب رنگ یکنواخت شود.",
        ],
        root_fa="سیلر",
        etymology_fa=(
            "وام‌واژه از انگلیسی sealer (از seal = مهر و نشان بستن). شناسهٔ این مدخل (sailor) "
            "بازماندهٔ یک ترجمهٔ ماشینی نادرست است و به دلیل تغییرناپذیری نشانی‌ها حفظ شده است؛ "
            "معادل و تعریف اصلاح شدند."
        ),
        origin_lang="en",
        references=[PUB55, SITE],
        related_terms=["sealing", "isolation", "facing", "shell"],
    ),

    # ------------------------------------------------------------------ آجر و بنایی
    "square-brick": rev(
        term_en="square brick",
        synonyms=["آجر سلاتی", "آجر مربع"],
        search_aliases=["آجر چهارگوش ۲۵", "آجر ایرانی"],
        usage_examples=["کف‌سازی حیاط با آجر چهارگوش و ملات ماسه‌سیمان اجرا شد."],
        root_fa="آجر",
        etymology_fa=(
            "«چهارگوش» = چهار + گوشه. واژه‌نامهٔ اصطلاحات آجری «آجر سلاتی» را آجر چهارگوش "
            "قرمز رنگ تعریف می‌کند؛ ابعاد رایج سنتی ۲۵ در ۲۵ سانتی‌متر است."
        ),
        origin_lang="fa",
        plural_fa="آجرهای چهارگوش",
        references=[BRICK, M8, EN_BRICK, TRAD],
        related_terms=["quarter", "three-quarter-brick", "broken-brick", "care", "masonry-course"],
    ),
    "three-quarter-brick": rev(
        term_en="three-quarter brick",
        term_de="Dreiviertelziegel",
        translation_notes=None,
        synonyms=["سه‌قدی", "آجر سه‌چهارم"],
        root_fa="آجر",
        etymology_fa=(
            "«قدی» در اصطلاح بنایی به تقسیم طولی آجر اشاره دارد؛ «آجر سه قدی» برابر سه‌چهارم آجر "
            "کامل است و برای تنظیم رج‌چینی و پرکردن فاصله‌ها به کار می‌رود."
        ),
        origin_lang="fa",
        references=[BRICK, M8, TRAD],
        related_terms=["square-brick", "quarter", "broken-brick", "four-dang"],
    ),
    "bullnose-brick": rev(
        term_en="bullnose brick",
        term_de="Formstein mit Rundkante",
        translation_notes={"de": N_COINED},
        synonyms=["لب‌شتری", "فتیله", "نیم‌گرد"],
        search_aliases=["آجر فارسی‌بر"],
        usage_examples=[
            "لبهٔ جان‌پناه با آجر فارسی‌بُر اجرا شد تا تیزی لبه گرفته و لب‌پریدگی کاهش یابد.",
        ],
        root_fa="آجر",
        etymology_fa=(
            "«فارسی‌بُر» به معنای اریب‌بریده است. واژه‌نامهٔ اصطلاحات آجری «فتیله»، «غوطه‌ای» و "
            "«نیم‌گرد یا لب‌شتری» را گردکردن لبهٔ آجر تعریف می‌کند که همان bullnose است."
        ),
        origin_lang="fa",
        references=[BRICK, EN_BRICK, TRAD],
        related_terms=["chamfer", "square-brick", "corner-brick", "cap"],
    ),
    "corner-brick": rev(
        term_en="corner brick",
        term_de="Eckstein",
        synonyms=["آجر کنج", "آجر گوشه"],
        antonyms=["آجر نره"],
        root_fa="آجر",
        etymology_fa=(
            "«نبش» در اصطلاح بنایی زاویهٔ خارجی دیوار است و در برابر آن «کنج» (زاویهٔ داخلی) "
            "قرار دارد؛ «آجر نبشی» برای ساخت درست این زاویه به کار می‌رود."
        ),
        origin_lang="fa",
        references=[BRICK, M8, EN_MASONRY, TRAD],
        related_terms=["header-brick", "square-brick", "masonry-course", "pier"],
    ),
    "header-brick": rev(
        term_en="header brick",
        term_de="Binder",
        synonyms=["نره", "کله", "نره‌چین"],
        antonyms=["راسته", "تماسه"],
        usage_examples=[
            "در چیدمان کله‌راسته، رج‌های نره و راسته یکی در میان اجرا می‌شوند.",
        ],
        root_fa="نره",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «نره» را آجرهایی تعریف می‌کند که از ضخامت پهلو هم قرار "
            "گرفته‌اند، و «کَلّه» بخش عرضی یا باریک آجر است که در نماچینی دیده می‌شود. معادل انگلیسی "
            "آن header و معادل آلمانی Binder است (در برابر Läufer = راسته)."
        ),
        origin_lang="fa",
        references=[BRICK, M8, EN_MASONRY, TRAD],
        related_terms=["contact-him", "corner-brick", "masonry-course", "clavicle-strap"],
    ),
    "broken-brick": rev(
        term_en="broken brick",
        synonyms=["قطعات آجر", "شکستهٔ آجر"],
        root_fa="آجر",
        etymology_fa="واژه‌نامهٔ اصطلاحات آجری آن را «قطعات مختلف آجر» تعریف می‌کند.",
        origin_lang="fa",
        references=[BRICK, TRAD],
        related_terms=["square-brick", "quarter", "three-quarter-brick", "blockage"],
    ),
    "quarter": rev(
        term_en="quarter brick",
        synonyms=["چارک", "چهار یک", "کلوک"],
        usage_examples=["برای تنظیم رج‌چینی، آجر کامل به چهار چارک تقسیم شد."],
        root_fa="چارک",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «چارک یا چهار یک» و «کلوک» را هر دو یک‌چهارم آجر کامل "
            "تعریف می‌کند؛ این قطعه برای پرکردن فاصله‌ها و تکمیل رج به کار می‌رود."
        ),
        origin_lang="fa",
        references=[BRICK, TRAD],
        related_terms=["clavicle-strap", "square-brick", "three-quarter-brick", "four-dang"],
    ),
    "four-dang": rev(
        term_en="four dang",
        synonyms=["چهاردنگ", "چار دانگ", "آجر سه‌چهارم"],
        root_fa="دنگ",
        etymology_fa=(
            "«دنگ» یکای سنتی تقسیم آجر است. واژه‌نامهٔ اصطلاحات آجری «چهار دانگ» را «سه قسمت از "
            "چهار قسمت آجر» تعریف می‌کند، یعنی سه‌چهارم آجر؛ این مقدار در همین بازبینی با منبع "
            "راستی‌آزمایی شد. معادل خارجی ندارد، زیرا یکای آن مخصوص بنایی سنتی ایران است."
        ),
        origin_lang="fa",
        references=[BRICK, TRAD],
        related_terms=["quarter", "three-quarter-brick", "square-brick", "broken-brick"],
    ),
    "brick-block": rev(
        term_en="infill brick",
        synonyms=["بندآجری", "آجر پرکننده"],
        root_fa="بند",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «بندآجری» را قطعهٔ آجری تعریف می‌کند که فاصلهٔ دو آجر را در "
            "سقف پر می‌کند. «بند» در بنایی هم به فاصلهٔ میان دو آجر (بند ملات) و هم به قطعهٔ "
            "پرکننده گفته می‌شود."
        ),
        origin_lang="fa",
        references=[M8, M9, TRAD],
        related_terms=["clavicle-strap", "concrete-beam", "masonry-course", "a-basket", "care"],
    ),
    "clavicle-strap": rev(
        term_en="arch joint filler",
        translation_notes={"en": N_COINED},
        synonyms=["بندکلوکی", "کلوک"],
        usage_examples=[
            "بند آجرهای قوس با قطعات کلوک پر شد تا درزها یکنواخت و پیوستگی رج‌ها تأمین گردد.",
        ],
        root_fa="کلوک",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «کلوک» را یک‌چهارم آجر و «بندکلوکی» را قطعهٔ آجری به اندازهٔ "
            "کلوک تعریف می‌کند که لای بند آجرهای قوس به کار می‌رود."
        ),
        origin_lang="fa",
        references=[M8, BRICK, TRAD],
        related_terms=["quarter", "arch-crown", "springing", "spur", "brick-block"],
    ),
    "masonry-course": rev(
        term_en="masonry course",
        term_de="Mauerschicht",
        synonyms=["رج", "رگچین", "رج آجر"],
        usage_examples=[
            "تراز و شاقولی بودن هر رج بنا پیش از اجرای رج بعدی کنترل شد.",
        ],
        root_fa="رج",
        etymology_fa=(
            "«رج» در فارسی به معنای ردیف است. واژه‌نامهٔ اصطلاحات آجری «رج بنا» را ردیف "
            "آجرچینی تعریف می‌کند که الگوی ساختن دیوارها است، و «رج آجر» را «رگچین» می‌نامد."
        ),
        origin_lang="fa",
        plural_fa="رج‌ها",
        references=[M8, BRICK, EN_MASONRY, TRAD],
        related_terms=["reasoning", "passing", "boarding", "header-brick", "brick-block"],
    ),
    "reasoning": rev(
        term_en="reference course",
        synonyms=["رج استاد", "رج اصولی"],
        root_fa="رج",
        etymology_fa=(
            "شناسهٔ این مدخل (reasoning) بازماندهٔ یک ترجمهٔ ماشینی نادرست است و به دلیل "
            "تغییرناپذیری نشانی‌ها حفظ شده؛ «رج استاد» رج مرجعی است که تراز و راستایی رج‌های بعدی "
            "از آن گرفته می‌شود."
        ),
        origin_lang="fa",
        references=[M8, PUB55],
        related_terms=["masonry-course", "draw-a-line", "vertical", "boarding"],
    ),
    "passing": rev(
        term_en="base course",
        synonyms=["پاخور", "رج پایینی"],
        root_fa="پاسنگ",
        etymology_fa=(
            "«پاسنگ» از «پا» و «سنگ». واژه‌نامهٔ اصطلاحات کارگاهی آن را «پاخوری پای در یا دیوار» "
            "تعریف می‌کند؛ رج پایینی که بر سطح پی یا کف‌سازی می‌نشیند و تراز شروع بنایی را تعیین "
            "می‌کند."
        ),
        origin_lang="fa",
        references=[M8, SITE],
        related_terms=["masonry-course", "blockage", "pillow", "reasoning"],
    ),
    "chamfer": rev(
        term_en="chamfer",
        term_ar="زاوية مشطوفة",
        translation_notes={"ar": N_COINED},
        synonyms=["فارسی‌بُر", "لب‌پخ", "ماهیچه"],
        usage_examples=[
            "گوشهٔ آجرها فارسی‌بُر (پخ) شد تا لبهٔ تیز نما از بین برود.",
        ],
        root_fa="پخ",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «پخ» را «گوشه‌ای از آجر را فارسی‌بر کردن یا در زاویهٔ "
            "دیوارها ماهیچه ساختن» و «لب‌پخ» را فارسی‌برکردن ضخامت آجر تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[BRICK, EN_BRICK, TRAD],
        related_terms=["bullnose-brick", "square-brick", "corner-brick"],
    ),
    "facing": rev(
        term_en="facing",
        synonyms=["نما", "روبنایی", "نماسازی"],
        search_aliases=["آجر نما"],
        root_fa="روکار",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «روکار» را «نمای ساختمان» و «روبنایی» را لایه‌ای تعریف "
            "می‌کند که روی بنا برای تزیین کشیده می‌شود."
        ),
        origin_lang="fa",
        references=[M5, PUB55, TRAD],
        related_terms=["shell", "exposure", "sap-skin", "lime-bloom", "pistol"],
    ),
    "cap": rev(
        term_en="coping",
        synonyms=["کاپینگ", "پوشش تاج دیوار"],
        root_fa="درپوش",
        etymology_fa=(
            "«درپوش» از «در» (به معنِ روی/بر) و «پوش». واژه‌نامهٔ اصطلاحات آجری آن را «قسمتی که "
            "روی دیوار آجری یا دیوارهای دیگر می‌سازند» تعریف می‌کند و نقش اصلی آن جلوگیری از نفوذ "
            "آب به بدنهٔ دیوار است."
        ),
        origin_lang="fa",
        plural_fa="درپوش‌ها",
        references=[M8, PUB55, TRAD],
        related_terms=["jan-panah", "sealing", "shriveled", "pier"],
    ),
    "jan-panah": rev(
        term_en="parapet",
        term_ar="سترة",
        translation_notes={
            "ar": "«سترة» معادل متداول عربی برای جان‌پناه/حفاظ بام است؛ در متون عربی «حاجز» و «درابزين» هم به کار می‌رود.",
        },
        synonyms=["دست‌انداز", "دیوارک بام"],
        search_aliases=["درابزين", "حفاظ بام"],
        usage_examples=[
            "حداقل ارتفاع جان‌پناه بام قابل استفاده در مقررات ملی ساختمان تعیین شده است.",
        ],
        root_fa="جان",
        etymology_fa=(
            "«جان‌پناه» ترکیبی فارسی به معنای پناهگاه جان است. واژه‌نامهٔ اصطلاحات آجری آن را "
            "«دست‌انداز لبهٔ بام» و «دست‌انداز» را لبهٔ ایوان، بام یا پله‌ها تعریف می‌کند."
        ),
        origin_lang="fa",
        plural_fa="جان‌پناه‌ها",
        references=[M12, M4, PUB55, TRAD],
        related_terms=["shriveled", "cap", "blade", "stiff-head"],
    ),
    "shriveled": rev(
        term_en="stair parapet",
        synonyms=["خرپشتهٔ پله", "سرپناه پله"],
        root_fa="خرپشته",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «خرپشته» را «سرپناه پلهٔ روی بام» تعریف می‌کند. شناسهٔ این "
            "مدخل (shriveled) بازماندهٔ ترجمهٔ ماشینی نادرست است و به دلیل تغییرناپذیری نشانی‌ها "
            "حفظ شده است."
        ),
        origin_lang="fa",
        references=[M12, TRAD],
        related_terms=["jan-panah", "cap", "boarding"],
    ),
    "blade": rev(
        term_en="partition wall",
        synonyms=["دیوار تیغه‌ای", "دیوار جداکننده"],
        search_aliases=["تیغه چینی", "تیغهٔ آجری"],
        usage_examples=[
            "تیغه‌های داخلی با آجر سوراخ‌دار و ضخامت ۱۰ سانتی‌متر اجرا شدند.",
        ],
        root_fa="تیغه",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «تیغه» را «دیوار شش‌سانتی‌متری که واسطهٔ دو فضا باشد» و "
            "«دیوار نازک و جداکننده» تعریف می‌کند؛ تیغه باربر نیست و باید به سازه مهار شود."
        ),
        origin_lang="fa",
        plural_fa="تیغه‌ها",
        references=[M8, PUB55, TRAD],
        related_terms=["ripe", "affiliation", "pier", "masonry-course"],
    ),
    "ripe": rev(
        term_en="adjoining partition wall",
        synonyms=["دیوار چسبیده", "تیغهٔ الحاقی"],
        root_fa="پکافته",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «پکافته» را «دیوار تیغه‌ای که به دیوار اصلی چسبیده است» "
            "تعریف می‌کند؛ این دیوار باربر نیست و برای جداکردن فضاها یا پوشش تأسیسات به کار می‌رود."
        ),
        origin_lang="fa",
        references=[M8, TRAD],
        related_terms=["blade", "affiliation", "pier"],
    ),
    "affiliation": rev(
        term_en="affiliation",
        synonyms=["الحاق", "پیوستگی"],
        root_fa="الحاق",
        root_ar="ل-ح-ق",
        etymology_fa=(
            "«الحاق» وام‌واژهٔ عربی از ریشهٔ «ل-ح-ق» (پیوستن) است؛ در بنایی به چسبیدن دیوار "
            "تیغه‌ای به دیوار اصلی و در سازه به اتصال بخش الحاقی به بدنه گفته می‌شود."
        ),
        origin_lang="ar",
        references=[M8, PUB55],
        related_terms=["ripe", "blade", "isolated", "sealing"],
    ),
    "pier": rev(
        term_en="pier",
        term_fr="pilier",
        translation_notes=None,
        synonyms=["ستون بنایی", "پایهٔ باربر"],
        root_fa="جرز",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «جرز» را «دیوار یا پایهٔ ضخیمی که باربر باشد» تعریف می‌کند؛ "
            "جرز معمولاً در دو سمت درگاه‌ها و دهانه‌ها قرار دارد و بار طبقات یا طاق را به پی "
            "منتقل می‌کند."
        ),
        origin_lang="fa",
        plural_fa="جرزها",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["spur", "pakar", "springing", "corner-brick", "cap"],
    ),
    "spur": rev(
        term_en="abutment",
        term_fr="pied-droit",
        translation_notes=None,
        synonyms=["جرز طاق‌نما", "تکیه‌گاه قوس"],
        root_fa="اسپر",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «اسپر» را «جرزهای طرفین یک طاق‌نما» تعریف می‌کند؛ این جرز "
            "بار و رانش جانبی قوس را تحمل می‌کند."
        ),
        origin_lang="fa",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["pier", "springing", "pakar", "arch-crown", "rise-up"],
    ),

    # ------------------------------------------------------------------ قوس و طاق
    "springing": rev(
        term_en="springing",
        synonyms=["پاطاق", "خط آغاز طاق"],
        root_fa="پاتاق",
        etymology_fa=(
            "«پاطاق» از «پا» و «طاق». واژه‌نامهٔ اصطلاحات آجری آن را «شروع طاق از روی پایه یا "
            "دیوار» تعریف می‌کند و «بالنج» را کمانی بالاتر از پاطاق می‌داند."
        ),
        origin_lang="fa",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["pakar", "arch-crown", "rise-up", "spur", "semicircular-arch", "behind-the-arm"],
    ),
    "pakar": rev(
        term_en="springing point",
        synonyms=["پاکار قوس", "پاطاق"],
        root_fa="پاکار",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «پاکار قوس» را هم‌معنی «پاطاق» می‌داند: «جایی که طاق از "
            "بالای پایه شروع می‌شود؛ محل اتکای هر یک از دو سر قوس بر پایه‌های جانبی»."
        ),
        origin_lang="fa",
        references=[M8, TRAD],
        related_terms=["springing", "spur", "pier", "arch-crown", "rise-up"],
    ),
    "arch-crown": rev(
        term_en="crown",
        term_fr="sommet de voûte",
        synonyms=["تاج", "کلید قوس"],
        root_fa="تاج",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «تاج» را «بالای قوس» و «تاج قوس» را «طرحی که در بالای "
            "تقاطع دو قوس زده می‌شود» تعریف می‌کند؛ پس این واژه دو حس دارد: نقطهٔ اوج ساختاری قوس "
            "و نقش تزئینی محل تقاطع دو قوس."
        ),
        origin_lang="fa",
        usage_examples=[
            "خیز قوس، فاصلهٔ عمودی میان تراز پاکار و تاج قوس اندازه‌گیری شد.",
        ],
        references=[M8, TRAD],
        related_terms=["springing", "pakar", "rise-up", "semicircular-arch", "behind-the-arm", "clavicle-strap"],
    ),
    "rise-up": rev(
        term_en="rise",
        synonyms=["خیز قوس", "ارتفاع قوس"],
        antonyms=["دهانه"],
        root_fa="خیز",
        etymology_fa=(
            "«خیز» از «خاستن»؛ نسبت خیز به دهانه، نوع قوس را تعیین می‌کند: در قوس نیم‌دایره خیز "
            "برابر شعاع و در قوس جناغی بیشتر است."
        ),
        origin_lang="fa",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["arch-crown", "springing", "semicircular-arch", "bending", "drop"],
    ),
    "semicircular-arch": rev(
        term_en="semicircular arch",
        synonyms=["قوس نیم‌دایره", "طاق رومی", "قوس گرد"],
        search_aliases=["رومی"],
        root_fa="رومی",
        etymology_fa=(
            "«رومی» در بنایی سنتی ایران به قوس نیم‌دایره گفته می‌شود، زیرا این نوع طاق از معماری "
            "روم و بیزانس به ایران رسید؛ واژه‌نامهٔ اصطلاحات آجری «جهازه» را قالب‌سازی زیر قوس "
            "رومی تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["rise-up", "arch-crown", "springing", "two-piece", "behind-the-arm"],
    ),
    "behind-the-arm": rev(
        term_en="spandrel",
        synonyms=["لچکی", "گوشهٔ قوس"],
        root_fa="بغل",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «پشت بغل» را «دو طرف قوس که عمودی ساخته شده است» تعریف "
            "می‌کند و «لچکی» را سه‌گوشهٔ به‌وجودآمده میان دو قوس و گنبد می‌داند؛ معادل علمی آن در "
            "انگلیسی spandrel و در فرانویسی écoinçon است."
        ),
        origin_lang="fa",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["springing", "arch-crown", "semicircular-arch", "two-piece"],
    ),
    "two-piece": rev(
        term_en="double shell",
        synonyms=["گنبد دوپوش", "دوپوسته"],
        root_fa="پوش",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «دوپوش» را گنبدی تعریف می‌کند که یک سقف در زیر و یک سقف در "
            "بالا دارد و فضایی میان این دو به وجود می‌آید؛ این فضای میانی نقش عایق و سازه‌ای دارد."
        ),
        origin_lang="fa",
        references=[M8, TRAD],
        related_terms=["shell", "semicircular-arch", "behind-the-arm", "arch-crown"],
    ),
    "zigzag-brickwork": rev(
        term_en="zigzag brickwork",
        synonyms=["جوک", "خرند جناغی"],
        search_aliases=["جُوَک"],
        root_fa="جوک",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «جوک» را «نوعی آجرکاری زیگزاگ» و «خرند جناغی» را چیدن آجر "
            "به شکل هفت و هشت تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[M8, TRAD],
        related_terms=["zigzag", "masonry-course", "contact-him", "facing"],
    ),
    "zigzag": rev(
        term_en="zigzag",
        synonyms=["هفت‌وهشت", "جناغی", "کنگره‌ای"],
        search_aliases=["زیگزاگ خرپا"],
        root_fa="زیگزاگ",
        etymology_fa=(
            "وام‌واژه از انگلیسی/فرانویسی zigzag؛ در بنایی به چیدمان کنگره‌ای آجر و در سقف تیرچه "
            "به میلگردهای زیگزاگی خرپای تیرچه گفته می‌شود."
        ),
        origin_lang="fr",
        references=[M8, M9],
        related_terms=["zigzag-brickwork", "shear", "a-basket", "concrete-beam"],
    ),

    # ------------------------------------------------------------------ اجرا و کارگاه
    "contact-him": rev(
        term_en="header-stretcher bond",
        term_fr="appareil anglais",
        term_de="Kreuzverband",
        term_ar="رصف متبادل",
        synonyms=["کله‌راسته", "خفته و راسته"],
        usage_examples=[
            "دیوار باربر با چیدمان کله‌راسته اجرا شد تا پیوستگی عرضی میان رج‌ها تأمین گردد.",
        ],
        root_fa="تماسه",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات کارگاهی «تماسه» را «وسیلهٔ اجرای دیوار کله‌راسته» تعریف می‌کند. "
            "واژه‌نامهٔ اصطلاحات آجری نیز «خفته و راسته» را آجرهایی می‌داند که یکی خوابیده و یکی "
            "ایستاده پهلوی هم قرار می‌گیرند. شناسهٔ این مدخل (contact-him) بازماندهٔ ترجمهٔ ماشینی "
            "نادرست است و به دلیل تغییرناپذیری نشانی‌ها حفظ شده است."
        ),
        origin_lang="other",
        references=[M8, EN_MASONRY, SITE, TRAD],
        related_terms=["header-brick", "masonry-course", "brick-block", "zigzag-brickwork"],
    ),
    "to-darken": rev(
        term_en="vault closing",
        synonyms=["کور کردن", "مهر کردن"],
        usage_examples=[
            "آجرکاری سقف با پرکردن فاصله‌های باقی‌مانده تاریک (کور) شد تا هیچ روزنهٔ نور باقی نماند.",
        ],
        root_fa="تاریک",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «تاریک کردن» را «آجرکاری سقف را به اتمام رسانیدن، به‌طوری که "
            "جلوی روشنایی گرفته شود» تعریف می‌کند و «کور کردن» و «مهر کردن» را هم‌معنی آن "
            "می‌داند."
        ),
        origin_lang="fa",
        references=[M8, TRAD],
        related_terms=["boarding", "masonry-course", "care", "two-piece", "to-wander"],
    ),
    "boarding": rev(
        term_en="wall completion",
        synonyms=["تخت کردن", "رج آخر"],
        root_fa="تخته",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «تخت کردن» را آجرکاری تا زیر سقف یا ردیف آخر آجرکاری دیوار "
            "تعریف می‌کند؛ «تخته شدن» پایان دیوارچینی و ترازکردن رج‌های بالایی است."
        ),
        origin_lang="fa",
        usage_examples=["پس از تخته‌شدن دیوار، کلاف بتنی روی آن اجرا شد."],
        references=[M8, TRAD],
        related_terms=["to-darken", "masonry-course", "reasoning", "vertical", "cap"],
    ),
    "to-wander": rev(
        term_en="to turn over",
        synonyms=["سروته کردن"],
        root_fa="سرگرداندن",
        etymology_fa=(
            "«سرگرداندن» در کارگاه به سروته‌کردن یک قطعه یا عضو بنایی گفته می‌شود تا تراز یا جهت "
            "چیدمان آن تنظیم شود."
        ),
        origin_lang="fa",
        references=[PUB55, SITE],
        related_terms=["to-darken", "draw-a-line", "vertical", "stiff-head"],
    ),
    "draw-a-line": rev(
        term_en="to mark out",
        synonyms=["خط‌کشی", "ریسمان‌کشی"],
        search_aliases=["خط کردن", "ریسمان رنگی"],
        usage_examples=[
            "پیش از شروع بنایی، راستای دیوار با ریسمان رنگی روی کف علامت‌گذاری شد.",
        ],
        root_fa="خط",
        root_ar="خ-ط-ط",
        etymology_fa=(
            "«خط» وام‌واژهٔ عربی از ریشهٔ «خ-ط-ط» است؛ «خط کردن» در کارگاه به نشان‌گذاری سطح با "
            "ریسمان رنگی یا خط‌کش گفته می‌شود. واژه‌نامهٔ اصطلاحات آجری «خط بنایی» را نوعی "
            "آجرکاری تزئینی با خطوط راست و زاویه‌دار تعریف می‌کند که با آن تفاوت دارد."
        ),
        origin_lang="ar",
        references=[PUB55, M8, TRAD],
        related_terms=["reasoning", "vertical", "to-wander", "masonry-course"],
    ),
    "vertical": rev(
        term_en="vertical",
        synonyms=["قائم", "شاقول"],
        antonyms=["ناشاقولی"],
        search_aliases=["شاقولی"],
        usage_examples=[
            "ناشاقولی دیوار با شاقول و تراز لیزری کنترل و در حد رواداری مجاز بود.",
        ],
        root_fa="شاقول",
        etymology_fa=(
            "«شاقول» وزنهٔ آویزانی است که راستای قائم را نشان می‌دهد؛ «شاقولی» هم‌ترازی با این "
            "راستا و «ناشاقولی» انحراف از آن است."
        ),
        origin_lang="fa",
        references=[M8, PUB55, M12],
        related_terms=["stiff-head", "overwhelmed", "reasoning", "draw-a-line", "get-stuck"],
    ),
    "stiff-head": rev(
        term_en="overhanging",
        pos="adjective",
        synonyms=["سرِسفت"],
        antonyms=["سرواافتاده", "ناشاقولی"],
        root_fa="سر",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «سرِسفت» را «دیوارهای عمودی که سر آن جلوتر از عمود است» "
            "تعریف می‌کند، یعنی دیواری که به بیرون متمایل شده باشد؛ دقیقاً در برابر «سرواافتاده»."
        ),
        origin_lang="fa",
        references=[M8, M12, TRAD],
        related_terms=["overwhelmed", "vertical", "get-stuck", "boarding"],
    ),
    "overwhelmed": rev(
        term_en="receding",
        pos="adjective",
        synonyms=["سرواافتاده", "واافتاده"],
        antonyms=["سرِسفت"],
        root_fa="وا",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «سرواافتاده» را «دیوارهای عمودی که از عمود خارج شده و سر آن "
            "عقب‌تر از عمود است» تعریف می‌کند؛ شناسهٔ این مدخل (overwhelmed) بازماندهٔ ترجمهٔ "
            "ماشینی نادرست است و به دلیل تغییرناپذیری نشانی‌ها حفظ شده است."
        ),
        origin_lang="fa",
        references=[M8, M12, TRAD],
        related_terms=["stiff-head", "vertical", "get-stuck"],
    ),
    "get-stuck": rev(
        term_en="to jam",
        synonyms=["گیر افتادن", "مهار شدن"],
        root_fa="تنگ",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات کارگاهی «تنگ افتادن» را «درگیر شدن و مهار شدن» تعریف می‌کند؛ در "
            "اجرا به گیرکردن قالب یا قطعه در ملات و در رفتار سازه‌ای به مهار جانبی عضو گفته می‌شود."
        ),
        origin_lang="fa",
        references=[PUB55, SITE],
        related_terms=["stiff-head", "overwhelmed", "vertical", "back-strap"],
    ),
    "back-strap": rev(
        term_en="waler",
        term_fr="moise de coffrage",
        term_de="Schalungsriegel",
        term_ar="عارضة الشدة",
        synonyms=["پشت‌بند قالب", "شمعهٔ قالب", "والِر"],
        usage_examples=[
            "فاصلهٔ پشت‌بندها بر پایهٔ فشار جانبی بتن تازه و ارتفاع بتن‌ریزی تعیین شد.",
        ],
        root_fa="بند",
        etymology_fa=(
            "«پشت‌بند» از «پشت» و «بند»؛ قطعات چوبی یا فلزی که پشت تخته‌های قالب بسته می‌شوند تا از "
            "شکم‌دادن قالب در هنگام بتن‌ریزی جلوگیری کنند. معادل انگلیسی آن waler و فرانویسی moise "
            "است."
        ),
        origin_lang="fa",
        references=[std("ACI 301", N_SCOPE), M9, PUB55],
        translation_notes={
            "en": "waler معادل مصوب انگلیسی عضو افقی مهارکنندهٔ قالب است.",
            "de": N_COINED,
            "ar": "«عارضة الشدة» معادل توصیفی رایج در متون عربی برای عضو افقی مهارکنندهٔ قالب است.",
        },
        related_terms=["pendant", "plate", "to-pump", "cramp", "traverse"],
    ),
    "pendant": rev(
        term_en="hanger",
        synonyms=["آویز سقف", "قطعهٔ تعلیق"],
        root_fa="آویز",
        etymology_fa="«آویز» از «آویختن»؛ قطعه‌ای که بار را به عضو بالادستی منتقل می‌کند یا اجزای سقف و تأسیسات را معلق نگه می‌دارد.",
        origin_lang="fa",
        references=[M9, PUB55],
        related_terms=["concrete-beam", "back-strap", "center-of-gravity", "plate"],
    ),
    "plate": rev(
        term_en="plate",
        synonyms=["صفحه", "ورق فولادی"],
        search_aliases=["بیس پلیت", "پلیت زیر ستون"],
        usage_examples=[
            "پلیت زیر ستون باید کاملاً با سطح تکیه‌گاه تماس داشته باشد و فضای خالی آن با دوغاب پر شود.",
        ],
        root_fa="پلیت",
        etymology_fa=(
            "وام‌واژه از انگلیسی plate، از فرانویسی قدیم plate (صفحهٔ فلزی) و یونانی platys "
            "(پهن)؛ در ایران بیشتر برای صفحهٔ زیر ستون (base plate) و ورق‌های تقویتی به کار "
            "می‌رود."
        ),
        origin_lang="en",
        references=[M10, ACI318],
        related_terms=["pillow", "embedded-steel", "pin", "cramp", "traverse"],
    ),
    "pillow": rev(
        term_en="bearing pad",
        synonyms=["قطعهٔ توزیع بار"],
        usage_examples=[
            "زیر سر تیرآهن بالشتک سیمانی اجرا شد تا بار به‌طور یکنواخت به دیوار بنایی منتقل شود.",
        ],
        root_fa="بالش",
        etymology_fa=(
            "از «بالش» و پسوند «ـک». واژه‌نامهٔ اصطلاحات آجری آن را «آجر یا قطعهٔ بتنی که زیر سر "
            "تیرآهن با مصالح پوششی دیگر قرار می‌دهند» تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[M10, M8, TRAD],
        related_terms=["plate", "concrete-beam", "pier", "passing"],
    ),
    "cramp": rev(
        term_en="cramp",
        synonyms=["میخ سرکج", "بست فلزی", "کرامپ"],
        root_fa="اسکوپ",
        etymology_fa=(
            "«اسکوپ» واژه‌ای صنفی در بنایی و سنگ‌کاری سنتی برای بست یا میلهٔ فلزی است که قطعات سنگ، "
            "آجر یا چوب را به هم پیوند می‌دهد؛ معادل انگلیسی آن cramp و فرانویسی crampon است."
        ),
        origin_lang="other",
        references=[EN_MASONRY, M8, PUB55],
        related_terms=["aspel", "pin", "pillow", "embedded-steel"],
    ),
    "aspel": rev(
        term_en="through rod",
        synonyms=["میلهٔ عبوری", "اشپل"],
        root_fa="اشپیل",
        etymology_fa=(
            "واژه‌ای صنفی در بنایی سنتی برای میلهٔ فلزی که از شکاف یا سوراخ قطعات عبور می‌کند و "
            "برای مهار، اتصال یا جابه‌جایی اجزای بنایی به کار می‌رود؛ ریشهٔ زبانی آن راستی‌آزمایی "
            "نشده است."
        ),
        origin_lang="other",
        references=[M8, PUB55],
        related_terms=["cramp", "pin", "back-strap"],
    ),
    "pin": rev(
        term_en="pin",
        term_ar="دبوس",
        translation_notes={"ar": "«دبوس» معادل متداول عربی برای پین/سنجاق فلزی در سازه است."},
        synonyms=["میلگرد برش‌گیر", "پین"],
        search_aliases=["سنجاقی"],
        usage_examples=[
            "سنجاقی‌ها (میلگردهای برش‌گیر) برای مهار نیروی برشی در فونداسیون کار گذاشته شدند.",
        ],
        root_fa="سنجاق",
        etymology_fa=(
            "«سنجاقی» از «سنجاق» (ابزار سوزن‌مانند برای اتصال)؛ در بتن مسلح به میلگردهای کوتاه "
            "برش‌گیر گفته می‌شود که اجزای بتنی را در محل پی و فونداسیون به هم متصل می‌کنند."
        ),
        origin_lang="fa",
        references=[M9, ACI318, ABA],
        related_terms=["armator", "cramp", "aspel", "orlip", "the-vault"],
    ),
    "the-vault": rev(
        term_en="rebar chair",
        synonyms=["خرک", "فاصله‌نگهدار میلگرد"],
        search_aliases=["خرک آرماتور"],
        usage_examples=[
            "میلگردهای مش فوقانی فونداسیون با خرک در تراز طراحی نگه داشته شدند.",
        ],
        root_fa="خرک",
        etymology_fa=(
            "«خرک» در فارسی به پایهٔ چنگال‌مانند گفته می‌شود؛ در بتن مسلح قطعه‌ای است که از "
            "میلگرد ساخته می‌شود و مش فوقانی را در ارتفاع طراحی نگه می‌دارد. معادل دقیق انگلیسی آن "
            "rebar chair است (نه rebar spacer که واژه‌ای عام‌تر است). شناسهٔ این مدخل (the-vault) "
            "بازماندهٔ ترجمهٔ ماشینی نادرست است و حفظ شده است."
        ),
        origin_lang="fa",
        references=[M9, ACI318, std("ACI 301", N_SCOPE)],
        related_terms=["armator", "a-basket", "wire-reinforcement", "orlip", "pin"],
    ),
    "a-basket": rev(
        term_en="cage reinforcement",
        synonyms=["سبدی", "میلگرد بافته"],
        root_fa="سبد",
        etymology_fa=(
            "«سبدی» از «سبد»؛ به میلگردهای بافته‌شده‌ای گفته می‌شود که برای بالا و پایین شناژ "
            "فونداسیون ساخته می‌شوند و شبکهٔ تسلیح آن را تشکیل می‌دهند."
        ),
        origin_lang="fa",
        references=[M9, ACI318, ABA],
        related_terms=["armator", "wire-reinforcement", "the-vault", "zigzag", "f-bar-bender"],
    ),
    "wire-reinforcement": rev(
        term_en="wire reinforcement",
        synonyms=["سیم آرماتوربندی", "مفتول بست"],
        search_aliases=["سیم رباط", "سیم گالوانیزه"],
        usage_examples=[
            "میلگردها با سیم آرماتوربندی به قطر ۱٫۵ میلی‌متر به یکدیگر بسته و مهار شدند.",
        ],
        root_fa="سیم",
        etymology_fa="«سیم» در فارسی به مفتول فلزی گفته می‌شود؛ سیم آرماتوربندی برای بستن و مهار میلگردها در شبکهٔ تسلیح به کار می‌رود.",
        origin_lang="fa",
        references=[M9, ACI318, PUB55],
        related_terms=["armator", "a-basket", "f-bar-bender", "orlip", "the-vault"],
    ),
    "f-bar-bender": rev(
        term_en="F-bar bender",
        synonyms=["آچار آرماتوربندی", "آچار خم‌کن میلگرد"],
        search_aliases=["آچار اف"],
        usage_examples=[
            "خم میلگرد با آچار F و با زاویه و قطر خم مطابق جدول آیین‌نامه انجام شد.",
        ],
        root_fa="آچار",
        etymology_fa=(
            "«آچار» واژه‌ای فارسی برای ابزار است؛ این آچار به دلیل شکل Fمانند بدنه و اهرمش چنین "
            "نامیده می‌شود و برای خم‌کردن میلگرد در آرماتوربندی به کار می‌رود."
        ),
        origin_lang="fa",
        references=[M9, ACI318, PUB55],
        related_terms=["armator", "orlip", "the-vault", "wire-reinforcement", "a-basket"],
    ),
}

# merge (not replace): a later batch may refine an earlier decision for the same id
for _tid, _patch in BATCH.items():
    REVIEW.setdefault(_tid, {}).update(_patch)
