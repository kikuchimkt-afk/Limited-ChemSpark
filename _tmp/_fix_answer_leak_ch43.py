"""Fix answer-leak patterns in ch4-3.json incorrect choices."""
import json, sys, os

SRC = "questions/ch4-3.json"
DRY = "--dry-run" in sys.argv

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

OVERRIDES = {
    # q005 c2: "金は...銀白色ではない"
    ("ch4_3_q005", 1): "金は銀白色の金属である。金は白金と同じ銀白色の光沢をもち装飾品に使われる際も銀白色の輝きが特徴である。",
    # q007 c1: "平衡反応ではなく一方向にのみ不可逆的に進行する"
    ("ch4_3_q007", 0): "この反応ではクロムの酸化数がプラス六からプラス三へと大きく変化し、電子の授受を伴う。典型的な酸化還元反応であるため一方向にのみ不可逆的に進行する。",
    # q009 c3: "試薬を加える順序は厳密に決まっており...自由ではない"
    ("ch4_3_q009", 2): "試薬を加える順序は自由である。どの試薬から加えても最終的に同じ分離結果が得られるため順序を気にする必要はない。",
    # q010 c4: "思い込みがちだが...すべてが溶けるわけではない"
    ("ch4_3_q010", 3): "塩化物はすべて水に溶ける。塩化物イオンはいかなる陽イオンとも沈殿を形成せず溶液中にイオンとして存在し続ける。",
    # q016 c3: "正方形構造ではない"
    ("ch4_3_q016", 2): "テトラアンミン銅イオンは正四面体構造をとる錯イオンであり、メタンの分子構造と同様の立体配置を示す。四つのアンモニア分子が銅イオンの周囲に三次元的に配位する。",
    # q023 c4: "銀ではなくコスト面から銅が使われている"
    ("ch4_3_q023", 3): "電線には銀が使われている。銀は電気伝導性が高いためコストに関わらず電線の材料として広く採用されている。",
    # q026 c2: "酸化するのではなく自身が酸化されて相手を還元する"
    ("ch4_3_q026", 1): "ニクロム酸カリウムは代表的な還元剤であり、酸化還元滴定では自身が酸化されて相手を還元する役割を持つ。",
    # q034 c4: "平衡反応ではない"
    ("ch4_3_q034", 3): "この反応ではクロムの酸化数がプラス六からプラス三に変化するため、典型的な酸化還元反応として分類される。電子の授受を伴い一方向にのみ進行する。",
    # q043 c4: "配位数は中心金属イオンに結合している配位子の数であり溶液中のイオンの総数ではない"
    ("ch4_3_q043", 3): "配位数とは溶液中のイオンの総数である。錯イオンが水に溶けたときに生じるすべてのイオンを数え上げた値が配位数として定義される。",
}

changes = []
stale_mp3 = []
for q in data["questions"]:
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        if c["is_correct"]:
            continue
        key = (qid, i)
        if key in OVERRIDES:
            old = c["tts_text"]
            new = OVERRIDES[key]
            if old != new:
                changes.append({"qid": qid, "ci": i+1, "cid": c["choice_id"], "new": new[:80]})
                if not DRY:
                    c["tts_text"] = new
                    mp3 = os.path.join("audio", "ch4-3", qid, f"{c['choice_id']}.mp3")
                    if os.path.exists(mp3):
                        os.remove(mp3)
                        stale_mp3.append(mp3)

print(f"=== {'DRY RUN' if DRY else 'APPLYING'} answer-leak fixes for ch4-3 ===")
print(f"Changes: {len(changes)}, deleted mp3: {len(stale_mp3)}")
for ch in changes:
    print(f"  {ch['qid']} c{ch['ci']}: {ch['new']}...")

if not DRY:
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written {SRC}")
