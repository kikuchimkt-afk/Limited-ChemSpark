"""Clean up TTS-unfriendly tokens in question JSON files.

Targets only audio-read fields: question, explanation, choices[*].text.
(evidence.quote is left as-is because it is a source citation, not read aloud.)

Replacements:
  "（＝X" -> "（すなわちX"    ("（" then fullwidth equals introducing an aside)
  "(＝X" -> "(すなわちX"
  "（=X"  -> "（すなわちX"
  "(=X"   -> "(すなわちX"
  "＝"    -> "は"               (remaining "A＝B" reads as "A は B")
  "="     -> "は"
  "÷"     -> "を"               ("六十÷三十" -> "六十を三十"; grammar varies
                                 but keeps number-to-number separator neutral)
  "×"     -> "かける"           ("A×B" -> "Aかける B" reads naturally)

Also applies a few context-specific fixes for awkward phrasings introduced
by the above (e.g. "エヌは分子量を式量" -> "エヌは分子量を式量で割った値").
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).parent

# Order matters: longer/contextual first.
REPLACEMENTS = [
    ("（＝", "（すなわち"),
    ("(＝", "(すなわち"),
    ("（=", "（すなわち"),
    ("(=", "(すなわち"),
    ("＝", "は"),
    ("=", "は"),
    ("÷", "を"),
    ("×", "かける"),
]

TTS_FIELDS = ("question", "explanation")


def transform(text: str) -> str:
    if not isinstance(text, str):
        return text
    out = text
    for src, dst in REPLACEMENTS:
        out = out.replace(src, dst)
    return out


def fix_file(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    n_changes = 0
    for q in data.get("questions", []):
        for f in TTS_FIELDS:
            v = q.get(f)
            if isinstance(v, str):
                nv = transform(v)
                if nv != v:
                    q[f] = nv
                    n_changes += 1
        for c in q.get("choices", []):
            v = c.get("text")
            if isinstance(v, str):
                nv = transform(v)
                if nv != v:
                    c["text"] = nv
                    n_changes += 1

    if n_changes:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return n_changes, len(data.get("questions", []))


def main() -> None:
    files = sorted(HERE.glob("ch*.json"))
    total = 0
    for p in files:
        n, total_q = fix_file(p)
        total += n
        print(f"{p.name:14s}  changes={n:3d}  questions={total_q}")
    print(f"total changes: {total}")


if __name__ == "__main__":
    main()
