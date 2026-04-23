"""Generalized restructurer for a chapter JSON file.

Parameterized version of ``_restructure_ch1_1.py``. Apply once per chapter
after initial question data has been authored.

Performs the following steps **idempotently** (safe to re-run only right
after initial authoring; running on already-restructured data is a no-op
thanks to the ``tts_*`` field check):

1. Shuffle choices so that the correct-answer position is evenly
   distributed across the four slots (1-4) in the stored JSON. Existing
   choices arrays are permuted in place.
2. Assign each choice a stable ``choice_id`` of the form
   ``<qid>_c<1..4>``. This id is what the browser app uses to track the
   correct answer while it shuffles choices at runtime.
3. Update any "選択肢X" (kanji) references inside the original explanation
   text to reflect the new positions BEFORE the TTS/display split step.
4. Move each TTS-friendly field (question / choices[].text / explanation)
   into ``tts_*`` counterparts and overwrite the primary fields with a
   DISPLAY form (arabic numerals, unit symbols, chemical formulas for
   well-known compounds).

Usage::

    python questions/_restructure_chapter.py ch1-2
    python questions/_restructure_chapter.py ch1-2 --seed 123  # custom RNG seed

IMPORTANT: Run ONCE per chapter right after authoring. Subsequent structural
fixes belong to dedicated scripts (_pad_wrongs, _rewrite_explanations, ...).

Assumptions about the input chapter JSON:
  - ``data['questions'][].choices`` has exactly 4 entries, each with
    ``is_correct`` set; exactly one choice is correct.
  - All text fields (``question``, ``choices[].text``, ``explanation``)
    are written in the TTS-friendly style: kanji numerals, Japanese unit
    words (度/パーセント/グラム/モル/...), Japanese chemical compound
    names (塩化ナトリウム, 二酸化炭素, ...), no element symbols / math /
    equations.
  - Explanation text may use "選択肢一".."選択肢四" (kanji) to refer to
    positions. These are remapped automatically; after splitting, the
    display ``explanation`` uses Arabic digits (選択肢1..4) while
    ``tts_explanation`` keeps kanji forms.

Display conversion rules applied:
  - Kanji numerals (integer, decimal "点", negative "マイナス") followed by
    known unit words (see ``UNITS``) are rewritten as Arabic digit + symbol.
  - Compound names in ``FORMULAS`` are substituted with chemical symbols
    (subscripts use unicode ₂). Element-level words (酸素, 水素, 塩素,
    ナトリウム, ...) are preserved so the surrounding prose stays natural.
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

HERE = Path(__file__).parent


# ---------------------------------------------------------------------------
# Number / unit conversion (for display form)
# ---------------------------------------------------------------------------

KANJI_DIGIT = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4,
               "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
DIGIT_CHARS = "零〇一二三四五六七八九十百千万"
DIGIT_CLASS = f"[{DIGIT_CHARS}]"


def _parse_int(s: str) -> int:
    if s in ("零", "〇"):
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
        elif ch == "万":
            result += (current if current else 1)
            result *= 10000
            current = 0
    return result + current


def _parse_kanji_number(s: str) -> str:
    if "点" in s or "・" in s:
        sep = "点" if "点" in s else "・"
        int_part, dec_part = s.split(sep, 1)
        int_val = _parse_int(int_part) if int_part else 0
        dec_str = "".join(str(KANJI_DIGIT[c]) for c in dec_part)
        return f"{int_val}.{dec_str}"
    return str(_parse_int(s))


# Longer multi-word units first so greedy matching picks them correctly.
UNITS: list[tuple[str, str]] = [
    ("立方センチメートルあたり", "cm³あたり"),
    ("立方センチメートル", "cm³"),
    ("キロジュール毎グラム", "kJ/g"),
    ("キロジュール毎モル", "kJ/mol"),
    ("キロジュール", "kJ"),
    ("グラム毎モル", "g/mol"),
    ("クーロン毎モル", "C/mol"),
    ("グラム", "g"),
    ("ミリリットル", "mL"),
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
    rf"({DIGIT_CLASS}+(?:[点・][零〇一二三四五六七八九]+)?)"
    r"(" + "|".join(re.escape(u) for u, _ in UNITS) + r")"
)


def _convert_numbers(text: str) -> str:
    def repl(m: re.Match) -> str:
        sign = "-" if m.group(1) else ""
        num = _parse_kanji_number(m.group(2))
        unit = UNIT_MAP[m.group(3)]
        return f"{sign}{num}{unit}"
    return NUM_RE.sub(repl, text)


# Convert standalone multi-digit kanji numerals (e.g. "二百七十三") to
# arabic display form. Single-character numerals are intentionally left as-is
# to avoid over-converting common words ("一部", "一般", etc.).
STANDALONE_NUM_RE = re.compile(
    rf"(?<![A-Za-z0-9₀-₉])({DIGIT_CLASS}+(?:[点・][零〇一二三四五六七八九]+)?)(?![A-Za-z0-9₀-₉])"
)


def _convert_standalone_numbers(text: str) -> str:
    def repl(m: re.Match) -> str:
        token = m.group(1)
        raw = token.replace("点", "").replace("・", "")
        if len(raw) <= 1:
            return token
        return _parse_kanji_number(token)
    return STANDALONE_NUM_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# Chemical formula substitution (for display form only)
# ---------------------------------------------------------------------------
# Longer names first. Only unambiguous compound substance names are
# substituted; element-level words are left in Japanese. Extend this list
# as new chapters introduce new compounds.
FORMULAS: list[tuple[str, str]] = [
    # TTS phonetic readings of general/molecular formulas (longer first)
    ("シーエヌエイチにエヌプラスに", "CₙH₂ₙ₊₂"),
    ("シーエヌエイチにエヌマイナスに", "CₙH₂ₙ₋₂"),
    ("シーエヌエイチにエヌ", "CₙH₂ₙ"),
    ("シースリーエイチシックスオースリー", "C₃H₆O₃"),
    ("シーフォーエイチエイトオーフォー", "C₄H₈O₄"),
    ("シーツーエイチフォーオーツー", "C₂H₄O₂"),
    ("シーエイチツーオー", "CH₂O"),
    # Japanese compound names → chemical formulas
    ("炭酸水素ナトリウム", "NaHCO₃"),
    ("炭酸カルシウム", "CaCO₃"),
    ("塩化マグネシウム", "MgCl₂"),
    ("塩化カルシウム", "CaCl₂"),
    ("塩化ナトリウム", "NaCl"),
    ("水酸化ナトリウム", "NaOH"),
    ("水酸化カルシウム", "Ca(OH)₂"),
    ("硫酸ナトリウム", "Na₂SO₄"),
    ("硝酸ナトリウム", "NaNO₃"),
    ("硫酸銅", "CuSO₄"),
    ("二酸化ケイ素", "SiO₂"),
    ("二酸化硫黄", "SO₂"),
    ("二酸化炭素", "CO₂"),
    ("一酸化炭素", "CO"),
    ("メタン", "CH₄"),
    ("アンモニア", "NH₃"),
]


def _convert_formulas(text: str) -> str:
    for ja, sym in FORMULAS:
        text = text.replace(ja, sym)
    return text


# ---------------------------------------------------------------------------
# Kanji single-digit + counter conversion (for display form)
# ---------------------------------------------------------------------------
# Converts patterns like 一種類→1種類, 四つ→4つ, 第一に→第1に.
# Uses negative lookbehind to avoid corrupting compound words
# (単一, 均一, 一定, 一般, 一方, 一見, 一切, 一連, 一致, 同一).

_KANJI_COUNTER_RULES: list[tuple[re.Pattern, str]] = [
    # N種類
    (re.compile(r"(?<![単均唯同])一種類"), "1種類"),
    (re.compile(r"二種類"), "2種類"),
    (re.compile(r"三種類"), "3種類"),
    (re.compile(r"四種類"), "4種類"),
    (re.compile(r"五種類"), "5種類"),
    # Nつ
    (re.compile(r"(?<![単均唯定不同])一つ"), "1つ"),
    (re.compile(r"二つ"), "2つ"),
    (re.compile(r"三つ"), "3つ"),
    (re.compile(r"四つ"), "4つ"),
    (re.compile(r"五つ"), "5つ"),
    (re.compile(r"六つ"), "6つ"),
    (re.compile(r"七つ"), "7つ"),
    (re.compile(r"八つ"), "8つ"),
    (re.compile(r"九つ"), "9つ"),
    # 第N (ordinals before に/の/章/節)
    (re.compile(r"第一(?=[にの章節])"), "第1"),
    (re.compile(r"第二(?=[にの章節])"), "第2"),
    (re.compile(r"第三(?=[にの章節])"), "第3"),
    (re.compile(r"第四(?=[にの章節])"), "第4"),
]


def _convert_kanji_counters(text: str) -> str:
    for pat, repl in _KANJI_COUNTER_RULES:
        text = pat.sub(repl, text)
    return text


# ---------------------------------------------------------------------------
# Katakana alphabet → Latin letter conversion (for display form)
# ---------------------------------------------------------------------------
# TTS fields spell out element symbols as katakana (エス, シー, etc.);
# display fields should use actual Latin letters (S, C, etc.).
_KATAKANA_ALPHA_RULES: list[tuple[str, str]] = [
    ("エス・シー・オー・ピー", "S・C・O・P"),
    ("ケー村", "K村"),
]


def _convert_katakana_alpha(text: str) -> str:
    for kata, latin in _KATAKANA_ALPHA_RULES:
        text = text.replace(kata, latin)
    return text


# ---------------------------------------------------------------------------
# 選択肢○ position reference conversion
# ---------------------------------------------------------------------------
KANJI_POS = {"一": 0, "二": 1, "三": 2, "四": 3}
POS_KANJI = {0: "一", 1: "二", 2: "三", 3: "四"}
POS_ARABIC = {0: "1", 1: "2", 2: "3", 3: "4"}

CHOICE_REF_RE = re.compile(r"選択肢([一二三四])")


def _remap_choice_refs(text: str, old_to_new: dict[int, int]) -> str:
    def repl(m: re.Match) -> str:
        old_pos = KANJI_POS[m.group(1)]
        new_pos = old_to_new.get(old_pos, old_pos)
        return f"選択肢{POS_KANJI[new_pos]}"
    return CHOICE_REF_RE.sub(repl, text)


def _choice_refs_to_arabic(text: str) -> str:
    def repl(m: re.Match) -> str:
        pos = KANJI_POS[m.group(1)]
        return f"選択肢{POS_ARABIC[pos]}"
    return CHOICE_REF_RE.sub(repl, text)


def to_display(text: str) -> str:
    if not isinstance(text, str):
        return text
    text = _convert_numbers(text)
    text = _convert_standalone_numbers(text)
    text = _convert_formulas(text)
    text = _convert_kanji_counters(text)
    text = _convert_katakana_alpha(text)
    text = _choice_refs_to_arabic(text)
    return text


# ---------------------------------------------------------------------------
# Main restructuring
# ---------------------------------------------------------------------------

def build_target_positions(n: int, rng: random.Random) -> list[int]:
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

    for i, c in enumerate(new_choices):
        assert c is not None
        c["label"] = str(i + 1)

    q["choices"] = new_choices
    return old_to_new


def assign_choice_ids(q: dict) -> None:
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        if "choice_id" not in c:
            c["choice_id"] = f"{qid}_c{i + 1}"


def split_tts_and_display(q: dict) -> None:
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


def is_already_restructured(data: dict) -> bool:
    """Heuristic: any question already has tts_* fields or choice_id."""
    for q in data.get("questions", []):
        if "tts_question" in q or "tts_explanation" in q:
            return True
        for c in q.get("choices", []):
            if "choice_id" in c or "tts_text" in c:
                return True
    return False


def process(path: Path, seed: int) -> None:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if is_already_restructured(data):
        raise SystemExit(
            f"{path.name} already appears restructured (tts_* fields or "
            f"choice_id detected). Refusing to run to avoid double-processing.\n"
            f"\n"
            f"If the file was authored directly in post-restructure shape "
            f"(i.e. tts_* and choice_id fields are already present), DO NOT "
            f"re-run this script. Instead run the standard quality gate:\n"
            f"\n"
            f"    python questions/_check_all.py {path.stem}\n"
            f"\n"
            f"which will flag any remaining display-conversion misses as "
            f"[DISP] errors. To auto-fix them, run:\n"
            f"\n"
            f"    python questions/_audit_display.py {path.stem} --apply\n"
            f"\n"
            f"Only restore a pre-restructure backup and re-run this script "
            f"when you need to re-shuffle choices from scratch."
        )

    questions = data["questions"]
    rng = random.Random(seed)
    targets = build_target_positions(len(questions), rng)

    for q, target in zip(questions, targets):
        old_to_new = shuffle_choices(q, target, rng)
        assign_choice_ids(q)
        if "explanation" in q:
            q["explanation"] = _remap_choice_refs(q["explanation"], old_to_new)
        split_tts_and_display(q)

    md = data.setdefault("metadata", {})
    md["display_policy"] = {
        "note": (
            "question / choices[].text / explanation は表示用"
            "（アラビア数字・単位記号・主要化学式）。"
            "tts_question / choices[].tts_text / tts_explanation は音声読み上げ用"
            "（漢数字・単位語・日本語化学名）。"
        ),
        "display_fields": ["question", "choices[].text", "explanation"],
        "tts_fields": ["tts_question", "choices[].tts_text", "tts_explanation"],
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

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"processed: {path.name} ({len(questions)} questions)")
    verify_distribution(questions)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter", help='Chapter id, e.g. "ch1-2"')
    p.add_argument("--seed", type=int, default=20260420,
                   help="RNG seed for deterministic shuffling (default: 20260420)")
    args = p.parse_args()

    target = HERE / f"{args.chapter}.json"
    if not target.exists():
        raise SystemExit(f"Chapter file not found: {target}")
    process(target, args.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
