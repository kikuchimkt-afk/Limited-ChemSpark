"""Show pattern of missing trap_detail choices."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

d = json.loads(Path("questions/ch1-1.json").read_text("utf-8"))
count = 0
for q in d["questions"]:
    for c in q["choices"]:
        if not c.get("is_correct") and not c.get("trap_detail"):
            qtype = q.get("question_type", "?")
            print(f'{q["id"]} | type={qtype} | trap_type={c.get("trap_type","NONE")}')
            print(f'  text: {c["text"][:80]}')
            print()
            count += 1
            if count >= 8:
                break
    if count >= 8:
        break
print(f"Total missing in ch1-1: {count} shown")
