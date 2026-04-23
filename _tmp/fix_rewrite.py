"""Fix broken tts_explanation fields that were set to objects instead of strings,
and also update the display 'explanation' field."""
import json, pathlib

fp = pathlib.Path("questions/ch4-2.json")
with open(fp, "r", encoding="utf-8") as f:
    data = json.load(f)

fixed = 0
for q in data["questions"]:
    te = q.get("tts_explanation")
    if isinstance(te, dict):
        # Extract the tts_explanation string
        new_tts = te.get("tts_explanation", "")
        new_exp = te.get("explanation", "")
        q["tts_explanation"] = new_tts
        if new_exp:
            q["explanation"] = new_exp
        fixed += 1
        print(f"  Fixed {q['id']}")

with open(fp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nFixed {fixed} entries")
