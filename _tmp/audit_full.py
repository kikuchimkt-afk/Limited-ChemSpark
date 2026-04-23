"""Audit ch1-X for all four issue types with full context.
Shows the actual text so manual verification is possible.
Usage: python _tmp/audit_full.py <chapter>
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
chapter = sys.argv[1] if len(sys.argv) > 1 else 'ch1-3'

sys.path.insert(0, str(Path('questions')))
from _restructure_chapter import to_display

JSON_PATH = Path(f'questions/{chapter}.json')
data = json.loads(JSON_PATH.read_text('utf-8'))

LEAK_PATTERNS = [r'実際には', r'正しくは', r'のが正しい', r'これは正しい記述',
    r'ではなく', r'が正しい。', r'本来は', r'正確には']

# Kanji patterns to detect in display fields (including explanation)
KANJI_QTY = re.compile(r'(?<![単均唯定不同一])([一二三四五六七八九十]+)(種類|つ|つの|つ折り)')
KANJI_ORD = re.compile(r'第([一二三四五六七八九十]+)(?=[にの章節])')
KANJI_MULTI = re.compile(r'[一二三四五六七八九十百千]{2,}')  # multi-digit standalone
KATA_ALPHA = re.compile(r'エス・シー・オー・ピー|ケー村')

print("=" * 80)
print(f"FULL AUDIT: {chapter}")
print("=" * 80)

# 1. LEAK
print("\n## 1. 誤答に正答リーク")
leak_count = 0
for q in data['questions']:
    for c in q['choices']:
        if c['is_correct']: continue
        for pat in LEAK_PATTERNS:
            if re.search(pat, c['text']):
                leak_count += 1
                print(f"\n  {q['id']} {c['choice_id']} [{pat}]:")
                print(f"    TEXT: {c['text']}")
                break
print(f"  → Total: {leak_count}")

# 2. DISPLAY MISMATCH (to_display vs actual)
print("\n## 2. to_display() ミスマッチ (question/choices)")
disp_count = 0
for q in data['questions']:
    tts_q = q.get('tts_question', '')
    exp_q = to_display(tts_q)
    if q['question'] != exp_q:
        disp_count += 1
        print(f"\n  {q['id']} question:")
        print(f"    ACTUAL: {q['question']}")
        print(f"    EXPECT: {exp_q}")
    for c in q['choices']:
        tts_t = c.get('tts_text', '')
        exp_t = to_display(tts_t)
        if c['text'] != exp_t:
            disp_count += 1
            print(f"\n  {q['id']} {c['choice_id']}:")
            print(f"    ACTUAL: {c['text']}")
            print(f"    EXPECT: {exp_t}")
print(f"  → Total: {disp_count}")

# 3. EXPLANATION の漢数字・カタカナ
print("\n## 3. Explanation の漢数字量詞・カタカナアルファベット")
exp_issues = 0
for q in data['questions']:
    text = q['explanation']
    issues = []
    
    m = KANJI_QTY.findall(text)
    if m:
        issues.append(f"漢数字量詞: {[''.join(x) for x in m]}")
    m = KANJI_ORD.findall(text)
    if m:
        issues.append(f"漢数字序数: 第{'、第'.join(m)}")
    m = KATA_ALPHA.findall(text)
    if m:
        issues.append(f"カタカナα: {m}")
    # Multi-digit kanji numbers
    m = KANJI_MULTI.findall(text)
    if m:
        # Filter out compound words
        real = [x for x in m if x not in ['一定', '一般', '一方', '一見', '一切', '一連', '一致', '同一', '均一', '単一', '不一致', '定比例']]
        if real:
            issues.append(f"多桁漢数字: {real}")
    
    if issues:
        exp_issues += 1
        print(f"\n  {q['id']}: {'; '.join(issues)}")
        print(f"    EXP: {text[:120]}...")
print(f"  → Total: {exp_issues}")

# 4. LENGTH BIAS
print("\n## 4. 長さバイアス (correct - max_wrong >= 10)")
bias_count = 0
for q in data['questions']:
    correct = next(c for c in q['choices'] if c['is_correct'])
    wrongs = [c for c in q['choices'] if not c['is_correct']]
    cl = len(correct['text'])
    max_wl = max(len(c['text']) for c in wrongs)
    if cl > max_wl and cl - max_wl >= 10:
        bias_count += 1
        print(f"\n  {q['id']}: correct={cl}, max_wrong={max_wl}, diff=+{cl-max_wl}")
        print(f"    正答: {correct['text'][:80]}")
        for w in wrongs:
            print(f"    誤答[{len(w['text']):2d}]: {w['text'][:80]}")
print(f"  → Total: {bias_count}")

print("\n" + "=" * 80)
print(f"SUMMARY: leak={leak_count}, disp_mismatch={disp_count}, exp_kanji={exp_issues}, bias={bias_count}")
print("=" * 80)
