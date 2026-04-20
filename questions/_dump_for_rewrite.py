"""Dump context needed to draft tts_explanation rewrites.

Writes a human-readable report to stdout (UTF-8) listing every question
whose current ``tts_explanation`` contains 選択肢N (kanji) references,
together with each choice's ``tts_text`` and the existing explanation.

The output is intended to be read by an LLM (or human) who will then
author ``questions/_rewrites/<chapter>.json``.

Usage::

    python questions/_dump_for_rewrite.py ch1-2 > _tmp/ch1-2_rewrite_input.txt

Output format per question::

    ================================================================================
    ID : ch1_2_q001
    Q  : <tts_question, up to 400 chars>
      ★c1: <choice_id> :: <tts_text>
       c2: <choice_id> :: <tts_text>
       c3: <choice_id> :: <tts_text>
       c4: <choice_id> :: <tts_text>
    EXPL (current tts_explanation): <...>

Drafting rules (repeated for the reader):
  - New tts_explanation MUST NOT contain 選択肢一..選択肢九.
  - Keep the original opening sentences where possible.
  - Replace numeric references with quoted CHOICE CONTENT, e.g.
    '選択肢四は化合物' -> '『二種類以上の元素からなる純物質』は化合物の定義'.
  - Keep TTS conventions: kanji numerals, Japanese unit words, Japanese
    compound names, no symbols/equations.
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CHOICE_REF_KANJI_RE = re.compile(r"選択肢[一二三四五六七八九]")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    args = p.parse_args()

    path = Path(__file__).with_name(f"{args.chapter}.json")
    data = json.loads(path.read_text("utf-8"))

    count = 0
    for q in data["questions"]:
        te = q.get("tts_explanation", "")
        if not CHOICE_REF_KANJI_RE.search(te):
            continue
        count += 1
        print("=" * 80)
        print(f"ID : {q['id']}")
        print(f"Q  : {q.get('tts_question', '')[:400]}")
        for i, c in enumerate(q["choices"]):
            mark = "★" if c.get("is_correct") else " "
            cid = c.get("choice_id", "")
            tt = c.get("tts_text", "")
            print(f"  {mark}c{i+1}: {cid} :: {tt}")
        print(f"EXPL (current tts_explanation): {te}")
    print("=" * 80)
    print(f"TOTAL questions needing rewrite: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
