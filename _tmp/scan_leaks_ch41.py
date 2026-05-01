"""Scan ch4-1.json for answer-leak patterns in incorrect choices."""
import json, re

with open("questions/ch4-1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

LEAK_PATTERNS = [
    (r"逆で", "逆で"),
    (r"正しくは", "正しくは"),
    (r"実際には", "実際には"),
    (r"実際は", "実際は"),
    (r"正しい記述", "正しい記述"),
    (r"これは正しい", "これは正しい"),
    (r"誤って覚え", "誤って覚え"),
    (r"勘違いされ", "勘違いされ"),
    (r"と思い込み", "思い込み"),
    (r"覚えがち", "覚えがち"),
    (r"陥りやすい", "陥りやすい"),
    (r"ではなく", "ではなく"),
    (r"ではない", "ではない"),
    (r"誤りで", "誤りで"),
    (r"誤りである", "誤りである"),
    (r"正確には", "正確には"),
]

issues = []
for q in data["questions"]:
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        txt = c.get("tts_text", c.get("text", ""))
        if c["is_correct"]:
            continue
        for pat, label in LEAK_PATTERNS:
            if re.search(pat, txt):
                issues.append({"qid": qid, "ci": i, "pat": label, "txt": txt[:120]})
                break

seen = set()
for iss in issues:
    key = f"{iss['qid']}_c{iss['ci']+1}"
    if key in seen:
        continue
    seen.add(key)
    print(f"[{iss['pat']}] {iss['qid']} c{iss['ci']+1}")
    print(f"  {iss['txt']}")
    print()

print(f"Unique affected choices: {len(seen)}")
