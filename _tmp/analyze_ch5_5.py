import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count patterns
multi_sentence = 0
single_sentence = 0

for q in data['questions']:
    for c in q['choices']:
        if not c['is_correct']:
            t = c['tts_text']
            sentences = [s for s in t.split('。') if s.strip()]
            if len(sentences) >= 2:
                multi_sentence += 1
                # Show first 30 examples
                if multi_sentence <= 30:
                    print(f"{q['id']} {c['choice_id']}:")
                    print(f"  FULL: {t}")
                    print(f"  KEEP: {sentences[0]}。")
                    print(f"  MOVE: {'。'.join(sentences[1:])}。" if len(sentences) > 1 else "")
                    print()
            else:
                single_sentence += 1

print(f"\nSummary: {multi_sentence} multi-sentence, {single_sentence} single-sentence")
