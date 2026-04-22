"""Dump all questions for manual review."""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ch = sys.argv[1] if len(sys.argv) > 1 else 'ch1-4'
d = json.loads(open(f'questions/{ch}.json', 'r', encoding='utf-8').read())
for i, q in enumerate(d['questions']):
    print(f"={'='*70}")
    print(f"Q{i+1:03d} [{q['id']}]  type={q['question_type']}  diff={q['difficulty']}")
    print(f"  cat={q['category']} / {q['sub_category']}")
    print(f"  Q: {q['question']}")
    for c in q['choices']:
        mark = '★' if c['is_correct'] else ' '
        print(f"  [{mark}] {c['label']}: {c['text']}")
        if c.get('trap_type'):
            print(f"       trap: {c['trap_type']} - {c.get('trap_detail','')}")
    print(f"  EXP: {q['explanation']}")
    # Check display explanation for mixed numerals
    exp = q['explanation']
    import re
    kanji_in_exp = re.findall(r'[一二三四五六七八九十百千]+[・〇一二三四五六七八九]+', exp)
    if kanji_in_exp:
        print(f"  ⚠️ MIXED NUMERALS in explanation: {kanji_in_exp}")
    arabic_mixed = re.findall(r'[0-9]+[・〇一二三四五六七八九]+|[一二三四五六七八九十百千]+[0-9]+', exp)
    if arabic_mixed:
        print(f"  ⚠️ MIXED ARABIC/KANJI in explanation: {arabic_mixed}")
