"""Validate question JSON files in this folder.

Checks:
  - JSON syntax
  - Required top-level keys: metadata, questions
  - Each question has: id, chapter, category, question, choices, explanation
  - Each question has exactly 4 choices
  - Exactly one choice has is_correct == true
  - Labels are "1","2","3","4"
  - Unique IDs across the file
  - question_type in {"correct","incorrect"} when present and matches
    the number of is_correct choices (both models still expect exactly 1
    correct choice, but we log for review)
  - TTS-unfriendly tokens (chemical formulas, math equations, °C, %, etc.)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

REQUIRED_Q_KEYS = ["id", "chapter", "category", "question", "choices", "explanation"]

# Tokens that are not voice-reading friendly. These are conservative regexes.
TTS_PATTERNS = [
    (re.compile(r"℃"), "degree symbol ℃ (use '度')"),
    (re.compile(r"[%％]"), "percent sign (use 'パーセント')"),
    (re.compile(r"(?<![A-Za-zぁ-んァ-ヶー一-龥])(?:H2O|CO2|NaCl|O2|O3|N2|H2|NH3|CaCO3|CH4|C2H6O)"), "chemical formula"),
    # crude: lone uppercase element symbol followed by digit like S8, Sx, H2
    (re.compile(r"\b[A-Z][a-z]?\d+\b"), "element+subscript like S8"),
    (re.compile(r"[×÷≠≦≧≒±√∞πΣ∫]"), "math symbol"),
    (re.compile(r"[=＝]"), "equals sign"),
]

# Fields in which TTS content will be read aloud
TTS_FIELDS = ["question", "explanation"]


def check_tts(text: str) -> list[str]:
    issues: list[str] = []
    for pat, label in TTS_PATTERNS:
        m = pat.search(text)
        if m:
            issues.append(f"{label}: '{m.group(0)}'")
    return issues


def validate_file(path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return 1, [f"[SYNTAX] {path.name}: {e}"]
    except Exception as e:
        return 1, [f"[READ] {path.name}: {e}"]

    if "metadata" not in data:
        errors.append(f"[META] {path.name}: missing 'metadata'")
    if "questions" not in data or not isinstance(data["questions"], list):
        errors.append(f"[META] {path.name}: missing 'questions' list")
        return len(errors), errors

    qs = data["questions"]
    ids = [q.get("id") for q in qs]
    dup = [i for i, c in Counter(ids).items() if c > 1]
    if dup:
        errors.append(f"[DUP] {path.name}: duplicate ids: {dup}")

    meta_total = data.get("metadata", {}).get("total_questions")
    if meta_total is not None and meta_total != len(qs):
        errors.append(
            f"[META] {path.name}: metadata.total_questions={meta_total} but found {len(qs)} questions"
        )

    for idx, q in enumerate(qs):
        qid = q.get("id", f"<index {idx}>")
        for k in REQUIRED_Q_KEYS:
            if k not in q:
                errors.append(f"[KEY] {path.name} {qid}: missing key '{k}'")
        choices = q.get("choices", [])
        if len(choices) != 4:
            errors.append(f"[CHC] {path.name} {qid}: expected 4 choices, got {len(choices)}")
        correct_count = sum(1 for c in choices if c.get("is_correct"))
        if correct_count != 1:
            errors.append(f"[CHC] {path.name} {qid}: expected 1 correct, got {correct_count}")
        labels = [c.get("label") for c in choices]
        if labels != ["1", "2", "3", "4"]:
            errors.append(f"[LBL] {path.name} {qid}: labels={labels}")
        qtype = q.get("question_type", "correct")
        for ci, c in enumerate(choices):
            # Trap fields should appear on the "distractor/ひっかけ" choice(s).
            # - When question_type == "correct" (正しいものを選べ):
            #     the 3 is_correct==false choices are distractors → need trap_*.
            # - When question_type == "incorrect" (誤りを含むものを選べ):
            #     the 1 is_correct==true choice is itself the wrong statement,
            #     so trap_* is required only on that choice.
            needs_trap = (
                (qtype == "correct" and not c.get("is_correct"))
                or (qtype == "incorrect" and c.get("is_correct"))
            )
            if needs_trap:
                for rk in ("trap_type", "trap_detail"):
                    if rk not in c:
                        errors.append(
                            f"[TRAP] {path.name} {qid} choice {ci+1}: missing '{rk}'"
                        )
            text = c.get("text", "")
            for issue in check_tts(text):
                errors.append(f"[TTS] {path.name} {qid} choice {ci+1}: {issue}")
        for fld in TTS_FIELDS:
            val = q.get(fld, "")
            if isinstance(val, str):
                for issue in check_tts(val):
                    errors.append(f"[TTS] {path.name} {qid} field {fld}: {issue}")

    return len(errors), errors


def main(argv: list[str]) -> int:
    files = sorted(HERE.glob("ch*.json"))
    if not files:
        print("no ch*.json files found")
        return 1

    total_errs = 0
    total_qs = 0
    per_file_summary: list[tuple[str, int, int]] = []
    all_errors: list[str] = []
    for p in files:
        with p.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                nq = len(data.get("questions", []))
            except Exception:
                nq = 0
        n_err, errs = validate_file(p)
        total_errs += n_err
        total_qs += nq
        per_file_summary.append((p.name, nq, n_err))
        all_errors.extend(errs)

    print("=== per-file summary ===")
    for name, nq, ne in per_file_summary:
        flag = "OK" if ne == 0 else f"ERR({ne})"
        print(f"  {name:14s}  questions={nq:3d}  {flag}")
    print(f"total questions: {total_qs}")
    print(f"total errors:    {total_errs}")

    if all_errors:
        print("\n=== errors (first 200) ===")
        for e in all_errors[:200]:
            print(e)
        if len(all_errors) > 200:
            print(f"... and {len(all_errors)-200} more errors")
    return 0 if total_errs == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
