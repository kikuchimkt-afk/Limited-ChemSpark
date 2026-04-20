"""Generate display-form fields for a chapter file.

Current main fields (question / choices[].text / explanation) were written
in TTS-friendly form (kanji numerals, unit words). This script:
  - Moves the current text into tts_* fields.
  - Generates a display form where kanji numerals followed by a unit word
    are converted to Arabic numerals + symbol (e.g. 百度 -> 100℃).

Usage:
    python _make_display.py ch1-1.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent

KANJI_DIGIT = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
               "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
DIGIT_CHARS = "零一二三四五六七八九十百千"
DIGIT_CLASS = f"[{DIGIT_CHARS}]"


def parse_int(s: str) -> int:
    if s == "零":
        return 0
    result = 0
    current = 0
    for ch in s:
        if ch in KANJI_DIGIT:
            current = KANJI_DIGIT[ch]
        elif ch == "十":
            result += (current if current else 1) * 10
            current = 0
        elif ch == "百":
            result += (current if current else 1) * 100
            current = 0
        elif ch == "千":
            result += (current if current else 1) * 1000
            current = 0
    return result + current


def parse_kanji_number(s: str) -> str:
    """Parse a kanji number string and return a decimal string."""
    if "点" in s:
        int_part, dec_part = s.split("点", 1)
        int_val = parse_int(int_part) if int_part else 0
        dec_str = "".join(str(KANJI_DIGIT[c]) for c in dec_part)
        return f"{int_val}.{dec_str}"
    return str(parse_int(s))


# Units to convert. Order matters (longer first) for substring matching.
UNITS: list[tuple[str, str]] = [
    ("立方センチメートルあたり", "cm³あたり"),
    ("立方センチメートル", "cm³"),
    ("キロジュール毎グラム", "kJ/g"),
    ("キロジュール毎モル", "kJ/mol"),
    ("キロジュール", "kJ"),
    ("グラム毎モル", "g/mol"),
    ("クーロン毎モル", "C/mol"),
    ("グラム", "g"),
    ("モル", "mol"),
    ("パーセント", "%"),
    ("リットル", "L"),
    ("アンペア", "A"),
    ("クーロン", "C"),
    ("度", "℃"),
    ("気圧", "atm"),
    ("パスカル", "Pa"),
    ("ケルビン", "K"),
]

# Build a single regex that matches (optional "マイナス") + kanji number
# + one of the units.
NUM_RE = re.compile(
    r"(マイナス)?"
    rf"({DIGIT_CLASS}+(?:点[零一二三四五六七八九]+)?)"
    r"(" + "|".join(re.escape(u) for u, _ in UNITS) + r")"
)

UNIT_MAP = dict(UNITS)


def convert_numbers(text: str) -> str:
    def repl(m: re.Match) -> str:
        sign = "-" if m.group(1) else ""
        num = parse_kanji_number(m.group(2))
        unit = UNIT_MAP[m.group(3)]
        return f"{sign}{num}{unit}"
    return NUM_RE.sub(repl, text)


def to_display(text: str) -> str:
    if not isinstance(text, str):
        return text
    return convert_numbers(text)


def process(path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    changed = 0
    for q in data.get("questions", []):
        # question
        if "question" in q and "tts_question" not in q:
            q["tts_question"] = q["question"]
        if "question" in q:
            new_q = to_display(q["question"])
            if new_q != q["question"]:
                changed += 1
            q["question"] = new_q
        # explanation
        if "explanation" in q and "tts_explanation" not in q:
            q["tts_explanation"] = q["explanation"]
        if "explanation" in q:
            new_e = to_display(q["explanation"])
            if new_e != q["explanation"]:
                changed += 1
            q["explanation"] = new_e
        # choices
        for c in q.get("choices", []):
            if "text" in c and "tts_text" not in c:
                c["tts_text"] = c["text"]
            if "text" in c:
                new_t = to_display(c["text"])
                if new_t != c["text"]:
                    changed += 1
                c["text"] = new_t

    # mark in metadata
    md = data.get("metadata", {})
    if "display_policy" not in md:
        md["display_policy"] = {
            "note": "question / choices[].text / explanation は表示用（数字・単位記号）。tts_question / tts_text / tts_explanation は音声読み上げ用（漢数字・単位語）。",
            "display_fields": ["question", "choices[].text", "explanation"],
            "tts_fields": ["tts_question", "choices[].tts_text", "tts_explanation"],
            "number_unit_mapping": UNIT_MAP,
        }
        data["metadata"] = md

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{path.name}: {changed} text segments converted")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: _make_display.py <file.json> [file2.json ...]")
        return 1
    for name in argv[1:]:
        p = HERE / name
        if not p.exists():
            print(f"not found: {p}")
            continue
        process(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
