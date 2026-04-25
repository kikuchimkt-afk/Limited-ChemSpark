"""Extract flagged questions' choices and current explanation for rewrite drafting."""
import json, pathlib

FLAGGED = {
    "ch3-2": ["ch3_2_q006"],
    "ch3-3": ["ch3_3_q035", "ch3_3_q045"],
    "ch3-4": ["ch3_4_q022", "ch3_4_q039", "ch3_4_q047"],
    "ch3-5": ["ch3_5_q017", "ch3_5_q020", "ch3_5_q026", "ch3_5_q029", "ch3_5_q034", "ch3_5_q036"],
    "ch4-1": ["ch4_1_q018", "ch4_1_q029"],
    "ch4-2": ["ch4_2_q003", "ch4_2_q009", "ch4_2_q019", "ch4_2_q033", "ch4_2_q042", "ch4_2_q046"],
    "ch4-3": ["ch4_3_q002", "ch4_3_q014", "ch4_3_q016", "ch4_3_q022", "ch4_3_q023", "ch4_3_q026", "ch4_3_q028", "ch4_3_q036", "ch4_3_q042", "ch4_3_q043", "ch4_3_q048"],
    "ch4-4": ["ch4_4_q001", "ch4_4_q006", "ch4_4_q007", "ch4_4_q012", "ch4_4_q013", "ch4_4_q014", "ch4_4_q015", "ch4_4_q017", "ch4_4_q018", "ch4_4_q019", "ch4_4_q027", "ch4_4_q029", "ch4_4_q039", "ch4_4_q047", "ch4_4_q049"],
}

q_dir = pathlib.Path("questions")

for ch, qids in FLAGGED.items():
    fp = q_dir / f"{ch}.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    questions = {q["id"]: q for q in data["questions"]}
    
    print(f"\n{'#'*70}")
    print(f"# {ch} ({len(qids)} questions)")
    print(f"{'#'*70}")
    
    for qid in qids:
        q = questions[qid]
        print(f"\n--- {qid} ---")
        print(f"Q: {q['tts_question']}")
        print(f"Type: {q['question_type']}")
        for c in q["choices"]:
            mark = ">>CORRECT<<" if c["is_correct"] else f"[trap:{c.get('trap_type','')}]"
            print(f"  {c['label']}. {mark} {c['tts_text'][:80]}...")
        print(f"Current tts_exp: {q['tts_explanation']}")
