"""Reset ``audio_voice`` fields for a chapter.

Use this before regenerating audio if you want the voice assignment to
be redrawn from scratch. Normally you do NOT need this — ``_generate.py``
is incremental and preserves existing assignments.

Usage::

    python questions/_reset_voices.py ch1-2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    args = p.parse_args()

    path = Path(__file__).with_name(f"{args.chapter}.json")
    data = json.loads(path.read_text("utf-8"))

    count = 0
    for q in data["questions"]:
        if "audio_voice" in q:
            del q["audio_voice"]
            count += 1

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"cleared audio_voice from {count} questions in {path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
