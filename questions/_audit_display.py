"""Audit a restructured chapter's DISPLAY fields.

Compares ``question`` / ``choices[].text`` to
``to_display(tts_question / tts_text)``. Any field where the current
display value differs from running ``to_display`` on the TTS source is
reported as a display-conversion miss.

NOTE: ``explanation`` is intentionally excluded from this audit. After
the Option A rewrite pattern (see WORKFLOW.md §3.6), ``tts_explanation``
is content-based (no 選択肢N) while the display ``explanation`` keeps
選択肢N (Arabic) for runtime remap. The two are expected to diverge.

Rationale:
  When a human/AI authors a chapter file directly in the post-restructure
  shape without running ``_restructure_chapter.py``, the display fields
  may remain identical to the TTS fields instead of having the
  Arabic-numeral / unit-symbol / chemical-formula conversions applied.
  This script catches that case deterministically using the SAME
  conversion table the restructure pipeline uses.

Usage::

    python questions/_audit_display.py ch1-2
    python questions/_audit_display.py ch1-2 --apply   # rewrite display fields in place

Exit code 0 if all audited display fields are already in canonical
display form, 1 otherwise.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
from _restructure_chapter import to_display  # noqa: E402


def audit(chapter: str, apply: bool) -> int:
    path = Path(__file__).with_name(f"{chapter}.json")
    data = json.loads(path.read_text("utf-8"))

    diffs: list[tuple[str, str, str, str]] = []
    for q in data["questions"]:
        tts = q.get("tts_question")
        if tts is not None:
            expect = to_display(tts)
            actual = q.get("question", "")
            if actual != expect:
                diffs.append((q["id"], "question", actual, expect))
                if apply:
                    q["question"] = expect
        for i, c in enumerate(q.get("choices", []), 1):
            tts = c.get("tts_text")
            if tts is None:
                continue
            expect = to_display(tts)
            actual = c.get("text", "")
            if actual != expect:
                diffs.append((q["id"], f"choices[{i}].text", actual, expect))
                if apply:
                    c["text"] = expect

    print(f"chapter={chapter}  fields-needing-display-conversion={len(diffs)}")
    for qid, field, actual, expect in diffs[:80]:
        print("-" * 78)
        print(f"{qid}  {field}")
        print(f"  actual : {actual}")
        print(f"  expect : {expect}")
    if len(diffs) > 80:
        print(f"... {len(diffs) - 80} more")

    if apply and diffs:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"\nrewrote {len(diffs)} field(s) in {path.name}")

    return 0 if not diffs else 1


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    p.add_argument("--apply", action="store_true",
                   help="write corrected display fields back to the chapter JSON")
    args = p.parse_args()
    return audit(args.chapter, apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
