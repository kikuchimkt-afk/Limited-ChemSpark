# Chapter Authoring Workflow

This document is the **single source of truth** for producing a new chapter
of the Chemistry Exam Training app. It is written as a **prescriptive
pipeline**: every non-authoring step is one named Python script called
with one command. Do NOT run ad-hoc `python -c ...` snippets, do NOT try
to "be clever" — if a step is not listed below, it is not part of the
pipeline. If you find yourself needing a new operation, add it as a
dedicated script under `questions/` or `audio/` and then update this
file.

The reference implementation is `ch1-1` (50 questions, audio complete).
Chapter `ch1-2` was produced with the exact procedure below.

---

## 0. Prerequisites

- Python 3.10+ on PATH.
- `pip install edge-tts` once per environment.
- Windows PowerShell (shell examples use PowerShell). On POSIX shells,
  replace `\` with `/` in script paths. Every Python script is
  cross-platform.
- Stable network access (Edge TTS is an online service).

Local preview server:

```powershell
python serve.py             # serves http://localhost:8000
```

---

## 1. Data model (authoritative)

A chapter JSON lives at `questions/<chapter>.json`. The schema below is
the **post-restructure** form — i.e., what validators and the browser
consume. During authoring (Step 3.1) you write the *raw* form, and
`_restructure_chapter.py` fills in the rest.

```jsonc
{
  "metadata": {
    "chapter": "1-2",
    "chapter_title": "粒子の結合",
    "total_questions": 50,
    "display_policy": { /* auto-filled by _restructure_chapter.py */ },
    "choice_shuffle_policy": { /* auto-filled */ }
  },
  "questions": [
    {
      "id": "ch1_2_q001",                 // snake_case id, unique per file
      "chapter": "1-2",
      "category": "definition|property|classification|procedure|confusion|mnemonic|comprehensive",
      "sub_category": "共有結合の定義",
      "difficulty": 1,                     // 1-3 (★★★)
      "question_type": "correct",          // "correct" | "incorrect"
      "question":      "問題文 (DISPLAY: アラビア数字・単位記号・化学式)",
      "tts_question":  "問題文 (TTS: 漢数字・単位語・日本語化学名)",
      "choices": [
        {
          "label": "1",                    // always "1".."4"
          "choice_id": "ch1_2_q001_c1",    // stable id; <qid>_c<n>
          "text":     "選択肢本文 (DISPLAY)",
          "tts_text": "選択肢本文 (TTS)",
          "is_correct": false,
          "trap_type": "concept_confusion",
          "trap_detail": "単体の定義にすり替えたひっかけ"
        }
        /* ...4 choices total, exactly one is_correct:true */
      ],
      "explanation":     "解説 (DISPLAY, 選択肢N はアラビア数字; アプリが実行時にシャッフル後の位置へ再写像)",
      "tts_explanation": "解説 (TTS, 選択肢N禁止・内容ベースで言及)",
      "evidence": [
        { "source_id": "1_2_def_001", "quote": "原文の引用" }
      ],
      "mnemonic": null,
      "audio_voice": "ja-JP-NanamiNeural"  // assigned by audio/_generate.py
    }
  ]
}
```

### Display vs TTS split

| Convention  | Display fields                       | TTS fields (`tts_*`)                         |
|-------------|--------------------------------------|----------------------------------------------|
| Numbers     | Arabic (`100`, `0.79`, `-115`)       | Kanji (`百`, `零点七九`, `マイナス百十五`)   |
| Units       | Symbols (`℃`, `%`, `g`, `mol`, `cm³`)| Japanese words (`度`, `パーセント`, `グラム`)|
| Compounds   | `NaCl`, `CO₂`, `MgCl₂` (subscripts)  | Japanese names (`塩化ナトリウム`)            |
| Elements    | Japanese (`酸素`, `水素`)            | Japanese (same)                              |
| Formulae / math | Allowed in display                | **Forbidden** — validator rejects            |
| `選択肢N`   | Arabic (app remaps)                  | **Forbidden** — rewrite to content-based    |

### Choice ordering policy

- JSON stores choices **balanced across positions 1–4** across the chapter.
- Browser app (`js/app.js`) **additionally shuffles at runtime**; the
  `choice_id` field tracks correctness regardless of display order.
- `tts_explanation` must therefore never reference choice positions.

---

## 2. Directory layout

```
Chemistry-Exam-Training/
├── index.html, css/, js/, serve.py    # web app
├── AGENTS.md, WORKFLOW.md             # guidance
├── questions/
│   ├── ch1-1.json .. ch6-3.json       # chapter data
│   ├── _template.json                 # skeleton to copy when authoring
│   ├── _rewrites/<chapter>.json       # tts_explanation rewrites
│   ├── _pads/<chapter>.json           # wrong-choice padding
│   ├── _restructure_chapter.py        # one-time restructure (shuffle+split)
│   ├── _pad_wrongs_chapter.py         # apply length-bias padding
│   ├── _rewrite_explanations.py      # apply tts_explanation rewrites
│   ├── _length_report.py             # diagnostic: length bias
│   ├── _list_rewrite_targets.py      # diagnostic: ids needing rewrite
│   ├── _dump_for_rewrite.py          # dump context for rewrite drafting
│   ├── _dump_for_pads.py             # dump context for pad drafting
│   ├── _reset_voices.py              # clear audio_voice (rarely needed)
│   ├── _validate.py                  # schema + TTS checks
│   └── (legacy ch1-1-specific scripts, historical reference only)
└── audio/
    ├── common/<voice>/choice_prefix_{1..4}.mp3
    ├── <chapter>/<qid>/question.mp3 / <cid>.mp3 / explanation.mp3
    ├── _generate.py                   # main audio synthesis
    └── _regen_explanations.py         # refresh explanation.mp3 after rewrites
