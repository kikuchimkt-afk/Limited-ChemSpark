import json
with open('questions/ch5-1.json','r',encoding='utf-8') as f:
    d = json.load(f)
for q in d['questions']:
    if q['id'] == 'ch5_1_q016':
        for c in q['choices']:
            if '一度もない' in c['tts_text']:
                old = c['tts_text']
                c['tts_text'] = old.replace('一度もない', 'いちどもない')
                c['text'] = '生命力説は現在も科学的に広く支持されており、実験によって否定されたことはいちどもない。'
                print('fixed tts_text')
with open('questions/ch5-1.json','w',encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print('saved')
