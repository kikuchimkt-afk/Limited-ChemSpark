"""Batch audio generation with retry logic for Edge TTS rate limits."""
import subprocess, sys, time

chapters = [
    'ch3-1','ch3-2','ch3-3','ch3-4','ch3-5',
    'ch4-1','ch4-2','ch4-3','ch4-4',
    'ch5-1','ch5-2','ch5-3','ch5-4','ch5-5',
    'ch6-1','ch6-2','ch6-3',
]

MAX_RETRIES = 5
RETRY_DELAY = 120  # seconds between retries

for ch in chapters:
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n=== {ch} (attempt {attempt}/{MAX_RETRIES}) ===", flush=True)
        result = subprocess.run(
            [sys.executable, r"audio\_generate.py", ch, "all"],
            cwd=r".",
        )
        if result.returncode == 0:
            print(f"  {ch} DONE", flush=True)
            time.sleep(5)  # short pause between chapters
            break
        else:
            print(f"  {ch} FAILED (exit {result.returncode})", flush=True)
            if attempt < MAX_RETRIES:
                print(f"  Waiting {RETRY_DELAY}s before retry...", flush=True)
                time.sleep(RETRY_DELAY)
            else:
                print(f"  {ch} GIVING UP after {MAX_RETRIES} attempts", flush=True)
