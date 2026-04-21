"""Extract all wrong choices from length-biased questions in ch5-5."""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for q in data['questions']:
    qid = q['id']
    correct_len = 0
    max_wrong = 0
    for c in q['choices']:
        tlen = len(c['tts_text'])
        if c['is_correct']:
            correct_len = tlen
        else:
            if tlen > max_wrong:
                max_wrong = tlen
    diff = correct_len - max_wrong
    if diff >= 10:
        print(f'\n=== {qid} (correct={correct_len}, max_wrong={max_wrong}, diff=+{diff}) ===')
        print(f'  Q: {q["tts_question"]}')
        for c in q['choices']:
            if not c['is_correct']:
                print(f'  {c["choice_id"]}: [{len(c["tts_text"])}] {c["tts_text"]}')
                if 'trap_detail' in c and c['trap_detail']:
                    print(f'    trap: {c["trap_detail"]}')
