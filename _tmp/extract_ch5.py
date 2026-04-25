"""Extract flagged questions for ch5-1 to ch5-5."""
import json, pathlib

CONTRAST_PATTERNS = [
    "ではなく", "ではありません", "誤り", "不正解", "異なり",
    "違い", "一方", "に対し", "しかし", "ただし", "注意",
    "逆", "混同", "間違", "ない", "ません", "区別",
    "すべて", "正解", "不正", "覚え", "セットで", "整理",
    "ポイント", "それぞれ", "比較", "対応", "まとめ",
]

CHAPTERS = ["ch5-1","ch5-2","ch5-3","ch5-4","ch5-5"]
q_dir = pathlib.Path("questions")

for ch in CHAPTERS:
    fp = q_dir / f"{ch}.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    flagged = []
    
    for q in questions:
        tts_exp = q.get("tts_explanation", "")
        exp_len = len(tts_exp)
        contrast_count = sum(1 for p in CONTRAST_PATTERNS if p in tts_exp)
        if exp_len < 100 and contrast_count <= 1:
            flagged.append(q)
    
    if not flagged:
        continue
    
    print(f"\n{'#'*70}")
    print(f"# {ch} ({len(flagged)} flagged)")
    print(f"{'#'*70}")
    
    for q in flagged:
        qid = q["id"]
        print(f"\n--- {qid} ---")
        print(f"Q: {q['tts_question']}")
        print(f"Type: {q['question_type']}")
        for c in q["choices"]:
            mark = ">>CORRECT<<" if c["is_correct"] else f"[trap:{c.get('trap_type','')}]"
            txt = c.get('tts_text', c.get('text',''))[:90]
            print(f"  {c['label']}. {mark} {txt}...")
        print(f"Exp: {q['tts_explanation']}")
