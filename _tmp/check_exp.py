import json, sys

sys.stdout.reconfigure(encoding='utf-8')

with open("questions/ch4-2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

short = []
for q in data["questions"]:
    exp = q["explanation"]
    l = len(exp)
    if l < 80:
        short.append(q["id"])
    print(f'{q["id"]}: [{l}ch] {exp[:120]}')

print(f"\nShort explanations (<80ch): {len(short)}")
for s in short:
    print(f"  {s}")
