"""Audit ch1-1.json for katakana alphabet in display fields.
Display fields should use actual alphabet letters, not katakana readings.
e.g. エヌ→N, エス→S, シー→C, オー→O, ピー→P, ケー→K
"""
import json, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('questions/ch1-1.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Katakana-to-alphabet mapping for element symbols and common abbreviations
# These are katakana representations that should be actual alphabet in display
KATA_ALPHA = {
    'エー': 'A', 'ビー': 'B', 'シー': 'C', 'ディー': 'D',
    'イー': 'E', 'エフ': 'F', 'ジー': 'G', 'エイチ': 'H',
    'アイ': 'I', 'ジェイ': 'J', 'ケー': 'K', 'エル': 'L',
    'エム': 'M', 'エヌ': 'N', 'オー': 'O', 'ピー': 'P',
    'キュー': 'Q', 'アール': 'R', 'エス': 'S', 'ティー': 'T',
    'ユー': 'U', 'ブイ': 'V', 'ダブリュー': 'W', 'エックス': 'X',
    'ワイ': 'Y', 'ゼット': 'Z',
}

# Specific patterns we expect in chemistry context (element symbol readings in display)
# These are patterns that indicate TTS-style katakana is used in display
CHEM_KATA_PATTERNS = [
    # Element symbol readings
    (r'エス・シー・オー・ピー', 'S・C・O・P (SCOP)'),
    (r'エスシーオーピー', 'SCOP'),
    (r'エヌエー', 'Na'),
    (r'ケーシーエル', 'KCl'),
    (r'エイチシーエル', 'HCl'),
    (r'エヌエイチ', 'NH'),
    (r'シーオー', 'CO'),
    (r'エスアイ', 'Si'),
    (r'ピーエイチ', 'pH'),
    # Individual letter readings that might appear
    (r'(?<![ァ-ン])エス(?![ァ-ヴー])', 'S'),  # standalone エス
    (r'(?<![ァ-ン])シー(?![ァ-ヴー])', 'C'),  # standalone シー  
    (r'(?<![ァ-ン])オー(?![ァ-ヴー])', 'O'),  # standalone オー
    (r'(?<![ァ-ン])ピー(?![ァ-ヴー])', 'P'),  # standalone ピー
    (r'(?<![ァ-ン])ケー(?![ァ-ヴー])', 'K'),  # standalone ケー
    (r'(?<![ァ-ン])エヌ(?![ァ-ヴー])', 'N'),  # standalone エヌ
    (r'(?<![ァ-ン])エル(?![ァ-ヴー])', 'L'),  # standalone エル
]

# Check all display fields
print("=" * 80)
print("KATAKANA ALPHABET AUDIT: ch1-1.json")
print("=" * 80)

# First, let's just look for any katakana sequences in display fields
# that look like alphabet readings
print("\n## Pattern-based search")
found_count = 0
for q in data['questions']:
    fields = [
        ('question', q['question']),
        ('explanation', q['explanation']),
    ]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    
    for fname, text in fields:
        for pattern, replacement in CHEM_KATA_PATTERNS:
            m = re.search(pattern, text)
            if m:
                found_count += 1
                print(f"  {q['id']} {fname}: [{m.group()}→{replacement}]")
                print(f"    context: ...{text[max(0,m.start()-10):m.end()+20]}...")

print(f"\n  Total pattern matches: {found_count}")

# More targeted: look for 「エス・シー・オー・ピー」pattern specifically (SCOP)
print("\n## SCOP related")
scop_count = 0
for q in data['questions']:
    fields = [
        ('question', q['question']),
        ('explanation', q['explanation']),
    ]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    
    for fname, text in fields:
        if 'エス' in text or 'シー' in text or 'オー' in text or 'ピー' in text:
            # But filter out common Japanese words
            # シーズン, オーバー, ピース etc should be excluded
            # Let's check for chemistry context
            if any(w in text for w in ['元素記号', 'スコップ', '頭文字', 'SCOP', '同素体']):
                scop_count += 1
                print(f"  {q['id']} {fname}:")
                print(f"    {text[:120]}")

print(f"\n  Total SCOP context: {scop_count}")

# Now let's do a broader check: any katakana that could be letter readings
print("\n## Broad katakana letter check in explanations")
# Check specifically for patterns like 「エス・シー・オー・ピー」
BROAD_PATTERNS = [
    r'エス・シー・オー・ピー',
    r'[エス|シー|オー|ピー|ケー|エヌ|エル|エイチ|エフ|ジー|ティー|ブイ|ダブリュー|エックス|ワイ|ゼット]',
]

for q in data['questions']:
    text = q['explanation']
    if 'エス・シー・オー・ピー' in text:
        print(f"  {q['id']} explanation contains 'エス・シー・オー・ピー'")
        print(f"    {text[:150]}")

# Check for display fields that suspiciously look like TTS
# i.e., explanation has katakana element names where formulas should be
print("\n## Display fields with TTS-style element symbol readings")
for q in data['questions']:
    fields = [
        ('explanation', q['explanation']),
    ]
    for c in q['choices']:
        fields.append((f"choice {c['choice_id']}", c['text']))
    
    for fname, text in fields:
        # 「エス・シー・オー・ピー」 should be 「S・C・O・P」 in display
        if 'エス・シー・オー・ピー' in text:
            print(f"  {q['id']} {fname}: エス・シー・オー・ピー → S・C・O・P")
            
print("\n" + "=" * 80)
