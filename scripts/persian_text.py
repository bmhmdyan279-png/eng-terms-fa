#!/usr/bin/env python3
"""Persian text engine: normalization, tokenization, stemming and root-finding.

Why this module exists
----------------------
The site used to rely on Pagefind alone. Pagefind is a generic tokenizer: it
does not know that «آجرها», «آجر» and «آجری» are the same headword, that
«آب‌بندی» and «بندکشی» share the root «بند», or that «مشخصات» is the broken
plural of «مشخصه». Persian technical queries therefore returned nothing.

This module implements a **conservative, lexicon-guarded** Persian morphology
pipeline:

1. ``normalize``      — orthographic canonicalization (ی/ک, اعراب, ارقام, ZWNJ).
2. ``tokenize``       — word splitting that respects the Persian half-space
                        (نیم‌فاصله): «آب‌بندی» yields the compound *and* its parts.
3. ``stem``           — inflectional stripping (plural, possessive, comparative,
                        verbal prefix). Safe affixes only need a length guard;
                        ambiguous affixes (ی، ات، ان، این) require the result to
                        exist in the lexicon, so we never stem into a non-word.
4. ``root``           — stem + derivational stripping + irregular maps
                        (Arabic broken plurals, Persian present-stem verbs), so
                        «بندی» and «بستن» both land on the root «بند».
5. ``index_forms``    — every surface form a query might use for one string.
6. ``suggest``        — typo tolerance (edit distance ≤ 1, keyboard-aware).

Design rule (mirrors the project's data policy): **when morphology is ambiguous,
do nothing.** A missed stem loses ranking; a wrong stem loses trust.

Usage
-----
    from persian_text import build_lexicon, normalize, root, index_forms

    lexicon = build_lexicon(records)          # from data/terms/*.yaml
    forms = index_forms("آب‌بندی پی", lexicon)

The exact same rules are mirrored in ``docs/assets/js/persian-stem.js``;
``tools/check_stemmer_parity.js`` proves the two agree in CI.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable

# --------------------------------------------------------------------------- #
# Character classes
# --------------------------------------------------------------------------- #

ZWNJ = "\u200c"  # نیم‌فاصله
ZWJ = "\u200d"
TATWEEL = "\u0640"  # کشیده
HARAKAT = "".join(chr(c) for c in range(0x064B, 0x0653))  # اعراب + تنوین + تشدید
SUPERSCRIPT_ALEF = "\u0670"
BIDI_MARKS = "\u200e\u200f\u202a\u202b\u202c\u202d\u202e"
HEH_YEH = "\u06c3"  # هٔ (heh + hamza above, as in خانهٔ)
HAMZA_YEH = "\u0626"  # ئ
ARABIC_YEH = "\u064a"
PERSIAN_YEH = "\u06cc"
ARABIC_KAF = "\u0643"
PERSIAN_KAF = "\u06a9"
TEH_MARBUTA = "\u0629"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ASCII_DIGITS = "0123456789"

PERSIAN_RE = re.compile(r"[\u0621-\u063a\u0641-\u064a\u066e-\u06d3\u06cc\u06a9\u06af\u067e\u0686\u0698\u06cc]")
LATIN_RE = re.compile(r"[A-Za-z]")
# NOTE the "+": without it `fullmatch` could never match a multi-digit token
# (a single-character class matches exactly one character) and every number in
# the corpus silently survived the content-token filter.
DIGIT_RE = re.compile(r"[0-9۰-۹٠-٩]+")
# \w already covers Arabic-script letters (they are category Lo), so the
# separator class must NOT include the whole \u0600-\u06ff block: that block
# also holds Arabic punctuation (، ؛ ؟ ٫ ٬) which would otherwise be glued to
# the word — «ساختمان،» instead of «ساختمان». U+200C (نیم‌فاصله) is not a \w
# character and must be excluded from the separators, otherwise «آب‌بندی»
# would be split before tokenize() ever sees the compound.
WORD_SPLIT_RE = re.compile(r"[^\w\u200c]+", re.UNICODE)

# --------------------------------------------------------------------------- #
# Affix tables — order matters (longest / most specific first)
# --------------------------------------------------------------------------- #

#: Inflectional suffixes safe to strip with only a length guard. «ها» and its
#: derivatives are overwhelmingly plural in Persian, and «تر»/«ترین» are
#: comparative; every colliding word (ماه، راه، بستر، برتر) is either shorter
#: than MIN_STEM_LENGTH after stripping or does not actually end with the affix.
SAFE_SUFFIXES = (
    "هایی", "های", "ها",
    "ترین", "تر",
)

#: Suffixes that collide with real morphology — the stripped result must be a
#: known word before we accept the reduction:
#:   * «ات» : مشخصات is a broken plural, not مشخص + ات
#:   * «ان» : مردان vs. words that merely end in ان
#:   * «ی»  : یای نسبت vs. words ending in ی (دیگری، پایه)
#:   * «ام/اش/مان/…» : enclitics vs. words like اندام
GUARDED_SUFFIXES = (
    "هایشان", "هایتان", "هایمان", "هایم",
    "یشان", "شان", "تان", "مان",
    "گانی", "گان", "یانی", "یان",
    "اتان", "اتی", "ات",
    "ینان", "ین", "ونات", "ون",
    "ان",
    "ندگی", "ایی", "گی", "گری",
    "مند", "وار", "ناک", "آسا", "گون",
    "زار", "کده", "گاه", "ستان", "دان",
    "ام", "اش", "ای", "یی", "ی",
)

#: Verbal / negative / quantifier prefixes. Always lexicon-guarded: Persian is
#: full of monosyllables that would be mangled otherwise («نازک» → «زک»).
PREFIXES = (
    "نمی", "می", "همی",
    "نا", "بی", "با", "هم", "هر", "هیچ", "خود",
    "پر", "کم", "نیم", "خوش", "بد",
    "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه", "ده",
)

#: Minimum stem length after stripping — never reduce below this.
MIN_STEM_LENGTH = 3

#: Minimum length of each half of an unspaced compound split.
MIN_PART_LENGTH = 3

#: Longest string for which a space-free variant is indexed (see index_forms).
MAX_COLLAPSED_LENGTH = 60

# --------------------------------------------------------------------------- #
# Lexicons
# --------------------------------------------------------------------------- #

#: Function words removed from queries before matching (kept in the index so
#: that phrase search still works).
STOPWORDS = frozenset(
    """
    و یا که از به در با برای بر علیه تا نیز هم چه هر یک دو سه این آن اینها آنها
    که چیست بوده باشد باشند بود بود بودن شد شدن شده می نمی دارد دارند داشت
    است هستند هستندی نیست تا وقتی پس سپس اما ولی اگر چون زیرا مثل مانند نظیر
    طبق براساس بر اساس درباره درمورد راجع به هنگام موقع بین میان مقابل جلوی
    پشت بالای زیر کنار نزد پیش تمام کل هرگونه هیچ هیچگونه دیگر سایر بقیه
    صورت طور حالت جهت سمت طرف مورد موارد بخش قسم قسمت
    """
    .split()
)

#: Persian irregular / strong verbs: infinitive → (past stem, present stem).
#: The present stem (بن مضارع) is the productive root of derived nouns:
#: «بستن» → «بند» → «آب‌بندی»، «بندکشی»، «بندِ آجر».
VERB_STEMS: dict[str, tuple[str, str]] = {
    "شدن": ("شد", "شو"),
    "کردن": ("کرد", "کن"),
    "دادن": ("داد", "ده"),
    "داشتن": ("داشت", "دار"),
    "گذاشتن": ("گذاشت", "گذار"),
    "گرفتن": ("گرفت", "گیر"),
    "زدن": ("زد", "زن"),
    "خوردن": ("خورد", "خور"),
    "آوردن": ("آورد", "آور"),
    "رفتن": ("رفت", "رو"),
    "دیدن": ("دید", "بین"),
    "گفتن": ("گفت", "گوی"),
    "شنیدن": ("شنید", "شنو"),
    "خواندن": ("خواند", "خوان"),
    "نوشتن": ("نوشت", "نویس"),
    "ساختن": ("ساخت", "ساز"),
    "ریختن": ("ریخت", "ریز"),
    "بستن": ("بست", "بند"),
    "دوختن": ("دوخت", "دوز"),
    "چیدن": ("چید", "چین"),
    "ساییدن": ("سایید", "ساب"),
    "کندن": ("کند", "کن"),
    "بریدن": ("برید", "بر"),
    "کشیدن": ("کشید", "کش"),
    "یافتن": ("یافت", "یاب"),
    "پختن": ("پخت", "پز"),
    "دویدن": ("دوید", "دو"),
    "چسبیدن": ("چسبید", "چسب"),
    "تراشیدن": ("تراشید", "تراش"),
    "لرزیدن": ("لرزید", "لرز"),
    "فشردن": ("فشرد", "فشار"),
    "آمیختن": ("آمیخت", "آمیز"),
    "افزودن": ("افزود", "افزا"),
    "کاستن": ("کاست", "کاه"),
    "نشستن": ("نشست", "نشین"),
    "خوابیدن": ("خوابید", "خواب"),
    "ایستادن": ("ایستاد", "ایست"),
    "فرسودن": ("فرسود", "فرسا"),
    "پوسیدن": ("پوسید", "پوس"),
    "جوشیدن": ("جوشید", "جوش"),
    "ورزیدن": ("ورزید", "ورز"),
    "پرداختن": ("پرداخت", "پرداز"),
    "پوشاندن": ("پوشاند", "پوشان"),
    "پوشیدن": ("پوشید", "پوش"),
    "برداشتن": ("برداشت", "بردار"),
    "بردن": ("برد", "بر"),
    "پاشیدن": ("پاشید", "پاش"),
    "کوبیدن": ("کوبید", "کوب"),
    "مالیدن": ("مالید", "مال"),
    "جوشاندن": ("جوشاند", "جوشان"),
    "چسباندن": ("چسباند", "چسبان"),
    "لرزاندن": ("لرزاند", "لرزان"),
    "نهادن": ("نهاد", "نه"),
    "تراشیدن": ("تراشید", "تراش"),
    "آمیختن": ("آمیخت", "آمیز"),
}

#: Reverse lookup: a present/past stem → its infinitive (the "root family").
STEM_TO_VERB: dict[str, str] = {}
for _inf, (_past, _present) in VERB_STEMS.items():
    STEM_TO_VERB.setdefault(_present, _inf)
    STEM_TO_VERB.setdefault(_past, _inf)

#: Personal endings of the Persian verb (present and past paradigms).
VERB_ENDINGS = ("", "م", "ی", "د", "یم", "ید", "ند", "ه", "های", "ها", "ایم", "اید", "اند")

#: Conjugated form → (infinitive, past stem, present stem).
#: Generated, not hand-written, so it stays consistent with VERB_STEMS.
CONJUGATIONS: dict[str, tuple[str, str, str]] = {}
for _inf, (_past, _present) in VERB_STEMS.items():
    for _stem in (_past, _present):
        for _ending in VERB_ENDINGS:
            CONJUGATIONS.setdefault(_stem + _ending, (_inf, _past, _present))

#: Arabic broken plurals (جمع مکسر) common in Persian technical writing.
#: These cannot be produced by suffix rules; they need an explicit map.
BROKEN_PLURALS: dict[str, str] = {
    "مشخصات": "مشخصه",
    "مصالح": "مصالح",       # treated as its own lemma in Persian usage
    "ابعاد": "بعد",
    "انواع": "نوع",
    "اجزا": "جزء",
    "اقسام": "قسم",
    "اعمال": "عمل",
    "اقلام": "قلم",
    "مواضع": "موضع",
    "اسناد": "سند",
    "اوراق": "ورق",
    "اطلاعات": "اطلاع",
    "مقاومت": "مقاومت",
    "مقایسه": "مقایسه",
    "محاسبات": "محاسبه",
    "ملاحظه": "ملاحظه",
    "تجهیزات": "تجهیز",
    "وسایل": "وسیله",
    "موارد": "مورد",
    "مراحل": "مرحله",
    "مزایا": "مزیت",
    "معایب": "عیب",
    "حفره": "حفره",
    "حفرات": "حفره",
    "لایه‌ها": "لایه",
    "ستون‌ها": "ستون",
    "ستونها": "ستون",
    "مقاطع": "مقطع",
    "منابع": "منبع",
    "مصارف": "مصرف",
    "محصولات": "محصول",
    "فرآورده‌ها": "فرآورده",
    "ضوابط": "ضابطه",
    "الزامات": "الزام",
    "مشاهدات": "مشاهده",
    "اندازه‌گیری‌ها": "اندازه‌گیری",
    "آزمایش‌ها": "آزمایش",
    "آزمایشات": "آزمایش",
    "تکنیک‌ها": "تکنیک",
    "روش‌ها": "روش",
    "انواع بتن": "نوع بتن",
    "قوس‌ها": "قوس",
    "طاق‌ها": "طاق",
    "رج‌ها": "رج",
    "بناها": "بنا",
    "سازه‌ها": "سازه",
    "سازه‌های": "سازه",
    "دانه‌ها": "دانه",
    "دانه‌بندی": "دانه‌بندی",
    "حباب‌ها": "حباب",
    "ترک‌ها": "ترک",
    "درزها": "درز",
    "درز‌ها": "درز",
    "پی‌ها": "پی",
    "لغزش": "لغزش",
}

#: Surface forms that must never be reduced.
#:
#: This list is deliberately *short*. The affix tables above are already
#: length-guarded (``MIN_STEM_LENGTH``) and lexicon-guarded, so nearly every
#: dangerous case is impossible by construction: «بهتر» → «به» is rejected for
#: length, «دیگری» → «دگر» is rejected because «دگر» is not a known word.
#: What is left here are lexicalized forms whose reduction *would* pass both
#: guards, plus compounds that must stay whole.
STEM_EXCEPTIONS = frozenset(
    """
    دیگری مهتر کهتر بهتر
    ملات مصالح ثابت نبات حیات ممات نباتی
    نبشی نره سره سله سیمه
    ماه راه چاه نگاه سیاه روباه کوتاه پناه گناه
    یکپارچه سرگرد پشتکار خودکار همکار درباره درون بیرون
    پایه لایه سایه خانه رشته شاخه خانواده
    پاسنگ پالانه پاکار پاتاق پلیت پوتر
    """
    .split()
)


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

_CHAR_MAP = {
    ARABIC_YEH: PERSIAN_YEH,
    HAMZA_YEH: PERSIAN_YEH,
    ARABIC_KAF: PERSIAN_KAF,
    TEH_MARBUTA: "\u0647",  # ة → ه
    HEH_YEH: "\u0647",      # هٔ → ه
    TATWEEL: "",
    ZWJ: "",
    SUPERSCRIPT_ALEF: "",
    "أ": "آ",
    "إ": "ا",
    "ٱ": "ا",
    "ى": PERSIAN_YEH,
}
for _mark in BIDI_MARKS:
    _CHAR_MAP[_mark] = ""
for _haraka in HARAKAT:
    _CHAR_MAP[_haraka] = ""
for _a, _b in zip(ARABIC_DIGITS, ASCII_DIGITS):
    _CHAR_MAP[_a] = _b
for _a, _b in zip(PERSIAN_DIGITS, ASCII_DIGITS):
    _CHAR_MAP[_a] = _b

#: Public alias — scripts/generate_stem_data.py exports this table to JS so the
#: browser stemmer and the build stemmer can never disagree about characters.
CHAR_MAP = _CHAR_MAP
_TRANSLATION = str.maketrans(_CHAR_MAP)


def normalize(text: str) -> str:
    """Canonical orthographic form used for every comparison and index key.

    * Arabic ی/ک → Persian ی/ک, ة → ه, هٔ → ه, أ/إ/ٱ → آ/ا/ا
    * diacritics, tatweel, ZWJ and bidi marks removed
    * Arabic-Indic and Persian digits → ASCII digits
    * NFKC, whitespace collapsed

    The half-space (ZWNJ) is **preserved** here: it is meaningful in Persian
    («می‌شود» ≠ «میشود» visually) and is handled by :func:`tokenize`.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.translate(_TRANSLATION)
    return re.sub(r"\s+", " ", text).strip()


