"""
Deep audit: detect tts_explanation that only explains the correct answer
without mentioning why incorrect choices are wrong.

Heuristic signals for "correct-only" explanations:
1. tts_explanation that doesn't contain any negation/contrast keywords
   like: ではなく, ではありません, 誤り, 逆, 不正解, 異なり, 違い,
         一方, に対し, しかし, ただし, 注意
2. Short length (< 80 chars) combined with missing contrast
3. Explanation that matches the correct choice too closely without
   addressing other choices
"""
import json, pathlib, re

CHAPTERS = [
    "ch1-1","ch1-2","ch1-3","ch1-4",
    "ch2-1","ch2-2","ch2-3",
    "ch3-1","ch3-2","ch3-3","ch3-4","ch3-5",
    "ch4-1","ch4-2","ch4-3","ch4-4",
]

CONTRAST_PATTERNS = [
    "ではなく", "ではありません", "誤り", "不正解", "異なり",
    "違い", "一方", "に対し", "しかし", "ただし", "注意",
    "逆", "混同", "間違", "ない", "ません", "区別",
    "すべて", "正解", "不正", "覚え", "セットで", "整理",
    "ポイント", "それぞれ", "比較", "対応", "まとめ",
]

q_dir = pathlib.Path("questions")
all_flagged = {}

for ch in CHAPTERS:
    fp = q_dir / f"{ch}.json"
    if not fp.exists():
        continue
    data = json.loads(fp.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    flagged = []
    
    for q in questions:
        qid = q["id"]
        tts_exp = q.get("tts_explanation", "")
        exp_len = len(tts_exp)
        
        # Count how many contrast markers are present
        contrast_count = sum(1 for p in CONTRAST_PATTERNS if p in tts_exp)
        
        # Flag questions that are short AND have very few contrast markers
        # These are most likely to be "correct-only" explanations
        if exp_len < 100 and contrast_count <= 1:
            flagged.append((qid, exp_len, contrast_count, tts_exp))
    
    if flagged:
        all_flagged[ch] = flagged

# Summary
total_flagged = sum(len(v) for v in all_flagged.values())
print(f"Total chapters scanned: {len(CHAPTERS)}")
print(f"Total questions flagged: {total_flagged}")
print()

for ch, items in all_flagged.items():
    print(f"{'='*70}")
    print(f"Chapter: {ch}  - {len(items)} flagged")
    print(f"{'='*70}")
    for qid, ln, cc, exp in items:
        print(f"  {qid} ({ln}ch, contrast={cc})")
        print(f"    → {exp}")
        print()
