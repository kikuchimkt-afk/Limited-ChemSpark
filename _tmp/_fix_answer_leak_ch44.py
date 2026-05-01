"""Fix answer-leak patterns in ch4-4.json incorrect choices."""
import json, sys, os

SRC = "questions/ch4-4.json"
DRY = "--dry-run" in sys.argv

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

OVERRIDES = {
    # q003 c1: "非晶質ではなく結晶性の物質に分類される"
    ("ch4_4_q003", 0): "ガラスは規則正しい結晶構造を持つ固体であり、水晶と同じく明確な融点を示す。結晶性の物質に分類され加熱すると特定の温度で急に液体になる。",
    # q013 c3: "銀白色ではない"
    ("ch4_4_q013", 2): "黄銅は銀白色である。銅と亜鉛が合金化すると銀白色の光沢を呈する。真ちゅうとも呼ばれ楽器や五円硬貨に使われる。",
    # q031 c1: "金属材料ではない"
    ("ch4_4_q031", 0): "二酸化ケイ素は金属材料の一種である。二酸化ケイ素は金属光沢を持ち電気伝導性を示す導体として金属材料に分類される。",
    # q031 c4: "逆で二酸化ケイ素はガラスやセメントの主要原料として使われている"
    ("ch4_4_q031", 3): "二酸化ケイ素はガラスの原料には使われない。ガラスの主原料は炭酸カルシウムと酸化ナトリウムであり二酸化ケイ素は含まれない。",
    # q045 c2: "侵入型合金ではない。炭素は鋼の構成元素には含まれておらず"
    ("ch4_4_q045", 1): "鋼は銅原子が鉄原子の位置に置き換わった置換型合金の代表例である。炭素は鋼の構成元素には含まれておらず鉄と銅だけからなる二元合金である。",
    # q049 c3: "実際は赤褐色である"
    ("ch4_4_q049", 2): "黒さびは四酸化三鉄からなるが赤色を呈する物質である。名称に「黒」がつくのは歴史的な慣習によるものであり外観は赤褐色の粉末状である。",
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
                    mp3 = os.path.join("audio", "ch4-4", qid, f"{c['choice_id']}.mp3")
                    if os.path.exists(mp3):
                        os.remove(mp3)
                        stale_mp3.append(mp3)

print(f"=== {'DRY RUN' if DRY else 'APPLYING'} answer-leak fixes for ch4-4 ===")
print(f"Changes: {len(changes)}, deleted mp3: {len(stale_mp3)}")
for ch in changes:
    print(f"  {ch['qid']} c{ch['ci']}: {ch['new']}...")

if not DRY:
    with open(SRC, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Written {SRC}")
