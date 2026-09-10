"""Content review — batch 5: پوشش کامل مترادف‌ها.

دو مدخل مکانیک بدون مترادف مانده بودند؛ هر دو یک معادل کهن/عربی دارند که
کاربر ممکن است جستجو کند، پس در داده ثبت می‌شود تا موتور جستجو مجبور به حدس
نباشد.
"""

from review_batch2 import M6
from review_batch3 import MECH
from review_data import REVIEW

BATCH = {
    "acceleration": {
        "synonyms": ["شتاب‌گیری", "تعجیل"],
        "search_aliases": ["شتاب زمین", "شتاب گرانش"],
        "usage_examples": [
            "شتاب مبنای طرح لرزه‌ای بر حسب بخشی از شتاب گرانش (g) بیان می‌شود.",
        ],
        "references": [MECH, M6],
    },
    "mass": {
        "synonyms": ["جرم جسم"],
        "search_aliases": ["کتله"],
        "usage_examples": [
            "جرم با یکای کیلوگرم سنجیده می‌شود و برخلاف وزن، به مکان جسم وابسته نیست.",
        ],
        "references": [MECH],
    },
}

for _tid, _patch in BATCH.items():
    REVIEW.setdefault(_tid, {}).update(_patch)
