"""Apply padding directly to ch4-3.json for length-biased questions."""
import json, os

SRC = "questions/ch4-3.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    # q009: correct=97, pad c3(55) and c4(75)
    "ch4_3_q009_c3": "試薬を加える順序は自由である。どの試薬から加えても最終的に同じ分離結果が得られるため順序を気にする必要はない。硫化水素は最初に通じてもよく、アンモニア水を先に加えてもすべての金属イオンが正しく分離される。",
    "ch4_3_q009_c4": "系統分析においてはまずアンモニア水を加えて金属イオンの水酸化物として沈殿させるのが正しい第一段階の手順であり、希塩酸は第三段階以降で使用する試薬にあたる。硫化水素は使用しない。",
    # q050: correct=124, pad all 3
    "ch4_3_q050_c1": "鉄の製錬では石灰石が還元剤として機能し、溶鉱炉から直接純鉄が得られる。コークスは燃料としてのみ使用され還元には関与しない。銅は銀白色で塩酸に溶ける。銀の電気伝導性は全金属中最低である。金は希硝酸にも溶ける。",
    "ch4_3_q050_c3": "遷移元素はすべて無色のイオンで一つの酸化数のみをとる。銅は銀白色で塩酸に溶ける。銀の電気伝導性は低い。金は硝酸に溶ける。電解精錬では純銅を陽極に接続する。系統分析は一段階のみで完了し塩化物はすべて沈殿する。",
    "ch4_3_q050_c4": "系統分析は一段階のみで完了し、試薬の添加順序はどの順番でも同じ結果が得られる。また塩化ナトリウムは水に溶けず沈殿する。鉄の製錬ではコークスは燃料としてのみ使用される。銅の電解精錬では純銅を陽極に銀を陰極に使用する。",
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

print(f"Applied {applied} pads")
