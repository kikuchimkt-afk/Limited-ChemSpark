"""Delete stale mp3 files for ch2-1 choices that were modified."""
import os

AUDIO_DIR = "audio/ch2-1"
MODIFIED_CHOICES = [
    "ch2_1_q002_c1", "ch2_1_q003_c1",
    "ch2_1_q004_c1", "ch2_1_q004_c3", "ch2_1_q004_c4",
    "ch2_1_q005_c1", "ch2_1_q005_c2", "ch2_1_q005_c3",
    "ch2_1_q006_c1", "ch2_1_q006_c2", "ch2_1_q006_c3",
    "ch2_1_q007_c4",
    "ch2_1_q010_c1",
    "ch2_1_q011_c1",
    "ch2_1_q015_c1",
    "ch2_1_q016_c2",
    "ch2_1_q017_c1",
    "ch2_1_q018_c3",
    "ch2_1_q020_c4",
    "ch2_1_q021_c2",
    "ch2_1_q022_c3",
    "ch2_1_q023_c2", "ch2_1_q023_c3",
    "ch2_1_q025_c1", "ch2_1_q025_c2",
    "ch2_1_q026_c3",
    "ch2_1_q027_c4",
    "ch2_1_q030_c1",
    "ch2_1_q033_c2",
    "ch2_1_q034_c2", "ch2_1_q034_c3", "ch2_1_q034_c4",
    "ch2_1_q036_c1",
    "ch2_1_q037_c1", "ch2_1_q037_c3", "ch2_1_q037_c4",
    "ch2_1_q046_c2",
    "ch2_1_q048_c1", "ch2_1_q048_c3",
]

deleted = 0
for cid in MODIFIED_CHOICES:
    # Extract question folder name (e.g., ch2_1_q002 from ch2_1_q002_c1)
    parts = cid.rsplit("_", 1)
    qdir = parts[0]
    mp3 = os.path.join(AUDIO_DIR, qdir, f"{cid}.mp3")
    if os.path.exists(mp3):
        os.remove(mp3)
        deleted += 1
        print(f"  deleted: {mp3}")
    else:
        print(f"  not found: {mp3}")

print(f"\nDeleted {deleted} stale mp3 files")
