import json

with open('questions/ch5-3.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count current positions
pos_count = {1: 0, 2: 0, 3: 0, 4: 0}
pos_qs = {1: [], 2: [], 3: [], 4: []}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count[i] += 1
            pos_qs[i].append(q['id'])

print("Before:", pos_count)
# Target: {1:13, 2:13, 3:12, 4:12}
# Need: pos1 OK(13), pos2: 15->13 move 2, pos3: 18->12 move 6, pos4: 4->12 need +8
# Move 2 from pos2 to pos4, move 6 from pos3 to pos4
moves_2_to_4 = pos_qs[2][:2]
moves_3_to_4 = pos_qs[3][:6]

for q in data['questions']:
    if q['id'] in moves_2_to_4:
        q['choices'][1], q['choices'][3] = q['choices'][3], q['choices'][1]
    elif q['id'] in moves_3_to_4:
        q['choices'][2], q['choices'][3] = q['choices'][3], q['choices'][2]

# Fix labels and choice_ids
for q in data['questions']:
    for i, c in enumerate(q['choices']):
        c['label'] = str(i + 1)
        c['choice_id'] = f"{q['id']}_c{i+1}"

# Recount
pos_count2 = {1: 0, 2: 0, 3: 0, 4: 0}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count2[i] += 1

print("After:", pos_count2)

with open('questions/ch5-3.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print("Saved.")