def fold(text: str) -> str:
    """:func:`normalize` + ZWNJ removal + casefold — the loosest match key."""
    normalized = normalize(text)
    return normalized.replace(ZWNJ, "").casefold().strip()


def strip_diacritics(text: str) -> str:
    """Remove harakat/tatweel only (used for the Arabic column)."""
    if not text:
        return ""
    return "".join(c for c in text if c not in HARAKAT and c != TATWEEL).strip()


def normalize_latin(text: str) -> str:
    """Lowercase + NFKC for EN/FR/DE columns, keeping spaces single."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip().casefold()


# --------------------------------------------------------------------------- #
# Tokenization
# --------------------------------------------------------------------------- #

def tokenize(text: str) -> list[str]:
    """Split into searchable tokens, honouring the Persian half-space.

    «آب‌بندی» → ['آب‌بندی', 'آب', 'بندی'] — the compound first (highest
    weight), then its parts, so that both «آب‌بندی» and «بند» can match.
    «می‌شود» → ['می‌شود', 'می', 'شود'].
    """
    normalized = normalize(text)
    if not normalized:
        return []
    tokens: list[str] = []
    seen: set[str] = set()

    def push(token: str) -> None:
        token = token.strip()
        if token and token not in seen:
            seen.add(token)
            tokens.append(token)

    for chunk in WORD_SPLIT_RE.split(normalized):
        if not chunk:
            continue
        push(chunk)
        if ZWNJ in chunk:
            for part in chunk.split(ZWNJ):
                push(part)
            push(chunk.replace(ZWNJ, ""))
        # Latin compounds with hyphens: «self-consolidating» → parts as well
        if "-" in chunk:
            for part in chunk.split("-"):
                push(part)
    return tokens


def content_tokens(text: str) -> list[str]:
    """:func:`tokenize` minus stopwords and pure-digit tokens."""
    out = []
    for token in tokenize(text):
        bare = token.replace(ZWNJ, "")
        if bare in STOPWORDS:
            continue
        if DIGIT_RE.fullmatch(bare):
            continue
        out.append(token)
    return out


# --------------------------------------------------------------------------- #
# Lexicon
# --------------------------------------------------------------------------- #

def build_lexicon(records: Iterable[dict] | None = None, extra: Iterable[str] = ()) -> set[str]:
    """Collect every known Persian word: curated base words + dataset words.

    The lexicon is the guard rail of the stemmer: an ambiguous affix is only
    stripped when the remainder is a known word. Records contribute their
    term_fa, synonyms, search_aliases, plural_fa and (importantly) ``root_fa``
    — so authors can teach the stemmer new roots simply by filling the field.
    """
    words: set[str] = set(STEM_EXCEPTIONS)
    words.update(STOPWORDS)
    words.update(BROKEN_PLURALS)
    words.update(BROKEN_PLURALS.values())
    words.update(STEM_TO_VERB)
    words.update(VERB_STEMS)
    words.update(CONJUGATIONS)
    for verb, (past, present) in VERB_STEMS.items():
        words.update({verb, past, present})
    for item in extra:
        words.update(tokenize(item))

    #: Prose fields feed the lexicon too: verb forms such as «شود» or «می‌گیرد»
    #: only become strippable once they are known words, which keeps the
    #: guarded prefix rule for «می» honest («میلگرد» must never lose «می»).
    for record in records or []:
        if not isinstance(record, dict):
            continue
        for field in ("term_fa", "root_fa", "plural_fa", "etymology_fa",
                      "definition_fa"):
            value = record.get(field)
            if isinstance(value, str):
                words.update(tokenize(value))
        for field in ("synonyms", "antonyms", "search_aliases", "usage_examples"):
            for value in record.get(field) or []:
                if isinstance(value, str):
                    words.update(tokenize(value))
    return {fold(w) for w in words if w}


def build_protected(records: Iterable[dict] | None = None) -> set[str]:
    """Headwords that must never be reduced.

    A dictionary headword is a lexicalized unit: «سیمان» is a loanword, not
    «سیم» + «ان»، and «رومی» is not «روم» + ی. Reducing them would create
    false root families («سیم آرماتوربندی» ← «سیمان»!).

    Only *single-token* headwords are protected. Multi-token headwords such as
    «آب بندی» are made of reducible parts — «بندی» must still reduce to «بند»,
    otherwise the whole root family disappears.
    """
    protected: set[str] = set()
    for record in records or []:
        if not isinstance(record, dict):
            continue
        candidates = [record.get("term_fa")]
        for field in ("synonyms", "search_aliases"):
            candidates.extend(record.get(field) or [])
        for value in candidates:
            if not isinstance(value, str) or not value.strip():
                continue
            tokens = tokenize(value)
            if len(tokens) == 1:
                protected.add(fold(tokens[0]))
    return protected


def _known(token: str, lexicon: set[str]) -> bool:
    return fold(token) in lexicon


# --------------------------------------------------------------------------- #
# Stemming & root-finding
# --------------------------------------------------------------------------- #

def _strip_suffix(token: str, lexicon: set[str]) -> str:
    """One round of suffix reduction: safe affixes, then lexicon-guarded ones."""
    for affix in SAFE_SUFFIXES:
        if token.endswith(affix) and len(token) - len(affix) >= MIN_STEM_LENGTH:
            return token[: -len(affix)]
    for affix in GUARDED_SUFFIXES:
        if token.endswith(affix) and len(token) - len(affix) >= MIN_STEM_LENGTH:
            rest = token[: -len(affix)]
            if _known(rest, lexicon):
                return rest
    return token


def _strip_prefix(token: str, lexicon: set[str]) -> str:
    """One round of prefix reduction — always lexicon-guarded."""
    for affix in PREFIXES:
        if token.startswith(affix) and len(token) - len(affix) >= MIN_STEM_LENGTH:
            rest = token[len(affix):]
            if _known(rest, lexicon):
                return rest
    return token


#: Lexicalized compounds that look splittable but must stay whole.
NO_SPLIT = frozenset({"سرگرد", "پشتکار", "خودکار", "درباره", "همکار", "چهارچوب"})


def split_compound(token: str, lexicon: set[str],
                   protected: frozenset[str] | set[str] | None = None) -> list[str]:
    """Split an unspaced Persian compound into its two known parts.

    Persian technical prose is full of Noun+Verb-derived compounds written
    without a half-space: «آجرکاری»، «بندکشی»، «خاکبرداری»، «نماسازی»،
    «سنگفرش»، «پشتبند». A query for «آجر» must find «آجرکاری».

    The split is accepted only when *both* parts are known words and each part
    is at least MIN_PART_LENGTH long — otherwise the token stays whole. That
    keeps «تیرچه» (remainder «چه» too short) and «میلگرد» («میل» unknown) intact.
    """
    protected = protected if protected is not None else set()
    bare = token.replace(ZWNJ, "")
    if bare in NO_SPLIT or fold(bare) in STOPWORDS:
        return []
    if len(bare) < 2 * MIN_PART_LENGTH:
        return []
    for cut in range(len(bare) - MIN_PART_LENGTH, MIN_PART_LENGTH - 1, -1):
        head, tail = bare[:cut], bare[cut:]
        if len(head) < MIN_PART_LENGTH or len(tail) < MIN_PART_LENGTH:
            continue
        head_known = _known(head, lexicon) or _known(stem(head, lexicon, protected), lexicon)
        tail_known = _known(tail, lexicon) or _known(stem(tail, lexicon, protected), lexicon)
        if head_known and tail_known:
            return [head, tail]
    return []


def stem(token: str, lexicon: frozenset[str] | set[str] | None = None,
         protected: frozenset[str] | set[str] | None = None) -> str:
    """Light inflectional stemming (suffixes only).

    Deterministic and idempotent: ``stem(stem(t)) == stem(t)``.
    ``protected`` holds headwords that must survive untouched (see
    :func:`build_protected`).
    """
    lexicon = lexicon if lexicon is not None else set()
    protected = protected if protected is not None else set()
    token = normalize(token).strip()
    if not token:
        return token
    bare = token.replace(ZWNJ, "")
    if bare in STEM_EXCEPTIONS or fold(bare) in STEM_EXCEPTIONS:
        return bare
    if fold(bare) in protected:
        return bare
    if bare in BROKEN_PLURALS or fold(bare) in BROKEN_PLURALS:
        return BROKEN_PLURALS.get(bare) or BROKEN_PLURALS[fold(bare)]

    current = bare
    for _ in range(2):  # «میلگردهایمان» → «میلگردهای» → «میلگرد»
        reduced = _strip_suffix(current, lexicon)
        if reduced == current:
            break
        current = reduced
    return current


#: Verb stems may legitimately be two letters long («شد»، «زد»، «داد») because
#: they come from an explicit table, not from a guess.
MIN_ROOT_LENGTH = 2


def root(token: str, lexicon: frozenset[str] | set[str] | None = None,
         protected: frozenset[str] | set[str] | None = None) -> str:
    """Deep reduction: suffixes → prefixes → broken plurals → verb paradigms.

    «بندی» → «بند»   «می‌شود» → «شد»   «ناشاقولی» → «شاقول»
    «مشخصات» → «مشخصه»   «آجرهایمان» → «آجر»
    """
    lexicon = lexicon if lexicon is not None else set()
    protected = protected if protected is not None else set()
    current = stem(token, lexicon, protected)
    folded = fold(current)
    if folded in BROKEN_PLURALS:
        current = BROKEN_PLURALS[folded]

    if fold(current) not in protected:
        current = _strip_prefix(current, lexicon)
    folded = fold(current)
    if folded in BROKEN_PLURALS:
        return BROKEN_PLURALS[folded]

    # A bare stem stays bare: «بند» is the productive base of «آب‌بندی» and
    # «بندکشی», so it must not be rewritten into «بستن» or into the past stem
    # «بست». This check precedes CONJUGATIONS because a bare stem is also a
    # (zero-ending) conjugated form.
    if folded in STEM_TO_VERB and folded not in STEM_EXCEPTIONS:
        return current

    conjugation = CONJUGATIONS.get(folded)
    if conjugation is not None and folded not in STEM_EXCEPTIONS:
        _infinitive, past, _present = conjugation
        return past if len(past) >= MIN_ROOT_LENGTH else current

    return stem(current, lexicon, protected)


def root_family(token: str, lexicon: frozenset[str] | set[str] | None = None,
                protected: frozenset[str] | set[str] | None = None) -> str | None:
    """The infinitive a token belongs to, when the token is a verb form."""
    folded = fold(token)
    if folded in CONJUGATIONS:
        return CONJUGATIONS[folded][0]
    return STEM_TO_VERB.get(fold(root(token, lexicon, protected)))


def roots_of(text: str, lexicon: frozenset[str] | set[str] | None = None,
             protected: frozenset[str] | set[str] | None = None) -> list[str]:
    """All distinct roots of a (possibly compound) Persian string.

    «آب‌بندی» → ['آب‌بندی', 'آب', 'بند'] — the compound itself is kept because
    Persian compounds are lexicalized units, not mere sums of their parts.
    """
    lexicon = lexicon if lexicon is not None else set()
    protected = protected if protected is not None else set()
    out: list[str] = []

    def push(value: str) -> None:
        value = fold(value)
        if value and value not in out:
            out.append(value)

    for token in content_tokens(text):
        push(token)
        push(root(token, lexicon, protected))
        for part in split_compound(token, lexicon, protected):
            push(part)
            push(root(part, lexicon, protected))
        if ZWNJ in token:
            for part in token.split(ZWNJ):
                push(part)
                push(root(part, lexicon, protected))
    return out


def record_roots(record: dict, lexicon: frozenset[str] | set[str] | None = None,
                 protected: frozenset[str] | set[str] | None = None) -> list[str]:
    """The roots a term record contributes to (author-declared root first).

    Used both by the search index and by the «هم‌ریشه‌ها» panel on term pages,
    so the two can never disagree.
    """
    lexicon = lexicon if lexicon is not None else set()
    protected = protected if protected is not None else set()
    roots: list[str] = []
    sources = [record.get("root_fa"), record.get("term_fa")]
    for field in ("synonyms", "search_aliases"):
        sources.extend(str(v) for v in (record.get(field) or []) if v)

    for source in sources:
        if not source:
            continue
        for token in content_tokens(str(source)):
            for candidate in (fold(token), fold(root(token, lexicon, protected))):
                if candidate and len(candidate) >= 2 and candidate not in roots:
                    roots.append(candidate)
            for part in split_compound(token, lexicon, protected):
                candidate = fold(root(part, lexicon, protected))
                if candidate and len(candidate) >= 2 and candidate not in roots:
                    roots.append(candidate)

    declared = fold(str(record.get("root_fa") or ""))
    if declared and declared in roots:
        roots.remove(declared)
        roots.insert(0, declared)
    return roots


# --------------------------------------------------------------------------- #
# Indexing & fuzzy matching
# --------------------------------------------------------------------------- #

def index_forms(text: str, lexicon: frozenset[str] | set[str] | None = None,
                protected: frozenset[str] | set[str] | None = None) -> list[str]:
    """Every surface form that should match `text` in search.

    Ordered from most to least specific so ranking can use the position:
    the folded full string first, then tokens, stems, roots, compound parts
    and finally the verbal family (infinitive + both stems).
    """
    if not text:
        return []
    lexicon = lexicon if lexicon is not None else set()
    protected = protected if protected is not None else set()
    forms: list[str] = []
    seen: set[str] = set()

    def push(value: str) -> None:
        value = fold(value)
        if value and value not in seen:
            seen.add(value)
            forms.append(value)

    def push_family(value: str) -> None:
        family = CONJUGATIONS.get(fold(value))
        if family:
            push(family[0])
            push(family[1])
            push(family[2])
        infinitive = STEM_TO_VERB.get(fold(value))
        if infinitive:
            push(infinitive)

    push(text)
    # Space-free variant: Persian headwords are written with a space, a
    # half-space or nothing at all («آب بندی» / «آب‌بندی» / «آببندی»). All three
    # must hit the same entry, so the de-spaced form is indexed too. Only for
    # short strings — a definition would become one absurd token.
    collapsed = fold(text).replace(" ", "")
    if collapsed != fold(text) and len(collapsed) <= MAX_COLLAPSED_LENGTH:
        push(collapsed)
    for token in tokenize(text):
        push(token)
        push(stem(token, lexicon, protected))
        token_root = root(token, lexicon, protected)
        push(token_root)
        parts = list(split_compound(token, lexicon, protected))
        if ZWNJ in token:
            parts.extend(part for part in token.split(ZWNJ) if part)
        for part in parts:
            push(part)
            part_root = root(part, lexicon, protected)
            push(part_root)
            push_family(part)
            push_family(part_root)
        # verbal family: «می‌شود» must also answer to «شدن»، «شد» and «شو»
        push_family(token)
        push_family(token_root)
    return forms


def _edit_distance(a: str, b: str, max_distance: int = 2) -> int:
    """Levenshtein distance with early exit (returns max_distance+1 when bigger)."""
    if a == b:
        return 0
    if abs(len(a) - len(b)) > max_distance:
        return max_distance + 1
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        best = i
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            value = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            current.append(value)
            best = min(best, value)
        if best > max_distance:
            return max_distance + 1
        previous = current
    return previous[-1]


#: Persian keyboard confusions — a typo is far more likely between adjacent keys
#: or between visually similar glyphs than at random.
CONFUSABLES = (
    ("ز", "ر"), ("ز", "ذ"), ("ر", "ز"), ("د", "ذ"), ("ذ", "د"),
    ("س", "ش"), ("ش", "س"), ("ت", "ط"), ("ط", "ت"), ("ه", "ح"),
    ("ح", "ه"), ("ق", "غ"), ("غ", "ق"), ("و", "ؤ"), ("ی", "ئ"),
    ("ج", "چ"), ("چ", "ج"), ("ک", "گ"), ("گ", "ک"), ("ف", "ق"),
)


def suggest(token: str, vocabulary: Iterable[str], max_distance: int = 1, limit: int = 5) -> list[str]:
    """Typo-tolerant candidates for one token, best first.

    Ranking: exact prefix > confusable-key substitution > edit distance 1 > 2.
    """
    target = fold(token)
    if not target:
        return []
    scored: list[tuple[int, str]] = []
    for word in vocabulary:
        candidate = fold(word)
        if not candidate or candidate == target:
            continue
        if candidate.startswith(target) and len(candidate) - len(target) <= 3:
            scored.append((0, candidate))
            continue
        if target.startswith(candidate) and len(target) - len(candidate) <= 3:
            scored.append((1, candidate))
            continue
        if len(candidate) == len(target) and sum(
            1 for a, b in zip(candidate, target) if a != b
        ) == 1:
            pair = next(
                (a, b) for a, b in zip(candidate, target) if a != b
            )
            if pair in CONFUSABLES:
                scored.append((2, candidate))
            else:
                scored.append((3, candidate))
            continue
        distance = _edit_distance(candidate, target, max_distance)
        if distance <= max_distance:
            scored.append((4 + distance, candidate))
    scored.sort()
    seen: set[str] = set()
    out: list[str] = []
    for _, candidate in scored:
        if candidate in seen:
            continue
        seen.add(candidate)
        out.append(candidate)
        if len(out) >= limit:
            break
    return out


def highlight(text: str, query_tokens: Iterable[str]) -> str:
    """Return `text` with query occurrences wrapped in <mark> (plain-text safe).

    The caller is responsible for HTML-escaping `text` first; markers are added
    on the escaped string using escaped needle forms.
    """
    out = text
    for token in sorted({t for t in query_tokens if t}, key=len, reverse=True):
        out = re.sub(f"({re.escape(token)})", r"<mark>\1</mark>", out, flags=re.IGNORECASE)
    return out


# --------------------------------------------------------------------------- #
# Reporting helper (used by the audit scripts and tests)
# --------------------------------------------------------------------------- #

def orthography_warnings(text: str) -> list[str]:
    """Persian orthography lint for authored content (half-space, ی/ک, digits).

    The dictionary teaches spelling, so its own text must be exemplary.
    """
    problems: list[str] = []
    if not text:
        return problems
    if ARABIC_YEH in text:
        problems.append("استفاده از «ي» عربی به‌جای «ی» فارسی")
    if ARABIC_KAF in text:
        problems.append("استفاده از «ك» عربی به‌جای «ک» فارسی")
    if TEH_MARBUTA in text:
        problems.append("«ة» عربی در متن فارسی")
    if any(c in text for c in HARAKAT):
        problems.append("اعراب‌گذاری عربی در متن فارسی")
    if any(c in text for c in ARABIC_DIGITS + PERSIAN_DIGITS):
        problems.append("رقم فارسی/عربی — در داده‌ها از رقم لاتین استفاده کنید")
    if re.search(r"می(?=[^\s\u200c])", text):
        problems.append("«می» چسبیده — باید «می‌» با نیم‌فاصله باشد")
    if re.search(r"نمی(?=[^\s\u200c])", text):
        problems.append("«نمی» چسبیده — باید «نمی‌» با نیم‌فاصله باشد")
    if re.search(r"ها(?=[\u0621-\u06ff])", text):
        problems.append("«ها»ی جمع چسبیده به واژهٔ بعد — باید نیم‌فاصله باشد")
    if re.search(r"\s{2,}", text):
        problems.append("فاصلهٔ دوبل")
    if text != text.strip():
        problems.append("فاصلهٔ اضافه در ابتدا/انتها")
    if re.search(r"\.\s*\.", text):
        problems.append("نقطهٔ دوبل")
    return problems


if __name__ == "__main__":  # pragma: no cover — manual smoke run
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_pages import load_all_terms

    records = [record for _, record in load_all_terms()]
    lex = build_lexicon(records)
    samples = sys.argv[1:] or ["آب‌بندی", "میلگردهایمان", "مشخصات", "می‌شود", "آجرها", "ناشاقولی"]
    print(json.dumps(
        {s: {"tokens": tokenize(s), "stem": stem(s, lex), "root": root(s, lex),
             "forms": index_forms(s, lex)} for s in samples},
        ensure_ascii=False, indent=2,
    ))
    print(f"lexicon size: {len(lex)}")
