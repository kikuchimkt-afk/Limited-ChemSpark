import json
data = json.load(open('questions/ch4-3.json', encoding='utf-8'))
short = [q for q in data['questions'] if len(q.get('tts_explanation', '')) < 80]
print(f'Short explanations: {len(short)}')
for q in short:
    print(f"  {q['id']}: {len(q['tts_explanation'])} chars - {q['tts_explanation'][:60]}...")
