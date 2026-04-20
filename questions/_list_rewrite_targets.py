"""List question ids whose tts_explanation contains 選択肢N (kanji) references.

These are the ids that must appear in ``questions/_rewrites/<chapter>.json``
before running ``_rewrite_explanations.py``.

Usage::

    python questions/_list_rewrite_targets.py ch1-2
    python questions/_list_rewrite_targets.py ch1-2 --format json
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
    p.add_argument("--format", choices=["plain", "json"], default="plain")
    args = p.parse_args()

    path = Path(__file__).with_name(f"{args.chapter}.json")
    data = json.loads(path.read_text("utf-8"))

    targets: list[str] = []
    for q in data["questions"]:
        te = q.get("tts_explanation", "")
        if CHOICE_REF_KANJI_RE.search(te):
            targets.append(q["id"])

    if args.format == "json":
        print(json.dumps(targets, ensure_ascii=False, indent=2))
    else:
        print(f"chapter={args.chapter} targets={len(targets)}/{len(data['questions'])}")
        for t in targets:
            print(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
