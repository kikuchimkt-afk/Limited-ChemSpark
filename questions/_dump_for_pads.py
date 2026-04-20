"""Dump context needed to draft wrong-choice padding.

For each question whose correct choice is >= 10 characters longer than
any wrong choice, prints the full ``tts_text`` of every choice, labelling
the correct one and the wrong ones. The intent is to give the drafter
enough context to craft longer replacements for the wrong choices in
``questions/_pads/<chapter>.json``.

Usage::

    python questions/_dump_for_pads.py ch1-2 > _tmp/ch1-2_pad_input.txt

Drafting rules:
  - DO NOT shorten the correct choice (it usually carries the essential
    criterion).
  - Lengthen selected WRONG choices so that ``max(len(wrong))`` approaches
    ``len(correct)`` or exceeds it.
  - Prefer "plain" replacements (no kanji numerals, no unit words,
    no compound formula names, no 選択肢N). Then ``text`` auto-syncs with
    ``tts_text``; otherwise the display value must be edited separately.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

THRESHOLD = 10


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    p.add_argument("--threshold", type=int, default=THRESHOLD,
                   help="min (correct - max_wrong) length diff to flag")
    args = p.parse_args()

    path = Path(__file__).with_name(f"{args.chapter}.json")
    data = json.loads(path.read_text("utf-8"))

    flagged = 0
    for q in data["questions"]:
        choices = q["choices"]
        correct = next(c for c in choices if c["is_correct"])
        wrongs = [c for c in choices if not c["is_correct"]]
        c_len = len(correct.get("text", ""))
        max_wl = max(len(c.get("text", "")) for c in wrongs)
        if c_len - max_wl < args.threshold:
            continue
        flagged += 1
        print("=" * 80)
        print(f"ID : {q['id']}")
        print(f"Q  : {q.get('tts_question', '')[:400]}")
        print(f"correct_len={c_len}  max_wrong_len={max_wl}  diff=+{c_len - max_wl}")
        for i, c in enumerate(choices):
            mark = "★CORRECT" if c.get("is_correct") else f"WRONG  "
            tt = c.get("tts_text", "")
            print(f"  c{i+1} ({mark}, len={len(c.get('text', ''))}): {tt}")
    print("=" * 80)
    print(f"TOTAL length-biased questions (diff>={args.threshold}): {flagged}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
