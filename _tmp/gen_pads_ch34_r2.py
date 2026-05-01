"""Generate additional pads for remaining length-biased questions in ch3-4"""
import json

with open("questions/ch3-4.json", "r", encoding="utf-8") as f:
    data = json.load(f)

PAD_TARGETS = {
    "ch3_4_q013": {
        "c2": "すべての器具を共洗いする。共洗いが必要なのは溶液を正確に量るホールピペットとビュレットだけでありメスフラスコやビーカーは純水でよいためすべてを共洗いする必要はない。",
        "c3": "すべての器具を加熱して乾燥させる。加熱乾燥はガラスの目盛りが狂う恐れがあるため行わない。純水で洗って濡れたまま使用するのが正しい操作手順である。",
    },
    "ch3_4_q050": {
        "c1": "メスフラスコは共洗いが必要であり加熱乾燥が正しい操作である。すべての器具を共洗いと加熱で処理することが最も正確な方法であり目盛り付き器具も例外なく加熱して十分に乾燥させてから使用するべきである。ビュレットやホールピペットも同様に加熱乾燥して共洗いしてから使うのが鉄則である。",
        "c3": "アレニウスのほうがブレンステッドより適用範囲が広い。すべての塩は中性であり溶解度積は濃度で変わる。アレニウスは気体や非水溶媒にも適用でき最も汎用的な定義として広く受け入れられている。塩は中性のため加水分解という現象は存在しない。",
        "c4": "強酸と強塩基の塩で最も効果的な緩衝液が作れると誤解されやすいが、緩衝液は弱酸とその塩または弱塩基とその塩で作るものであり強酸強塩基の塩では作れない。強酸強塩基の塩のイオンは安定しているため水素イオンの吸収や供給ができず緩衝作用を発揮できない。",
    },
}

pads = {}
for q in data["questions"]:
    qid = q["id"]
    if qid not in PAD_TARGETS:
        continue
    pads[qid] = {}
    for choice in q["choices"]:
        cid = choice["choice_id"]
        suffix = cid.replace(f"{qid}_", "")
        if suffix in PAD_TARGETS[qid]:
            old_tts = choice["tts_text"]
            new_tts = PAD_TARGETS[qid][suffix]
            pads[qid][old_tts] = new_tts

with open("questions/_pads/ch3-4.json", "w", encoding="utf-8") as f:
    json.dump(pads, f, ensure_ascii=False, indent=2)

print(f"Generated pads for {sum(len(v) for v in pads.values())} choices across {len(pads)} questions")
