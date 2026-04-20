import json
import os

target_file = os.path.join("questions", "ch6-3.json")
pads_file = os.path.join("questions", "_pads", "ch6-3.json")

def normalize(text):
    return text.replace(" ", "").replace("　", "")

with open(target_file, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(pads_file, "r", encoding="utf-8") as f:
    pads = json.load(f)

modified = 0

for q in data["questions"]:
    qid = q["id"]
    if qid in pads:
        for c in q["choices"]:
            if not c.get("is_correct", False):
                orig_text = normalize(c["text"])
                for pk, pv in pads[qid].items():
                    norm_pk = normalize(pk)
                    # 前方一致もしくは包含でマッチした場合に上書き
                    prefix_len = min(5, len(norm_pk))
                    if orig_text == norm_pk or orig_text.startswith(norm_pk[:prefix_len]) or norm_pk.startswith(orig_text[:prefix_len]):
                        c["text"] = pv
                        modified += 1
                        break

with open(target_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Force applied {modified} pads to {target_file}")
