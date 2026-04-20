"""Apply length-bias mitigation to wrong choices of a chapter.

Reads per-chapter rewrite data from
``questions/_pads/<chapter>.json`` with this schema::

    {
      "ch1_1_q006": {
        "液体に溶けている固体を、ろ紙を用いて分離する操作である。":
          "液体に溶けて均一な溶液になっている固体を、ろ紙の目を用いて液体から直接取り除く操作である。",
        ...
      },
      ...
    }

Each top-level key is a question id; each nested key is the CURRENT
``tts_text`` of a wrong choice (the matching key). The value is the new
``tts_text`` to write. If the replacement contains no kanji numerals, unit
words, compound-formula names, or 選択肢○ references, the display ``text``
is set identically; otherwise, re-run the relevant display conversion
beforehand or edit ``text`` manually.

Usage::

    python questions/_pad_wrongs_chapter.py ch1-2

Why this step exists:
    Authors tend to make the correct choice long and incorrect choices
    short. After restructuring, that length bias makes the correct answer
    visually obvious. This script lets you pad selected WRONG choices so
    the correct one is no longer the longest. Do NOT shorten the correct
    answer (it usually contains the essential criterion).

Identifying targets:
    Run ``python questions/_length_report.py <chapter>`` (if present) or
    manually inspect questions where correct length exceeds max wrong
    length by >= 10 characters.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
PADS_DIR = HERE / "_pads"

KANJI = "零一二三四五六七八九十百千"
# Replacement text is considered "plain" (display == tts) if it has none of
# these patterns. Keep in sync with the conversion rules in
# ``_restructure_chapter.py``.
NEEDS_DISPLAY_CONVERSION = re.compile(
    rf"(?:[{KANJI}]+(?:点[零一二三四五六七八九]+)?"
    r"(?:立方センチメートル|キロジュール|グラム|モル|パーセント|リットル|"
    r"アンペア|クーロン|度|気圧|パスカル|ケルビン))"
    r"|(?:塩化ナトリウム|塩化マグネシウム|二酸化炭素|二酸化ケイ素|"
    r"二酸化硫黄|一酸化炭素|アンモニア|メタン|炭酸カルシウム|水酸化ナトリウム)"
    r"|選択肢[一二三四]"
)


def apply(chapter: str) -> int:
    pads_file = PADS_DIR / f"{chapter}.json"
    if not pads_file.exists():
        raise SystemExit(f"No pads file at {pads_file}.")
    pads: dict[str, dict[str, str]] = json.loads(pads_file.read_text("utf-8"))

    qfile = HERE / f"{chapter}.json"
    data = json.loads(qfile.read_text("utf-8"))

    applied = 0
    unmatched: list[tuple[str, str]] = []
    for qid, mapping in pads.items():
        q = next((x for x in data["questions"] if x["id"] == qid), None)
        if q is None:
            unmatched.extend((qid, k) for k in mapping)
            continue
        for old, new in mapping.items():
            target = next(
                (c for c in q["choices"] if c.get("tts_text") == old),
                None,
            )
            if target is None:
                unmatched.append((qid, old))
                continue
            target["tts_text"] = new
            if NEEDS_DISPLAY_CONVERSION.search(new):
                print(
                    f"  [{qid}] WARNING: replacement contains display-convertible "
                    f"tokens. Run _restructure-style conversion or edit 'text' "
                    f"manually.\n      new: {new}"
                )
            else:
                target["text"] = new
            applied += 1

    if unmatched:
        print("UNMATCHED (review required):")
        for qid, t in unmatched:
            print(f"  - {qid}: {t!r}")

    qfile.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"applied {applied} replacements / total {sum(len(v) for v in pads.values())}")
    return 0 if not unmatched else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter", help='Chapter id, e.g. "ch1-2"')
    args = p.parse_args()
    return apply(args.chapter)


if __name__ == "__main__":
    raise SystemExit(main())
