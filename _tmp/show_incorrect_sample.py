"""Show what an incorrect-type question looks like with current data."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

d = json.loads(Path("questions/ch1-1.json").read_text("utf-8"))

# Find first incorrect-type question
for q in d["questions"]:
    if q.get("question_type") == "incorrect":
        print(f"=== {q['id']} (type=incorrect) ===")
        print(f"Q: {q['question'][:60]}...")
        print()
        for i, c in enumerate(q["choices"], 1):
            td = c.get("trap_detail", "")
            correct = c.get("is_correct", False)
            tt = c.get("trap_type", "NONE")
            
            if correct:
                marker = "×"  # is_correct in incorrect type = the wrong statement to pick
                detail = td or "誤りを含む記述。"
            elif td:
                marker = "○"
                detail = td
            else:
                marker = "○"
                detail = "この記述は正しい。"  # fallback
            
            print(f"  選択肢{i} {marker} {detail}")
            print(f"    text: {c['text'][:60]}")
            print(f"    trap_detail: {td or '(なし)'}")
            print()
        break
