"""Full dump of ch1-1.json for manual review: 
Show each question with its display text, choice lengths, and flags."""
import json, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('questions/ch1-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

LEAK_PATTERNS = [r'実際には', r'正しくは', r'のが正しい', r'これは正しい記述',
    r'ではなく', r'が正しい。', r'本来は', r'正確には']

for q in data['questions']:
    flags = []
    
    # Check leak
    for c in q['choices']:
        if c['is_correct']: continue
        for pat in LEAK_PATTERNS:
            if re.search(pat, c['text']):
                flags.append(f"LEAK:{c['choice_id']}")
                break
    
    # Check length bias
    correct_len = 0
    wrong_lens = []
    for c in q['choices']:
        if c['is_correct']:
            correct_len = len(c['text'])
        else:
            wrong_lens.append(len(c['text']))
    avg_wrong = sum(wrong_lens) / len(wrong_lens) if wrong_lens else 0
    diff = correct_len - avg_wrong
    if diff >= 10:
        flags.append(f"BIAS:+{diff:.0f}")
    
    # Check kanji nums in question
    if re.search(r'[一二三四五六七八九十]つ', q['question']):
        flags.append("KANJI_Q")
    
    flag_str = f" [{', '.join(flags)}]" if flags else ""
    
    print(f"\n{'='*70}")
    print(f"{q['id']} ({q['category']}/{q['sub_category']}) diff={q['difficulty']} type={q['question_type']}{flag_str}")
    print(f"Q: {q['question']}")
    for c in q['choices']:
        mark = "✓" if c['is_correct'] else "✗"
        print(f"  {mark} [{len(c['text']):2d}] {c['text'][:100]}")
    print(f"  Explanation({len(q['explanation'])}): {q['explanation'][:120]}...")
