"""Content review — batch 3: باقی اصطلاحات ساختمانی و کارگاهی (بخش ۲ از ۲).

شامل جداسازی حس‌های چندمعنایی (دول/دوال، تاج قوس، تنش)، اصلاح معادل‌های
انگلیسی که از ترجمهٔ ماشینی باقی مانده بودند، و پرکردن شکاف ترجمه فقط در
مواردی که معادل قابل دفاع وجود دارد.
"""

from review_batch2 import (
    ABA,
    ACI318,
    BRICK,
    EN_BRICK,
    EN_MASONRY,
    M10,
    M12,
    M4,
    M5,
    M7,
    M8,
    M9,
    N_COINED,
    PUB55,
    SITE,
    STRENGTH,
    TRAD,
)
from review_data import N_SCOPE, N_TERM, REVIEW, bk, rev, std

DURABILITY = std("ACI 201.2R", N_SCOPE)
CONSTRUCTION = std("ACI 301", N_SCOPE)
PLACING = std("ACI 304R", N_SCOPE)
CONSOLIDATION = std("ACI 309R", N_SCOPE)
COLD = std("ACI 306R", N_SCOPE)
ADMIXTURE = std("ASTM C494", N_SCOPE)
EN_ADMIXTURE = std("EN 934-2", N_SCOPE)
AGGREGATE = std("ASTM C33", N_SCOPE)
FINES = std("ASTM C117", N_SCOPE)
READYMIX = std("ASTM C94", N_SCOPE)
LAB = std("ASTM C192", N_SCOPE)
MECH = bk("هیبی — مکانیک مهندسی", N_TERM)

