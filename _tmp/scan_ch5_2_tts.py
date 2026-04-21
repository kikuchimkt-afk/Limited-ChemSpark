import json, sys
sys.stdout.reconfigure(encoding='utf-8')

tts_pats = ['シーエヌエイチ','シーツー','シースリー','シーフォー',
            'エイチツー','エイチフォー','エイチシックス','エイチエイト',
            'オーツー','オースリー','オーフォー',
            'エヌプラスに','エヌマイナスに','シーエイチツーオー']

with open('questions/ch5-2.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for q in d['questions']:
    if any(p in q.get('question', '') for p in tts_pats):
        print(f"  {q['id']} question: {q['question'][:100]}")
    for c in q.get('choices', []):
        if any(p in c.get('text', '') for p in tts_pats):
            print(f"  {q['id']} choice {c['label']}: {c['text'][:100]}")
