import json, re, os
LEAK = [r"逆で",r"正しくは",r"実際には",r"実際は",r"正しい記述",r"これは正しい",r"誤って覚え",r"勘違いされ",r"と思い込み",r"覚えがち",r"陥りやすい",r"ではなく",r"ではない",r"誤りで",r"誤りである",r"正確には"]
for ch in ["ch1-1","ch1-2","ch1-3","ch1-4"]:
    d = json.load(open(f"questions/{ch}.json", encoding="utf-8"))
    cnt = 0
    for q in d["questions"]:
        for i, c in enumerate(q["choices"]):
            if not c["is_correct"]:
                if any(re.search(p, c.get("tts_text","")) for p in LEAK):
                    cnt += 1
    print(f"{ch}: {cnt} leaks")
