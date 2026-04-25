"""Check quality of per-choice breakdown data across all chapters.
Report: questions where trap_detail is missing for wrong choices."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

qdir = Path("questions")
chapters = sorted(f.stem for f in qdir.glob("ch[0-9]*.json") if "backup" not in f.stem)

grand_total = 0
grand_missing = 0
grand_fallback_text = 0  # wrong choices showing choice text as fallback
grand_fallback_correct = 0  # incorrect-type distractors showing "この記述は正しい"

for ch in chapters:
    d = json.loads((qdir / f"{ch}.json").read_text("utf-8"))
    ch_missing_text = 0
    ch_missing_correct = 0
    for q in d["questions"]:
        qtype = q.get("question_type", "correct")
        for c in q["choices"]:
            if c.get("is_correct"):
                continue
            grand_total += 1
            if not c.get("trap_detail"):
                if qtype == "incorrect":
                    ch_missing_correct += 1
                    grand_fallback_correct += 1
                else:
                    ch_missing_text += 1
                    grand_fallback_text += 1
                grand_missing += 1
    
    if ch_missing_text > 0 or ch_missing_correct > 0:
        print(f"{ch}: correct型でtrap_detail欠損={ch_missing_text}, incorrect型ダミー正解={ch_missing_correct}")

print(f"\n{'='*60}")
print(f"全チャプター合計:")
print(f"  不正解選択肢 合計: {grand_total}")
print(f"  trap_detail あり:  {grand_total - grand_missing} ({(grand_total - grand_missing)/grand_total*100:.1f}%)")
print(f"  trap_detail なし:  {grand_missing} ({grand_missing/grand_total*100:.1f}%)")
print(f"    → correct型で欠損（選択肢テキストで代替表示）: {grand_fallback_text}")
print(f"    → incorrect型ダミー正解（「この記述は正しい」表示）: {grand_fallback_correct}")
