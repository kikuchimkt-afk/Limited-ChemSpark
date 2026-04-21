"""Extract current wrong choice tts_text for biased questions and generate stub pads."""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pads = {}
for q in data['questions']:
    cl = 0
    for c in q['choices']:
        if c['is_correct']:
            cl = len(c['tts_text'])
            break
    mw = max((len(c['tts_text']) for c in q['choices'] if not c['is_correct']), default=0)
    if cl - mw < 10:
        continue
    qid = q['id']
    pads[qid] = {}
    for c in q['choices']:
        if c['is_correct'] or len(c['tts_text']) >= cl - 9:
            continue
        pads[qid][c['tts_text']] = f"__REPLACE__ (current={len(c['tts_text'])}, target>={cl-9})"

# Write stub file
with open('_tmp/stub_pads.json', 'w', encoding='utf-8') as f:
    json.dump(pads, f, ensure_ascii=False, indent=2)

print(f'Stub pads: {len(pads)} questions')
for qid, qp in pads.items():
    for k, v in qp.items():
        print(f'  {qid} [{len(k)}]: {k}')
