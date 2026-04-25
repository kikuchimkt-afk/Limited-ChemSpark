"""Preview generated trap_details for a few questions."""
import json, sys, re
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "questions")
from _add_distractor_details import generate_trap_detail

qdir = Path("questions")
count = 0

for ch_name in ['ch1-1', 'ch2-1', 'ch3-4', 'ch5-3']:
    d = json.loads((qdir / f"{ch_name}.json").read_text("utf-8"))
    for q in d["questions"]:
        if q.get("question_type") != "incorrect":
            continue
        
        has_missing = any(not c.get("is_correct") and not c.get("trap_detail") for c in q["choices"])
        if not has_missing:
            continue
        
        print(f"\n{'='*70}")
        print(f"{ch_name} / {q['id']}")
        print(f"Q: {q['question'][:60]}...")
        print(f"解説: {q.get('tts_explanation','')[:100]}...")
        print()
        
        for i, c in enumerate(q["choices"]):
            is_correct = c.get("is_correct", False)
            td = c.get("trap_detail", "")
            
            if is_correct:
                marker = "×(答え)"
                detail_display = td or "(既存)"
            elif td:
                marker = "○(既存td)"
                detail_display = td[:60]
            else:
                marker = "○(生成)"
                generated = generate_trap_detail(c, q, q["choices"])
                detail_display = generated
            
            print(f"  {i+1}. {marker}: {detail_display}")
        
        count += 1
        if count >= 8:
            break
    if count >= 8:
        break
