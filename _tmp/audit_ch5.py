"""Deep audit for ch5-1 to ch5-5."""
import json, pathlib

CHAPTERS = ["ch5-1","ch5-2","ch5-3","ch5-4","ch5-5"]

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
    data = json.loads(fp.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    flagged = []
    dup_choices = []
    
    for q in questions:
        qid = q["id"]
        tts_exp = q.get("tts_explanation", "")
        exp_len = len(tts_exp)
        contrast_count = sum(1 for p in CONTRAST_PATTERNS if p in tts_exp)
        
        if exp_len < 100 and contrast_count <= 1:
            flagged.append((qid, exp_len, contrast_count, tts_exp))
        
        # duplicate choices
        choice_texts = [c.get("tts_text", c.get("text", "")) for c in q.get("choices", [])]
        seen = {}
        for i, ct in enumerate(choice_texts):
            if ct in seen:
                dup_choices.append((qid, seen[ct]+1, i+1))
            else:
                seen[ct] = i
    
    if flagged or dup_choices:
        all_flagged[ch] = (flagged, dup_choices)
    else:
        all_flagged[ch] = ([], [])

total_flagged = sum(len(v[0]) for v in all_flagged.values())
total_dups = sum(len(v[1]) for v in all_flagged.values())
print(f"Total flagged: {total_flagged}, Duplicate choices: {total_dups}")
print()

for ch in CHAPTERS:
    flagged, dups = all_flagged[ch]
    print(f"{'='*70}")
    print(f"Chapter: {ch} - {len(flagged)} flagged, {len(dups)} duplicates")
    print(f"{'='*70}")
    for qid, ln, cc, exp in flagged:
        print(f"  {qid} ({ln}ch, contrast={cc})")
        print(f"    -> {exp}")
        print()
    for qid, c1, c2 in dups:
        print(f"  [DUP] {qid}: choice {c1} == choice {c2}")
