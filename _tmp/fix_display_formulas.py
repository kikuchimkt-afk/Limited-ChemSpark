"""Fix display fields: replace TTS readings with chemical formulas."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('questions/ch5-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Mapping: TTS reading -> display chemical formula
replacements = {
    'シーエヌエイチにエヌプラスに': 'CₙH₂ₙ₊₂',
    'シーエヌエイチにエヌマイナスに': 'CₙH₂ₙ₋₂',
    'シーエヌエイチにエヌ': 'CₙH₂ₙ',
    'シーフォーエイチエイトオーフォー': 'C₄H₈O₄',
    'シースリーエイチシックスオースリー': 'C₃H₆O₃',
    'シーツーエイチフォーオーツー': 'C₂H₄O₂',
    'シーエイチツーオー': 'CH₂O',
}

count = 0
for q in data['questions']:
    # Fix question
    orig = q['question']
    for tts, chem in replacements.items():
        q['question'] = q['question'].replace(tts, chem)
    if q['question'] != orig:
        count += 1
        print(f"  {q['id']} question: {q['question'][:80]}")

    # Fix choices text
    for c in q['choices']:
        orig = c['text']
        for tts, chem in replacements.items():
            c['text'] = c['text'].replace(tts, chem)
        if c['text'] != orig:
            count += 1
            print(f"  {q['id']} choice {c['label']}: {c['text']}")

    # Fix explanation
    orig = q['explanation']
    for tts, chem in replacements.items():
        q['explanation'] = q['explanation'].replace(tts, chem)
    if q['explanation'] != orig:
        count += 1
        print(f"  {q['id']} explanation: {q['explanation'][:80]}")

with open('questions/ch5-1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nFixed {count} fields total.")
