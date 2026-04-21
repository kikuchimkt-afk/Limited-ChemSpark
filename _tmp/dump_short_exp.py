"""Extract all short explanations from ch5-1 for rewriting."""
import json
with open('questions/ch5-1.json','r',encoding='utf-8') as f:
    data = json.load(f)

for q in data['questions']:
    exp = q['tts_explanation']
    if len(exp) < 100:
        correct = ''
        for c in q['choices']:
            if c['is_correct']:
                correct = c['tts_text']
                break
        print(f"=== {q['id']} [{len(exp)}] sub={q.get('sub_category','')} ===")
        print(f"Q: {q['tts_question']}")
        print(f"A: {correct}")
        print(f"E: {exp}")
        print()
