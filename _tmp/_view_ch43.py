import json
d = json.load(open("questions/ch4-3.json", "r", encoding="utf-8"))
qids = ["ch4_3_q005","ch4_3_q007","ch4_3_q009","ch4_3_q010","ch4_3_q016","ch4_3_q023","ch4_3_q026","ch4_3_q034","ch4_3_q043"]
for q in d["questions"]:
    if q["id"] in qids:
        print(f"\n=== {q['id']}: {q['tts_question'][:60]} ===")
        for i, c in enumerate(q["choices"]):
            tag = "★" if c["is_correct"] else " "
            print(f"  {tag}c{i+1}: {c['tts_text'][:150]}")
