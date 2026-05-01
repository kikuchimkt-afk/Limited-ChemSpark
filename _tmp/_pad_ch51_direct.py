"""Pad ch5-1 q005."""
import json, os

SRC = "questions/ch5-1.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch5_1_q005_c2": "有機化合物と無機化合物の種類数はほぼ同数である。どちらも約十万種類が知られている。",
    "ch5_1_q005_c3": "有機化合物は数千種類程度であり、無機化合物より少ない。炭素を含む化合物の多様性は限定的である。",
    "ch5_1_q005_c4": "有機化合物は百種類程度で、種類は限られている。炭素の結合様式に大きな変化がないためである。",
}

applied = 0
for q in data["questions"]:
    for c in q["choices"]:
        cid = c["choice_id"]
        if cid in PADS:
            old = c["tts_text"]
            new = PADS[cid]
            if old != new:
                c["tts_text"] = new
                applied += 1
                mp3 = os.path.join("audio", "ch5-1", q["id"], f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"Applied {applied} pads")
