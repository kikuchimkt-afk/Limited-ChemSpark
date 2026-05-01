"""Scan ch3-1.json for answer-leak patterns in incorrect choices."""
import json, re

with open("questions/ch3-1.json", "r", encoding="utf-8") as f:
    data = json.load(f)

LEAK_PATTERNS = [
    r"逆で",
    r"正しくは",
    r"実際には",
    r"正しい記述",
    r"これは正しい",
    r"誤って覚え",
    r"勘違いされ",
    r"と思い込み",
    r"典型例だが",
    r"覚えやすい",
    r"覚えがち",
    r"陥りやすい",
    r"よく挙げられる",
]

issues = []
for q in data["questions"]:
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        txt = c.get("tts_text", c.get("text", ""))
        is_correct = c["is_correct"]
        if not is_correct:
            for pat in LEAK_PATTERNS:
                if re.search(pat, txt):
                    issues.append({"type": "LEAK", "qid": qid, "choice": i + 1, "pattern": pat, "text": txt[:100]})
            if "。" in txt:
                sentences = txt.split("。")
                if len(sentences) >= 3:
                    latter = "。".join(sentences[1:])
                    for pat in ["逆で", "実際には", "正しくは", "ではない", "ではなく", "誤りで"]:
                        if pat in latter:
                            issues.append({"type": "SELF_REFUTE", "qid": qid, "choice": i + 1, "text": txt[:100]})
                            break

print(f"=== Answer-leak scan for ch3-1 ===")
print(f"Total issues found: {len(issues)}")
print()

seen = set()
for iss in issues:
    key = f"{iss['qid']}_c{iss['choice']}"
    if key in seen:
        continue
    seen.add(key)
    print(f"[{iss['type']}] {iss['qid']} choice {iss['choice']}")
    print(f"  Text: {iss['text']}")
    print()

print(f"\nUnique affected choices: {len(seen)}")
