"""Generate natural-sounding padded wrong choices for ch5-5."""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pads = {}

for q in data['questions']:
    qid = q['id']
    correct_len = 0
    for c in q['choices']:
        if c['is_correct']:
            correct_len = len(c['tts_text'])
            break

    max_wrong = max((len(c['tts_text']) for c in q['choices'] if not c['is_correct']), default=0)
    if correct_len - max_wrong < 10:
        continue

    q_pads = {}
    sub = q.get('sub_category', '')

    for c in q['choices']:
        if c['is_correct'] or len(c['tts_text']) >= correct_len - 10:
            continue

        curr = c['tts_text']
        base = curr.rstrip('。')
        needed = correct_len - len(curr)

        if needed <= 20:
            suffix = f'これは{sub}の基礎知識である。'
        elif needed <= 35:
            suffix = f'この性質は{sub}を理解するうえで重要な基本事項として広く知られている。'
        elif needed <= 50:
            suffix = f'この性質は{sub}を学ぶ際の出発点となる基本的な知識であり、関連する多くの化学反応の理解に不可欠である。'
        else:
            suffix = f'この性質は{sub}における最も基本的な事項であり、関連する化学的性質や反応機構を正しく理解するための出発点として極めて重要である。'

        new = base + '。' + suffix

        while len(new) > correct_len + 5 and new.count('。') > 2:
            last = new.rfind('。', 0, len(new)-1)
            if last > len(base):
                new = new[:last+1]
            else:
                break

        if len(new) > len(curr):
            q_pads[curr] = new

    if q_pads:
        pads[qid] = q_pads

with open('questions/_pads/ch5-5.json', 'w', encoding='utf-8') as f:
    json.dump(pads, f, ensure_ascii=False, indent=2)

print(f'Pads: {len(pads)} questions, {sum(len(v) for v in pads.values())} choices')
for qid, qp in pads.items():
    for old, new in qp.items():
        print(f'  {qid}: {len(old)}->{len(new)}')
