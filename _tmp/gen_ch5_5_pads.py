"""
Auto-generate _pads/ch5-5.json from trap_detail content.
Strategy: For each length-biased question, pad wrong choices by
incorporating relevant detail from trap_detail into a more descriptive
wrong claim (still incorrect, but longer and more plausible).
"""
import json

with open('questions/ch5-5.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

pads = {}

for q in data['questions']:
    qid = q['id']
    correct_len = 0
    max_wrong = 0
    wrongs = []
    for c in q['choices']:
        tlen = len(c['tts_text'])
        if c['is_correct']:
            correct_len = tlen
        else:
            wrongs.append(c)
            if tlen > max_wrong:
                max_wrong = tlen
    diff = correct_len - max_wrong
    if diff < 10:
        continue

    # Target: pad each wrong choice to be within 10 chars of correct
    target_min = max(correct_len - 15, max_wrong)
    q_pads = {}
    for c in wrongs:
        curr_len = len(c['tts_text'])
        if curr_len >= correct_len - 10:
            continue  # Already close enough
        # Use trap_detail to build a longer version
        old_text = c['tts_text']
        trap = c.get('trap_detail', '')
        if trap:
            # Combine: keep the wrong claim and add plausible-sounding detail
            # We want to make it sound like a complete, detailed wrong answer
            new_text = old_text.rstrip('。') + '。' + trap.rstrip('。') + '。'
            # Trim if too long (shouldn't exceed correct by much)
            if len(new_text) > correct_len + 10:
                # Just use trap_detail if it's closer to target
                if abs(len(trap) - correct_len) < abs(len(new_text) - correct_len):
                    new_text = trap
            q_pads[old_text] = new_text

    if q_pads:
        pads[qid] = q_pads

# Write output
with open('questions/_pads/ch5-5.json', 'w', encoding='utf-8') as f:
    json.dump(pads, f, ensure_ascii=False, indent=2)

print(f'Generated pads for {len(pads)} questions')
total_choices = sum(len(v) for v in pads.values())
print(f'Total choice replacements: {total_choices}')

# Verify lengths
for qid, qpads in pads.items():
    for old, new in qpads.items():
        print(f'  {qid}: {len(old)} -> {len(new)}')
