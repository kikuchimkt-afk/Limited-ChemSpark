"""Delete stale mp3 files for ch2-2 choices that were modified."""
import os

AUDIO_DIR = "audio/ch2-2"
MODIFIED_CHOICES = [
    "ch2_2_q001_c1", "ch2_2_q001_c2", "ch2_2_q001_c4",
    "ch2_2_q002_c1", "ch2_2_q002_c2",
    "ch2_2_q003_c1", "ch2_2_q003_c2", "ch2_2_q003_c4",
    "ch2_2_q004_c1", "ch2_2_q004_c3", "ch2_2_q004_c4",
    "ch2_2_q005_c1", "ch2_2_q005_c2", "ch2_2_q005_c3",
    "ch2_2_q006_c1", "ch2_2_q006_c2", "ch2_2_q006_c3",
    "ch2_2_q007_c1",
    "ch2_2_q008_c1",
    "ch2_2_q009_c4",
    "ch2_2_q010_c1",
    "ch2_2_q011_c1", "ch2_2_q011_c4",
    "ch2_2_q012_c2", "ch2_2_q012_c4",
    "ch2_2_q013_c2", "ch2_2_q013_c4",
    "ch2_2_q015_c1",
    "ch2_2_q017_c1", "ch2_2_q017_c3",
    "ch2_2_q018_c2",
    "ch2_2_q019_c1",
    "ch2_2_q020_c1",
    "ch2_2_q021_c1", "ch2_2_q021_c2", "ch2_2_q021_c3",
    "ch2_2_q027_c1", "ch2_2_q027_c4",
    "ch2_2_q031_c4",
    "ch2_2_q032_c2",
    "ch2_2_q036_c1",
    "ch2_2_q041_c2", "ch2_2_q041_c3",
    "ch2_2_q042_c2", "ch2_2_q042_c3",
    "ch2_2_q043_c1",
    "ch2_2_q044_c4",
    "ch2_2_q046_c2", "ch2_2_q046_c3", "ch2_2_q046_c4",
    "ch2_2_q047_c2",
    "ch2_2_q048_c3", "ch2_2_q048_c4",
    "ch2_2_q050_c4",
]

deleted = 0
for cid in MODIFIED_CHOICES:
    parts = cid.rsplit("_", 1)
    qdir = parts[0]
    mp3 = os.path.join(AUDIO_DIR, qdir, f"{cid}.mp3")
    if os.path.exists(mp3):
        os.remove(mp3)
        deleted += 1

print(f"Deleted {deleted} stale mp3 files")
