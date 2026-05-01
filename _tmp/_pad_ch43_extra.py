"""Extra padding for ch4-3 q050."""
import json, os

SRC = "questions/ch4-3.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch4_3_q050_c1": "鉄の製錬では石灰石が還元剤として機能し、溶鉱炉から直接純鉄が得られる。コークスは燃料としてのみ使用され還元には関与しない。銅は銀白色で塩酸に溶ける。銀の電気伝導性は全金属中最低である。金は希硝酸にも溶ける。錯イオンの配位結合ではイオン結合と同じ力が働く。",
    "ch4_3_q050_c4": "系統分析は一段階のみで完了し、試薬の添加順序はどの順番でも同じ結果が得られる。また塩化ナトリウムは水に溶けず沈殿する。鉄の製錬ではコークスは燃料としてのみ使用される。銅の電解精錬では純銅を陽極に銀を陰極に使用する。錯イオンの配位数はすべて二である。",
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
                mp3 = os.path.join("audio", "ch4-3", q["id"], f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Applied {applied} extra pads")
