"""
Add trap_detail to all incorrect-type distractor choices that are missing it.
Strategy: Extract relevant sentences from tts_explanation for each choice.
"""
import json, sys, re
from pathlib import Path
from difflib import SequenceMatcher

sys.stdout.reconfigure(encoding="utf-8")

def split_sentences(text):
    """Split Japanese text into sentences."""
    # Split on 。but keep the delimiter
    parts = re.split(r'(。)', text)
    sentences = []
    for i in range(0, len(parts) - 1, 2):
        sentences.append(parts[i] + parts[i+1])
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1])
    return [s.strip() for s in sentences if s.strip()]

def extract_key_terms(text):
    """Extract key terms (nouns/content words) from text."""
    # Remove common particles and verb endings
    # Use character n-grams for matching instead
    cleaned = re.sub(r'[、。「」『』（）\s]', '', text)
    # Generate 3-grams
    ngrams = set()
    for i in range(len(cleaned) - 2):
        ngrams.add(cleaned[i:i+3])
    return ngrams

def find_relevant_explanation(choice_text, explanation, all_choices):
    """Find the part of explanation most relevant to this choice."""
    sentences = split_sentences(explanation)
    if not sentences:
        return None
    
    choice_ngrams = extract_key_terms(choice_text)
    if not choice_ngrams:
        return None
    
    # Score each sentence by overlap with choice text
    scored = []
    for sent in sentences:
        sent_ngrams = extract_key_terms(sent)
        if not sent_ngrams:
            continue
        overlap = len(choice_ngrams & sent_ngrams)
        # Normalize by choice length
        score = overlap / max(len(choice_ngrams), 1)
        scored.append((score, sent))
    
    if not scored:
        return None
    
    # Sort by score descending
    scored.sort(key=lambda x: -x[0])
    
    # Take the best matching sentence(s)
    best_score = scored[0][0]
    if best_score < 0.15:  # Too low overlap
        return None
    
    # Collect sentences with good scores
    relevant = []
    for score, sent in scored:
        if score >= best_score * 0.6 and score >= 0.15:
            relevant.append(sent)
        if len(relevant) >= 2:
            break
    
    result = ''.join(relevant)
    # Trim if too long
    if len(result) > 120:
        result = result[:117] + '…'
    
    return result

def generate_trap_detail(choice, question, all_choices):
    """Generate trap_detail for a correct distractor in an incorrect-type question."""
    ct = choice.get("text", "")
    tts_ct = choice.get("tts_text", ct)
    explanation = question.get("tts_explanation", "")
    
    # Try to extract from explanation
    relevant = find_relevant_explanation(tts_ct, explanation, all_choices)
    
    if relevant:
        # Check if the relevant text essentially repeats the choice text
        ratio = SequenceMatcher(None, tts_ct, relevant).ratio()
        if ratio > 0.7:
            # Too similar to choice text, just mark as correct
            return "この記述は正しい。"
        return f"正しい。{relevant}"
    
    return "この記述は正しい。"

def process_chapter(ch_name, dry_run=False):
    """Process a single chapter, adding missing trap_details."""
    qdir = Path("questions")
    fpath = qdir / f"{ch_name}.json"
    d = json.loads(fpath.read_text("utf-8"))
    
    updated = 0
    for q in d["questions"]:
        if q.get("question_type") != "incorrect":
            continue
        
        all_choices = q["choices"]
        for c in all_choices:
            if c.get("is_correct") or c.get("trap_detail"):
                continue
            
            # This is a correct distractor without trap_detail
            detail = generate_trap_detail(c, q, all_choices)
            if detail:
                if not dry_run:
                    c["trap_detail"] = detail
                    if not c.get("trap_type"):
                        c["trap_type"] = "correct_statement"
                updated += 1
    
    if not dry_run and updated > 0:
        fpath.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    return updated

# Process all chapters
qdir = Path("questions")
chapters = sorted(f.stem for f in qdir.glob("ch[0-9]*.json") if "backup" not in f.stem)

total = 0
dry_run = "--dry-run" in sys.argv

if dry_run:
    print("=== DRY RUN ===\n")

for ch in chapters:
    count = process_chapter(ch, dry_run=dry_run)
    if count > 0:
        print(f"{ch}: {'would add' if dry_run else 'added'} {count} trap_details")
        total += count

print(f"\nTotal: {total} trap_details {'would be added' if dry_run else 'added'}")
