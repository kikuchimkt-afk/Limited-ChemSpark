import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('questions/ch1-3.json','r',encoding='utf-8'))
PATS = [r'実際には', r'正しくは', r'のが正しい', r'これは正しい記述', r'ではなく', r'が正しい。', r'本来は', r'正確には']
count = 0
for q in d['questions']:
    for c in q['choices']:
        if c['is_correct']: continue
        for pat in PATS:
            if re.search(pat, c['text']):
                count += 1
                print(f"{q['id']} {c['choice_id']} [{pat}]:")
                print(f"  {c['text']}")
                print()
                break
print(f"Total: {count}")
