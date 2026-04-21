"""
Rebuild pads from current ch5-5.json state.
Read current tts_text values and create new pad entries for still-biased questions.
"""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find still-biased questions (diff >= 10)
biased = []
for q in data['questions']:
    cl = 0
    for c in q['choices']:
        if c['is_correct']:
            cl = len(c['tts_text'])
            break
    mw = max((len(c['tts_text']) for c in q['choices'] if not c['is_correct']), default=0)
    if cl - mw >= 10:
        biased.append(q['id'])
        # Print current wrong choices for reference
        print(f"\n=== {q['id']}: correct={cl} max_wrong={mw} diff=+{cl-mw} ===")
        for c in q['choices']:
            if not c['is_correct']:
                print(f"  [{len(c['tts_text'])}] {c['tts_text'][:80]}")

print(f"\nTotal biased: {len(biased)}")
