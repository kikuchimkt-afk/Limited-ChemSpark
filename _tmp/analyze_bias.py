import json
with open('questions/ch5-5.json','r',encoding='utf-8') as f:
    data = json.load(f)
for q in data['questions']:
    cl = 0; mw = 0
    for c in q['choices']:
        if c['is_correct']: cl = len(c['tts_text'])
        elif len(c['tts_text']) > mw: mw = len(c['tts_text'])
    d = cl - mw
    if d >= 15:
        qid = q['id']
        print(f'\n=== {qid}: correct={cl} max_wrong={mw} diff=+{d} target>={cl-8} ===')
        for c in q['choices']:
            if not c['is_correct']:
                print(f'  [{len(c["tts_text"])}] {c["tts_text"]}')
