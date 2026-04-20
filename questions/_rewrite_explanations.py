"""Apply tts_explanation rewrites from ``_rewrites/<chapter>.json`` to a chapter.

Purpose: remove "選択肢N" positional references from ``tts_explanation`` so
pre-generated explanation audio stays valid even after the app shuffles the
choice order at runtime. Display ``explanation`` is left untouched (it keeps
the Arabic "選択肢N" references; the app rewrites them at render time via
``js/app.js :: remapChoiceRefs``).

Usage::

    python questions/_rewrite_explanations.py ch1-1
    python questions/_rewrite_explanations.py ch1-2 --dry-run

Workflow:
    1. Author a rewrite dict in ``questions/_rewrites/<chapter>.json`` whose
       keys are question ids and whose values are the new ``tts_explanation``
       strings, paraphrased to reference choice CONTENT instead of numbers.
    2. Run this script to patch the chapter JSON.
    3. Run ``audio/_regen_explanations.py <chapter>`` to rebuild MP3s.

Rules for rewrites:
    - Must NOT contain "選択肢一" .. "選択肢九" (asserted by this script).
    - Keep the opening definitional sentences unchanged wherever possible.
    - Replace numeric references with quoted or paraphrased CHOICE CONTENT.
    - Keep the TTS-friendly conventions of the chapter (kanji numerals,
      Japanese element/compound names, no symbols or equations).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).parent
REWRITES_DIR = HERE / "_rewrites"

BANNED = tuple(f"選択肢{d}" for d in "一二三四五六七八九")


def load_rewrites(chapter: str) -> dict[str, str]:
    f = REWRITES_DIR / f"{chapter}.json"
    if not f.exists():
        raise SystemExit(
            f"No rewrite file at {f}. Create one with "
            f"{{question_id: new_tts_explanation}} entries before running."
        )
    return json.loads(f.read_text("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter", help='Chapter id, e.g. "ch1-2"')
    p.add_argument("--dry-run", action="store_true",
                   help="Validate the rewrite file without touching the chapter JSON.")
    args = p.parse_args()

    rewrites = load_rewrites(args.chapter)
    for qid, new_te in rewrites.items():
        for banned in BANNED:
            if banned in new_te:
                raise SystemExit(
                    f"{qid}: rewrite still contains forbidden phrase '{banned}'.\n"
                    f"   Rewrite must reference choice CONTENT, not positions.\n"
                    f"   Offending text: {new_te!r}"
                )

    chapter_file = HERE / f"{args.chapter}.json"
    data = json.loads(chapter_file.read_text("utf-8"))

    ids_in_file = {q["id"] for q in data["questions"]}
    missing = set(rewrites) - ids_in_file
    if missing:
        raise SystemExit(
            f"IDs in rewrite file not found in {chapter_file.name}: {sorted(missing)}"
        )

    updated = 0
    for q in data["questions"]:
        qid = q["id"]
        if qid in rewrites:
            q["tts_explanation"] = rewrites[qid]
            updated += 1

    if args.dry_run:
        print(f"[dry-run] {updated} rewrites would be applied to {chapter_file.name}.")
        return 0

    chapter_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {updated} tts_explanation entries in {chapter_file.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
