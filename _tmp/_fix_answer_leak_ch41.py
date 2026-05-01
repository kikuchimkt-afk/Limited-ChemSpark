"""Fix answer-leak patterns in ch4-1.json incorrect choices."""
import json, sys, os

SRC = "questions/ch4-1.json"
DRY = "--dry-run" in sys.argv

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

# key = (qid, choice_index_0based) -> new tts_text
OVERRIDES = {
    # q035 c2: "逆でハーバー法がアンモニア合成で..."
    ("ch4_1_q035", 1): "ハーバー法で硝酸を作り、オストワルト法でアンモニアを作る。ハーバー法は窒素酸化物を経由して硝酸を合成し、オストワルト法は窒素と水素から直接アンモニアを合成する。",
    # q035 c3: "誤って覚えやすい典型例だが、白金触媒を使うのは..."
    ("ch4_1_q035", 2): "三つの製法すべて白金触媒を使用し、すべて同じ条件で反応する。ハーバー法もオストワルト法も接触法もいずれも白金触媒を用いて高温高圧で反応させる共通の工業プロセスである。",
    # q035 c4: "三酸化硫黄を水に直接入れると危険なため濃硫酸に吸収させて..."
    ("ch4_1_q035", 3): "接触法では三酸化硫黄を直接水に溶かして硫酸にする。三酸化硫黄を大量の水に加えて溶解させるだけで濃硫酸が効率よく得られる簡便な方法である。",
    # q038 c1: "典型元素は同じ族の元素同士で化学的性質が類似しており全く異なるわけではない"
    ("ch4_1_q038", 0): "典型元素では同じ族でも性質が全く異なる。同じ族に属していても価電子数が異なるため化学的性質に共通点は見られない。",
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
                    mp3 = os.path.join("audio", "ch4-1", qid, f"{c['choice_id']}.mp3")
                    if os.path.exists(mp3):
                        os.remove(mp3)
                        stale_mp3.append(mp3)

print(f"=== {'DRY RUN' if DRY else 'APPLYING'} answer-leak fixes for ch4-1 ===")
print(f"Changes: {len(changes)}, deleted mp3: {len(stale_mp3)}")
for ch in changes:
    print(f"  {ch['qid']} c{ch['ci']}: {ch['new']}...")

if not DRY:
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written {SRC}")
