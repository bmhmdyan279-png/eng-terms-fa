#!/usr/bin/env python3
"""Export the dictionary in portable formats.

    output/anki.apkg   Anki flashcard deck (front: فارسی / back: معادل‌ها + تعریف)
    output/terms.csv   spreadsheet-friendly CSV (UTF-8 BOM for Excel)
    output/terms.pdf   printable edition (Vazirmatn, Persian shaping included)

Usage:
    python scripts/generate_exports.py [--out DIR]
"""

import argparse
import csv
import shutil
from datetime import datetime, timezone
from pathlib import Path

import arabic_reshaper
import genanki
from bidi.algorithm import get_display
from fpdf import FPDF

from build_pages import ROOT, SITE_URL, load_all_terms, load_meta

DEFAULT_OUT = ROOT / "output"
FONT_DIR = ROOT / "tools" / "fonts"

ANKI_MODEL_ID = 1876250101
ANKI_DECK_ID = 1876250102
ANKI_DECK_NAME = "فرهنگ واژگان تخصصی مهندسی"

CSV_FIELDS = [
    "term_fa", "term_en", "term_fr", "term_de", "term_ar",
    "pos", "domain", "definition_fa",
    "synonyms", "antonyms", "search_aliases", "usage_examples",
    "root_fa", "root_ar", "etymology_fa", "origin_lang", "plural_fa", "abbrev_en",
    "status", "review_level", "reviewed_by", "reviewed_at",
    "references", "reference_notes", "related_terms", "slug", "url",
]


#: The subsetted Vazirmatn carries no accented Latin glyphs. Etymology notes now
#: quote foreign headwords («élasticité», «Läufer», «poutre», «caementum»), and
#: fpdf2 only *warns* about missing glyphs — it drops them silently. The print
#: edition therefore transliterates Latin accents; the web pages and the
#: JSON/RDF/CSV exports keep the exact spelling.
_LATIN_FOLD = str.maketrans({
    "à": "a", "á": "a", "â": "a", "ã": "a", "ä": "a", "å": "a", "ā": "a", "æ": "ae",
    "ç": "c", "ć": "c", "č": "c", "è": "e", "é": "e", "ê": "e", "ë": "e", "ē": "e",
    "ğ": "g", "ì": "i", "í": "i", "î": "i", "ï": "i", "ñ": "n", "ò": "o", "ó": "o",
    "ô": "o", "õ": "o", "ö": "o", "ø": "o", "ù": "u", "ú": "u", "û": "u", "ü": "u",
    "ý": "y", "ÿ": "y", "ß": "ss", "š": "s", "ž": "z", "×": "x", "‑": "-",
})


def fold_latin_accents(text: str) -> str:
    """ASCII-fold Latin accents for fonts that lack the glyphs (print only)."""
    return str(text or "").translate(_LATIN_FOLD)


def fa_display(text: str, fold_accents: bool = False) -> str:
    """Reshape Persian for PDF rendering (visual order)."""
    if fold_accents:
        text = fold_latin_accents(text)
    return get_display(arabic_reshaper.reshape(text or ""))


def _terms():
    return [record for _, record in load_all_terms()]


def write_csv(terms, out_dir: Path) -> Path:
    path = out_dir / "terms.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for t in terms:
            writer.writerow(
                {
                    "term_fa": t.get("term_fa", ""),
                    "term_en": t.get("term_en", ""),
                    "term_fr": t.get("term_fr") or "",
                    "term_de": t.get("term_de") or "",
                    "term_ar": t.get("term_ar") or "",
                    "pos": t.get("pos", ""),
                    "domain": "|".join(t.get("domain") or []),
                    "definition_fa": t.get("definition_fa", ""),
                    "synonyms": "|".join(t.get("synonyms") or []),
                    "antonyms": "|".join(t.get("antonyms") or []),
                    "search_aliases": "|".join(t.get("search_aliases") or []),
                    "usage_examples": "|".join(t.get("usage_examples") or []),
                    "root_fa": t.get("root_fa") or "",
                    "root_ar": t.get("root_ar") or "",
                    "etymology_fa": t.get("etymology_fa") or "",
                    "origin_lang": t.get("origin_lang") or "",
                    "plural_fa": t.get("plural_fa") or "",
                    "abbrev_en": t.get("abbrev_en") or "",
                    "status": t.get("status", "draft"),
                    "review_level": t.get("review_level") or "",
                    "reviewed_by": t.get("reviewed_by") or "",
                    "reviewed_at": t.get("reviewed_at") or "",
                    "reference_notes": "|".join(
                        str(ref.get("note") or "") for ref in (t.get("references") or [])
                        if isinstance(ref, dict)
                    ),
                    "slug": t.get("slug", ""),
                    "references": "|".join(
                        r.get("code", "") if isinstance(r, dict) else str(r)
                        for r in (t.get("references") or [])
                    ),
                    "related_terms": "|".join(t.get("related_terms") or []),
                    "url": f"{SITE_URL}terms/{t.get('slug')}/",
                }
            )
    return path


