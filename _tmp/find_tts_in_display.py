"""Find all text (display) fields that contain TTS-style formula readings."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('questions/ch5-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tts_patterns = [
    'シーエヌエイチ', 'シーツー', 'シースリー', 'シーフォー',
    'エイチツー', 'エイチフォー', 'エイチシックス', 'エイチエイト',
    'オーツー', 'オースリー', 'オーフォー',
    'エヌプラスに', 'エヌマイナスに', 'にエヌ',
    'シーエイチツーオー', 'ツーエイチフォーオーツー',
]

issues = []
for q in data['questions']:
    # Check question text
    if any(p in q['question'] for p in tts_patterns):
        issues.append((q['id'], 'question', q['question']))
    # Check choices text
    for c in q['choices']:
        if any(p in c['text'] for p in tts_patterns):
            issues.append((q['id'], f"choice {c['label']}", c['text']))
    # Check explanation
    if any(p in q['explanation'] for p in tts_patterns):
        issues.append((q['id'], 'explanation', q['explanation']))

print(f"Total issues: {len(issues)}")
for qid, field, txt in issues:
    print(f"  {qid} [{field}]: {txt[:80]}")
