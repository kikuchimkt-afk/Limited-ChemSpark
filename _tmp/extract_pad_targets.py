"""Extract wrong choices needing padding (read-only diagnostic)."""
import json, sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

d = json.load(open('questions/ch3-5.json', 'r', encoding='utf-8'))
for q in d['questions']:
    corr = [c for c in q['choices'] if c['is_correct']][0]
    cl = len(corr['tts_text'])
    wrongs = [(c['choice_id'], c['tts_text'], len(c['tts_text']), c.get('trap_type','')) for c in q['choices'] if not c['is_correct']]
    mw = max(w[2] for w in wrongs)
    if cl - mw >= 10:
        print(f"### {q['id']} (correct={cl}, target>={cl-9}) sub={q['sub_category']}")
        for cid, txt, l, tt in wrongs:
            gap = cl - l
            print(f"  {cid} [{tt}] (len={l}, need+{gap}): {txt}")
        print()
