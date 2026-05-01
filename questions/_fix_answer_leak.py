#!/usr/bin/env python3
"""Fix choices that leak the correct answer in their text.

Two patterns fixed:
1. correct-type wrong choices: "Wrong claim. 逆でCorrect." → keep first sentence only
2. incorrect-type correct choices: "Fact. これは正しい記述であり..." → keep first sentence only

Usage: python questions/_fix_answer_leak.py <chapter> [--dry-run]
"""
import json, sys, re, io
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Manual overrides: choice_id → replacement text (for both text and tts_text)
OVERRIDES = {
    # q001 c1: truncated mess
    "ch3_5_q001_c1": "酸化と還元は独立した反応であり、一方だけが単独で進行することがある。",
    # q001 c2: embedded correction in single sentence
    "ch3_5_q001_c2": "物質が水素を受け取る反応が酸化であり、水素を失う反応が還元である。",
    # q003 c4: truncated
    "ch3_5_q003_c4": "酸化剤は自身が酸化される物質であり、相手を還元する役割をもつ。",
    # q019 c1: truncated
    "ch3_5_q019_c1": "この語呂合わせは金が最もイオン化傾向が大きい順番を表しており、酸化されやすい順に並んでいる。",
    # q019 c2: truncated
    "ch3_5_q019_c2": "この語呂合わせは酸化数の大小の順番に関するものである。",
    # q006 c2: "誤って覚えがちだが" embedded
    "ch3_5_q006_c2": "電気分解で析出する物質の量は流した電気量に反比例する。",
    # q006 c3: "誤って覚えやすい典型例だが" embedded
    "ch3_5_q006_c3": "ファラデー定数は不要であり、電気量だけで析出量が直接決まる。",
    # q007 c1: "誤解しがちな説明だが" embedded
    "ch3_5_q007_c1": "放電すると正極のみで硫酸鉛が生成し、負極では変化しない。",
    # q023 c4: "誤って覚えやすい典型例だが" embedded
    "ch3_5_q023_c4": "半反応式は不要であり、電子一モルあたり常に一モルの物質が析出する。",
    # q048 c1: "誤って覚えやすい典型例だが" embedded
    "ch3_5_q048_c1": "燃料電池は化石燃料を燃焼させて電気を取り出す装置である。",
    # q048 c3: "思い込みがちだが" embedded
    "ch3_5_q048_c3": "燃料電池の生成物は二酸化炭素である。",
    # q011 c1: embedded correction
    "ch3_5_q011_c1": "過酸化水素は酸化還元反応に関与しない中性の物質である。",
    # q030 c1: complex multi-error choice - keep only errors
    "ch3_5_q030_c1": "電子を受け取るのが酸化である。酸化剤は自身が酸化される。イオン化傾向大が正極になる。電気分解が化学エネルギーを電気エネルギーに変換する。",
    # q045 c2: complex multi-error - keep only errors
    "ch3_5_q045_c2": "イオン化傾向が大きいほど酸化されにくい。銅は希塩酸に溶ける。金は硝酸に溶ける。イオン化傾向が大きい金属が正極になる。",
    # q007 c4: "思い込みがちだが" embedded
    "ch3_5_q007_c4": "放電すると硫酸が生成されるため電解液の密度が上昇する。",
    # q029 c1: subject repeat in same sentence
    "ch3_5_q029_c1": "鉛蓄電池の正極活物質は鉛である。",
    # q034 c3: subject repeat
    "ch3_5_q034_c3": "電池の極性はイオン化傾向と無関係に決まる。",
    # q034 c4: subject repeat
    "ch3_5_q034_c4": "この覚え方は電気分解に関するものである。",
}

# Markers that indicate a correction sentence
CORRECTION_MARKERS = ["逆で", "正しくは", "ではない。", "ではなく"]

# Markers within a sentence indicating embedded correction
EMBEDDED_MARKERS = [
    "と勘違いされやすいが、", "と誤解されやすいが、", "と思い込みがちだが、",
    "と誤って覚えがちだが、", "と誤って覚えやすい典型例だが、",
    "が丁寧に考えると誤りで、", "もっともらしく聞こえる説明だが、",
    "と説明されることがあるが", "と初学者は誤解しがちな説明だが、",
]

