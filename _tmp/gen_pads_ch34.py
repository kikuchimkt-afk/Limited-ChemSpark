"""Generate proper pads JSON for ch3-4 in the format expected by _pad_wrongs_chapter.py"""
import json

with open("questions/ch3-4.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Map: qid -> {choice_id_suffix -> new_tts_text}
PAD_TARGETS = {
    "ch3_4_q006": {
        "c1": "弱酸と強塩基の塩は酸性を示す。強い方の親の性質を受け継ぐため酸性になり、弱酸由来のイオンが水素イオンを放出して水溶液を酸性にする。",
    },
    "ch3_4_q009": {
        "c2": "ブレンステッドの定義では水素イオンを与えるものが酸である。水素イオンを受け取るものが塩基であるとされ水溶液中に限定される定義である。",
        "c3": "ブレンステッドの定義は水溶液以外にも適用できる。気体の反応や非水溶媒の反応にも使うことができる広い適用範囲をもつ定義である。",
        "c4": "アレニウスの定義では水中で水素イオンを生じるものが酸である。水中で水酸化物イオンを生じるものが塩基であり水溶液限定の定義である。",
    },
    "ch3_4_q013": {
        "c4": "ビュレットは純水で洗って濡れたまま使う。内壁に残った純水が溶液を適度に薄めて安定させる効果があり純水のまま使用して問題はない。",
    },
    "ch3_4_q018": {
        "c2": "近似なしで常に二次方程式を解く必要がある。電離度の大きさに関係なく厳密な計算が求められるため解の公式を使って水素イオン濃度を正確に求めなければならない。",
        "c4": "電離定数が大きいほど電離度は小さい。電離定数と電離度は反比例の関係にあり電離定数が大きい酸ほど電離しにくく弱酸に分類される。",
    },
    "ch3_4_q025": {
        "c1": "イオン積が溶解度積以下のときに沈殿する。不飽和でも沈殿が生じる条件は存在しイオン濃度が低いほど沈殿が析出しやすい性質がある。",
        "c2": "混合前の濃度をそのまま使ってイオン積を計算する。体積変化は無視してよい。混合によりイオン濃度は変わらないとみなせるため希釈補正は不要である。",
        "c4": "溶解度積とイオン積の比較は不要である。沈殿の有無は溶液の色だけで判断できる。色の変化がなければ沈殿は生じないと結論づけてよい。",
    },
    "ch3_4_q048": {
        "c1": "水溶液は中性を示す。塩化ナトリウムは強酸と強塩基の塩であるため加水分解が起きず中性を示す。ナトリウムイオンと塩化物イオンはともに安定なイオンである。",
        "c4": "塩化ナトリウムは強酸と強塩基の正塩である。塩酸と水酸化ナトリウムの中和で生じる正塩である。正塩は酸由来の水素が完全に置き換わった塩のことである。",
    },
    "ch3_4_q050": {
        "c1": "メスフラスコは共洗いが必要であり加熱乾燥が正しい操作である。すべての器具を共洗いと加熱で処理することが最も正確な方法であり目盛り付き器具も例外なく加熱して十分に乾燥させてから使用するべきである。",
        "c3": "アレニウスのほうがブレンステッドより適用範囲が広い。すべての塩は中性であり溶解度積は濃度で変わる。アレニウスは気体や非水溶媒にも適用でき最も汎用的な定義として広く受け入れられている。",
    },
}

# Build the pads JSON in the required format: {qid: {old_tts_text: new_tts_text}}
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
