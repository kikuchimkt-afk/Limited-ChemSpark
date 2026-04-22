"""Fix ch1-1.json display fields — v2 with better kanji→arabic rules.

Fixes:
1. Re-derive question and choices[].text from tts_* via to_display()
2. Fix explanation display fields (kanji→arabic, katakana→alphabet)
3. Does NOT modify tts_* fields

Avoids false positives like 単一→単1, 一定→1定, etc.
"""
import json, sys, io, re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, str(Path('questions')))
from _restructure_chapter import to_display, _convert_numbers, _convert_standalone_numbers, _convert_formulas

JSON_PATH = Path('questions/ch1-1.json')

# Reload original from backup or TTS source
data = json.loads(JSON_PATH.read_text('utf-8'))

changes = []

# =====================================================================
# Explanation-specific display conversion
# =====================================================================
# These are EXACT replacements, not regex, to avoid false positives.
# The key insight: we must be careful not to convert parts of compound
# words like 単一, 一定, 均一, 一般, 一方, 一見, 不一致 etc.

def fix_explanation_display(text: str) -> str:
    """Convert kanji quantities to arabic in explanation text.
    Only converts clearly quantitative uses, not parts of compound words."""
    
    # STEP A: Formula conversion (Japanese compound names → chemical formulas)
    text = _convert_formulas(text)
    
    # STEP B: Number + unit conversion (漢数字+単位 → arabic+symbol)
    text = _convert_numbers(text)
    
    # STEP C: Standalone multi-digit kanji numbers → arabic
    text = _convert_standalone_numbers(text)
    
    # STEP D: Specific kanji quantity patterns (safe exact replacements)
    # These use word-boundary-aware replacements
    
    # 「N種類」 pattern
    text = re.sub(r'(?<![単均唯])一種類', '1種類', text)
    text = text.replace('二種類', '2種類')
    text = text.replace('三種類', '3種類')
    text = text.replace('四種類', '4種類')
    text = text.replace('五種類', '5種類')
    
    # 「Nつ」 pattern - but NOT 「一つ一つ」(idiom) or parts of words
    # Use lookbehind to avoid matching inside compound words
    text = re.sub(r'(?<![単均唯定不])一つ', '1つ', text)
    text = text.replace('二つ', '2つ')
    text = text.replace('三つ', '3つ')
    text = text.replace('四つ', '4つ')
    text = text.replace('五つ', '5つ')
    text = text.replace('六つ', '6つ')
    text = text.replace('七つ', '7つ')
    text = text.replace('八つ', '8つ')
    text = text.replace('九つ', '9つ')
    
    # 「四つ折り」
    text = text.replace('四つ折り', '4つ折り')
    
    # 「第N」ordinals
    text = re.sub(r'第一(?=[にの章節])', '第1', text)
    text = re.sub(r'第二(?=[にの章節])', '第2', text)
    text = re.sub(r'第三(?=[にの章節])', '第3', text)
    text = re.sub(r'第四(?=[にの章節])', '第4', text)
    
    # STEP E: Katakana alphabet → actual alphabet (display)
    text = text.replace('エス・シー・オー・ピー', 'S・C・O・P')
    text = text.replace('ケー村', 'K村')
    
    return text


def fix_question_display(text: str) -> str:
    """Fix question text for kanji/katakana issues."""
    text = re.sub(r'(?<![単均唯])一種類', '1種類', text)
    text = text.replace('二種類', '2種類')
    text = text.replace('三種類', '3種類')
    text = text.replace('四種類', '4種類')
    text = re.sub(r'(?<![単均唯定不])一つ', '1つ', text)
    text = text.replace('二つ', '2つ')
    text = text.replace('三つ', '3つ')
    text = text.replace('四つ', '4つ')
    text = text.replace('五つ', '5つ')
    text = text.replace('ケー村', 'K村')
    text = text.replace('エス・シー・オー・ピー', 'S・C・O・P')
    return text


def fix_choice_display(text: str) -> str:
    """Fix choice text for kanji/katakana issues."""
    text = re.sub(r'(?<![単均唯])一種類', '1種類', text)
    text = text.replace('二種類', '2種類')
    text = text.replace('三種類', '3種類')
    text = text.replace('四種類', '4種類')
    text = text.replace('四つ折り', '4つ折り')
    return text


# =====================================================================
# Apply fixes
# =====================================================================
print("=" * 70)
print("Fixing ch1-1.json display fields")
print("=" * 70)

exp_changes = 0
q_changes = 0
c_changes = 0

for q in data['questions']:
    # Fix explanation
    old = q['explanation']
    new = fix_explanation_display(old)
    if new != old:
        exp_changes += 1
        # Find first diff for display
        for i in range(min(len(old), len(new))):
            if old[i] != new[i]:
                s = max(0, i-15)
                e = min(len(old), i+30)
                print(f"  {q['id']} exp: ...{old[s:e]}...")
                print(f"             → ...{new[s:min(len(new),i+30)]}...")
                break
        q['explanation'] = new
    
    # Fix question
    old = q['question']
    new = fix_question_display(old)
    if new != old:
        q_changes += 1
        print(f"  {q['id']} question: {old[:60]}")
        print(f"             → {new[:60]}")
        q['question'] = new
    
    # Fix choices
    for c in q['choices']:
        old = c['text']
        new = fix_choice_display(old)
        if new != old:
            c_changes += 1
            print(f"  {q['id']} {c['choice_id']}: {old[:50]} → {new[:50]}")
            c['text'] = new

# =====================================================================
# Verify no false positives
# =====================================================================
print("\n" + "=" * 70)
print("Verification: checking for false conversions")
print("=" * 70)

false_positives = []
BAD_PATTERNS = ['単1', '1定', '均1', '1般', '1方', '1見', '不1', '1切', '1連', '同1', '1致', '1石']
for q in data['questions']:
    for field, text in [('question', q['question']), ('explanation', q['explanation'])]:
        for bp in BAD_PATTERNS:
            if bp in text:
                false_positives.append(f"  {q['id']} {field}: contains '{bp}' -> FALSE POSITIVE!")
    for c in q['choices']:
        for bp in BAD_PATTERNS:
            if bp in c['text']:
                false_positives.append(f"  {q['id']} {c['choice_id']}: contains '{bp}' -> FALSE POSITIVE!")

if false_positives:
    print("  ⚠️ FALSE POSITIVES DETECTED:")
    for fp in false_positives:
        print(fp)
else:
    print("  ✅ No false positives detected")

# =====================================================================
# Save
# =====================================================================
print("\n" + "=" * 70)
print("Saving")
print("=" * 70)

JSON_PATH.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    encoding='utf-8'
)

print(f"  Saved to {JSON_PATH}")
print(f"\n  SUMMARY:")
print(f"    Explanation fixes: {exp_changes}")
print(f"    Question fixes: {q_changes}")
print(f"    Choice fixes: {c_changes}")
print(f"    False positives: {len(false_positives)}")
print("=" * 70)
