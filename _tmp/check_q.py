import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('questions/ch1-3.json','r',encoding='utf-8'))
for q in d['questions']:
    if q['id'] == 'ch1_3_q040':
        print("=== q040 ===")
        print(f"EXP: {q['explanation']}")
        print(f"TTS_EXP: {q['tts_explanation']}")
        break
