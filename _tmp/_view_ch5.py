import json
for ch, qids in [("ch5-1", ["ch5_1_q013"]), ("ch5-5", ["ch5_5_q030", "ch5_5_q041"])]:
    d = json.load(open(f"questions/{ch}.json", "r", encoding="utf-8"))
    for q in d["questions"]:
        if q["id"] in qids:
            print(f"\n=== [{ch}] {q['id']}: {q['tts_question'][:60]} ===")
            for i, c in enumerate(q["choices"]):
                tag = "★" if c["is_correct"] else " "
                print(f"  {tag}c{i+1}: {c['tts_text'][:150]}")
