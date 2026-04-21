"""
Fix ch5-5 wrong choices: remove embedded explanations.
Pattern: "Wrong claim。Explanation why it's wrong。" -> keep only "Wrong claim。"
The removed explanation is merged into trap_detail.
Also updates both text and tts_text fields.
"""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
for q in data['questions']:
    for c in q['choices']:
        if not c['is_correct']:
            tts = c.get('tts_text', '')
            txt = c.get('text', '')
            
            tts_sentences = [s for s in tts.split('。') if s.strip()]
            txt_sentences = [s for s in txt.split('。') if s.strip()]
            
            if len(tts_sentences) >= 2:
                # Keep only the first sentence (the wrong claim)
                new_tts = tts_sentences[0] + '。'
                explanation_part = '。'.join(tts_sentences[1:]) + '。'
                
                # Update trap_detail with the removed explanation
                old_detail = c.get('trap_detail', '')
                if old_detail and explanation_part not in old_detail:
                    c['trap_detail'] = explanation_part.rstrip('。') + '。'
                else:
                    c['trap_detail'] = explanation_part.rstrip('。') + '。'
                
                c['tts_text'] = new_tts
                fixed += 1
            
            if len(txt_sentences) >= 2:
                new_txt = txt_sentences[0] + '。'
                c['text'] = new_txt

print(f"Fixed {fixed} wrong choices (removed embedded explanations)")

# Verify no correct choices were modified
for q in data['questions']:
    correct_count = sum(1 for c in q['choices'] if c['is_correct'])
    assert correct_count == 1, f"{q['id']}: {correct_count} correct choices"

with open('questions/ch5-5.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("Saved questions/ch5-5.json")
