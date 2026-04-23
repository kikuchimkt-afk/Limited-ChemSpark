"""
Regenerate display explanation from tts_explanation via to_display().
This removes choice-number references (選択肢N) from display explanations,
replacing them with content-based references matching the TTS side.

Usage: python _tmp/regen_display_explanation.py <chapter> [--dry-run]
"""
import json, sys, io, importlib.util
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import to_display from _restructure_chapter.py
spec = importlib.util.spec_from_file_location("restructure", "questions/_restructure_chapter.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
to_display = mod.to_display

chapter = sys.argv[1] if len(sys.argv) > 1 else 'ch1-1'
dry_run = '--dry-run' in sys.argv

path = Path(f'questions/{chapter}.json')
data = json.loads(path.read_text('utf-8'))

changed = 0
for q in data['questions']:
    new_exp = to_display(q['tts_explanation'])
    old_exp = q['explanation']
    if old_exp != new_exp:
        changed += 1
        # Show first difference
        if dry_run or True:
            # Find where they differ
            old_short = old_exp[:120]
            new_short = new_exp[:120]
            print(f"  {q['id']}:")
            if old_short != new_short:
                print(f"    OLD: {old_short}...")
                print(f"    NEW: {new_short}...")
            else:
                # Find diff later in string
                for i in range(len(min(old_exp, new_exp, key=len))):
                    if i < len(old_exp) and i < len(new_exp) and old_exp[i] != new_exp[i]:
                        start = max(0, i-30)
                        print(f"    OLD@{i}: ...{old_exp[start:i+50]}...")
                        print(f"    NEW@{i}: ...{new_exp[start:i+50]}...")
                        break
        if not dry_run:
            q['explanation'] = new_exp

print(f"\n{chapter}: {changed} explanations regenerated")

if not dry_run and changed > 0:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print("Saved.")
else:
    print("(dry-run, no changes saved)")
