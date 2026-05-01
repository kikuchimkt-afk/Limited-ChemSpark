"""Generate pads for ch3-2 length-biased questions."""
import json

with open("questions/ch3-2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

PAD_TARGETS = {
    "ch3_2_q003": {
        "c1": "反応速度は反応物の濃度に依存しない。反応物の量を増やしても減らしても反応速度には影響しない性質がある。",
        "c2": "速度定数は反応物の濃度によって変わる。反応物の濃度を二倍にすると速度定数も二倍になる関係がある。",
        "c4": "べき乗の指数は必ず化学反応式の係数と一致する。反応式の係数をそのまま指数に用いれば正確な速度式が完成する。",
    },
    "ch3_2_q025": {
        "c1": "触媒を反応系に加えると反応速度が上がるのと同時に生成物の総量まで増加する。触媒は速度を上げるだけでなく平衡の位置も移動させて生成物量を増やす効果がある。",
        "c2": "反応速度は温度のみで決まり触媒は無関係。速度式の指数は係数と一致する。律速段階は最速の段階。触媒は反応エンタルピーを変える。四箇所すべてが反応速度の性質である。",
        "c4": "活性化エネルギーが大きいほど反応速度は大きい。壁が高いほど分子のエネルギーが大きくなり反応速度は増加するため活性化エネルギーは大きいほど有利である。",
    },
    "ch3_2_q045": {
        "c2": "粒子のすべての衝突がそのまま生成物を生む。遷移状態は存在しない。多段階反応ではすべての段階が等しく速度に寄与する。温度は反応速度と無関係である。触媒は活性化エネルギーを上げる。五つの主張を総合した記述である。",
        "c3": "律速段階は最も速い段階であり触媒は生成物量を増やす。律速段階は反応全体を最速で完了させる段階であり触媒は生成物の最終量を増加させる効果を持つ。",
        "c4": "活性化エネルギーが大きいほど反応のエネルギーが大きく反応の勢いが増すため反応速度が速くなる。壁が高いほど分子に大きな運動エネルギーが蓄えられ有効な衝突が増える。",
    },
    "ch3_2_q049": {
        "c1": "濃度・温度・触媒・表面積の四つの因子はいずれも反応速度を低下させる方向に寄与する。これら四つの因子を変化させても反応速度は増大しない特徴がある。",
        "c2": "触媒を加えることと温度を上げることは全く同じ効果を示す。どちらも同じメカニズムで反応速度を上げるため使い分ける必要はない。",
        "c3": "温度のみが速度に影響し他の三因子は無関係である。濃度や触媒や表面積は反応速度に影響しない要因であり変化させても速度は一定である。",
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

with open("questions/_pads/ch3-2.json", "w", encoding="utf-8") as f:
    json.dump(pads, f, ensure_ascii=False, indent=2)

print(f"Generated pads for {sum(len(v) for v in pads.values())} choices across {len(pads)} questions")
