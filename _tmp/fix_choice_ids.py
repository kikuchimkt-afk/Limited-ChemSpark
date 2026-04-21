import json

with open('questions/ch5-2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed = 0
for q in data['questions']:
    qid = q['id']
    for i, c in enumerate(q['choices']):
        expected_id = f"{qid}_c{i+1}"
        if c['choice_id'] != expected_id:
            print(f"  {qid} choice {i+1}: {c['choice_id']} -> {expected_id}")
            c['choice_id'] = expected_id
            fixed += 1

print(f"\nFixed {fixed} choice_ids")

with open('questions/ch5-2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
