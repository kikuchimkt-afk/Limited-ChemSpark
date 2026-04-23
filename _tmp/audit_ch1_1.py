"""Audit ch1-1.json for four issues"""
import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('questions/ch1-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

LEAK_PATTERNS = [
    r'実際には', r'正しくは', r'のが正しい', r'これは正しい記述',
    r'ではなく', r'が正しい。', r'本来は', r'正確には',
]

print("=" * 80)
print("AUDIT REPORT: ch1-1.json")
print("=" * 80)

# 1. Answer leaking
print("\n## 1. 誤答に正答リーク")
leak_count = 0
for q in data['questions']:
    for c in q['choices']:
        if c['is_correct']:
            continue
        for pat in LEAK_PATTERNS:
            if re.search(pat, c['text']):
                print(f"  {q['id']} {c['choice_id']}: [{pat}]")
                print(f"    text: {c['text'][:100]}")
                leak_count += 1
                break
print(f"  Total: {leak_count}")

# 2. Length bias (diff >= 10)
print("\n## 2. 長さバイアス (diff >= 10)")
bias_count = 0
for q in data['questions']:
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
        bias_count += 1
        print(f"  {q['id']}: correct={correct_len}, avg_wrong={avg_wrong:.0f}, diff={diff:+.0f}")
        print(f"    正答: {q['choices'][[i for i,c in enumerate(q['choices']) if c['is_correct']][0]]['text'][:80]}")
print(f"  Total: {bias_count}")

# 3. Kanji numerals in display fields
print("\n## 3. 漢数字がdisplay用フィールドに使用")
kanji_count = 0
# Specifically looking for kanji numbers as quantities in display text
KANJI_QTY = re.compile(r'([一二三四五六七八九十]+)(種類|個|本|回|倍|番|つ|段階|次|成分|方|枚|群|層|名)')
KANJI_ORDINAL = re.compile(r'(第[一二三四五六七八九十]+)')

for q in data['questions']:
    fields = [
        ('question', q['question']),
        ('explanation', q['explanation']),
    ]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    
    for fname, text in fields:
        # Check for kanji quantities
        m = KANJI_QTY.findall(text)
        if m:
            kanji_count += 1
            print(f"  {q['id']} {fname}: {[''.join(x) for x in m]}")
            print(f"    -> {text[:80]}")
        # Check for kanji ordinals in display
        m2 = KANJI_ORDINAL.findall(text)
        if m2:
            kanji_count += 1
            print(f"  {q['id']} {fname} ordinal: {m2}")

print(f"  Total: {kanji_count}")

# 4. Display fields that should use Arabic but use 漢数字 instead
# Look for patterns like 四つ, 三本, 二種 etc. in question/explanation/choice text
print("\n## 4. 「四つの」「三つの」等、display用に漢数字＋助数詞")
counter_count = 0
DISPLAY_KANJI_NUM = re.compile(r'[一二三四五六七八九十]つの|[一二三四五六七八九十]組の')
for q in data['questions']:
    fields = [('question', q['question']), ('explanation', q['explanation'])]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    for fname, text in fields:
        m = DISPLAY_KANJI_NUM.findall(text)
        if m:
            counter_count += 1
            print(f"  {q['id']} {fname}: {m} -> {text[:80]}")
print(f"  Total: {counter_count}")

# 5. Check for 「度」 pattern (should be ℃ in display)
print("\n## 5. 「度」が表示用でも使われている (℃ であるべき)")
degree_count = 0
# Pattern: number + 度 (temperature context)
DEGREE_PAT = re.compile(r'\d+度(?!合|数)')
for q in data['questions']:
    fields = [('question', q['question']), ('explanation', q['explanation'])]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    for fname, text in fields:
        m = DEGREE_PAT.findall(text)
        if m:
            degree_count += 1
            print(f"  {q['id']} {fname}: {m} in: {text[:80]}")
print(f"  Total: {degree_count}")

# 6. Check question text for patterns like 「四つのうち」==> should be 「4つのうち」
print("\n## 6. question text の漢数字パターン検出")
q_kanji_count = 0
Q_KANJI = re.compile(r'[一二三四五六七八九十]つ|四つ|三つ|二つ')
for q in data['questions']:
    text = q['question']
    m = Q_KANJI.findall(text)
    if m:
        q_kanji_count += 1
        print(f"  {q['id']}: {m} -> {text}")
print(f"  Total: {q_kanji_count}")

print("\n" + "=" * 80)
