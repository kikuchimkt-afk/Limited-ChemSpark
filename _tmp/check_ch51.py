import json
with open('questions/ch5-1.json','r',encoding='utf-8') as f:
    data = json.load(f)
for q in data['questions']:
    if q['id'] in ('ch5_1_q016','ch5_1_q048'):
        cl = 0
        for c in q['choices']:
            if c['is_correct']: cl = len(c['tts_text'])
        print(f"\n=== {q['id']} correct={cl} sub={q.get('sub_category','')} ===")
        for c in q['choices']:
            mark = '✓' if c['is_correct'] else ' '
            print(f"  {mark} [{len(c['tts_text'])}] {c['tts_text']}")
