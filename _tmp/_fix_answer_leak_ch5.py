"""Fix answer-leak patterns in ch5-1 and ch5-5."""
import json, os

fixes = {
    "ch5-1": {
        # q013 c1: "有機化合物ではなく、無機化合物に分類される" → 正しい記述だがリーク表現を除去
        ("ch5_1_q013", 0): "一酸化炭素は炭素を含むため有機化合物に分類される。炭素を骨格に持つ化合物はすべて有機化合物として扱われる。",
    },
    "ch5-5": {
        # q030 c3: "両者は電荷が逆であるため混合すると互いの洗浄力を打ち消し合う"
        ("ch5_5_q030", 2): "セッケンは親水基が陽イオンとなる陽イオン界面活性剤であり合成洗剤は親水基が陰イオンとなる陰イオン界面活性剤である。両者は電荷が異なる界面活性剤として分類される。",
        # q041 c4: "イオン性の問題ではなく分子構造が原因である"
        ("ch5_5_q041", 3): "合成洗剤の疎水基である長い炭化水素鎖が水溶液中で特定の配置をとることで水溶液全体が中性を示すようになる。炭化水素鎖の空間配置が液性を決定する主要因である。",
    },
}

for ch, overrides in fixes.items():
    path = f"questions/{ch}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    changes = 0
    for q in data["questions"]:
        for i, c in enumerate(q["choices"]):
            if c["is_correct"]:
                continue
            key = (q["id"], i)
            if key in overrides:
                old = c["tts_text"]
                new = overrides[key]
                if old != new:
                    c["tts_text"] = new
                    changes += 1
                    mp3 = os.path.join("audio", ch, q["id"], f"{c['choice_id']}.mp3")
                    if os.path.exists(mp3):
                        os.remove(mp3)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{ch}: {changes} changes applied")
