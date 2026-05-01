"""
Fix answer-leak patterns in ch3-4.json incorrect choices.

Patterns removed:
1. Self-refuting second sentences ("逆で〜", "正しくは〜", "〜ではない")
2. "これは正しい記述であり〜" meta-phrases in correct-statement choices
3. "誤って覚えやすい典型例だが" meta-phrases
4. "初学者が陥りやすい" meta-phrases

Usage:
  python _tmp/_fix_answer_leak_ch34.py --dry-run   # preview changes
  python _tmp/_fix_answer_leak_ch34.py              # apply changes
"""
import json, re, sys, copy

SRC = "questions/ch3-4.json"
DRY = "--dry-run" in sys.argv

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# ── Per-choice override map ──────────────────────────────────────
# key = (qid, choice_index_0based)
# value = replacement tts_text (display text auto-derived later)
OVERRIDES = {
    # q001 c2: remove self-refute
    ("ch3_4_q001", 1): "水酸化物イオンを生じるものが酸である。",
    # q001 c4: remove self-refute
    ("ch3_4_q001", 3): "水素イオンを受け取るものが酸である。",
    # q002 c2: remove self-refute
    ("ch3_4_q002", 1): "水素イオンを受け取るものが酸である。",
    # q004 c3: remove self-refute
    ("ch3_4_q004", 2): "ピーエイチが大きいほど酸性が強い。",
    # q006 c1: remove "勘違いされやすい" + self-refute
    ("ch3_4_q006", 0): "弱酸と強塩基の塩は酸性を示す。強い方の親の性質を受け継ぐため酸性になる。",
    # q008 c3: remove self-refute
    ("ch3_4_q008", 2): "イオン積が溶解度積以下のときに沈殿が生じる。飽和に達していなくても固体が析出する。",
    # q009 c2: remove "これは正しい記述であり"
    ("ch3_4_q009", 1): "ブレンステッドの定義では水素イオンを与えるものが酸である。",
    # q009 c3: remove "これは正しい記述であり"
    ("ch3_4_q009", 2): "ブレンステッドの定義は水溶液以外にも適用できる。",
    # q011 c4: remove self-refute
    ("ch3_4_q011", 3): "強酸は電離度が小さく弱酸は電離度が大きい。",
    # q012 c3: remove self-refute
    ("ch3_4_q012", 2): "希釈すると電離度は小さくなる。濃度が下がるほどイオンに解離しにくくなるためである。",
    # q013 c4: truncate at "典型例だが"
    ("ch3_4_q013", 3): "ビュレットは純水で洗って濡れたまま使う。内壁に残った純水が溶液を適度に薄めて安定させる効果がある。",
    # q017 c3: remove self-refute
    ("ch3_4_q017", 2): "アンモニアは酸である。水に溶けると水素イオンを放出して酸性を示す物質である。",
    # q018 c2: remove "典型例だが"
    ("ch3_4_q018", 1): "近似なしで常に二次方程式を解く必要がある。電離度の大きさに関係なく厳密な計算が求められる。",
    # q018 c4: remove self-refute
    ("ch3_4_q018", 3): "電離定数が大きいほど電離度は小さい。電離定数と電離度は反比例の関係にある。",
    # q020 c1: remove self-refute
    ("ch3_4_q020", 0): "一価の強酸である。水溶液中ではほぼ完全に電離し一段階の電離のみ起こる。",
    # q020 c4: remove self-refute
    ("ch3_4_q020", 3): "液体であるため扱いやすい。室温で液体として存在するため秤量が容易で標準物質に適している。",
    # q023 c2: remove self-refute
    ("ch3_4_q023", 1): "イオン積が溶解度積以下のときに沈殿する。溶液が不飽和であっても固体が析出する場合がある。",
    # q023 c4: remove self-refute
    ("ch3_4_q023", 3): "塩化銀は黄色の沈殿である。光を当てると白色に変色する性質がある。",
    # q024 c2: remove "これは正しい記述であり"
    ("ch3_4_q024", 1): "酸の強弱は電離度で決まる。電離度がほぼ一なら強酸、十分小さければ弱酸と分類される。",
    # q024 c3: remove "これは正しい記述であり"
    ("ch3_4_q024", 2): "強酸はほぼ完全に電離する。塩酸や硫酸などの強酸は水溶液中でほぼすべての分子が電離する。",
    # q024 c4: remove "これは正しい記述であり"
    ("ch3_4_q024", 3): "同じ濃度なら強酸の方がピーエイチが小さい。強酸の方が電離度が大きいため水素イオン濃度が高くなる。",
    # q025 c1: remove self-refute
    ("ch3_4_q025", 0): "イオン積が溶解度積以下のときに沈殿する。不飽和でも沈殿が生じる条件は存在する。",
    # q025 c2: remove "典型例だが"
    ("ch3_4_q025", 1): "混合前の濃度をそのまま使ってイオン積を計算する。体積変化は無視してよい。",
    # q025 c4: remove "思い込みがちだが"
    ("ch3_4_q025", 3): "溶解度積とイオン積の比較は不要である。沈殿の有無は溶液の色だけで判断できる。",
    # q026 c2: remove self-refute
    ("ch3_4_q026", 1): "弱酸と強塩基の塩は酸性を示す。弱酸由来のイオンが水素イオンを放出するためである。",
    # q026 c3: remove self-refute
    ("ch3_4_q026", 2): "強酸と弱塩基の塩は塩基性を示す。弱塩基由来のイオンが水酸化物イオンを放出するためである。",
    # q028 c1: remove self-refute
    ("ch3_4_q028", 0): "酸を加えると酢酸が分解する。酢酸分子が不安定になり炭素と酸素に分かれる反応が進行する。",
    # q028 c3: remove self-refute
    ("ch3_4_q028", 2): "酢酸ではなく水酸化物イオンが消費される。水酸化物イオンと水素イオンの中和反応が主要な変化である。",
    # q031 c1: remove "正しくは"
    ("ch3_4_q031", 0): "「太いヤツはトモ洗い」と覚える。太い器具ほど溶液の正確な量り取りに使われるためである。",
    # q033 c2: remove self-refute
    ("ch3_4_q033", 1): "ブレンステッドは水溶液のみに適用され適用範囲が狭い。気体の反応には使えない定義である。",
    # q036 c1: remove self-refute
    ("ch3_4_q036", 0): "酸性を示す。弱酸由来のイオンが水素イオンを放出して酸性になる。",
    # q036 c2: remove self-refute
    ("ch3_4_q036", 1): "中性を示す。加水分解は起きない。ナトリウムイオンも酢酸イオンも安定で水と反応しない。",
    # q038 c2: remove self-refute
    ("ch3_4_q038", 1): "水素イオンではなく電子のやりとりの覚え方である。酸化還元反応の概念を野球のポジションに例えたものである。",
    # q038 c4: remove self-refute
    ("ch3_4_q038", 3): "ピッチャーが塩基でキャッチャーが酸である。塩基が水素イオンを投げて酸が受け取る仕組みである。",
    # q044 c3: remove self-refute
    ("ch3_4_q044", 2): "「弱い親の遺伝子を継ぐ」で覚える。弱い方の酸または塩基の性質が現れるため弱い方に注目する。",
    # q048 c1: remove "これは正しい記述であり"
    ("ch3_4_q048", 0): "水溶液は中性を示す。塩化ナトリウムは強酸と強塩基の塩であるため加水分解が起きず中性を示す。",
    # q048 c3: remove "これは正しい記述であり"
    ("ch3_4_q048", 2): "ナトリウムイオンも塩化物イオンも加水分解しない。両方とも強酸・強塩基由来で安定なイオンであるため加水分解しない。",
    # q048 c4: remove "これは正しい記述であり"
    ("ch3_4_q048", 3): "塩化ナトリウムは強酸と強塩基の正塩である。塩酸と水酸化ナトリウムの中和で生じる正塩である。",
    # q050 c1: fix chaotic text
    ("ch3_4_q050", 0): "メスフラスコは共洗いが必要であり加熱乾燥が正しい操作である。すべての器具を共洗いと加熱で処理することが最も正確な方法である。",
    # q050 c3: fix chaotic text
    ("ch3_4_q050", 2): "アレニウスのほうがブレンステッドより適用範囲が広い。すべての塩は中性であり溶解度積は濃度で変わる。",
}

changes = []

for q in data["questions"]:
    qid = q["id"]
    for i, c in enumerate(q["choices"]):
        if c["is_correct"]:
            continue
        key = (qid, i)
        if key in OVERRIDES:
            old_tts = c["tts_text"]
            new_tts = OVERRIDES[key]
            if old_tts != new_tts:
                changes.append({
                    "qid": qid,
                    "choice": i + 1,
                    "old": old_tts[:80],
                    "new": new_tts[:80],
                })
                if not DRY:
                    c["tts_text"] = new_tts

print(f"=== {'DRY RUN' if DRY else 'APPLYING'} answer-leak fixes for ch3-4 ===")
print(f"Changes: {len(changes)}")
print()

for ch in changes:
    print(f"  {ch['qid']} c{ch['choice']}:")
    print(f"    OLD: {ch['old']}")
    print(f"    NEW: {ch['new']}")
    print()

if not DRY:
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written {SRC}")
