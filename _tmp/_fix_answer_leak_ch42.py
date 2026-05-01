"""Fix answer-leak patterns in ch4-2.json incorrect choices."""
import json, sys, os

SRC = "questions/ch4-2.json"
DRY = "--dry-run" in sys.argv

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# key = (qid, choice_index_0based) -> new tts_text
OVERRIDES = {
    # q014: "誤りを含むものを選べ" - 正しい選択肢に「これは正しい記述」タグ
    ("ch4_2_q014", 0): "リチウムは赤色の炎色反応を示す。リチウムを含む化合物を炎に入れると電子遷移により特徴的な赤色の光を発する。",
    ("ch4_2_q014", 1): "ナトリウムは黄色の炎色反応を示す。ナトリウム化合物を炎にかざすと輝線スペクトルにより鮮やかな黄色の炎が観察される。",
    ("ch4_2_q014", 2): "カリウムは赤紫色の炎色反応を示す。カリウム化合物を炎に入れると赤紫色の光を発し、コバルトガラスを通すと確認しやすい。",
    # q016: 同パターン
    ("ch4_2_q016", 0): "マグネシウムは熱水とは反応するが常温の水とは反応しにくい。マグネシウムは表面に酸化皮膜を形成するため常温では水との反応が穏やかである。",
    ("ch4_2_q016", 1): "カルシウムは常温の水と反応する。カルシウムは常温の水と反応して水酸化カルシウムと水素を生じる。",
    # q022: 同パターン
    ("ch4_2_q022", 0): "アルミニウムが還元剤としてはたらく。アルミニウムが電子を放出して酸化鉄中の鉄イオンを金属鉄に還元する反応である。",
    ("ch4_2_q022", 2): "反応で酸化アルミニウムと鉄が生成する。アルミニウムが酸化されて酸化アルミニウムになり、酸化鉄が還元されて金属鉄が得られる。",
    ("ch4_2_q022", 3): "酸化鉄が酸化剤としてはたらく。酸化鉄がアルミニウムから電子を受け取り鉄に還元される。",
    # q024: 同パターン
    ("ch4_2_q024", 1): "食塩水にアンモニアと二酸化炭素を吹き込む。飽和食塩水にまずアンモニアを溶かし次に二酸化炭素を通じて反応させる。",
    ("ch4_2_q024", 2): "中間で溶解度の小さい炭酸水素ナトリウムが沈殿する。四種の塩のうち炭酸水素ナトリウムが最も溶解度が小さいため優先的に析出する。",
    ("ch4_2_q024", 3): "炭酸水素ナトリウムを加熱して炭酸ナトリウムを得る。沈殿した炭酸水素ナトリウムを加熱分解すると二酸化炭素と水が放出され炭酸ナトリウムが残る。",
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
                    mp3 = os.path.join("audio", "ch4-2", qid, f"{c['choice_id']}.mp3")
                    if os.path.exists(mp3):
                        os.remove(mp3)
                        stale_mp3.append(mp3)

print(f"=== {'DRY RUN' if DRY else 'APPLYING'} answer-leak fixes for ch4-2 ===")
print(f"Changes: {len(changes)}, deleted mp3: {len(stale_mp3)}")
for ch in changes:
    print(f"  {ch['qid']} c{ch['ci']}: {ch['new']}...")

if not DRY:
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written {SRC}")
