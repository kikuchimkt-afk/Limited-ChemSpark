"""Fix answer-leak patterns in ch1-1, ch1-2, ch1-3, ch1-4."""
import json, os, re

LEAK = [r"逆で",r"正しくは",r"実際には",r"実際は",r"正しい記述",r"これは正しい",r"誤って覚え",r"勘違いされ",r"と思い込み",r"覚えがち",r"陥りやすい",r"ではなく",r"ではない",r"誤りで",r"誤りである",r"正確には"]

def strip_leak(txt):
    """Remove the leak portion (after the first sentence) and replace with
    a plausible-sounding explanation that supports the wrong claim."""
    # Split at the leak pattern location
    for p in LEAK:
        m = re.search(p, txt)
        if m:
            # Find the sentence boundary before the leak
            pos = m.start()
            # Look backwards for a period/。
            boundary = txt.rfind("。", 0, pos)
            if boundary == -1:
                boundary = txt.rfind("。", 0, pos)
            if boundary > 0:
                return txt[:boundary+1]
            else:
                return txt[:pos].rstrip("。、 ")
    return txt

def auto_fix_chapter(ch):
    path = f"questions/{ch}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    changes = 0
    for q in data["questions"]:
        for i, c in enumerate(q["choices"]):
            if c["is_correct"]:
                continue
            txt = c["tts_text"]
            has_leak = any(re.search(p, txt) for p in LEAK)
            if not has_leak:
                continue
            
            # Strip the leak portion - keep only the wrong claim
            stripped = strip_leak(txt)
            if stripped and len(stripped) > 10 and stripped != txt:
                c["tts_text"] = stripped
                changes += 1
                mp3 = os.path.join("audio", ch, q["id"], f"{c['choice_id']}.mp3")
                if os.path.exists(mp3):
                    os.remove(mp3)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{ch}: {changes} changes applied")

for ch in ["ch1-1", "ch1-2", "ch1-3", "ch1-4"]:
    auto_fix_chapter(ch)
