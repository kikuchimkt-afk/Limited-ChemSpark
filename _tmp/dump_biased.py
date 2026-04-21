import json
d = json.loads(open('questions/ch5-2.json', 'r', encoding='utf-8').read())
biased = ['ch5_2_q007','ch5_2_q012','ch5_2_q015','ch5_2_q030']
for q in d['questions']:
    if q['id'] in biased:
        print(f"{q['id']}:")
        for c in q['choices']:
            if not c['is_correct']:
                print(f"  {c['choice_id']}: {c['tts_text']}")
