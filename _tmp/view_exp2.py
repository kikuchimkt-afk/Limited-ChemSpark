import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('questions/ch5-1.json','r',encoding='utf-8') as f:
    data = json.load(f)
for q in data['questions'][:10]:
    correct = ''
    for c in q['choices']:
        if c['is_correct']:
            correct = c['tts_text']
    print(f"=== {q['id']} [{len(q['tts_explanation'])}] sub={q.get('sub_category','')} ===")
    print(f"Q: {q['tts_question']}")
    print(f"A: {correct}")
    print(f"E: {q['tts_explanation']}")
    print()
