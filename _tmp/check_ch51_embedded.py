"""Check ch5-1 wrong choices for embedded explanations (trap_detail leaking into text)."""
import json
with open('questions/ch5-1.json','r',encoding='utf-8') as f:
    data = json.load(f)

issues = 0
for q in data['questions']:
    for c in q['choices']:
        if c['is_correct']:
            continue
        txt = c['tts_text']
        # Check for multiple sentences - could indicate embedded explanation
        sentences = [s for s in txt.split('。') if s.strip()]
        if len(sentences) >= 2:
            issues += 1
            print(f"{q['id']}: [{len(txt)}] {txt}")

print(f"\nTotal wrong choices with 2+ sentences: {issues}")
