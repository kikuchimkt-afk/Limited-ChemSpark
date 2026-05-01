"""Apply padding directly to ch4-1.json for length-biased questions."""
import json, os

SRC = "questions/ch4-1.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch4_1_q050_c1": "すべてのハロゲン化水素は例外なく強酸であり水溶液中で完全に電離する。塩素の洗気瓶は濃硫酸を先に通して水蒸気を除去し、次に水を通して塩化水素を除去するのが正しい手順である。オストワルト法では鉄触媒を用いてアンモニアを酸化する。",
    "ch4_1_q050_c3": "ハロゲンの酸化力は原子番号が大きいほど電子雲が広がり電子を引きつけやすくなるため強くなる。フッ化水素は他のハロゲン化水素と同じく強酸である。接触法の触媒は白金であり、ハーバー法の触媒は酸化バナジウムである。気体捕集法は気体の密度だけで決まる。",
    "ch4_1_q050_c4": "アンモニアの乾燥には酸性乾燥剤の濃硫酸と中性乾燥剤の塩化カルシウムのどちらも使用できる。これらはいずれもアンモニアと化学反応を起こさず水分だけを選択的に除去する万能乾燥剤である。気体の捕集法はすべて水上置換で統一される。",
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
                mp3 = os.path.join("audio", "ch4-1", q["id"], f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Applied {applied} pads")
