"""Deep comparison: for each question in ch1-1, compare tts_explanation vs explanation.
Highlight cases where explanation has 選択肢N but tts_explanation describes with different content-based wording."""
import json, pathlib, sys, re
sys.stdout.reconfigure(encoding="utf-8")

fp = pathlib.Path("questions/ch1-1.json")
data = json.loads(fp.read_text(encoding="utf-8"))

for q in data["questions"]:
    qid = q["id"]
    disp = q.get("explanation", "")
    tts = q.get("tts_explanation", "")
    
    # Find 選択肢N references in display
    refs = re.findall(r'選択肢[1-4一二三四]', disp)
    if refs:
        print(f"\n{'='*60}")
        print(f"{qid} - display has {len(refs)} 選択肢 refs: {refs}")
        print(f"DISP: {disp[:200]}...")
        print(f"TTS:  {tts[:200]}...")
