"""Generic chapter display fixer:
1. _audit_display.py --apply for question/choices
2. Fix explanation display fields (kanji counters, katakana alpha, formulas, numbers)
3. Run _check_all.py validation

Usage: python _tmp/fix_chapter_display.py <chapter>
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chapter = sys.argv[1] if len(sys.argv) > 1 else 'ch1-2'

sys.path.insert(0, str(Path('questions')))
from _restructure_chapter import (
    _convert_numbers, _convert_standalone_numbers, _convert_formulas,
    _convert_kanji_counters, _convert_katakana_alpha
)

JSON_PATH = Path(f'questions/{chapter}.json')
data = json.loads(JSON_PATH.read_text('utf-8'))

print(f"Fixing explanation display fields for {chapter}...")
exp_changes = 0
for q in data['questions']:
    old = q['explanation']
    new = old
    new = _convert_numbers(new)
    new = _convert_standalone_numbers(new)
    new = _convert_formulas(new)
    new = _convert_kanji_counters(new)
    new = _convert_katakana_alpha(new)
    
    if new != old:
        exp_changes += 1
        for i in range(min(len(old), len(new))):
            if old[i] != new[i]:
                s = max(0, i-15)
                e = min(len(old), i+30)
                print(f"  {q['id']}: ...{old[s:e]}...")
                print(f"        → ...{new[s:min(len(new),i+30)]}...")
                break
        q['explanation'] = new

# Verify no false positives
BAD = ['単1', '1定', '均1', '1般', '1方', '1見', '不1', '1切', '1連', '同1', '1致']
fps = 0
for q in data['questions']:
    for bp in BAD:
        if bp in q['explanation']:
            print(f"  ⚠️ FALSE POSITIVE: {q['id']} exp contains '{bp}'")
            fps += 1

JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding='utf-8')
print(f"\nFixed {exp_changes} explanations, {fps} false positives")
print("Saved.")
