"""Pre-generate MP3 audio for chapter question files using Microsoft Edge TTS.

For each question, the following audio files are produced:

- ``question.mp3``            problem statement (``tts_question``)
- ``<choice_id>.mp3`` (x4)    each choice body (``choices[].tts_text``), keyed
                              by ``choice_id`` so the mapping is stable even
                              when the app shuffles choice order at runtime.
- ``explanation.mp3``         explanation (``tts_explanation``)

Each question is assigned a single voice (male or female) randomly on first
generation and the choice is persisted in the question JSON as
``audio_voice``. Subsequent runs use the recorded voice to keep speaker
identity consistent for that question.

Shared "いち"..."よん" prefix clips are generated per voice under
``audio/common/<voice>/`` so the runtime can concatenate the correct-voice
prefix + choice body while still allowing the app to shuffle choices.
The short prefix (number only, no "選択肢") keeps the pace brisk.

Usage::

    python audio/_generate.py                    # default: ch1-1, q001-q005
    python audio/_generate.py ch1-1 all          # all questions of a chapter
    python audio/_generate.py ch1-1 6-50         # questions 6 through 50

Requires: pip install edge-tts
"""

from __future__ import annotations

import asyncio
import json
import random
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "questions"
AUDIO_DIR = ROOT / "audio"

VOICES = ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"]  # female, male
RATE = "-10%"
VOICE_SEED = 20260420


async def synth(text: str, out_path: Path, *, voice: str,
                rate: str = RATE) -> None:
    """Synthesize ``text`` to an MP3 at ``out_path``."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    comm = edge_tts.Communicate(text, voice=voice, rate=rate)
    await comm.save(str(out_path))


async def gen_common(voice: str) -> int:
    """Generate いち〜よん prefix clips for a specific voice."""
    common_dir = AUDIO_DIR / "common" / voice
    labels = {1: "いち", 2: "に", 3: "さん", 4: "よん"}
    count = 0
    for n, text in labels.items():
        out = common_dir / f"choice_prefix_{n}.mp3"
        if out.exists():
            continue
        print(f"  [common/{voice}] {out.name} <- {text}")
        await synth(text, out, voice=voice)
        count += 1
    return count


async def gen_question(q: dict, chapter_dir: Path, voice: str) -> int:
    """Generate all audio clips for a single question. Returns count."""
    qid = q["id"]
    qdir = chapter_dir / qid
    count = 0

    out = qdir / "question.mp3"
    if not out.exists():
        await synth(q["tts_question"], out, voice=voice)
        count += 1
        print(f"  [{qid}|{voice.split('-')[-1]}] question.mp3")

    for c in q["choices"]:
        out = qdir / f"{c['choice_id']}.mp3"
        if not out.exists():
            await synth(c["tts_text"], out, voice=voice)
            count += 1
            print(f"  [{qid}|{voice.split('-')[-1]}] {out.name}")

    out = qdir / "explanation.mp3"
    if not out.exists():
        await synth(q["tts_explanation"], out, voice=voice)
        count += 1
        print(f"  [{qid}|{voice.split('-')[-1]}] explanation.mp3")

    return count


def parse_range(spec: str, total: int) -> list[int]:
    if spec == "all":
        return list(range(1, total + 1))
    if "-" in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(spec)]


def ensure_voice_assigned(q: dict, rng: random.Random) -> str:
    """Return voice for ``q``. Assigns a random voice and persists it in the
    question dict if not already set."""
    if q.get("audio_voice") in VOICES:
        return q["audio_voice"]
    voice = rng.choice(VOICES)
    q["audio_voice"] = voice
    return voice


async def main_async(chapter: str, spec: str) -> None:
    qfile = QUESTIONS_DIR / f"{chapter}.json"
    with qfile.open(encoding="utf-8") as f:
        data = json.load(f)
    questions = data["questions"]

    indices = parse_range(spec, len(questions))
    chapter_dir = AUDIO_DIR / chapter

    # Deterministic voice assignment, seeded by chapter for reproducibility.
    rng = random.Random(f"{VOICE_SEED}:{chapter}")

    print(f"chapter={chapter} target={indices} rate={RATE}")

    # Ensure each targeted question has a voice assigned (even questions
    # outside the range already have their voice locked in by prior runs).
    # Walk all questions in order so that the random sequence stays stable
    # regardless of which range is being processed.
    for q in questions:
        ensure_voice_assigned(q, rng)

    voices_needed = sorted({questions[i - 1]["audio_voice"] for i in indices})
    for v in voices_needed:
        await gen_common(v)

    total_new = 0
    for i in indices:
        q = questions[i - 1]
        total_new += await gen_question(q, chapter_dir, q["audio_voice"])

    # Persist the updated voice assignments.
    with qfile.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Summary of voice distribution in the targeted range.
    from collections import Counter
    dist = Counter(questions[i - 1]["audio_voice"] for i in indices)
    print("voice distribution in range:", dict(dist))
    print(f"done: {total_new} new clips under {chapter_dir}")


def main(argv: list[str]) -> int:
    chapter = argv[1] if len(argv) > 1 else "ch1-1"
    spec = argv[2] if len(argv) > 2 else "1-5"
    asyncio.run(main_async(chapter, spec))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
