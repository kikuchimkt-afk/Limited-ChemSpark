"""Apply padding directly to ch2-3.json for length-biased questions."""
import json, os

SRC = "questions/ch2-3.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch2_3_q042_c2": "エタノールは炭素鎖をもつため無極性分子とみなされ水にはまったく溶けない。炭素鎖の疎水性が支配的でありヒドロキシ基があっても水との親和性は生まれない。エタノールは油脂と同じ溶解挙動を示す。",
    "ch2_3_q042_c3": "すべての物質は水に溶ける。無極性分子も水和で溶ける。似たものは似たものを溶かさない。物質の極性に関わらず水の高い溶解力であらゆる分子が水和される。溶媒の種類を問わず均一に溶解する。",
    "ch2_3_q042_c4": "水和はイオン結晶にのみ起こり極性分子には起こらない。極性分子は水分子と相互作用できず水中では沈殿として残る。溶解するのはイオン結晶のみであり極性分子は有機溶媒でしか溶けない。",
    "ch2_3_q044_c1": "コロイドにはブラウン運動やチンダル現象は観察されず、真の溶液と同じ挙動を示す。コロイド粒子は真の溶液中の分子と同じ大きさであるため特有の現象は起こらない。半透膜も通過できるためろ過で分離できない。",
    "ch2_3_q044_c3": "コロイド粒子はイオンと同じ大きさであり通常のろ紙でろ過できる。凝析と塩析は全く同じ現象である。チンダル現象は真の溶液でも起こる。コロイドと真の溶液に本質的な差異はなく同一の手法で精製される。",
    "ch2_3_q044_c4": "疎水コロイドは多量の電解質が必要で、親水コロイドは少量で沈殿する。疎水コロイドは水分子の層で安定化されており電荷中和だけでは沈殿しないため大量の電解質を投入して脱水和させる必要がある。",
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
                mp3 = os.path.join("audio", "ch2-3", q["id"], f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Applied {applied} pads")
