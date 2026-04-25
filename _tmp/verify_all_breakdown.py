"""Simulate the JS per-choice breakdown logic for EVERY question in EVERY chapter.
Check for:
1. Empty/blank detail text
2. Missing choice text
3. Logic errors (wrong marker for question type)
4. Redundant display
5. Sample output for manual review
"""
import json, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

qdir = Path("questions")
chapters = sorted(f.stem for f in qdir.glob("ch[0-9]*.json") if "backup" not in f.stem)

issues = []
samples = {}  # chapter -> list of sample outputs

for ch in chapters:
    d = json.loads((qdir / f"{ch}.json").read_text("utf-8"))
    ch_samples = []

    for q in d["questions"]:
        qid = q["id"]
        qtype = q.get("question_type", "correct")
        # The JS uses q.type but the JSON field is question_type
        # Check: does app.js read "type" or "question_type"?
        choices = q["choices"]

        for i, c in enumerate(choices):
            ct = c.get("text", "")
            td = c.get("trap_detail", "")
            is_correct = c.get("is_correct", False)

            # Simulate JS logic
            if is_correct:
                if qtype == "incorrect":
                    marker = "×"
                    detail = f"{ct} → {td}" if td else f"{ct} → 誤りを含む記述。"
                    css = "wrong"
                else:
                    marker = "○"
                    detail = f"{ct} → 正解。"
                    css = "correct"
            else:
                if qtype == "incorrect":
                    marker = "○"
                    detail = f"{ct} → {td}" if td else f"{ct} → 正しい記述。"
                    css = "correct"
                else:
                    marker = "×"
                    detail = f"{ct} → {td}" if td else ct
                    css = "wrong"

            # CHECK 1: empty detail
            if not detail or detail.strip() == "":
                issues.append((ch, qid, f"c{i+1}", "EMPTY detail"))

            # CHECK 2: empty choice text
            if not ct or ct.strip() == "":
                issues.append((ch, qid, f"c{i+1}", "EMPTY choice text"))

            # CHECK 3: marker consistency
            if qtype == "correct":
                if is_correct and marker != "○":
                    issues.append((ch, qid, f"c{i+1}", f"correct型正解 marker={marker} should be ○"))
                if not is_correct and marker != "×":
                    issues.append((ch, qid, f"c{i+1}", f"correct型不正解 marker={marker} should be ×"))
            elif qtype == "incorrect":
                if is_correct and marker != "×":
                    issues.append((ch, qid, f"c{i+1}", f"incorrect型答え marker={marker} should be ×"))
                if not is_correct and marker != "○":
                    issues.append((ch, qid, f"c{i+1}", f"incorrect型ダミー marker={marker} should be ○"))

            # CHECK 4: detail too short (< 5 chars)
            if len(detail) < 5:
                issues.append((ch, qid, f"c{i+1}", f"detail too short: '{detail}'"))

            # CHECK 5: correct型で trap_detail なし不正解 → choice textのみ表示（解説なし）
            if qtype == "correct" and not is_correct and not td:
                issues.append((ch, qid, f"c{i+1}", f"correct型不正解でtrap_detailなし → テキストのみ: {ct[:40]}"))

        # Collect samples (first 2 per chapter)
        if len(ch_samples) < 2:
            lines = [f"--- {qid} (type={qtype}) ---"]
            lines.append(f"Q: {q.get('question','')[:60]}...")
            for i, c in enumerate(choices):
                ct = c.get("text", "")
                td = c.get("trap_detail", "")
                is_correct = c.get("is_correct", False)
                if is_correct:
                    if qtype == "incorrect":
                        m, d2 = "×", f"{ct} → {td}" if td else f"{ct} → 誤りを含む記述。"
                    else:
                        m, d2 = "○", f"{ct} → 正解。"
                else:
                    if qtype == "incorrect":
                        m, d2 = "○", f"{ct} → {td}" if td else f"{ct} → 正しい記述。"
                    else:
                        m, d2 = "×", f"{ct} → {td}" if td else ct
                lines.append(f"  選択肢{i+1} {m} {d2[:80]}")
            ch_samples.append("\n".join(lines))

    samples[ch] = ch_samples

# Report
print("=" * 70)
print("ISSUE REPORT")
print("=" * 70)
if not issues:
    print("NO ISSUES FOUND ✅")
else:
    # Group by type
    from collections import Counter
    type_counts = Counter(i[3].split(":")[0].split("→")[0].strip() for i in issues)
    for typ, cnt in type_counts.most_common():
        print(f"  {typ}: {cnt} 件")
    print(f"\n  合計: {len(issues)} 件")
    print()
    # Show first few of each type
    seen_types = set()
    for ch, qid, cid, msg in issues[:20]:
        print(f"  {ch}/{qid}/{cid}: {msg[:80]}")

print()
print("=" * 70)
print("SAMPLE OUTPUT (2 questions per chapter)")
print("=" * 70)
for ch in chapters:
    for s in samples.get(ch, []):
        print(s)
        print()
