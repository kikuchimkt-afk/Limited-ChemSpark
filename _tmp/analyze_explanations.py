"""Analyze tts_explanation length across ch5 chapters."""
import json, os

for ch in ['ch5-1','ch5-2','ch5-3','ch5-4','ch5-5']:
    path = f'questions/{ch}.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    lengths = [len(q['tts_explanation']) for q in data['questions']]
    short = [q['id'] for q in data['questions'] if len(q['tts_explanation']) < 80]
    avg = sum(lengths) / len(lengths)
    mn = min(lengths)
    mx = max(lengths)
    print(f"{ch}: avg={avg:.0f} min={mn} max={mx} short(<80)={len(short)}/50")
    if len(short) <= 10:
        for qid in short:
            q = next(q for q in data['questions'] if q['id'] == qid)
            print(f"  {qid}: [{len(q['tts_explanation'])}] {q['tts_explanation'][:60]}...")
