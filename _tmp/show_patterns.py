"""Show sample per-choice breakdown for all 4 question patterns."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

qdir = Path("questions")

# Find examples of each pattern
patterns = {
    "correct型 (trap_detailあり)": None,
    "correct型 (trap_detailなし)": None,
    "incorrect型 (trap_detailあり)": None,
    "incorrect型 (trap_detailなし)": None,
}

for ch_name in sorted(f.stem for f in qdir.glob("ch[0-9]*.json")):
    d = json.loads((qdir / f"{ch_name}.json").read_text("utf-8"))
    for q in d["questions"]:
        qtype = q.get("question_type", "correct")
        has_missing_td = any(not c.get("trap_detail") and not c.get("is_correct") for c in q["choices"])
        
        if qtype == "correct" and not has_missing_td and patterns["correct型 (trap_detailあり)"] is None:
            patterns["correct型 (trap_detailあり)"] = (ch_name, q)
        elif qtype == "correct" and has_missing_td and patterns["correct型 (trap_detailなし)"] is None:
            patterns["correct型 (trap_detailなし)"] = (ch_name, q)
        elif qtype == "incorrect" and not has_missing_td and patterns["incorrect型 (trap_detailあり)"] is None:
            patterns["incorrect型 (trap_detailあり)"] = (ch_name, q)
        elif qtype == "incorrect" and has_missing_td and patterns["incorrect型 (trap_detailなし)"] is None:
            patterns["incorrect型 (trap_detailなし)"] = (ch_name, q)

for label, data in patterns.items():
    print(f"\n{'='*70}")
    print(f"パターン: {label}")
    print(f"{'='*70}")
    if data is None:
        print("  (該当なし)")
        continue
    
    ch_name, q = data
    qtype = q.get("question_type", "correct")
    print(f"  章: {ch_name} / {q['id']} / type={qtype}")
    print(f"  Q: {q['question'][:50]}...")
    print()
    
    for i, c in enumerate(q["choices"]):
        ct = c.get("text", "")
        td = c.get("trap_detail", "")
        is_correct = c.get("is_correct", False)
        
        # Simulate JS logic
        if is_correct:
            if qtype == "incorrect":
                marker = "×"
                detail = f"{ct} → {td}" if td else f"{ct} → 誤りを含む記述。"
            else:
                marker = "○"
                detail = f"{ct} → 正解。"
        else:
            if qtype == "incorrect":
                marker = "○"
                detail = f"{ct} → {td}" if td else f"{ct} → 正しい記述。"
            else:
                marker = "×"
                detail = f"{ct} → {td}" if td else ct
        
        has_td_mark = "✓" if td else "✗"
        print(f"  選択肢{i+1} {marker} [td:{has_td_mark}] {detail[:80]}")
    print()