def write_anki(terms, out_dir: Path) -> Path:
    model = genanki.Model(
        ANKI_MODEL_ID,
        "Engineering Term FA",
        fields=[
            {"name": "fa"}, {"name": "en"}, {"name": "definition"},
            {"name": "fr"}, {"name": "de"}, {"name": "ar"},
            {"name": "root"}, {"name": "synonyms"}, {"name": "example"},
        ],
        templates=[
            {
                "name": "Engineering term",
                "qfmt": '<div dir="rtl" style="font-size:28px;text-align:center">{{fa}}</div>',
                "afmt": (
                    '<div dir="rtl" style="font-size:28px;text-align:center">{{fa}}</div>'
                    '<hr id="answer">'
                    '<div style="text-align:center;font-size:20px">{{en}}</div>'
                    '<div dir="rtl" style="margin-top:8px">{{definition}}</div>'
                    '<div dir="rtl" style="margin-top:8px;color:#444">ریشه: {{root}}</div>'
                    '<div dir="rtl" style="margin-top:4px;color:#444">مترادف: {{synonyms}}</div>'
                    '<div dir="rtl" style="margin-top:4px;color:#666;font-style:italic">{{example}}</div>'
                    '<div style="margin-top:8px;color:#666">FR: {{fr}} | DE: {{de}} | AR: {{ar}}</div>'
                ),
            }
        ],
    )
    deck = genanki.Deck(ANKI_DECK_ID, ANKI_DECK_NAME)
    for t in terms:
        deck.add_note(
            genanki.Note(
                model=model,
                fields=[
                    t.get("term_fa", ""),
                    t.get("term_en", ""),
                    t.get("definition_fa", ""),
                    t.get("term_fr") or "",
                    t.get("term_de") or "",
                    t.get("term_ar") or "",
                    t.get("root_fa") or "",
                    "، ".join(t.get("synonyms") or []),
                    (t.get("usage_examples") or [""])[0],
                ],
                tags=["engineering", t.get("status", "draft"),
                      t.get("review_level") or "draft"],
            )
        )
    path = out_dir / "anki.apkg"
    genanki.Package(deck).write_to_file(str(path))
    return path


