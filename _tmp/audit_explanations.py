"""
Audit tts_explanation comprehensiveness and detect duplicate choices.

For each question:
1. Flag if tts_explanation is <= 60 chars (likely too brief / correct-only)
2. Flag if any two choices share identical text
3. Report per-chapter summary
"""
import json, sys, pathlib

CHAPTERS = [
    "ch1-1","ch1-2","ch1-3","ch1-4",
    "ch2-1","ch2-2","ch2-3",
    "ch3-1","ch3-2","ch3-3","ch3-4","ch3-5",
    "ch4-1","ch4-2","ch4-3","ch4-4",
]

q_dir = pathlib.Path("questions")

for ch in CHAPTERS:
    fp = q_dir / f"{ch}.json"
    if not fp.exists():
        print(f"[SKIP] {ch} - file not found")
        continue
    data = json.loads(fp.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    
    short_explanations = []
    dup_choices = []
    
    for q in questions:
        qid = q["id"]
        tts_exp = q.get("tts_explanation", "")
        
        # Check short explanation
        if len(tts_exp) <= 60:
            short_explanations.append((qid, len(tts_exp), tts_exp[:50]))
        
        # Check duplicate choices
        choice_texts = [c.get("tts_text", c.get("text", "")) for c in q.get("choices", [])]
        seen = {}
        for i, ct in enumerate(choice_texts):
            if ct in seen:
                dup_choices.append((qid, seen[ct]+1, i+1))
            else:
                seen[ct] = i
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Chapter: {ch}  ({len(questions)} questions)")
    print(f"{'='*60}")
    
    if short_explanations:
        print(f"  [SHORT EXPLANATION] {len(short_explanations)} questions with tts_explanation <= 60 chars:")
        for qid, ln, preview in short_explanations:
            print(f"    {qid}: {ln} chars - \"{preview}...\"")
    else:
        print(f"  [SHORT EXPLANATION] None found (all > 60 chars)")
    
    if dup_choices:
        print(f"  [DUPLICATE CHOICES] {len(dup_choices)} questions with identical choice texts:")
        for qid, c1, c2 in dup_choices:
            print(f"    {qid}: choice {c1} == choice {c2}")
    else:
        print(f"  [DUPLICATE CHOICES] None found")

print(f"\n{'='*60}")
print("AUDIT COMPLETE")
