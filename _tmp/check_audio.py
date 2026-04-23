import os, json

for ch in ['ch5-1', 'ch5-2', 'ch5-3', 'ch5-4', 'ch5-5']:
    audio_dir = f'audio/{ch}'
    json_path = f'questions/{ch}.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    qids = [q['id'] for q in data['questions']]
    
    if not os.path.isdir(audio_dir):
        print(f'{ch}: NO AUDIO DIR (need {len(qids)*6} files)')
        continue
    
    total_mp3 = 0
    short_dirs = []
    for qid in qids:
        qdir = os.path.join(audio_dir, qid)
        if not os.path.isdir(qdir):
            short_dirs.append((qid, 'MISSING DIR'))
            continue
        files = os.listdir(qdir)
        total_mp3 += len(files)
        if len(files) < 6:
            short_dirs.append((qid, f'{len(files)}/6 files: {files}'))
    
    print(f'{ch}: {total_mp3}/{len(qids)*6} mp3 files')
    if short_dirs:
        for qid, info in short_dirs:
            print(f'  INCOMPLETE: {qid} -> {info}')
