"""Check display explanation for consistency issues in ch1-4."""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ch = sys.argv[1] if len(sys.argv) > 1 else 'ch1-4'
d = json.loads(open(f'questions/{ch}.json', 'r', encoding='utf-8').read())

issues = []
for i, q in enumerate(d['questions']):
    exp = q['explanation']
    qid = q['id']
    
    # Find kanji numerals in explanation (display field should use Arabic)
    # But 選択肢N references are OK (app remaps them)
    # Check for mixed formats like 二十二・4 or 十二・〇1
    mixed = re.findall(r'[一二三四五六七八九十百千]+[・〇一二三四五六七八九]*[0-9]+|[0-9]+[・〇一二三四五六七八九十百千]+', exp)
    
    # Check for kanji numbers that should be display (Arabic) 
    # Exclude 選択肢N context
    exp_no_ref = re.sub(r'選択肢[一二三四0-9]+', '', exp)
    kanji_nums = re.findall(r'[一二三四五六七八九十百千][・〇一二三四五六七八九十百千]+', exp_no_ref)
    
    # Check for full-width dots with kanji (decimal numbers in kanji like 六・〇二)
    kanji_decimal = re.findall(r'[一二三四五六七八九十百千]+・[〇一二三四五六七八九]+', exp)
    
    if mixed or kanji_nums or kanji_decimal:
        issues.append((qid, i+1))
        print(f"Q{i+1:03d} [{qid}]:")
        if mixed:
            print(f"  MIXED: {mixed}")
        if kanji_decimal:
            print(f"  KANJI DECIMAL: {kanji_decimal}")
        # Show the explanation with context
        # Find positions
        for m in re.finditer(r'[一二三四五六七八九十百千・〇]+', exp):
            span = m.group()
            if len(span) >= 2 and not re.match(r'^[一二三四]$', span):
                start = max(0, m.start()-15)
                end = min(len(exp), m.end()+15)
                print(f"    ...{exp[start:end]}...")

print(f"\nTotal issues: {len(issues)}/{len(d['questions'])}")
