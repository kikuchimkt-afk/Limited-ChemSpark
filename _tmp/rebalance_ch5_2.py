import json

with open('questions/ch5-2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count current positions
pos_count = {1: 0, 2: 0, 3: 0, 4: 0}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count[i] += 1

print("Before:", pos_count)

# Target: {1:13, 2:13, 3:12, 4:12} - need to move 6 from pos3 to pos1(+3) and pos4(+3)
# Find questions where correct is at position 3
pos3_questions = []
for q in data['questions']:
    for i, c in enumerate(q['choices']):
        if c['is_correct'] and i == 2:  # 0-indexed
            pos3_questions.append(q['id'])

print(f"Position 3 questions ({len(pos3_questions)}): {pos3_questions}")

# Move first 3 to position 1 (swap c[0] and c[2])
# Move next 3 to position 4 (swap c[2] and c[3])
moves_to_1 = pos3_questions[:3]
moves_to_4 = pos3_questions[3:6]

for q in data['questions']:
    if q['id'] in moves_to_1:
        q['choices'][0], q['choices'][2] = q['choices'][2], q['choices'][0]
        # Update labels
        for i, c in enumerate(q['choices']):
            c['label'] = str(i + 1)
    elif q['id'] in moves_to_4:
        q['choices'][2], q['choices'][3] = q['choices'][3], q['choices'][2]
        for i, c in enumerate(q['choices']):
            c['label'] = str(i + 1)

# Recount
pos_count2 = {1: 0, 2: 0, 3: 0, 4: 0}
for q in data['questions']:
    for i, c in enumerate(q['choices'], 1):
        if c['is_correct']:
            pos_count2[i] += 1

print("After:", pos_count2)

with open('questions/ch5-2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')

print("Saved.")