```

Never delete the `_rewrites/` and `_pads/` JSON files — they document
what structural edits were applied and must exist to re-run the pipeline.

---

## 3. Per-chapter pipeline (prescriptive)

Replace `ch1-2` below with the target chapter id throughout. **Run the
commands in order. Do not skip or reorder steps.**

### Canonical quality gate (run at every checkpoint)

```powershell
python questions\_check_all.py ch1-2
```

This runs `_validate.py`, `_list_rewrite_targets.py`,
`_audit_display.py`, and `_length_report.py` back-to-back. When it
prints `ALL CHECKS PASSED`, the chapter is in a valid state and you may
proceed. Use `--strict` to also fail on length bias.

### Two accepted authoring paths

There are two valid ways to produce `questions/<chapter>.json`. Pick one:

**Path A — Raw-form authoring (recommended for new chapters)**
Write the file in pre-restructure shape and run the structural
pipeline (Steps 3.1 → 3.4). Fast to author; the scripts do the heavy
lifting (shuffling, choice_id assignment, TTS/display split).

**Path B — Post-restructure authoring (for AI-generated chapters)**
Write the file already in post-restructure shape (`tts_*`, `choice_id`,
balanced correct positions all present). Skip Step 3.3 and go directly
to Step 3.4. The quality gate will enforce that the display fields and
TTS fields are internally consistent; any misses are auto-fixable via
`_audit_display.py --apply`.

Either way, every downstream step (3.5–3.10) is identical.

### Step 3.1. Author `questions/<chapter>.json`

This is the only step that requires drafting.

1. Copy the skeleton:

   ```powershell
   Copy-Item questions\_template.json questions\ch1-2.json
   ```

2. Fill in `metadata.chapter`, `chapter_title`, `source_file`,
   `category_distribution`, and the 50-question `questions[]` array.

**If using Path A (raw-form authoring):**
   - Write all strings in **TTS-friendly form** (漢数字・単位語・日本語化学名).
   - Exactly 4 choices; exactly one `is_correct:true`.
   - May refer to wrong choices in `explanation` as `選択肢一`..`選択肢四`
     (kanji, ORIGINAL positions).
   - Do NOT set `tts_*`, `choice_id`, or `audio_voice` — Step 3.3
     generates them.

**If using Path B (post-restructure authoring):**
   - Balance correct-answer positions across slots 1–4 yourself
     (target ≈ `total_questions/4` per slot).
   - For every question, write **both** the display fields
     (`question` / `choices[].text` / `explanation`) **and** the TTS
     fields (`tts_question` / `choices[].tts_text` / `tts_explanation`).
   - Display fields use Arabic numerals, unit symbols, chemical formulas
     (see `display_policy` in `ch1-2.json` for the mapping).
   - TTS fields use kanji numerals, Japanese unit words, Japanese
     compound names; no formulas / symbols / `選択肢N`.
   - Assign each choice `choice_id = "<qid>_c<n>"`.
   - Include `metadata.display_policy` and `metadata.choice_shuffle_policy`
     (copy them verbatim from `ch1-1.json` / `ch1-2.json`).
   - Do NOT set `audio_voice` — Step 3.7 assigns it.

Reference: mirror the style of `questions/ch1-1.json` /
`questions/ch1-2.json` (trap annotations, evidence, metadata block).

### Step 3.2. Validate raw authoring

```powershell
python questions\_check_all.py ch1-2
```

At this stage the validator still accepts the pre-restructure form (no
`tts_*` / `choice_id` required). Expected: `ALL CHECKS PASSED`. Fix
anything reported before proceeding.

Skip Step 3.3 if you chose **Path B** (post-restructure authoring); go
straight to Step 3.4.

### Step 3.3. Restructure (shuffle + TTS/display split) — Path A only

**This step is one-way and idempotent-guarded.** The script refuses to
run if the file already contains `tts_*` fields (Path B users should
skip this step entirely). Back up first if you expect to iterate.

```powershell
python questions\_restructure_chapter.py ch1-2
```

What it does:
1. Shuffles each question's choices so correct-answer positions are
   evenly distributed across slots 1–4 (seed `20260420`; pass
   `--seed N` to change).
2. Assigns `choice_id = <qid>_c<n>`.
3. Remaps `選択肢N` in `explanation` to the new positions.
4. Moves original text into `tts_*` and writes DISPLAY forms with
   Arabic numerals, unit symbols, and major chemical formulas.
5. Adds `display_policy` / `choice_shuffle_policy` to metadata.

### Step 3.4. Re-validate (post-restructure)

```powershell
python questions\_check_all.py ch1-2
```

The quality gate now enforces the full restructured schema, including
the display-form audit (`[DISP]` errors). Expected failures remaining
after this step — and the specific sub-steps that resolve them — are
documented below.

| Error | Resolution step |
|-------|-----------------|
| `[TTS] … tts_*: chemical formula / unit symbol / ℃ / %` | Edit `tts_text` to Japanese equivalent; re-run the quality gate. |
| `[DISP] … differs from to_display(tts_*)` | `python questions\_audit_display.py ch1-2 --apply` (auto-rewrites the display field). |
| `[REF] … tts_explanation contains '選択肢四'` | Go to Step 3.6. |
| `[ID] … choice_id=None` | Path A: restore a backup and re-run Step 3.3. Path B: assign `choice_id` yourself. |
| Length-bias row in the report | Go to Step 3.5 (optional). |

| Error | Resolution step |
|-------|-----------------|
| `[TTS] … tts_*: chemical formula / unit symbol / ℃ / %` | Edit `tts_text` to Japanese equivalent, re-run validate. |
| `[REF] … tts_explanation contains '選択肢四'` | Go to Step 3.6. |
| `[ID] … choice_id=None` | Restore a backup and re-run Step 3.3. |

### Step 3.5. Fix length bias in wrong choices (optional)

Diagnose:

```powershell
python questions\_length_report.py ch1-2
```

If any question is reported as "length-biased" (correct ≥ 10 chars
longer than every wrong), produce drafting context:

```powershell
New-Item -ItemType Directory -Force -Path _tmp | Out-Null
python questions\_dump_for_pads.py ch1-2 > _tmp\ch1-2_pad_input.txt
```

Read `_tmp/ch1-2_pad_input.txt` and author `questions/_pads/ch1-2.json`
in this exact shape (keys = question ids, inner map = old `tts_text` →
new `tts_text` of wrong choices only):

```json
{
  "ch1_2_q006": {
    "<current tts_text of a wrong choice>": "<new tts_text, longer>"
  }
}
```

Apply and re-verify:

```powershell
python questions\_pad_wrongs_chapter.py ch1-2
python questions\_check_all.py ch1-2
```

If the report still flags questions, iterate on `_pads/ch1-2.json`.

`_pad_wrongs_chapter.py` **automatically deletes the stale
`audio/<chapter>/<qid>/<choice_id>.mp3` files of the modified choices** so
that the next `python audio/_generate.py <chapter> all` run regenerates
them. If you want to keep the existing mp3 files for any reason (e.g. you
intend to batch-delete them manually), pass `--keep-audio`:

```powershell
python questions\_pad_wrongs_chapter.py ch1-2 --keep-audio
```

Do NOT skip the mp3 deletion step. `audio/_generate.py` uses file
existence as its only skip check and will silently keep the old audio
otherwise.

### Step 3.6. Rewrite `tts_explanation` to remove `選択肢N`

Only `tts_explanation` (audio) needs this; the displayed `explanation`
is remapped at runtime by `js/app.js :: remapChoiceRefs`.

List affected ids:

```powershell
python questions\_list_rewrite_targets.py ch1-2
```

Produce drafting context:

```powershell
New-Item -ItemType Directory -Force -Path _tmp | Out-Null
python questions\_dump_for_rewrite.py ch1-2 > _tmp\ch1-2_rewrite_input.txt
```

Read `_tmp/ch1-2_rewrite_input.txt` and author
`questions/_rewrites/ch1-2.json` in this exact shape (keys MUST include
every id listed in Step 3.6a above; add more if you want to rephrase
others):

```json
{
  "ch1_2_q001": "選択肢N を一切含まない新しい tts_explanation 本文",
  "ch1_2_q002": "..."
}
```

Rules (enforced by `_rewrite_explanations.py` and re-checked by
`_validate.py`):
- MUST NOT contain `選択肢一`..`選択肢九`.
- Refer to choice CONTENT instead: `『一種類の元素からなる純物質』は単体の定義`.
- Preserve TTS conventions (漢数字・単位語・日本語化学名・記号禁止).

Apply and verify:

```powershell
python questions\_rewrite_explanations.py ch1-2 --dry-run
python questions\_rewrite_explanations.py ch1-2
python questions\_check_all.py ch1-2
```

The final quality gate should report `ALL CHECKS PASSED`.

**Critical format rule:** The rewrite JSON values MUST be plain strings,
not nested objects. Correct:

```json
{ "ch1_2_q001": "新しい解説テキスト" }
```

Incorrect (will silently corrupt the chapter JSON):

```json
{ "ch1_2_q001": { "tts_explanation": "新しい解説テキスト" } }
```

If you accidentally apply a malformed rewrite, restore the chapter JSON
from git (`git checkout -- questions/<chapter>.json`), fix the rewrite
file, and re-apply.

### Step 3.6b. Manual content verification

After all automated checks pass, manually verify the educational
quality of each question. This step catches issues that automated
validators cannot detect.

**Checklist** (read through all 50 questions):

1. **No `選択肢N` in display `explanation`** — although the app remaps
   these at runtime, verify none slipped through by searching the file:

   ```powershell
   Select-String '選択肢' questions\ch1-2.json
   ```

2. **Explanation covers ALL choices** — for each question, verify that
   `tts_explanation` explains:
   - Why the correct answer is correct (with evidence).
   - Why each incorrect answer is wrong (at least the key error).
   - Rate each question: ✅ sufficient, ⚠️ partial, ❌ missing.

3. **Scientific accuracy** — verify that correct answers are factually
   accurate and that incorrect answers' `trap_detail` correctly
   identifies the error.

4. **Incorrect choice quality** — verify that wrong choices do not
   contain embedded mini-explanations that give away the answer (e.g.
   "…であるため還元性を持たない非還元糖に分類される" is acceptable
   as an elaborated wrong claim, but should not accidentally teach the
   correct concept).

If explanations need improvement, add entries to
`questions/_rewrites/<chapter>.json` and re-apply:

```powershell
python questions\_rewrite_explanations.py ch1-2 --dry-run
python questions\_rewrite_explanations.py ch1-2
python questions\_check_all.py ch1-2
```

Note: this step only updates `tts_explanation`. The display-side
`explanation` field must be edited separately if you want it to match
(the display field is what users read on screen; `tts_explanation` is
what gets synthesized to audio).

### Step 3.7. Generate audio

```powershell
pip install edge-tts         # once per environment
python audio\_generate.py ch1-2 all
```

The script:
- Assigns each question a random voice (Nanami / Keita) on first run
  and persists it as `audio_voice`.
- Generates `audio/common/<voice>/choice_prefix_{1..4}.mp3` once per
  voice.
- Generates `audio/ch1-2/<qid>/question.mp3`,
  `<choice_id>.mp3` × 4, `explanation.mp3`.
- Skips files that already exist (safe to re-run / interrupt).

**Important:** `_generate.py` detects *missing* files, not *stale*
ones. Whenever you re-run `_pad_wrongs_chapter.py` or
`_rewrite_explanations.py` / `_regen_explanations.py`, the stale mp3
files must be deleted **before** `_generate.py` (the padding script
does this automatically; the rewrite-explanations flow is handled by
`audio/_regen_explanations.py`). If you edit a `tts_*` field manually,
delete the corresponding mp3 yourself (see the "Quick fix" example at
the bottom of this document).

Partial runs:

```powershell
python audio\_generate.py ch1-2 1-10
python audio\_generate.py ch1-2 25
```

### Step 3.8. Regenerate stale `explanation.mp3`

Only needed if Step 3.6 rewrote any explanations (it usually does).

```powershell
python audio\_regen_explanations.py ch1-2
```

This reads `questions/_rewrites/ch1-2.json`, deletes the listed
`explanation.mp3` files, and re-synthesizes them.

### Step 3.9. Enable the chapter in the app

Edit `js/app.js`, find the `CHAPTERS` list, set `enabled: true` on the
new entry. Example:

```js
const CHAPTERS = [
  { id: 'ch1-1', title: '第1章-1 物質の構成', enabled: true },
  { id: 'ch1-2', title: '第1章-2 粒子の結合', enabled: true },
  ...
];
```

Preview:

```powershell
python serve.py      # open http://localhost:8000
```

### Step 3.10. Manual smoke test

- Start the chapter.
- Listen to question + choice audio on a couple of items.
- Answer correctly and incorrectly; verify the **displayed** explanation
  references line up with the shuffled on-screen positions.
- Listen to the explanation audio; confirm it does NOT say `選択肢N`.
- Toggle ゆっくり / ナチュラル / 早め speed during playback.
- Finish the chapter and check "カテゴリ別成績".

---

## 4. Script reference card

Every command below takes the chapter id (e.g. `ch1-2`) as a single
positional argument unless stated.

### Canonical entry point

| Script | Purpose |
|--------|---------|
| `questions/_check_all.py` | Run every quality check in order and print a single pass/fail summary. **This is the only command you need at each checkpoint.** Pass `--strict` to also gate on length bias, or `--no-length` to skip the length report. |

### Diagnostics / drafting helpers (read-only or local-only output)

| Script | Purpose |
|--------|---------|
| `questions/_validate.py`            | Schema + TTS + display-form checks (invoked by `_check_all.py`). |
| `questions/_audit_display.py`       | Verify `question` / `choices[].text` are in canonical DISPLAY form (Arabic numerals, unit symbols, chemical formulas). Pass `--apply` to auto-rewrite. |
| `questions/_length_report.py`       | List questions where the correct choice is much longer than every wrong choice. |
| `questions/_list_rewrite_targets.py`| Print ids whose `tts_explanation` still contains `選択肢N`. |
| `questions/_dump_for_rewrite.py`    | Print id + choices + current explanation for each target; pipe to a file and read it before drafting `_rewrites/<chapter>.json`. |
| `questions/_dump_for_pads.py`       | Print length-biased questions with each choice; pipe to a file and read it before drafting `_pads/<chapter>.json`. |

### Mutations (write back into `questions/<chapter>.json`)

| Script | Purpose | Prerequisite |
|--------|---------|--------------|
| `questions/_restructure_chapter.py` | One-time restructure: shuffle, choice_id, TTS/display split. | Raw authored file exists. |
| `questions/_pad_wrongs_chapter.py`  | Apply wrong-choice padding. | `questions/_pads/<chapter>.json` exists. |
| `questions/_rewrite_explanations.py`| Apply `tts_explanation` rewrites. | `questions/_rewrites/<chapter>.json` exists. |
| `questions/_reset_voices.py`        | Clear `audio_voice` for every question (rarely needed; e.g. to force re-assignment before mass re-sync). | — |

### Audio

| Script | Purpose |
|--------|---------|
| `audio/_generate.py <chapter> [range]` | Synthesize all missing question / choice / explanation MP3s. Incremental. `range` can be `all`, `N`, or `A-B`. |
| `audio/_regen_explanations.py <chapter>` | Delete & regenerate only the explanation MP3s listed in `questions/_rewrites/<chapter>.json`. Run after Step 3.6. |

### Serving

| Script | Purpose |
|--------|---------|
| `serve.py [port]` | Static file server for local preview; default port 8000. |

---

## 5. Runtime contract with `js/app.js`

If you change any of these assumptions, update the app in lockstep.

- Audio path for choice `N` in voice `V`:
  `audio/common/<V>/choice_prefix_<N>.mp3` followed by
  `audio/<chapter>/<qid>/<choice_id>.mp3`.
- Explanation path: `audio/<chapter>/<qid>/explanation.mp3`.
- Playback speeds use `HTMLAudioElement.playbackRate`. MP3s are
  synthesized at Edge-TTS rate `-10%`; `natural` speed uses `1.11x`.
  If you change the synthesis rate, update `SPEED_MAP` in `js/app.js`.
- `remapChoiceRefs` in `js/app.js` assumes `選択肢N` in `explanation`
  (display) refers to the 1-indexed position in `q.choices[]` as stored
  in JSON. Don't reorder choices after restructuring without re-running
  remap.

---

## 6. Completion checklist per chapter

Before marking a chapter done, run each command and confirm:

| Check | Command | Expected |
|-------|---------|----------|
| All content checks | `python questions\_check_all.py ch1-2 --strict` | `ALL CHECKS PASSED`. |
| Manual content verification | Section 3.6b | All explanations rated ✅. |
| All voices assigned | (manually) every question has `audio_voice`. |
| All MP3s exist | `audio/<chapter>/<qid>/` contains 6 files for every question. |
| Common prefixes | `audio/common/<voice>/choice_prefix_{1..4}.mp3` exists for every voice in use. |
| App enabled | `CHAPTERS` entry has `enabled: true`. |
| Smoke test | Section 3.10. |

---

## 7. Known limitations

- `_restructure_chapter.py` FORMULAS list is curated; add compounds as
  new chapters require them. Keep longer names earlier in the list so
  greedy matching stays correct.
- Edge TTS occasionally mispronounces rare compounds. If you hear an
  issue, edit the `tts_text`, delete the affected MP3, and re-run
  `audio\_generate.py`:

  ```powershell
  Remove-Item audio\ch1-2\ch1_2_q007\ch1_2_q007_c2.mp3
  python audio\_generate.py ch1-2 7
  ```

- There is no dedicated script to re-synthesize `question.mp3` /
  `<cid>.mp3` on `tts_*` edits. Delete the file and re-run
  `audio\_generate.py <chapter> <n>`.
- Legacy `*_ch1_1.py` scripts (`_restructure_ch1_1.py`, `_pad_wrongs.py`,
  `_rewrite_tts_explanations_ch1_1.py`, `_make_display.py`,
  `_fix_tts.py`, `_fix_chains.py`) are historical records. **Do not run
  them on other chapters.** Always use the `_chapter.py` / general
  variants listed in Section 4.
- `_rewrite_explanations.py` does **not validate** the shape of
  rewrite values. If you accidentally use `{"qid": {"tts_explanation":
  "..."}}`  instead of `{"qid": "..."}`, the script will silently write
  a dict object into `tts_explanation`, corrupting the chapter JSON.
  Always verify the rewrite file format before applying. If corruption
  occurs, restore the file with `git checkout -- questions/<chapter>.json`,
  fix the rewrite file, and re-run.
- `tts_explanation` and display `explanation` are independent fields.
  `_rewrite_explanations.py` only updates `tts_explanation`. If you
  want the display explanation to match, edit the chapter JSON by hand
  or add display-side edits as a separate manual step.
