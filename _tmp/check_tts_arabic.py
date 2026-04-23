import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ch = sys.argv[1] if len(sys.argv) > 1 else 'ch1-4'
d = json.loads(open(f'questions/{ch}.json', 'r', encoding='utf-8').read())
for q in d['questions']:
    for field in ['tts_question', 'tts_explanation']:
        v = q.get(field, '')
        if re.search(r'[0-9]', v):
            # extract just the arabic-containing segment
            for m in re.finditer(r'.{0,20}[0-9]+.{0,20}', v):
                print(f"  {q['id']} {field}: ...{m.group()}...")
    for c in q['choices']:
        v = c.get('tts_text', '')
        if re.search(r'[0-9]', v):
            for m in re.finditer(r'.{0,20}[0-9]+.{0,20}', v):
                print(f"  {q['id']} {c['choice_id']} tts_text: ...{m.group()}...")
