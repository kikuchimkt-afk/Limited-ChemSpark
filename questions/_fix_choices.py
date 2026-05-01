#!/usr/bin/env python3
"""Apply choice-level content fixes from a JSON data file.

Usage:
    python questions/_fix_choices.py <chapter> [--dry-run] [--keep-audio]

Reads questions/_choice_fixes/<chapter>.json and applies text/tts_text/trap_detail
updates to matching choices in questions/<chapter>.json.

Data format (keys are choice_ids):
{
    "ch3_5_q001_c1": {
        "text": "new display text",
        "tts_text": "new tts text",
        "trap_detail": "new trap detail"
    }
}

Only specified fields are updated; omitted fields are left unchanged.
Stale audio files are deleted unless --keep-audio is passed.
"""
import json, sys, os
from pathlib import Path

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)

    chapter = args[0]
    dry_run = "--dry-run" in args
    keep_audio = "--keep-audio" in args

    root = Path(__file__).resolve().parent.parent
    q_path = root / "questions" / f"{chapter}.json"
    fix_path = root / "questions" / "_choice_fixes" / f"{chapter}.json"

    if not q_path.exists():
        print(f"ERROR: {q_path} not found"); sys.exit(1)
    if not fix_path.exists():
        print(f"ERROR: {fix_path} not found"); sys.exit(1)

    with open(q_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(fix_path, "r", encoding="utf-8") as f:
        fixes = json.load(f)

    applied = 0
    audio_deleted = 0
    stale_audio = []

    for q in data["questions"]:
        for ch in q["choices"]:
            cid = ch.get("choice_id")
            if cid not in fixes:
                continue
            fix = fixes[cid]
            changes = []
            for field in ("text", "tts_text", "trap_detail"):
                if field in fix and fix[field] != ch.get(field):
                    changes.append(field)
                    if not dry_run:
                        ch[field] = fix[field]
            if changes:
                applied += 1
                print(f"  {cid}: updated {', '.join(changes)}")
                # Mark audio for deletion if tts_text changed
                if "tts_text" in changes and not keep_audio:
                    audio_dir = root / "audio" / chapter / q["id"]
                    mp3 = audio_dir / f"{cid}.mp3"
                    if mp3.exists():
                        if not dry_run:
                            mp3.unlink()
                        audio_deleted += 1
                        stale_audio.append(str(mp3))

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Applied {applied} choice fixes.")
    if audio_deleted:
        print(f"{'Would delete' if dry_run else 'Deleted'} {audio_deleted} stale mp3 files.")
    
    # Check for fix entries that didn't match any choice
    all_cids = {ch["choice_id"] for q in data["questions"] for ch in q["choices"]}
    unmatched = set(fixes.keys()) - all_cids
    if unmatched:
        print(f"WARNING: {len(unmatched)} fix entries didn't match: {unmatched}")

    if not dry_run:
        with open(q_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Ensure trailing newline
        with open(q_path, "a", encoding="utf-8") as f:
            f.write("\n")
        print(f"Saved {q_path}")

if __name__ == "__main__":
    main()
