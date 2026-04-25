"""Verify ch1-1.json data integrity after display explanation fix."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

d = json.load(open("questions/ch1-1.json", encoding="utf-8"))

print("=== q001 explanation (display) ===")
print(d["questions"][0]["explanation"])
print()
print("=== q001 tts_explanation ===")
print(d["questions"][0]["tts_explanation"])
print()

# Check first 5 questions
for q in d["questions"][:5]:
    qid = q["id"]
    exp = q["explanation"]
    has_ref = "選択肢" in exp
    print(f"{qid}: len={len(exp)}, has_選択肢={has_ref}")
    print(f"  display: {exp[:80]}...")
    print()
