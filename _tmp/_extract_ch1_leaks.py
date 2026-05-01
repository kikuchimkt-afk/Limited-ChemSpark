"""Extract all leak choice IDs and texts for ch1-1 through ch1-4."""
import json, re, os

LEAK = [r"逆で",r"正しくは",r"実際には",r"実際は",r"正しい記述",r"これは正しい",r"誤って覚え",r"勘違いされ",r"と思い込み",r"覚えがち",r"陥りやすい",r"ではなく",r"ではない",r"誤りで",r"誤りである",r"正確には"]

for ch in ["ch1-1","ch1-2","ch1-3","ch1-4"]:
    d = json.load(open(f"questions/{ch}.json", encoding="utf-8"))
    print(f"\n{'='*60}")
    print(f"=== {ch} ===")
    for q in d["questions"]:
        for i, c in enumerate(q["choices"]):
            if c["is_correct"]:
                continue
            txt = c.get("tts_text","")
            matched = None
            for p in LEAK:
                if re.search(p, txt):
                    matched = p
                    break
            if matched:
                print(f"\n--- {q['id']} c{i+1} [{c['choice_id']}] pat={matched} ---")
                print(f"  Q: {q['tts_question'][:60]}")
                print(f"  T: {txt[:200]}")
