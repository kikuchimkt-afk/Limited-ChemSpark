"""Report length bias in a chapter's choices.

Usage::

    python questions/_length_report.py ch1-1

Output:
  - Correct-answer position distribution (should be roughly 1:1:1:1).
  - Average lengths of correct vs wrong choices.
  - Percentage of questions where the correct choice is the longest.
  - List of questions where (correct length) - (max wrong length) >= 10.
    These are strong candidates for ``_pad_wrongs_chapter.py``.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def report(chapter: str) -> int:
    p = Path(__file__).with_name(f"{chapter}.json")
    data = json.loads(p.read_text("utf-8"))
    qs = data["questions"]

    pos = Counter()
    longest_is_correct = 0
    correct_len_total = 0
    wrong_len_total = 0
    wrong_count = 0
    flagged: list[tuple[str, int, int, int]] = []

    for q in qs:
        choices = q["choices"]
        for i, c in enumerate(choices):
            if c.get("is_correct"):
                pos[i + 1] += 1
                cl = len(c.get("text", ""))
                correct_len_total += cl
                lens = [len(cc.get("text", "")) for cc in choices]
                if cl == max(lens):
                    longest_is_correct += 1
            else:
                wrong_len_total += len(c.get("text", ""))
                wrong_count += 1
        correct = next(c for c in choices if c["is_correct"])
        wrongs = [c for c in choices if not c["is_correct"]]
        cl = len(correct.get("text", ""))
        max_wl = max(len(c.get("text", "")) for c in wrongs)
        if cl > max_wl and cl - max_wl >= 10:
            flagged.append((q["id"], cl, max_wl, cl - max_wl))

    n = len(qs)
    print(f"chapter={chapter}  questions={n}")
    print(f"Correct-position distribution: {dict(sorted(pos.items()))}")
    print(
        f"Longest-is-correct: {longest_is_correct}/{n} "
        f"({longest_is_correct / n * 100:.0f}%)"
    )
    if n:
        print(f"Avg correct length: {correct_len_total / n:.1f}")
    if wrong_count:
        print(f"Avg wrong length:   {wrong_len_total / wrong_count:.1f}")
    print(f"Length-biased (diff>=10): {len(flagged)} questions")
    for qid, cl, wl, diff in flagged:
        print(f"  {qid}: correct={cl} max_wrong={wl} diff=+{diff}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    args = p.parse_args()
    return report(args.chapter)


if __name__ == "__main__":
    raise SystemExit(main())
