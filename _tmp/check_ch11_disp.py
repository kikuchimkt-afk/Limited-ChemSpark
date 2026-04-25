"""Count 選択肢N references in display explanation across all ch1-1 questions."""
import json, pathlib, sys, re
sys.stdout.reconfigure(encoding="utf-8")

fp = pathlib.Path("questions/ch1-1.json")
data = json.loads(fp.read_text(encoding="utf-8"))

affected = []
for q in data["questions"]:
    qid = q["id"]
    disp = q.get("explanation", "")
    refs = re.findall(r'選択肢[1-4一二三四]', disp)
    if refs:
        affected.append((qid, len(refs), disp))

print(f"ch1-1: {len(affected)}/{len(data['questions'])} questions have 選択肢N in display explanation")
print()

for qid, cnt, disp in affected:
    print(f"--- {qid} ({cnt} refs) ---")
    print(disp)
    print()
