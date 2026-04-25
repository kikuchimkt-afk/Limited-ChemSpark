"""Dry-run _fix_display_explanations on all chapters to see how many need syncing."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path("questions")))
from _restructure_chapter import to_display

sys.stdout.reconfigure(encoding="utf-8")

qdir = Path("questions")
chapters = sorted(f.stem for f in qdir.glob("ch[0-9]*.json") if "backup" not in f.stem)

total_all = 0
for ch in chapters:
    d = json.loads((qdir / f"{ch}.json").read_text("utf-8"))
    changed = 0
    for q in d["questions"]:
        tts_exp = q.get("tts_explanation", "")
        if not tts_exp:
            continue
        new_disp = to_display(tts_exp)
        old_disp = q.get("explanation", "")
        if old_disp != new_disp:
            changed += 1
    if changed > 0:
        print(f"{ch}: {changed} explanations need sync")
        total_all += changed
    else:
        print(f"{ch}: OK")

print(f"\nTotal: {total_all} explanations across all chapters")
