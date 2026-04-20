# Agent Guide

**Read `WORKFLOW.md` in full before doing anything.** It is prescriptive:
every non-authoring step is a single named Python script with a single
command. Follow it verbatim.

## One command to rule them all

At every checkpoint, run:

```powershell
python questions\_check_all.py <chapter>
```

It chains `_validate.py`, `_list_rewrite_targets.py`,
`_audit_display.py`, and `_length_report.py` in order and prints a
single pass/fail summary. When it says `ALL CHECKS PASSED`, proceed.
Otherwise fix the errors and re-run it until it passes.

## Hard rules

1. **Do not invent commands.** If a step is not listed in `WORKFLOW.md`
   Section 3 or the Script Reference (Section 4), it is not part of the
   pipeline. Do NOT run `python -c ...`, heredocs, inline one-liners,
   `sed`, `awk`, or ad-hoc shell scripts to mutate `questions/*.json` or
   audio files. If you need a new operation, add a real `.py` file under
   `questions/` or `audio/`, document it in `WORKFLOW.md`, and then run
   it.
2. **Do not skip the quality gate.** Run `python questions\_check_all.py
   <chapter>` at every checkpoint prescribed by Section 3.
3. **Do not run legacy scripts** (`_restructure_ch1_1.py`, `_pad_wrongs.py`,
   `_rewrite_tts_explanations_ch1_1.py`, `_make_display.py`,
   `_fix_tts.py`, `_fix_chains.py`) on any chapter other than `ch1-1`.
   They are frozen historical records. Always use the `_chapter.py`
   generalized variants.
4. **Do not edit `questions/*.json` by hand** to apply structural
   changes. Persist edits as data under `questions/_rewrites/<chapter>.json`
   or `questions/_pads/<chapter>.json` and apply them via
   `_rewrite_explanations.py` / `_pad_wrongs_chapter.py`. That keeps the
   pipeline reproducible.
5. **Do not change TTS conventions.** TTS fields never contain chemical
   formulas, degree/percent symbols, math symbols, equations, or
   `選択肢N`. Display fields may use `NaCl`, `CO₂`, `℃`, `%`, `g/mol`,
   and Arabic `選択肢N` (the app remaps them).
6. **Do not mix authoring paths.** Pick Path A or Path B (see below)
   and stick with it for the whole chapter.

## Two accepted authoring paths

`WORKFLOW.md` §3 defines two valid ways to produce a chapter JSON:

- **Path A — raw-form authoring**: write in TTS-friendly form only,
  run `_restructure_chapter.py` to shuffle + split.
- **Path B — post-restructure authoring**: write both display and TTS
  sides, `choice_id`, balanced correct positions — skip
  `_restructure_chapter.py`.

Both paths MUST pass `_check_all.py`. If Path B produces `[DISP]`
errors, run `python questions\_audit_display.py <chapter> --apply` to
auto-fix the display side from the TTS source.

## Canonical per-chapter pipeline

Run these in order. No deviation. See `WORKFLOW.md` Section 3 for full
detail on each.

```powershell
# 1. Author (manual)
Copy-Item questions\_template.json questions\<chapter>.json
# ... fill in 50 questions, Path A or Path B ...

# 2. Validate authoring
python questions\_check_all.py <chapter>

# 3. Restructure (Path A only; skip for Path B)
python questions\_restructure_chapter.py <chapter>

# 4. Validate restructured
python questions\_check_all.py <chapter>

# 5. (Optional) Length bias
python questions\_dump_for_pads.py <chapter> > _tmp\<chapter>_pad_input.txt
#   draft questions\_pads\<chapter>.json using that file
python questions\_pad_wrongs_chapter.py <chapter>
python questions\_check_all.py <chapter>

# 6. Rewrite stale tts_explanation
python questions\_list_rewrite_targets.py <chapter>
python questions\_dump_for_rewrite.py <chapter> > _tmp\<chapter>_rewrite_input.txt
#   draft questions\_rewrites\<chapter>.json using that file
python questions\_rewrite_explanations.py <chapter> --dry-run
python questions\_rewrite_explanations.py <chapter>
python questions\_check_all.py <chapter>

# 7. Audio
python audio\_generate.py <chapter> all
python audio\_regen_explanations.py <chapter>

# 8. Enable in js/app.js CHAPTERS (manual)
# 9. Smoke test (manual)
```

## Runtime contract

- Audio is pre-generated at Edge TTS rate `-10%`; app plays back at
  `1.0x` / `1.11x` / `1.25x` via `HTMLAudioElement.playbackRate`.
- Choices are stored balanced across positions 1–4 and re-shuffled at
  runtime using `choice_id`.
- Display `explanation` references (`選択肢N` in Arabic) are remapped at
  render time by `js/app.js :: remapChoiceRefs`. TTS (`tts_explanation`)
  cannot be remapped at runtime — that is why it must be content-based.

If in doubt, re-read `WORKFLOW.md`. Do not improvise.
