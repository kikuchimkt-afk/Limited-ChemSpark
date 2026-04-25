"""Check ch1-1 for tts_explanation vs explanation mismatches and 選択肢N in tts fields."""
import json, pathlib, re, sys
sys.stdout.reconfigure(encoding="utf-8")

fp = pathlib.Path("questions/ch1-1.json")
data = json.loads(fp.read_text(encoding="utf-8"))

issues = []
for q in data["questions"]:
    qid = q["id"]
    tts_exp = q.get("tts_explanation", "")
    disp_exp = q.get("explanation", "")
    
    # Check for 選択肢 in tts_explanation
    if "選択肢" in tts_exp:
        issues.append((qid, "TTS_EXP_HAS_SENTAKUSHI", tts_exp[:100]))
    
    # Check for 選択肢 in tts_question
    tts_q = q.get("tts_question", "")
    if "選択肢" in tts_q:
        issues.append((qid, "TTS_Q_HAS_SENTAKUSHI", tts_q[:100]))
    
    # Check for 選択肢 in tts_text of choices
    for c in q.get("choices", []):
        tts_t = c.get("tts_text", "")
        if "選択肢" in tts_t:
            issues.append((qid, f"TTS_CHOICE_{c['label']}_HAS_SENTAKUSHI", tts_t[:100]))

    # Check display explanation for 選択肢 (this is allowed but let's see)
    if "選択肢" in disp_exp:
        issues.append((qid, "DISP_EXP_HAS_SENTAKUSHI", disp_exp[:100]))

if not issues:
    print("No issues found in ch1-1")
else:
    print(f"Found {len(issues)} issues:")
    for qid, typ, preview in issues:
        print(f"  {qid} [{typ}]: {preview}...")

# Also print q001 tts_explanation for inspection
q001 = data["questions"][0]
print(f"\n=== q001 tts_explanation ===")
print(q001["tts_explanation"])
print(f"\n=== q001 explanation (display) ===")
print(q001["explanation"])
