"""Merge ch4-1 pad batch files into a single _pads/ch4-1.json."""
import json, pathlib

pads_dir = pathlib.Path(__file__).resolve().parent.parent / "questions" / "_pads"
merged = {}

for i in range(1, 6):
    batch = pads_dir / f"ch4-1_batch{i}.json"
    if batch.exists():
        with open(batch, encoding="utf-8") as f:
            data = json.load(f)
        for qid, mappings in data.items():
            if qid in merged:
                merged[qid].update(mappings)
            else:
                merged[qid] = dict(mappings)

out = pads_dir / "ch4-1.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"Merged {len(merged)} questions into {out}")
total = sum(len(v) for v in merged.values())
print(f"Total choice rewrites: {total}")

# Clean up batch files
for i in range(1, 6):
    batch = pads_dir / f"ch4-1_batch{i}.json"
    if batch.exists():
        batch.unlink()
        print(f"Deleted {batch.name}")