BATCH = {
    # ------------------------------------------------------------------ مصالح و روسازی
    "asphalt": rev(
        term_en="asphalt",
        definition_fa=(
            "مخلوط سنگدانه (شن و ماسه) و قیر که در دمای مشخص تولید و پخش می‌شود و پس از تراکم و "
            "خنک‌شدن، سطحی نفوذناپذیر، یکپارچه و مقاوم در برابر سایش ایجاد می‌کند؛ در روسازی راه، "
            "کف حیاط و بام به کار می‌رود."
        ),
        synonyms=["قیر و آسفالت", "آسفالت گرم"],
        search_aliases=["آسفالت‌کاری"],
        usage_examples=[
            "آسفالت باید در دمای مجاز پخش و بی‌درنگ با غلتک متراکم شود.",
        ],
        root_fa="آسفالت",
        etymology_fa=(
            "وام‌واژه از فرانسوی asphalte یا انگلیسی asphalt، از یونانی ásphaltos به معنای قیر "
            "طبیعی؛ در ایران به مخلوط سنگدانه و قیر برای روسازی گفته می‌شود."
        ),
        origin_lang="fr",
        references=[PUB55, M5],
        related_terms=["burnt-asphalt", "blockage", "cumin", "care", "sealing"],
    ),
    "burnt-asphalt": rev(
        term_en="burnt asphalt",
        definition_fa=(
            "آسفالتی که به‌دلیل حرارت بیش از حد یا نگهداری طولانی در دمای بالا، قیر آن خاصیت "
            "چسبندگی و شکل‌پذیری خود را از دست داده است؛ در اجرا پوسته می‌شود، از هم می‌پاشد و باید "
            "برداشته و جایگزین گردد."
        ),
        synonyms=["آسفالت سوخته‌شده"],
        root_fa="آسفالت",
        etymology_fa="«سوخته» اشاره به عبور قیر از دمای مجاز دارد که باعث اکسیدشدن و شکنندگی آسفالت می‌شود.",
        origin_lang="fr",
        usage_examples=["لکه‌های پوسته‌شدهٔ آسفالت سوخته برداشته و با آسفالت نو جایگزین شد."],
        references=[PUB55, M5],
        related_terms=["asphalt", "cumin", "blockage"],
    ),
    "lime-bloom": rev(
        term_en="lime bloom",
        synonyms=["شوره", "سفیدک", "شورهٔ آهکی"],
        search_aliases=["افلوئورسانس", "شوره زدن"],
        usage_examples=[
            "ظهور شورهٔ آهکی روی نمای آجری نشانهٔ نفوذ رطوبت و وجود نمک‌های محلول در ملات است.",
        ],
        root_fa="آلوئک",
        etymology_fa=(
            "«آلوئک» واژه‌ای صنفی در بنایی سنتی برای شورهٔ آهکی است؛ معادل علمی آن efflorescence "
            "است و به مهاجرت نمک‌های محلول به سطح و تبلور آن‌ها پس از تبخیر آب گفته می‌شود."
        ),
        origin_lang="other",
        references=[DURABILITY, BRICK, M5],
        related_terms=["brackish-soil", "pointing-mortar", "sealing", "cap", "ginger"],
    ),
    "brackish-soil": rev(
        term_en="brackish soil",
        definition_fa=(
            "خاک‌های نمکی و شور که به‌دلیل وجود املاح محلول (به‌ویژه سولفات و کلرید) برای پی‌سازی "
            "مشکل‌سازند؛ در تماس با بتن و فولاد می‌توانند موجب حملهٔ شیمیایی، خوردگی آرماتور و "
            "تخریب تدریجی سازه شوند و نیاز به سیمان مقاوم یا حفاظت ویژه دارند."
        ),
        synonyms=["خاک شور", "زمین شوره‌زار"],
        search_aliases=["خاک شوره"],
        root_fa="شوره",
        etymology_fa="«شوره» به نمک و املاح سطح زمین گفته می‌شود؛ ترکیب آن با «خاک» نوع خاک مشکل‌ساز را می‌سازد.",
        origin_lang="fa",
        usage_examples=[
            "به‌دلیل سولفات‌دار بودن خاک، از سیمان مقاوم در برابر سولفات استفاده شد.",
        ],
        references=[DURABILITY, M7, std("ASTM C1202", N_SCOPE)],
        related_terms=["lime-bloom", "hard-ground", "hit-the-ground", "blind-well", "siman"],
    ),
    "gravel": rev(
        term_en="gravel",
        synonyms=["شن", "قلوه‌سنگ", "سنگدانهٔ درشت"],
        search_aliases=["سنگدانه", "شن و ماسه"],
        usage_examples=[
            "سنگدانهٔ درشت باید عاری از خاک و مواد زیان‌آور باشد و دانه‌بندی آن در محدودهٔ استاندارد قرار گیرد.",
        ],
        root_fa="سنگ",
        etymology_fa=(
            "«سنگ‌دانه» ترکیبی فارسی و معادل مصوب aggregate است؛ در کارگاه «شن» برای دانهٔ ریز و "
            "«قلوه‌سنگ» یا «شن» برای دانهٔ درشت به کار می‌رود."
        ),
        origin_lang="fa",
        plural_fa="سنگدانه‌ها",
        references=[AGGREGATE, M5, std("ASTM C136", N_SCOPE), std("ASTM C127", N_SCOPE)],
        related_terms=["silt", "cumin", "blockage", "beton", "pycnometer", "mesh-sieve-size"],
    ),
    "silt": rev(
        term_en="silt",
        definition_fa=(
            "دانه‌های بسیار ریز خاک با ابعادی میان رس و ماسه (تقریباً ۰٫۰۰۲ تا ۰٫۰۷۵ میلی‌متر) که "
            "در مهندسی خاک به‌دلیل ظرفیت زهکشی پایین، حساسیت به آب و خطر روان‌گرایی اهمیت دارد و در "
            "فارسی «لای» نیز نامیده می‌شود."
        ),
        synonyms=["لای"],
        root_fa="سیلت",
        etymology_fa="وام‌واژه از انگلیسی silt (رسوب ریزدانه)؛ معادل فارسی سنتی آن «لای» است.",
        origin_lang="en",
        references=[FINES, M7],
        related_terms=["gravel", "brackish-soil", "hard-ground", "beton"],
    ),
    "cumin": rev(
        term_en="base course",
        synonyms=["زیرسازی", "لایهٔ بستر"],
        search_aliases=["زیره‌چینی"],
        usage_examples=[
            "لایهٔ زیره با دانهٔ خشن پخش و متراکم شد تا بار کف‌سازی پخش و زهکشی تأمین شود.",
        ],
        root_fa="زیره",
        etymology_fa=(
            "«زیره» در بنایی به لایهٔ زیرین کار گفته می‌شود (نه گیاه زیره)؛ واژه‌نامهٔ اصطلاحات "
            "کارگاهی آن را در ردیف اصطلاحات زیرسازی آورده است."
        ),
        origin_lang="fa",
        references=[PUB55, M7],
        related_terms=["blockage", "asphalt", "gravel", "care", "hard-ground"],
    ),
    "blockage": rev(
        term_en="stone bedding",
        synonyms=["قلوه‌سنگ متراکم", "بستر سنگی"],
        search_aliases=["بلوکاژ"],
        usage_examples=["بلوکاژ با قلوه‌سنگ و ملات آهک پخش و با تخماق کوبیده شد."],
        root_fa="بلوکاژ",
        etymology_fa=(
            "وام‌واژه از فرانسوی blocage (پرکردن با سنگ و ملات)؛ در ایران به لایهٔ زیرین از قلوه‌سنگ "
            "یا مصالح دانه‌ای گفته می‌شود که کوبیده و متراکم می‌شود تا بستر یکنواختی برای کف‌سازی "
            "ایجاد کند."
        ),
        origin_lang="fr",
        references=[PUB55, M7],
        related_terms=["cumin", "passing", "hard-ground", "gravel", "tamper"],
    ),
    "hard-ground": rev(
        term_en="hard ground",
        term_fr="sol dur",
        term_de="fester Untergrund",
        translation_notes={
            "fr": N_COINED,
            "de": N_COINED,
        },
        synonyms=["دج سرخ", "زمین متراکم"],
        usage_examples=[
            "پس از کف‌برداری، زمین از نوع دج بود و پی مستقیماً روی آن اجرا شد.",
        ],
        root_fa="دج",
        etymology_fa=(
            "«دج» در اصطلاح کارگاهی به زمین سخت و متراکم با ظرفیت باربری مناسب گفته می‌شود؛ در "
            "واژه‌نامه‌های صنفی «دج سرخ» نیز آمده و برای ساختمان مرغوب شمرده شده است. چون یک اصطلاح "
            "محلی است، معادل خارجی مصوب ندارد و ترجمه‌های فرانویسی و آلمانی توصیفی‌اند."
        ),
        origin_lang="other",
        references=[M7, SITE],
        related_terms=["hit-the-ground", "blockage", "brackish-soil", "blind-well", "cumin"],
    ),
    "hit-the-ground": rev(
        term_en="compacted ground",
        synonyms=["زمین کوبیده"],
        search_aliases=["زمین زد"],
        root_fa="زمین",
        etymology_fa=(
            "«زمین زِد» در اصطلاح کارگاهی به زمین سختی گفته می‌شود که فشردگی و مقاومت دانه‌های آن "
            "کمتر از «دج» است و برای اجرای پی نیاز به بررسی ظرفیت باربری دارد."
        ),
        origin_lang="other",
        usage_examples=["ظرفیت باربری زمین زِد با آزمایش بارگذاری صفحه‌ای کنترل شد."],
        references=[M7, SITE],
        related_terms=["hard-ground", "blockage", "tamper", "brackish-soil"],
    ),

    # ------------------------------------------------------------------ بتن و اجرا
    "to-pump": rev(
        term_en="to pump",
        synonyms=["پمپاژ", "بوم‌ریزی"],
        search_aliases=["پمپاژ بتن", "بوم بتن"],
        usage_examples=[
            "پمپاژ بتن باید پیوسته انجام شود تا از گیرش بتن درون لوله جلوگیری گردد.",
            "پس از پایان بتن‌ریزی، لولهٔ بوم با توپی پاک‌کننده تمیز شد.",
        ],
        root_fa="پمپ",
        etymology_fa=(
            "«پمپ» وام‌واژه از فرانسوی pompe و انگلیسی pump، از لاتین pompa؛ «پمپاژ بتن» انتقال بتن "
            "تازه با فشار از طریق لوله و بوم به محل قالب‌بندی است."
        ),
        origin_lang="fr",
        references=[PLACING, READYMIX, CONSOLIDATION],
        related_terms=["vibrator", "a-ball", "batching", "concrete-beam", "back-strap"],
    ),
    "a-ball": rev(
        term_en="ball",
        definition_fa=(
            "قطعهٔ کروی پلاستیکی، لاستیکی یا فلزی که در کارگاه چند کاربرد دارد: توپ پاک‌کنندهٔ لولهٔ "
            "پمپ بتن که با فشار هوا درون لوله رانده می‌شود، فاصله‌نگهدار یا مهارکننده در اتصالات، و "
            "در گفتار صنفی به هر قطعهٔ کروی نیز گفته می‌شود."
        ),
        synonyms=["گوی", "توپک"],
        search_aliases=["توپی پمپ", "توپ پاک‌کننده"],
        usage_examples=["پیش از پایان پمپاژ، توپی پاک‌کننده درون لولهٔ بوم رانده شد."],
        root_fa="توپ",
        etymology_fa=(
            "«توپی» از «توپ» و پسوند نسبت «ی». واژه‌نامهٔ اصطلاحات کارگاهی آن را «شیء کروی "
            "پلاستیک» تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[PLACING, SITE],
        related_terms=["to-pump", "the-vault", "pillow", "pin"],
    ),
    "tizon": rev(
        term_en="quick-setting admixture",
        term_fr="accélérateur de prise",
        term_de="Erstarrungsbeschleuniger",
        translation_notes=None,
        synonyms=["زودگیر", "شتاب‌دهندهٔ گیرش", "پرگیر"],
        antonyms=["کندگیر"],
        search_aliases=["تیزاب"],
        usage_examples=[
            "برای ترمیم فوری و بتن‌ریزی در هوای سرد، از افزودنی زودگیر مطابق استاندارد استفاده شد.",
        ],
        root_fa="تیز",
        etymology_fa=(
            "«تیزون» از «تیز» و پسوند «ـون»؛ در کارگاه به مواد یا افزودنی پرگیر و زودگیر گفته "
            "می‌شود که زمان گیرش ملات یا بتن را کوتاه می‌کند. معادل هنجاری آن در استانداردهای "
            "افزودنی، شتاب‌دهنده (accelerator) است."
        ),
        origin_lang="fa",
        references=[ADMIXTURE, EN_ADMIXTURE, COLD, std("ASTM C403", N_SCOPE)],
        related_terms=["siman", "batching", "sealing", "to-darken", "control"],
    ),
    "concrete-beam": rev(
        term_en="concrete beam",
        synonyms=["تیر بتنی", "پوتیر"],
        search_aliases=["پوتر", "شاه‌تیر بتنی"],
        usage_examples=[
            "لنگر خمشی بحرانی پوتر در میانهٔ دهانه و برش بحرانی در نزدیکی تکیه‌گاه است.",
        ],
        root_fa="پوتر",
        etymology_fa=(
            "«پوتر» وام‌واژه از فرانسوی poutre (تیر، شاه‌تیر) است که در فارسی فنی برای تیر بتنی یا "
            "فولادی به کار می‌رود؛ شکل «پوتیر» نیز دیده می‌شود."
        ),
        origin_lang="fr",
        plural_fa="پوترها",
        references=[M9, ACI318, std("EN 1992-1-1", N_SCOPE), STRENGTH],
        related_terms=["bending-moment", "shear", "armator", "pendant", "orlip", "bending"],
    ),
    "orlip": rev(
        term_en="overlap",
        synonyms=["وصلهٔ پوششی", "روی‌هم‌افتادگی"],
        search_aliases=["اورلپ آرماتور", "طول وصله"],
        usage_examples=[
            "طول اورلپ میلگردهای طولی باید دست‌کم برابر مقدار محاسبه‌شدهٔ وصله در آیین‌نامه باشد.",
        ],
        root_fa="اورلپ",
        etymology_fa=(
            "وام‌واژه از انگلیسی overlap (روی‌هم‌افتادگی)؛ در آرماتوربندی به طول هم‌پوشانی دو "
            "میلگرد در وصلهٔ پوششی گفته می‌شود که نیرو از راه چسبندگی میان آن‌ها منتقل می‌شود."
        ),
        origin_lang="en",
        references=[M9, ACI318, ABA],
        related_terms=["armator", "wire-reinforcement", "f-bar-bender", "pin", "the-vault"],
    ),
    "embedded-steel": rev(
        term_en="embedded steel",
        definition_fa=(
            "فولادی که در ملات، آجر یا بتن پوشانده و از دید پنهان شده است؛ واژه‌نامهٔ اصطلاحات آجری "
            "«آهن گُم» را آهن سقفی تعریف می‌کند که روی آن با آجر پوشیده شده باشد. پوشش مناسب، "
            "محافظت در برابر خوردگی و آتش را بر عهده دارد."
        ),
        synonyms=["فولاد مدفون", "آهن پوشیده"],
        search_aliases=["آهن گم"],
        usage_examples=[
            "پوشش بتن روی آهن گُم باید حداقل مقدار آیین‌نامه‌ای باشد تا از خوردگی جلوگیری شود.",
        ],
        root_fa="آهن",
        etymology_fa=(
            "«گُم» به معنای ناپیدا و گمشده است؛ «آهن گُم» فولادی است که در بافت بنا پنهان شده باشد."
        ),
        origin_lang="fa",
        references=[M9, std("ACI 222R", N_SCOPE), TRAD],
        related_terms=["armator", "john-is-plastered", "concrete-beam", "pillow"],
    ),
    "john-is-plastered": rev(
        term_en="gypsum-encased steel",
        term_fr="acier enrobé de plâtre",
        term_de="gipsummantelter Stahl",
        term_ar="حديد مكسو بالجبس",
        translation_notes={
            "fr": N_COINED,
            "de": N_COINED,
            "ar": N_COINED,
        },
        definition_fa=(
            "عضوی فولادی (معمولاً جان تیرآهن یا پروفیل) که با پوشش گچ محافظت شده است؛ پوشش گچ علاوه "
            "بر جلوگیری از تماس مستقیم فولاد با عوامل مخرب و خوردگی، به‌دلیل آبِ تبلور خود مقاومت "
            "عضو را در برابر آتش افزایش می‌دهد."
        ),
        synonyms=["آهن گچ‌پوش", "فولاد گچ‌اندود"],
        search_aliases=["جان گچ گرفته"],
        root_fa="جان",
        etymology_fa=(
            "«جان» در فارسی فنی به جان (web) مقطع فولادی گفته می‌شود؛ «جان گچ گرفته» عضوی است که "
            "جان آن با گچ پوشانده شده باشد. این اصطلاح در واژه‌نامه‌های هنجاری معادل مصوب خارجی "
            "ندارد، پس ترجمه‌های آن توصیفی ثبت شده‌اند. شناسهٔ این مدخل بازماندهٔ ترجمهٔ ماشینی "
            "نادرست است و به دلیل تغییرناپذیری نشانی‌ها حفظ شده است."
        ),
        origin_lang="fa",
        references=[M10, PUB55, M12],
        related_terms=["embedded-steel", "plate", "sap-skin", "shell", "concrete-beam"],
    ),
    "elasticity": rev(
        term_en="elasticity",
        synonyms=["کشسانی", "ارتجاع"],
        antonyms=["خمیری‌شدگی", "شکنندگی"],
        root_fa="الاستیسیته",
        etymology_fa=(
            "وام‌واژه از فرانسوی élasticité، از یونانی elásein (راندن، کشیدن)؛ معادل مصوب فرهنگستان "
            "«کشسانی» است."
        ),
        origin_lang="fr",
        usage_examples=["در محدودهٔ کشسان، با برداشتن بار، تغییر شکل عضو کاملاً بازمی‌گردد."],
        references=[STRENGTH, std("ASTM C469", N_SCOPE)],
        related_terms=["modulus-of-elasticity", "strain", "tension", "bending"],
    ),
    "bending": rev(
        term_en="bending",
        synonyms=["خمش", "انحنا"],
        root_fa="خم",
        etymology_fa="«خمش» از «خم» و پسوند اسم مصدر «ـش»؛ حالت باربری غالب در تیرها و دال‌ها است.",
        origin_lang="fa",
        usage_examples=[
            "در خمش، الیاف یک سمت مقطع کوتاه و الیاف سمت دیگر کشیده می‌شوند و در محور خنثی تنش صفر است.",
        ],
        references=[STRENGTH, M9, std("ASTM C78", N_SCOPE)],
        related_terms=["bending-moment", "shear", "tension", "strain", "concrete-beam", "rise-up"],
    ),
    "tension": rev(
        term_en="tension",
        definition_fa=(
            "نیروی کششی وارد بر واحد سطح مقطع یک عضو. به‌طور کلی‌تر «تنش» (stress) نیرو بر واحد "
            "سطح است و «تنش کششی» نوعی از آن است که در جهت طویل‌کردن عضو اثر می‌کند. مقاومت کششی بتن "
            "ناچیز است، پس تنش کششی عمدتاً توسط آرماتور تحمل می‌شود."
        ),
        synonyms=["تنش کششی", "کشش"],
        antonyms=["تنش فشاری", "فشار"],
        root_fa="تنش",
        etymology_fa=(
            "«تنش» معادل مصوب فرهنگستان برای stress است. برخی واژه‌نامه‌های صنفی آن را به «تنیدن» "
            "نسبت داده‌اند که از نظر مهندسی نادرست است: در مهندسی، تنش نیرو بر واحد سطح است و این "
            "مدخل به‌طور خاص به تنش کششی (tension) می‌پردازد."
        ),
        origin_lang="fa",
        usage_examples=["ترک‌های عمود بر محور تیر، نشانهٔ غلبهٔ تنش کششی است."],
        references=[STRENGTH, M9, std("EN 1992-1-1", N_SCOPE), std("ASTM C1583", N_SCOPE)],
        related_terms=["shear", "bending-moment", "strain", "fatigue", "modulus-of-elasticity", "armator"],
    ),
    "drop": rev(
        term_en="drop",
        definition_fa=(
            "کاهش تراز یا مقدار یک کمیت نسبت به حالت اولیه؛ این واژه چند حس فنی دارد: نشست پی "
            "(settlement)، افت سطح بتن تازه پیش از گیرش (plastic settlement)، افت اسلامپ میان "
            "کارخانه و محل مصرف (slump loss) و جابه‌جایی عمودی تیر زیر بار (deflection)."
        ),
        synonyms=["نشست", "افتادگی", "افت سطح"],
        search_aliases=["افت اسلامپ", "نشست پی"],
        usage_examples=[
            "افت اسلامپ میان کارخانهٔ بتن و محل مصرف نباید از حد مجاز بیشتر شود.",
            "نشست پی باید از مقدار مجاز آیین‌نامه کمتر بماند.",
        ],
        root_fa="افت",
        etymology_fa=(
            "اسم مصدر از «افتادن». چون این واژه چندمعنایی است، حس‌های آن در تعریف جدا شده‌اند؛ معادل "
            "انگلیسی هر حس متفاوت است (settlement، slump loss، deflection)."
        ),
        origin_lang="fa",
        references=[M7, std("ASTM C143", N_SCOPE), DURABILITY],
        related_terms=["tolerance", "hard-ground", "blind-well", "rise-up", "bending"],
    ),
    "exposure": rev(
        term_en="exposed",
        synonyms=["نمایان", "بدون پوشش"],
        search_aliases=["اکسپوز", "بتن اکسپوز"],
        usage_examples=["دیوار بتنی این پروژه به‌صورت اکسپوزه و بدون نازک‌کاری اجرا شد."],
        root_fa="اکسپوزه",
        etymology_fa=(
            "وام‌واژه از فرانسوی exposé (آشکار، در معرض)؛ در معماری ایران به سطحی گفته می‌شود که "
            "بدون نازک‌کاری رها شده باشد. در استانداردهای بتن، «ردهٔ در معرضی» (exposure class) "
            "شدت عوامل مخرب محیطی را دسته‌بندی می‌کند."
        ),
        origin_lang="fr",
        references=[std("EN 206", N_SCOPE), M4, PUB55],
        related_terms=["facing", "shell", "isolated", "cap", "brackish-soil"],
    ),

    # ------------------------------------------------------------------ ابزار و کارگاه
    "tamper": rev(
        term_en="tamper",
        synonyms=["کوبه", "دستک کوبش"],
        search_aliases=["قورباغه‌ای", "کوبهٔ دستی", "دکمه‌گیر"],
        usage_examples=[
            "لایه‌های خاک زیر کف در ضخامت مجاز ریخته و با تخماق کوبیده شد.",
        ],
        root_fa="تخماق",
        etymology_fa=(
            "«تخماق» واژه‌ای کهن (هم‌ریشه با ترکی tokmak/döğmek = کوبیدن) برای کوبهٔ سنگین است؛ "
            "واژه‌نامهٔ اصطلاحات کارگاهی آن را «کوبهٔ سنگین» تعریف می‌کند."
        ),
        origin_lang="tr",
        plural_fa="تخماق‌ها",
        references=[M7, LAB, SITE],
        related_terms=["jig-jigging", "vibrator", "hard-ground", "hit-the-ground", "blockage"],
    ),
    "traverse": rev(
        term_en="traverse",
        synonyms=["تراورس چوبی", "تختهٔ پهن"],
        root_fa="تراورس",
        etymology_fa=(
            "وام‌واژه از فرانسوی traverse و انگلیسی traverse (چیز عرضی)؛ واژه‌نامهٔ اصطلاحات "
            "کارگاهی آن را «تخته‌های قطور و عریض» تعریف می‌کند که به‌صورت افقی روی تکیه‌گاه‌ها قرار "
            "می‌گیرند."
        ),
        origin_lang="fr",
        references=[M12, PUB55, SITE],
        related_terms=["back-strap", "plate", "pendant", "pillow", "care"],
    ),
    "sap-skin": rev(
        term_en="sandpaper",
        synonyms=["سمباده", "کاغذ ساینده"],
        search_aliases=["پوست ساپ", "سنباده"],
        usage_examples=["سطح گچی پیش از رنگ‌آمیزی با سمبادهٔ شمارهٔ مناسب پرداخت شد."],
        root_fa="ساپ",
        etymology_fa=(
            "«ساپ» صورت کوتاه‌شدهٔ «سندپیپر» (sandpaper) است؛ «پوست ساپ» همان سمباده است که سطح آن "
            "با دانه‌های ساینده پوشانده شده است."
        ),
        origin_lang="en",
        references=[PUB55],
        related_terms=["pistol", "facing", "shell", "isolation"],
    ),
    "pistol": rev(
        term_en="spray gun",
        synonyms=["پیستولهٔ رنگ", "دستگاه پاشش"],
        search_aliases=["اسپری", "شات‌کریت"],
        usage_examples=["اندود نما با پیستوله و فشار هوا به‌طور یکنواخت پاشیده شد."],
        root_fa="پیستوله",
        etymology_fa=(
            "وام‌واژه از فرانسوی pistolet؛ در کارگاه به دستگاه پاشندهٔ رنگ، ملات یا بتن پاششی "
            "(شات‌کریت) گفته می‌شود."
        ),
        origin_lang="fr",
        references=[PUB55],
        related_terms=["sap-skin", "facing", "sealing", "shell"],
    ),
    "shell": rev(
        term_en="shell",
        definition_fa=(
            "روکش نازکی که روی گنبدها یا آجرکاری‌ها کشیده می‌شود و نقش پوشش محافظ یا سطح نهایی را "
            "دارد؛ این روکش می‌تواند از ماسه و سیمان، بتن یا مصالح مشابه باشد. در سازه، «پوسته» به "
            "عناصر نازک خمیدهٔ بتنی نیز گفته می‌شود."
        ),
        synonyms=["روکش", "قشر"],
        root_fa="پوست",
        etymology_fa=(
            "از «پوست» و پسوند «ـه». واژه‌نامهٔ اصطلاحات آجری «پوسته» را «روکشی که روی گنبدها یا "
            "آجرکاری‌ها می‌کشند» تعریف می‌کند."
        ),
        origin_lang="fa",
        references=[M9, PUB55, TRAD],
        related_terms=["facing", "two-piece", "sealing", "sailor", "sap-skin"],
    ),
    "care": rev(
        term_en="brick paving",
        synonyms=["فرش آجر", "فرش کف", "آجر فرش"],
        usage_examples=[
            "پس از ساخت سقف تیغه‌ای، آجرکاری کف به شیوهٔ فرش آجر اجرا شد.",
        ],
        root_fa="پالانه",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات آجری «پالانه» را «آجرکاری که مانند فرش آجر بعد از ساختن سقف انجام "
            "می‌شود (سقف‌های تیغه‌ای)» تعریف می‌کند و «فرش کف» را آجرکاری کف بنا می‌داند."
        ),
        origin_lang="fa",
        references=[PUB55, M8, TRAD],
        related_terms=["blockage", "cumin", "square-brick", "sealing", "asphalt"],
    ),
    "fancy-lace": rev(
        term_en="diamond wire mesh",
        synonyms=["توری مشبک", "فنس"],
        search_aliases=["توری فنسی", "توری سیمی"],
        usage_examples=[
            "محوطهٔ کارگاه با توری فنسی حصارکشی شد و مصالح انبارشده با آن محافظت گردید.",
        ],
        root_fa="توری",
        etymology_fa=(
            "واژه‌نامهٔ اصطلاحات کارگاهی «توری فنسی» را «کلاف‌بندی مشبک از مفتول‌های نازک نرم "
            "(۲ و ۳ میلی‌متری)» تعریف می‌کند که به‌دلیل چشمه‌های لوزی‌شکل، «توری لوزی» نیز خوانده "
            "می‌شود."
        ),
        origin_lang="other",
        references=[M12, SITE],
        related_terms=["wire-reinforcement", "zigzag", "a-basket"],
    ),
    "index-arrow": rev(
        term_en="king post",
        synonyms=["شاخص خرپا", "عضو قائم خرپا"],
        search_aliases=["خرپای شاه‌تیری"],
        usage_examples=[
            "در خرپای شاه‌تیری، تیر شاخص نیروی گره میانی را به تیر بالایی منتقل می‌کند.",
        ],
        root_fa="شاخص",
        etymology_fa=(
            "«شاخص» در فارسی به چیزی گفته می‌شود که برجسته و نمایان باشد؛ «تیر شاخص» عضو قائم "
            "میانهٔ خرپاست و معادل انگلیسی آن king post است. ترجمهٔ آلمانی آن در این بازبینی "
            "راستی‌آزمایی نشد و عمداً تهی مانده است."
        ),
        origin_lang="fa",
        references=[MECH, M10],
        related_terms=["bending-moment", "traverse", "concrete-beam", "zigzag"],
    ),

    # ------------------------------------------------------------------ تأسیسات و زیرزمین
    "riser": rev(
        term_en="riser",
        synonyms=["لولهٔ بالارونده", "کانال تأسیسات"],
        search_aliases=["رایزر تأسیسات"],
        usage_examples=[
            "رایزر آب گرم و سرد در داکت عمودی مشترک و با دسترسی بازرسی اجرا شد.",
        ],
        root_fa="رایزر",
        etymology_fa="وام‌واژه از انگلیسی riser (بالارونده)؛ در تأسیسات ساختمان به مسیر عمودی لوله یا کانال گفته می‌شود.",
        origin_lang="en",
        plural_fa="رایزرها",
        references=[M4, PUB55],
        related_terms=["gallery", "the-well", "septic-tank"],
    ),
    "septic-tank": rev(
        term_en="septic tank",
        synonyms=["مخزن سپتیک", "چاه سپتیک"],
        usage_examples=[
            "پساب خروجی از سپتیک تانک باید به میدان جذب یا چاه جذبی منتقل شود.",
        ],
        root_fa="سپتیک",
        etymology_fa=(
            "«سپتیک» وام‌واژه از فرانسوی/انگلیسی septic، از یونانی sēptikos (فسادآور) و اشاره به "
            "تجزیهٔ بی‌هوازی دارد؛ «تانک» از انگلیسی tank. این مخزن پسماند را با ته‌نشینی و تجزیهٔ "
            "بی‌هوازی جدا می‌کند."
        ),
        origin_lang="fr",
        references=[M4, PUB55],
        related_terms=["cesspool-tank", "the-well", "blind-well", "riser"],
    ),
    "cesspool-tank": rev(
        term_en="cesspool tank",
        synonyms=["چاه فاضلاب", "مخزن جمع‌آوری پساب"],
        search_aliases=["سیسپول"],
        usage_examples=[
            "مخزن جمع‌آوری پساب باید به‌طور دوره‌ای تخلیه و گازهای آن کنترل شود.",
        ],
        root_fa="سیسپول",
        etymology_fa=(
            "«سیسپول» صورت فارسی‌شدهٔ انگلیسی cesspool است؛ برخلاف سپتیک تانک، تجزیهٔ مؤثر و "
            "خروجی تصفیه‌شده ندارد و عمدتاً برای نگهداری و تخلیهٔ دوره‌ای پساب به کار می‌رود."
        ),
        origin_lang="en",
        references=[M4, PUB55],
        related_terms=["septic-tank", "the-well", "blind-well"],
    ),
    "the-well": rev(
        term_en="shaft",
        synonyms=["چاهک", "محفظهٔ عمودی"],
        root_fa="چاه",
        etymology_fa=(
            "«چاهک» تصغیر «چاه» است؛ در ساختمان به محفظهٔ عمودی با ارتفاع محدود برای دسترسی به "
            "تأسیسات، زهکشی یا بازرسی گفته می‌شود."
        ),
        origin_lang="fa",
        plural_fa="چاهک‌ها",
        references=[M7, PUB55],
        related_terms=["blind-well", "wheel-well", "gallery", "septic-tank"],
    ),
    "blind-well": rev(
        term_en="blind well",
        synonyms=["چاه پرشده", "چاه پنهان"],
        usage_examples=[
            "پیش از گودبرداری، چاه‌های کور محدوده شناسایی و با مصالح دانه‌ای متراکم پر شدند.",
        ],
        root_fa="چاه",
        etymology_fa=(
            "«کور» در فارسی به معنای نابینا و پوشیده است؛ «چاه کور» چاهی است که دهانهٔ آن پوشیده و "
            "محل آن در سطح زیر بنا مشخص نیست و خطر نشست موضعی پی را ایجاد می‌کند."
        ),
        origin_lang="fa",
        references=[M7, M12],
        related_terms=["the-well", "wheel-well", "drop", "brackish-soil", "sealing"],
    ),
    "wheel-well": rev(
        term_en="well windlass",
        synonyms=["چرخ آبکشی", "محالهٔ چاه"],
        root_fa="چرخ",
        etymology_fa="«چرخ چاه» سازهٔ چرخشی است که با چرخاندن آن آب از چاه بالا کشیده می‌شود؛ از چوب یا فلز ساخته می‌شد.",
        origin_lang="fa",
        references=[M7, PUB55],
        related_terms=["the-well", "blind-well"],
    ),
    "retaining-wall": rev(
        term_en="retaining wall",
        synonyms=["دیوار نگهبان", "دیوار حائل خاک"],
        usage_examples=[
            "دیوار حائل گودبرداری باید در برابر لغزش، واژگونی و ظرفیت باربری زمین کنترل شود.",
        ],
        root_fa="حائل",
        root_ar="ح-و-ل",
        etymology_fa=(
            "«حائل» وام‌واژهٔ عربی به معنای مانع و جداکننده است؛ در مهندسی به سازه‌ای گفته می‌شود که "
            "خاک یا مصالح پشت خود را در برابر نیروی جانبی نگه می‌دارد. توجه: واژه‌نامهٔ اصطلاحات "
            "آجری «دیوار حائل» را «دیوار جداکنندهٔ فضا» تعریف کرده که تعریفی عامیانه است؛ تعریف "
            "مهندسی همین مدخل معتبر است."
        ),
        origin_lang="ar",
        plural_fa="دیوارهای حائل",
        references=[M7, ACI318, std("EN 1992-1-1", N_SCOPE)],
        related_terms=["pier", "blade", "brackish-soil", "drop", "tension"],
    ),

    # ------------------------------------------------------------------ واژه‌های چندمعنایی/صنفی
    "countries": rev(
        term_en="mortar bucket",
        definition_fa=(
            "این واژه در منابع دو حس دارد: (۱) در گفتار کارگاهی، «دول» صورت محلی «دلو» است و به سطل "
            "بنایی گفته می‌شود که برای حمل ملات، آب یا مصالح به کار می‌رود و معمولاً فلزی یا "
            "پلاستیکی با دستهٔ محکم است؛ (۲) در بنایی سنتی، «دوال» به برجستگی‌هایی گفته می‌شود که "
            "مانند طاقچه بر بدنهٔ دیوار می‌ساختند. هر دو حس در این مدخل نگه داشته شده‌اند."
        ),
        synonyms=["دلو بنایی", "سطل ملات", "دوال"],
        search_aliases=["دول"],
        usage_examples=["ملات با دول (سطل بنایی) به طبقهٔ بالا برده شد."],
        root_fa="دول",
        etymology_fa=(
            "«دول/دلو» از عربی «دلو» به معنای سطل آب است؛ «دوال» در واژه‌نامهٔ اصطلاحات آجری به "
            "برجستگی‌های طاقچه‌مانند روی بدنهٔ دیوار گفته می‌شود. داده‌های پیشین پروژه این مدخل را "
            "با معنای نخست ثبت کرده بودند و در این بازبینی، حس دوم نیز مستند شد. شناسهٔ مدخل "
            "(countries) بازماندهٔ ترجمهٔ ماشینی نادرست است و حفظ شده است."
        ),
        origin_lang="ar",
        root_ar="د-ل-و",
        references=[PUB55, SITE, TRAD],
        related_terms=["basket", "pillow", "tamper", "pointing-mortar"],
    ),
    "basket": rev(
        term_en="corbel",
        synonyms=["کنسول بنایی", "پیش‌آمدگی آجری"],
        search_aliases=["سله", "پیش‌طره"],
        usage_examples=[
            "تکیه‌گاه طاقچه با سِله‌های آجری پله‌ای از بدنهٔ دیوار بیرون آورده شد.",
        ],
        root_fa="سله",
        etymology_fa=(
            "«سِله» واژه‌ای صنفی در بنایی سنتی برای جزء پیش‌آمده‌ای است که از سطح دیوار بیرون می‌زند؛ "
            "واژه‌نامهٔ اصطلاحات آجری «پیش‌طره» را پیشامدگی سقف بالکن و سایبان بالای پنجره تعریف "
            "می‌کند که از همین خانواده است. معادل علمی آن corbel است."
        ),
        origin_lang="other",
        references=[M8, EN_MASONRY, TRAD],
        related_terms=["pier", "cap", "stiff-head", "countries", "masonry-course"],
    ),
    "stone-cement": rev(
        term_en="stone cement",
        definition_fa=(
            "سیمان آسیاب‌شدهٔ بسیار نرم یا سیمانی که از آسیاب سنگ‌های آهکی پخته به دست می‌آید و به "
            "عنوان مادهٔ چسباننده در ملات‌های خاص، بندکشی و ترمیم سطوح بتنی به کار می‌رود."
        ),
        synonyms=["سیمان نرم", "پودر سیمان"],
        search_aliases=["سیمان سنگ‌شده"],
        root_fa="سیمان",
        etymology_fa=(
            "ترکیب «سیمان» و «سنگ‌شده»؛ در متون قدیمی‌تر به سیمان‌های طبیعی (natural cement) که از "
            "پختن و آسیاب سنگ آهک رسی به دست می‌آمدند نیز گفته می‌شد."
        ),
        origin_lang="fa",
        references=[std("استاندارد ملی ایران ۳۸۹", N_TERM), std("ASTM C150", N_TERM), std("ASTM C989", N_SCOPE)],
        related_terms=["siman", "pointing-mortar", "cement-matrix", "beton"],
    ),
    "ginger": rev(
        term_en="brick wetting",
        translation_notes=None,
        definition_fa=(
            "عمل ترکردن یا خیساندن آجر پیش از بنایی، تا آب ملات را جذب نکند و پیوستگی میان آجر و "
            "ملات به‌درستی برقرار شود. واژه‌نامهٔ اصطلاحات آجری «زنجاب» را «سیراب کردن آجرها» و "
            "«آبخور» را آجری تعریف می‌کند که آب در آن نفوذ کرده و نرم شده باشد."
        ),
        synonyms=["آبخور", "سیراب کردن آجر", "خیساندن آجر"],
        search_aliases=["زنجاب"],
        usage_examples=[
            "آجرها پیش از چیدن زنجاب (سیراب) شدند تا آب ملات را نمکند.",
        ],
        root_fa="زنجاب",
        etymology_fa=(
            "«زنجاب» در بنایی سنتی به سیراب‌کردن آجرها گفته می‌شود. معادل انگلیسی پیشین این مدخل "
            "(pre-wetted brick) به خود آجر اشاره داشت، در حالی که واژهٔ فارسی نامِ عمل است؛ در این "
            "بازبینی معادل اصلاح شد. شناسهٔ مدخل (ginger) بازماندهٔ ترجمهٔ ماشینی نادرست است و "
            "حفظ شده است."
        ),
        origin_lang="other",
        references=[M8, BRICK, TRAD],
        related_terms=["pointing-mortar", "masonry-course", "lime-bloom", "gravel", "broken-brick"],
    ),
    "passing": {"term_en": "wall base course"},
}

for _tid, _patch in BATCH.items():
    REVIEW.setdefault(_tid, {}).update(_patch)
