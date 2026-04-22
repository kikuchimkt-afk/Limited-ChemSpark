import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('questions/ch1-1.json', 'r', encoding='utf-8'))
for q in d['questions']:
    if q['id'] in ['ch1_1_q045', 'ch1_1_q046', 'ch1_1_q047']:
        print(f"=== {q['id']} ===")
        print(f"Q: {q['question']}")
        print(f"E: {q['explanation']}")
        for c in q['choices']:
            mark = "T" if c['is_correct'] else "F"
            print(f"  {mark} {c['choice_id']}: {c['text']}")
        print()
