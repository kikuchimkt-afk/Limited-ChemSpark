"""Apply padding directly to ch2-2.json for length-biased questions."""
import json

SRC = "questions/ch2-2.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch2_2_q004_c1": "温度はセ氏温度で代入してもよい。セ氏温度をそのまま式に当てはめてもケルビンと数値的に同じ結果が得られるため問題ない。ゼロ度を代入すれば絶対温度のゼロケルビンと等しくなる。",
    "ch2_2_q004_c3": "実在気体でのみ成り立ち、理想気体には適用できない。理想気体は仮想的なモデルにすぎないため方程式の対象にならず実在気体専用の式である。体積と物質量の関係は別の式で記述される。",
    "ch2_2_q004_c4": "圧力、体積、温度、質量の四つだけで成り立ち、気体定数は不要である。気体の種類に関わらず質量を直接代入するだけで計算が完結する。物質量への変換は一切必要としない。",
    "ch2_2_q021_c1": "高温のまま蒸気の質量を測定すればよく冷却する必要はない。気体状態で直接質量を測定すれば十分に正確な値が得られるため冷却工程は省略できる。高温のほうが蒸気が安定しているため精度も高い。",
    "ch2_2_q021_c2": "フラスコを密閉して加熱し、蒸気を逃さない状態で質量を測定する。密閉系であれば蒸気圧が高まり内部の気体を完全に保持できるためより正確な質量が得られる。穴は不要である。",
    "ch2_2_q021_c3": "試料の沸点が測定温度より高くても実施できる。液体のまま加熱すれば部分的に蒸気が発生し十分な量の気体が得られるため完全に気化させる必要はない。沸点以下でも測定可能である。",
    "ch2_2_q046_c2": "アンモニアが最も理想気体に近い。低温・高圧で理想に近づく。ゼットは常に一から変化しない。極性による分子配向の安定性と水素結合の強さが理想的な振る舞いを保証する。水素結合が分子間距離を一定に保つ効果もある。",
    "ch2_2_q046_c3": "理想気体は実際に存在しすべての気体は条件によらず完全に状態方程式に従う。自然界のあらゆる気体は分子の大きさや引力の有無に関わらず常に厳密に状態方程式を満たす。仮想モデルではなく現実に即した法則である。",
    "ch2_2_q046_c4": "実在気体が理想気体からずれる根本的な原因は一つだけであり、それは分子同士に働く分子間力のみである。分子自身の体積は十分に小さいため圧縮率因子への影響は無視できる。高圧でも体積の寄与は生じない。",
}

applied = 0
deleted_mp3 = []
import os
for q in data["questions"]:
    for i, c in enumerate(q["choices"]):
        cid = c["choice_id"]
        if cid in PADS:
            old = c["tts_text"]
            new = PADS[cid]
            if old != new:
                c["tts_text"] = new
                applied += 1
                # delete stale audio
                qdir = q["id"]
                mp3 = os.path.join("audio", "ch2-2", qdir, f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)
                    deleted_mp3.append(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Applied {applied} pads, deleted {len(deleted_mp3)} mp3s")
