"""Regenerate display explanation from tts_explanation using to_display().
This eliminates 選択肢N references from the display explanation,
making it consistent with the audio narration."""
import json, sys, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _restructure_chapter import to_display

def fix_explanations(chapter: str, dry_run: bool) -> int:
    path = Path(__file__).with_name(f"{chapter}.json")
    data = json.loads(path.read_text("utf-8"))
    
    changed = 0
    for q in data["questions"]:
        tts_exp = q.get("tts_explanation", "")
        if not tts_exp:
            continue
        new_disp = to_display(tts_exp)
        old_disp = q.get("explanation", "")
        if old_disp != new_disp:
            changed += 1
            if not dry_run:
                q["explanation"] = new_disp
    
    if dry_run:
        print(f"[dry-run] {changed} explanations would be updated in {chapter}.json")
    else:
        if changed:
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        print(f"Updated {changed} explanations in {chapter}.json")
    
    return changed

def main():
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    fix_explanations(args.chapter, args.dry_run)

if __name__ == "__main__":
    main()
