"""Apply padding directly to ch4-2.json for length-biased questions."""
import json, os

SRC = "questions/ch4-2.json"
with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

PADS = {
    "ch4_2_q050_c1": "アンモニアソーダ法の最終製品は炭酸水素ナトリウムであり、中間生成物の炭酸ナトリウムを水に溶かして再結晶させることで得られる。アルカリ金属は水中で保存し、炎色反応は示さない。両性金属は鉄と銅であり、ホール・エルー法は水溶液の電気分解である。テルミット反応ではアルミニウムが酸化剤としてはたらく。",
    "ch4_2_q050_c3": "水素はアルカリ金属元素である。アルカリ金属は水中に保存する。水酸化ナトリウムは風解性を持ちソーダ灰とも呼ばれる。両性金属は鉄と銅である。ホール・エルー法は水溶液の電気分解である。テルミット反応ではアルミニウムが酸化剤である。アンモニアソーダ法の最終製品は炭酸水素ナトリウムである。アルカリ土類金属はベリリウムとマグネシウムを含む。",
    "ch4_2_q050_c4": "アルカリ土類金属はベリリウムとマグネシウムを含む第二族元素の総称であり、マグネシウムはカルシウムと同様に常温の水と激しく反応する。アンモニアソーダ法の最終製品は炭酸水素ナトリウムであり加熱分解は行わない。両性金属は鉄と銅の二つだけであり亜鉛やスズは含まれない。ホール・エルー法は水溶液中で電気分解を行う方法である。",
}

applied = 0
for q in data["questions"]:
    for c in q["choices"]:
        cid = c["choice_id"]
        if cid in PADS:
            old = c["tts_text"]
            new = PADS[cid]
            if old != new:
                c["tts_text"] = new
                applied += 1
                mp3 = os.path.join("audio", "ch4-2", q["id"], f"{cid}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)

with open(SRC, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Applied {applied} pads")
