import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
for ch in ['ch1-1','ch1-2','ch1-3']:
    d = json.loads(open(f'questions/{ch}.json','r',encoding='utf-8').read())
    hits = []
    for q in d['questions']:
        if re.search(r'選択肢[0-9一二三四五]', q['explanation']):
            hits.append(q['id'])
    print(f"{ch}: {len(hits)}/{len(d['questions'])} explanations have choice refs")
    for h in hits:
        print(f"  {h}")
