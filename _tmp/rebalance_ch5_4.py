import json

with open('questions/ch5-4.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pos_count = {1: 0, 2: 0, 3: 0, 4: 0}
pos_qs = {1: [], 2: [], 3: [], 4: []}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count[i] += 1
            pos_qs[i].append(q['id'])

print("Before:", pos_count)
# Target: {1:13, 2:13, 3:12, 4:12} (total 50)
# Current: {1:14, 2:11, 3:16, 4:9}
# Move: pos1 14->13 (-1 to pos4), pos3 16->12 (-4: 2 to pos2, 2 to pos4)
moves_1_to_4 = pos_qs[1][:1]
moves_3_to_2 = pos_qs[3][:2]
moves_3_to_4 = pos_qs[3][2:4]

for q in data['questions']:
    if q['id'] in moves_1_to_4:
        q['choices'][0], q['choices'][3] = q['choices'][3], q['choices'][0]
    elif q['id'] in moves_3_to_2:
        q['choices'][2], q['choices'][1] = q['choices'][1], q['choices'][2]
    elif q['id'] in moves_3_to_4:
        q['choices'][2], q['choices'][3] = q['choices'][3], q['choices'][2]

# Fix labels and choice_ids
for q in data['questions']:
    for i, c in enumerate(q['choices']):
        c['label'] = str(i + 1)
        c['choice_id'] = f"{q['id']}_c{i+1}"

pos_count2 = {1: 0, 2: 0, 3: 0, 4: 0}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count2[i] += 1

print("After:", pos_count2)

with open('questions/ch5-4.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print("Saved.")
