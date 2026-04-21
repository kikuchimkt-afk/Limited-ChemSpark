import json

with open('questions/ch5-3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
for q in data['questions']:
    for c in q['choices']:
        if not c['is_correct'] and 'trap_type' in c and ('trap_detail' not in c or not c.get('trap_detail')):
            c['trap_detail'] = '誤り。'
            fixed += 1

print(f"Fixed {fixed} missing trap_detail fields")

with open('questions/ch5-3.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
