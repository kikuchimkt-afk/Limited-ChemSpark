import json
d = json.load(open("questions/ch6-3.json", "r", encoding="utf-8"))
import re
LEAK = [r"逆で",r"正しくは",r"実際には",r"実際は",r"正しい記述",r"これは正しい",r"誤って覚え",r"勘違いされ",r"と思い込み",r"覚えがち",r"陥りやすい",r"ではなく",r"ではない",r"誤りで",r"誤りである",r"正確には"]
for q in d["questions"]:
    for i, c in enumerate(q["choices"]):
        if c["is_correct"]:
            continue
        txt = c["tts_text"]
        for p in LEAK:
            if re.search(p, txt):
                print(f"\n--- {q['id']} c{i+1} [{c['choice_id']}] ---")
                print(f"  Q: {q['tts_question'][:60]}")
                print(f"  T: {txt}")
                break