def write_pdf(terms, out_dir: Path) -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_font("Vazir", "", str(FONT_DIR / "Vazirmatn-Regular-subset.ttf"))
    pdf.add_font("Vazir", "B", str(FONT_DIR / "Vazirmatn-Bold-subset.ttf"))
    pdf.add_page()

    # title page
    pdf.ln(30)
    pdf.set_font("Vazir", "B", 24)
    pdf.cell(0, 12, fa_display("فرهنگ واژگان تخصصی مهندسی"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Vazir", "", 13)
    pdf.cell(0, 9, fa_display("معادل دقیق اصطلاحات مهندسی فارسی، انگلیسی و سایر زبان‌ها"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 9, fa_display("عمران • بتن • ساختمان • مکانیک"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)
    pdf.set_font("Vazir", "", 10)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    pdf.cell(0, 7, fa_display(f"نسخهٔ چاپی — {today}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 7, SITE_URL, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 7, fa_display("مجوز محتوا: CC BY-SA 4.0"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)
    pdf.set_font("Vazir", "", 9)
    pdf.multi_cell(
        0, 6,
        fa_display("توجه: این فرهنگ در حال بازبینی تخصصی است؛ وضعیت هر مدخل در نسخهٔ وب نمایش داده می‌شود."),
        align="C",
    )

    # terms
    pdf.add_page()
    domain_titles = {d["id"]: d.get("title_fa", d["id"]) for d in load_meta().get("domains", [])}
    pos_fa = {"noun": "اسم", "verb": "فعل", "adjective": "صفت", "phrase": "عبارت"}
    status_fa = {"draft": "پیش‌نویس", "reviewed": "بازبینی‌شده", "published": "منتشرشده"}
    for t in terms:
        if pdf.get_y() > 245:
            pdf.add_page()
        pdf.set_font("Vazir", "B", 13)
        pdf.cell(0, 8, fa_display(t.get("term_fa", "")), new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.set_font("Vazir", "", 10)
        en = str(t.get("term_en") or "")
        if en:
            pdf.cell(0, 6, en, new_x="LMARGIN", new_y="NEXT", align="R")

        # other languages (only verified/non-null values make it this far).
        # FR/DE use the core Helvetica font: the subsetted Vazirmatn lacks
        # accented Latin glyphs (é, ô, ü, ß ...). Arabic needs Vazirmatn.
        others = []
        for label, field in (("FR", "term_fr"), ("DE", "term_de")):
            value = str(t.get(field) or "").strip()
            if value:
                others.append(f"{label}: {value}")
        if others:
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 6, "  |  ".join(others), new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.set_font("Vazir", "", 10)
        ar_value = str(t.get("term_ar") or "").strip()
        if ar_value:
            pdf.cell(0, 6, "AR: " + fa_display(ar_value), new_x="LMARGIN", new_y="NEXT", align="R")

        # domain • pos • status
        domains = "، ".join(domain_titles.get(d, d) for d in t.get("domain") or []) or "عمومی"
        meta_line = f"{domains} • {pos_fa.get(t.get('pos'), t.get('pos') or '')} • {status_fa.get(t.get('status'), t.get('status') or '')}"
        pdf.set_font("Vazir", "", 8)
        pdf.cell(0, 5, fa_display(meta_line), new_x="LMARGIN", new_y="NEXT", align="R")

        pdf.set_font("Vazir", "", 10)
        pdf.multi_cell(0, 6, fa_display(t.get("definition_fa", "")), new_x="LMARGIN", new_y="NEXT", align="R")

        # ساخت‌واژه و ریشه‌شناسی — ارزش اصلی نسخهٔ چاپی برای واژه‌شناسان
        morphology = []
        if t.get("root_fa"):
            piece = "ریشه: " + str(t["root_fa"])
            if t.get("root_ar"):
                piece += " | ریشهٔ عربی: " + str(t["root_ar"])
            if t.get("origin_lang"):
                piece += " | زبان مبدأ: " + str(t["origin_lang"])
            morphology.append(piece)
        if t.get("synonyms"):
            morphology.append("مترادف: " + "، ".join(str(v) for v in t["synonyms"]))
        if t.get("antonyms"):
            morphology.append("متضاد: " + "، ".join(str(v) for v in t["antonyms"]))
        if t.get("etymology_fa"):
            morphology.append("ریشه‌شناسی: " + str(t["etymology_fa"]))
        if morphology:
            pdf.set_font("Vazir", "", 8)
            pdf.multi_cell(0, 5, fa_display(" • ".join(morphology), fold_accents=True),
                           new_x="LMARGIN", new_y="NEXT", align="R")
            pdf.set_font("Vazir", "", 10)

        # references
        refs = t.get("references") or []
        if refs:
            pdf.set_font("Vazir", "", 8)
            ref_texts = []
            for ref in refs:
                if isinstance(ref, dict):
                    edition = f"، ویرایش {ref['edition']}" if ref.get("edition") else ""
                    ref_texts.append(f"{ref.get('code', '')}{edition}")
                else:
                    ref_texts.append(str(ref))
            pdf.multi_cell(0, 5, fa_display("منابع: " + "؛ ".join(ref_texts)), new_x="LMARGIN", new_y="NEXT", align="R")
        pdf.ln(3)

    path = out_dir / "terms.pdf"
    pdf.output(str(path))
    return path


def generate_exports(out_dir: Path = DEFAULT_OUT) -> dict:
    terms = _terms()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = write_csv(terms, out_dir)
    anki_path = write_anki(terms, out_dir)
    pdf_path = write_pdf(terms, out_dir)
    return {
        "terms": len(terms),
        "csv": csv_path,
        "anki": anki_path,
        "pdf": pdf_path,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    result = generate_exports(Path(args.out))
    print(f"✅ exports written for {result['terms']} terms:")
    for key in ("csv", "anki", "pdf"):
        print(f"   - {result[key]}")


if __name__ == "__main__":
    main()
