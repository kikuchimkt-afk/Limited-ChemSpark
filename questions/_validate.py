"""Validate chapter JSON files.

Checks:
  - JSON syntax
  - Required top-level keys: metadata, questions
  - Each question has: id, chapter, category, question, choices, explanation
  - Each question has exactly 4 choices
  - Exactly one choice has is_correct == true
  - Labels are "1","2","3","4"
  - Unique question ids per file
  - question_type in {"correct","incorrect"} when present and matches the
    distractor-annotation pattern (trap_type / trap_detail on the right
    choices).
  - For restructured files (those containing ``tts_*`` fields):
    - Each question has tts_question and tts_explanation; each choice has
      tts_text and choice_id.
    - choice_id format: "<qid>_c1".."<qid>_c4".
    - TTS fields must NOT contain display-only tokens (℃, %, chemical
      formulas, math symbols, equals signs).
    - tts_explanation must NOT contain "選択肢N" (kanji) references
      because choice positions are randomized at runtime; use
      content-based phrasing instead.
    - Display fields (``question`` and each ``choices[].text``) must
      equal ``to_display(tts_*)``; any divergence is a display
      conversion miss (typically caused by skipping
      ``_restructure_chapter.py`` during authoring). Run
      ``_audit_display.py --apply`` to fix automatically.

Usage::

    python questions/_validate.py              # all ch*.json in this folder
    python questions/_validate.py ch1-1        # single chapter
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent

sys.path.insert(0, str(HERE))
from _restructure_chapter import to_display  # noqa: E402

REQUIRED_Q_KEYS = ["id", "chapter", "category", "question", "choices", "explanation"]

# Tokens unsuitable for TTS (Edge TTS). These checks apply to tts_* fields
# only; display fields may legitimately contain ℃, %, H₂O, NaCl, etc.
TTS_BAD_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"℃"), "degree symbol ℃ (use 'ど'/'度')"),
    (re.compile(r"[%％]"), "percent sign (use 'パーセント')"),
    (re.compile(
        r"(?<![A-Za-zぁ-んァ-ヶー一-龥])"
        r"(?:H[₂2]O|CO[₂2]|NaCl|O[₂2]|O[₃3]|N[₂2]|H[₂2]|NH[₃3]|"
        r"CaCO[₃3]|CH[₄4]|MgCl[₂2]|SiO[₂2]|C[₂2]H[₆6]O)"
    ), "chemical formula"),
    (re.compile(r"\b[A-Z][a-z]?\d+\b"), "element+subscript like S8"),
    (re.compile(r"[×÷≠≦≧≒±√∞πΣ∫]"), "math symbol"),
    (re.compile(r"[=＝]"), "equals sign"),
    (re.compile(r"[₀-₉]"), "unicode subscript digit"),
]

CHOICE_REF_KANJI_RE = re.compile(r"選択肢[一二三四五六七八九]")


def check_tts(text: str) -> list[str]:
    issues: list[str] = []
    for pat, label in TTS_BAD_PATTERNS:
        m = pat.search(text)
        if m:
            issues.append(f"{label}: '{m.group(0)}'")
    return issues


def is_restructured(data: dict) -> bool:
    for q in data.get("questions", []):
        if "tts_question" in q or "tts_explanation" in q:
            return True
        for c in q.get("choices", []):
            if "tts_text" in c or "choice_id" in c:
                return True
    return False


def validate_file(path: Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text("utf-8"))
    except json.JSONDecodeError as e:
        return 1, [f"[SYNTAX] {path.name}: {e}"]

    if "metadata" not in data:
        errors.append(f"[META] {path.name}: missing 'metadata'")
    if "questions" not in data or not isinstance(data["questions"], list):
        errors.append(f"[META] {path.name}: missing 'questions' list")
        return len(errors), errors

    qs = data["questions"]
    restructured = is_restructured(data)

    ids = [q.get("id") for q in qs]
    for qid, count in Counter(ids).items():
        if count > 1:
            errors.append(f"[DUP] {path.name}: duplicate id '{qid}' appears {count} times")

    meta_total = data.get("metadata", {}).get("total_questions")
    if meta_total is not None and meta_total != len(qs):
        errors.append(
            f"[META] {path.name}: metadata.total_questions={meta_total} "
            f"but found {len(qs)} questions"
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

            if restructured:
                cid = c.get("choice_id")
                expected = f"{qid}_c{ci+1}"
                if cid != expected:
                    errors.append(
                        f"[ID] {path.name} {qid} choice {ci+1}: "
                        f"choice_id={cid!r} expected {expected!r}"
                    )
                if "tts_text" not in c:
                    errors.append(
                        f"[TTS] {path.name} {qid} choice {ci+1}: missing tts_text"
                    )
                tts_text = c.get("tts_text", "")
                for issue in check_tts(tts_text):
                    errors.append(
                        f"[TTS] {path.name} {qid} choice {ci+1} tts_text: {issue}"
                    )
                expected_disp = to_display(tts_text)
                actual_disp = c.get("text", "")
                if actual_disp != expected_disp:
                    errors.append(
                        f"[DISP] {path.name} {qid} choice {ci+1} text "
                        f"differs from to_display(tts_text). Run "
                        f"'python questions/_audit_display.py {path.stem} --apply' "
                        f"to fix."
                    )

        if restructured:
            for fld in ("tts_question", "tts_explanation"):
                if fld not in q:
                    errors.append(f"[TTS] {path.name} {qid}: missing '{fld}'")
                else:
                    for issue in check_tts(q[fld]):
                        errors.append(
                            f"[TTS] {path.name} {qid} field {fld}: {issue}"
                        )
            if "tts_question" in q:
                expected_q = to_display(q["tts_question"])
                if q.get("question", "") != expected_q:
                    errors.append(
                        f"[DISP] {path.name} {qid} question differs from "
                        f"to_display(tts_question). Run "
                        f"'python questions/_audit_display.py {path.stem} --apply' "
                        f"to fix."
                    )
            te = q.get("tts_explanation", "")
            if CHOICE_REF_KANJI_RE.search(te):
                errors.append(
                    f"[REF] {path.name} {qid}: tts_explanation contains "
                    f"'{CHOICE_REF_KANJI_RE.search(te).group(0)}'. "
                    f"Rewrite to content-based phrasing via _rewrite_explanations.py."
                )
            if q.get("audio_voice") and q["audio_voice"] not in (
                "ja-JP-NanamiNeural", "ja-JP-KeitaNeural"
            ):
                errors.append(
                    f"[VOICE] {path.name} {qid}: unknown audio_voice {q['audio_voice']!r}"
                )

    return len(errors), errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter", nargs="?",
                   help="Single chapter id (e.g. ch1-1). If omitted, validate all.")
    args = p.parse_args()

    if args.chapter:
        files = [HERE / f"{args.chapter}.json"]
    else:
        files = sorted(HERE.glob("ch*.json"))
        files = [f for f in files if ".backup." not in f.name]
    files = [f for f in files if f.exists()]
    if not files:
        print("no chapter files found")
        return 1

    total_errs = 0
    total_qs = 0
    per_file_summary: list[tuple[str, int, int]] = []
    all_errors: list[str] = []
    for path in files:
        try:
            data = json.loads(path.read_text("utf-8"))
            nq = len(data.get("questions", []))
        except Exception:
            nq = 0
        n_err, errs = validate_file(path)
        total_errs += n_err
        total_qs += nq
        per_file_summary.append((path.name, nq, n_err))
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
            print(f"... and {len(all_errors) - 200} more errors")
    return 0 if total_errs == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
