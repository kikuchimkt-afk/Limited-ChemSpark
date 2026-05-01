import json
d = json.load(open("questions/ch4-4.json", "r", encoding="utf-8"))
qids = ["ch4_4_q003","ch4_4_q013","ch4_4_q031","ch4_4_q045","ch4_4_q049"]
for q in d["questions"]:
    if q["id"] in qids:
        print(f"\n=== {q['id']}: {q['tts_question'][:60]} ===")
        for i, c in enumerate(q["choices"]):
            tag = "★" if c["is_correct"] else " "
            print(f"  {tag}c{i+1}: {c['tts_text'][:150]}")
