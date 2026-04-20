"""Restructure ch1-1.json:

1. Shuffle choices so correct-answer positions are evenly distributed (1/2/3/4).
2. Assign stable ``choice_id`` to each choice (so the app can shuffle at runtime
   while still tracking which is correct).
3. Update ``選択肢○`` references inside explanation to reflect the new positions.
4. Split each text field into a TTS form (kanji numerals, Japanese chemical
   names) and a display form (Arabic numerals, unit symbols, chemical formulas).

Input fields are currently TTS-friendly; they are moved into ``tts_*`` fields.
The primary fields are overwritten with the display form.

Usage::

    python _restructure_ch1_1.py
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

HERE = Path(__file__).parent
TARGET = HERE / "ch1-1.json"
SEED = 20260420


# ---------------------------------------------------------------------------
# Number / unit conversion (for display form)
# ---------------------------------------------------------------------------

KANJI_DIGIT = {"零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
               "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
DIGIT_CHARS = "零一二三四五六七八九十百千"
DIGIT_CLASS = f"[{DIGIT_CHARS}]"


def _parse_int(s: str) -> int:
    if s == "零":
        return 0
    result, current = 0, 0
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


def _parse_kanji_number(s: str) -> str:
    if "点" in s:
        int_part, dec_part = s.split("点", 1)
        int_val = _parse_int(int_part) if int_part else 0
        dec_str = "".join(str(KANJI_DIGIT[c]) for c in dec_part)
        return f"{int_val}.{dec_str}"
    return str(_parse_int(s))


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
UNIT_MAP = dict(UNITS)

NUM_RE = re.compile(
    r"(マイナス)?"
    rf"({DIGIT_CLASS}+(?:点[零一二三四五六七八九]+)?)"
    r"(" + "|".join(re.escape(u) for u, _ in UNITS) + r")"
)


def _convert_numbers(text: str) -> str:
    def repl(m: re.Match) -> str:
        sign = "-" if m.group(1) else ""
        num = _parse_kanji_number(m.group(2))
        unit = UNIT_MAP[m.group(3)]
        return f"{sign}{num}{unit}"
    return NUM_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# Chemical formula substitution (for display form only)
# ---------------------------------------------------------------------------
# Longer names first. Only unambiguous compound substance names are
# substituted; element-level words (酸素, 水素, 塩素, ナトリウム, etc.) are
# left in Japanese so that the surrounding prose remains natural.
FORMULAS: list[tuple[str, str]] = [
    ("塩化マグネシウム", "MgCl₂"),
    ("塩化ナトリウム", "NaCl"),
    ("二酸化ケイ素", "SiO₂"),
    ("二酸化炭素", "CO₂"),
]


def _convert_formulas(text: str) -> str:
    for ja, sym in FORMULAS:
        text = text.replace(ja, sym)
    return text


# ---------------------------------------------------------------------------
# 選択肢○ position reference conversion
# ---------------------------------------------------------------------------
KANJI_POS = {"一": 0, "二": 1, "三": 2, "四": 3}
POS_KANJI = {0: "一", 1: "二", 2: "三", 3: "四"}
POS_ARABIC = {0: "1", 1: "2", 2: "3", 3: "4"}

CHOICE_REF_RE = re.compile(r"選択肢([一二三四])")


def _remap_choice_refs(text: str, old_to_new: dict[int, int]) -> str:
    """Rewrite 選択肢X (kanji) references according to old->new index map."""
    def repl(m: re.Match) -> str:
        old_pos = KANJI_POS[m.group(1)]
        new_pos = old_to_new.get(old_pos, old_pos)
        return f"選択肢{POS_KANJI[new_pos]}"
    return CHOICE_REF_RE.sub(repl, text)


def _choice_refs_to_arabic(text: str) -> str:
    """For display form: 選択肢一 -> 選択肢1."""
    def repl(m: re.Match) -> str:
        pos = KANJI_POS[m.group(1)]
        return f"選択肢{POS_ARABIC[pos]}"
    return CHOICE_REF_RE.sub(repl, text)


def to_display(text: str) -> str:
    """TTS-friendly text -> display text."""
    if not isinstance(text, str):
        return text
    text = _convert_numbers(text)
    text = _convert_formulas(text)
    text = _choice_refs_to_arabic(text)
    return text


# ---------------------------------------------------------------------------
# Main restructuring
# ---------------------------------------------------------------------------

def build_target_positions(n: int, rng: random.Random) -> list[int]:
    """Return a list of ``n`` target correct-answer indices (0-3) with even
    distribution. Shuffled for order variety."""
    per_slot = [n // 4] * 4
    for i in range(n % 4):
        per_slot[i] += 1
    positions: list[int] = []
    for slot, cnt in enumerate(per_slot):
        positions.extend([slot] * cnt)
    rng.shuffle(positions)
    return positions


def shuffle_choices(q: dict, target_correct: int,
                    rng: random.Random) -> dict[int, int]:
    """Move the correct choice to ``target_correct`` and randomly permute the
    remaining three choices among the other slots.

    Returns ``old_to_new`` mapping so callers can fix choice-index references
    in explanation text.
    """
    choices = q["choices"]
    correct_idx = next(i for i, c in enumerate(choices) if c.get("is_correct"))
    wrong_indices = [i for i in range(4) if i != correct_idx]
    rng.shuffle(wrong_indices)
    other_slots = [i for i in range(4) if i != target_correct]

    new_choices: list[dict | None] = [None] * 4
    new_choices[target_correct] = choices[correct_idx]
    old_to_new = {correct_idx: target_correct}
    for slot, orig in zip(other_slots, wrong_indices):
        new_choices[slot] = choices[orig]
        old_to_new[orig] = slot

    # Relabel and ensure label uses arabic for display too.
    for i, c in enumerate(new_choices):
        assert c is not None
        c["label"] = str(i + 1)

    q["choices"] = new_choices
    return old_to_new


def assign_choice_ids(q: dict) -> None:
    """Stable identifier independent of position so the app can shuffle at
    runtime and still identify the correct answer."""
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        if "choice_id" not in c:
            c["choice_id"] = f"{qid}_c{i + 1}"


def split_tts_and_display(q: dict) -> None:
    """Move TTS-friendly text into ``tts_*`` fields and overwrite primary
    fields with the display form."""
    if "question" in q and "tts_question" not in q:
        q["tts_question"] = q["question"]
    if "question" in q:
        q["question"] = to_display(q["tts_question"])

    if "explanation" in q and "tts_explanation" not in q:
        q["tts_explanation"] = q["explanation"]
    if "explanation" in q:
        q["explanation"] = to_display(q["tts_explanation"])

    for c in q.get("choices", []):
        if "text" in c and "tts_text" not in c:
            c["tts_text"] = c["text"]
        if "text" in c:
            c["text"] = to_display(c["tts_text"])


def verify_distribution(questions: list[dict]) -> None:
    from collections import Counter
    pos = Counter()
    for q in questions:
        for i, c in enumerate(q["choices"]):
            if c.get("is_correct"):
                pos[i + 1] += 1
    print(f"  correct-position distribution: {dict(sorted(pos.items()))}")


def process(path: Path) -> None:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data["questions"]
    rng = random.Random(SEED)
    targets = build_target_positions(len(questions), rng)

    for q, target in zip(questions, targets):
        old_to_new = shuffle_choices(q, target, rng)
        assign_choice_ids(q)
        # Remap 選択肢X references in the TTS text before splitting.
        if "explanation" in q:
            q["explanation"] = _remap_choice_refs(q["explanation"], old_to_new)
        split_tts_and_display(q)

    # metadata updates
    md = data.setdefault("metadata", {})
    md["display_policy"] = {
        "note": (
            "question / choices[].text / explanation は表示用"
            "（アラビア数字・単位記号・主要化学式）。"
            "tts_question / choices[].tts_text / tts_explanation は音声読み上げ用"
            "（漢数字・単位語・日本語化学名）。"
        ),
        "display_fields": ["question", "choices[].text", "explanation"],
        "tts_fields": [
            "tts_question", "choices[].tts_text", "tts_explanation"
        ],
        "number_unit_mapping": UNIT_MAP,
        "formula_mapping": dict(FORMULAS),
    }
    md["choice_shuffle_policy"] = {
        "note": (
            "choices[].choice_id は問題内で固有の安定識別子。"
            "アプリはユーザ提示時に choices を配列としてシャッフルし、"
            "choice_id と is_correct を参照して採点する。"
        ),
        "runtime_shuffle": True,
        "correct_positions_balanced_in_file": True,
    }

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"processed: {path.name} ({len(questions)} questions)")
    verify_distribution(questions)


if __name__ == "__main__":
    process(TARGET)
