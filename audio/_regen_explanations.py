"""Delete and regenerate explanation.mp3 files for questions whose
tts_explanation was rewritten (tracked by ``questions/_rewrites/<chapter>.json``).

Usage::

    python audio/_regen_explanations.py ch1-1

Pre-requisites:
  1. The rewrite set exists at ``questions/_rewrites/<chapter>.json``.
  2. ``python questions/_rewrite_explanations.py <chapter>`` has been run
     so the chapter JSON has the new ``tts_explanation`` values.
  3. Each affected question has an ``audio_voice`` assigned (set by
     ``audio/_generate.py`` on its initial pass).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _generate as gen  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def load_rewrite_ids(chapter: str) -> set[str]:
    f = ROOT / "questions" / "_rewrites" / f"{chapter}.json"
    if not f.exists():
        raise SystemExit(f"No rewrite file at {f}.")
    return set(json.loads(f.read_text("utf-8")).keys())


async def regen(chapter: str) -> None:
    qfile = ROOT / "questions" / f"{chapter}.json"
    with qfile.open(encoding="utf-8") as f:
        data = json.load(f)
    questions = data["questions"]
    chapter_dir = ROOT / "audio" / chapter

    target_ids = load_rewrite_ids(chapter)
    affected = [q for q in questions if q["id"] in target_ids]

    print(f"chapter={chapter} regenerating explanation.mp3 for {len(affected)} questions")

    voices_needed = sorted({q.get("audio_voice") for q in affected if q.get("audio_voice")})
    for v in voices_needed:
        await gen.gen_common(v)

    count = 0
    for q in affected:
        qid = q["id"]
        voice = q.get("audio_voice")
        if not voice:
            print(f"  [{qid}] skipped (no audio_voice assigned yet)")
            continue
        out = chapter_dir / qid / "explanation.mp3"
        if out.exists():
            out.unlink()
        await gen.synth(q["tts_explanation"], out, voice=voice)
        count += 1
        tag = voice.split("-")[-1]
        print(f"  [{qid}|{tag}] explanation.mp3")

    print(f"done: {count} explanation.mp3 files refreshed under {chapter_dir}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter", nargs="?", default="ch1-1")
    args = p.parse_args()
    asyncio.run(regen(args.chapter))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
