"""Check and fix display explanation for all chapters.
For each question, compares explanation to to_display(tts_explanation).
If they differ but explanation has no 選択肢N refs, safe to overwrite.
"""
import json, re, sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

spec = importlib.util.spec_from_file_location("restructure", "questions/_restructure_chapter.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
to_display = mod.to_display

chapter = sys.argv[1] if len(sys.argv) > 1 else 'ch1-4'
apply = '--apply' in sys.argv

path = Path(f'questions/{chapter}.json')
data = json.loads(path.read_text('utf-8'))

CHOICE_REF = re.compile(r'選択肢[0-9一二三四五]')

diffs = 0
has_refs = 0
for q in data['questions']:
    old = q['explanation']
    new = to_display(q['tts_explanation'])
    
    if old != new:
        diffs += 1
        old_has_ref = bool(CHOICE_REF.search(old))
        if old_has_ref:
            has_refs += 1
            print(f"  ⚠️ {q['id']}: has 選択肢N ref in explanation - SKIPPED")
        else:
            if apply:
                q['explanation'] = new
            # Show diff summary
            # Find first diff position
            for j in range(min(len(old), len(new))):
                if old[j] != new[j]:
                    s = max(0, j-20)
                    print(f"  {q['id']}:")
                    print(f"    OLD: ...{old[s:j+40]}...")
                    print(f"    NEW: ...{new[s:j+40]}...")
                    break

print(f"\n{chapter}: {diffs} explanations differ from to_display(tts_explanation)")
print(f"  - {has_refs} skipped (have 選択肢N refs)")
print(f"  - {diffs - has_refs} {'fixed' if apply else 'fixable'}")

if apply and (diffs - has_refs) > 0:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print("Saved.")
