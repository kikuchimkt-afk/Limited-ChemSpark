import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('questions/ch1-3.json','r',encoding='utf-8'))
# Check specific questions where we made changes
targets = ['ch1_3_q018', 'ch1_3_q020', 'ch1_3_q021', 'ch1_3_q025', 'ch1_3_q026',
           'ch1_3_q030', 'ch1_3_q037', 'ch1_3_q040', 'ch1_3_q042', 'ch1_3_q044', 'ch1_3_q050',
           'ch1_3_q001', 'ch1_3_q003', 'ch1_3_q009']
for q in d['questions']:
    if q['id'] in targets:
        print(f"=== {q['id']} ===")
        print(f"Q(disp): {q['question']}")
        for c in q['choices']:
            mark = "T" if c['is_correct'] else "F"
            print(f"  {mark} text: {c['text'][:80]}")
        print(f"EXP(disp): {q['explanation'][:150]}")
        print()
