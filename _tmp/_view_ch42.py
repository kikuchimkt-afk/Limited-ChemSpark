import json
d = json.load(open("questions/ch4-2.json", "r", encoding="utf-8"))
qids = ["ch4_2_q014", "ch4_2_q016", "ch4_2_q022", "ch4_2_q024"]
for q in d["questions"]:
    if q["id"] in qids:
        print(f"\n=== {q['id']}: {q['tts_question'][:60]} ===")
        for i, c in enumerate(q["choices"]):
            tag = "★" if c["is_correct"] else " "
            print(f"  {tag}c{i+1}: {c['tts_text'][:120]}")