SELF_LABEL = "これは正しい記述であり"


def extract_wrong_claim(text):
    """Extract just the wrong claim from a self-destructing choice."""
    # Check embedded markers first
    for marker in EMBEDDED_MARKERS:
        if marker in text:
            idx = text.index(marker)
            claim = text[:idx] + "。"
            return claim

    # Split by sentence
    parts = [p for p in text.split("。") if p.strip()]
    if len(parts) <= 1:
        return text

    # Check if 2nd+ sentences are corrections
    for i, part in enumerate(parts[1:], 1):
        is_correction = False
        for m in CORRECTION_MARKERS:
            if m in part:
                is_correction = True
                break
        # Also check if it restates the subject with different predicate
        if not is_correction and len(parts[0]) > 4 and len(part) > 4:
            # If starts with similar subject (first 3-5 chars match)
            if part[:3] in parts[0][:15]:
                is_correction = True
        if is_correction:
            return "。".join(parts[:i]) + "。"

    return text


def extract_correct_statement(text):
    """Remove self-labeling from correct-statement choices in incorrect-type questions."""
    if SELF_LABEL in text:
        idx = text.index(SELF_LABEL)
        # Find the end of the actual statement (before self-label)
        before = text[:idx].rstrip()
        if before.endswith("。"):
            return before
        # Sometimes there's no period before self-label
        return before + "。" if not before.endswith("。") else before
    return text


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python questions/_fix_answer_leak.py <chapter> [--dry-run]")
        sys.exit(1)

    chapter = args[0]
    dry_run = "--dry-run" in args
    root = Path(__file__).resolve().parent.parent
    q_path = root / "questions" / f"{chapter}.json"

    with open(q_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    stats = {"correct_type_fixed": 0, "incorrect_type_fixed": 0, "overrides": 0, "audio_deleted": 0}

    for q in data["questions"]:
        qtype = q.get("question_type", "correct")

        for ch in q["choices"]:
            cid = ch.get("choice_id", "")
            old_text = ch["text"]
            old_tts = ch.get("tts_text", old_text)
            new_text = None
            new_tts = None

            # Check manual override first
            if cid in OVERRIDES:
                new_tts = OVERRIDES[cid]
                # For display text, use same (this chapter has no formula differences in these)
                new_text = new_tts
                stats["overrides"] += 1

            elif qtype == "correct" and not ch.get("is_correct", False):
                # Wrong choice in correct-type question
                fixed = extract_wrong_claim(old_tts)
                if fixed != old_tts:
                    new_tts = fixed
                    new_text = extract_wrong_claim(old_text)
                    stats["correct_type_fixed"] += 1

            elif qtype == "incorrect" and not ch.get("is_correct", False):
                # Correct-statement choice in incorrect-type question
                fixed = extract_correct_statement(old_tts)
                if fixed != old_tts:
                    new_tts = fixed
                    new_text = extract_correct_statement(old_text)
                    stats["incorrect_type_fixed"] += 1

            if new_text and new_text != old_text:
                print(f"  {cid}:")
                print(f"    OLD: {old_text[:60]}...")
                print(f"    NEW: {new_text[:60]}...")
                if not dry_run:
                    ch["text"] = new_text
                    ch["tts_text"] = new_tts
                    # Delete stale audio
                    mp3 = root / "audio" / chapter / q["id"] / f"{cid}.mp3"
                    if mp3.exists():
                        mp3.unlink()
                        stats["audio_deleted"] += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}correct-type fixes: {stats['correct_type_fixed']}")
    print(f"{prefix}incorrect-type fixes: {stats['incorrect_type_fixed']}")
    print(f"{prefix}manual overrides: {stats['overrides']}")
    print(f"{prefix}audio files deleted: {stats['audio_deleted']}")

    if not dry_run:
        with open(q_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        with open(q_path, "a", encoding="utf-8") as f:
            f.write("\n")
        print(f"Saved {q_path}")


if __name__ == "__main__":
    main()
