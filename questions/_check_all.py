"""Run every checkpoint for a chapter in one command.

This is the *canonical* quality gate. Run it at every checkpoint in the
WORKFLOW.md pipeline. If it prints ``ALL CHECKS PASSED``, the chapter is
in a valid state and you may proceed to the next step.

Checks performed (in order):
  1. ``_validate.py``             — schema + TTS + display-form audit
  2. ``_list_rewrite_targets.py`` — no 選択肢N (kanji) in tts_explanation
  3. ``_length_report.py``        — no correct-vs-wrong length bias
  4. ``_audit_display.py``        — double-check display form (already
                                    enforced by _validate.py, run here
                                    for a clear per-check report)

This script is a thin orchestrator. It does NOT implement new checks —
if you need a new check, add it to the appropriate underlying script so
_check_all.py picks it up automatically.

Usage::

    python questions/_check_all.py ch1-2
    python questions/_check_all.py ch1-2 --strict     # also fail on length-bias
    python questions/_check_all.py ch1-2 --no-length  # skip the length check

Exit code: 0 if every check passes (respecting --strict/--no-length), 1
otherwise.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = Path(__file__).parent
PY = sys.executable


def run(label: str, cmd: list[str]) -> tuple[int, str]:
    print(f"--- {label} -----------------------------------------")
    print(f"$ {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    stdout = r.stdout or ""
    stderr = r.stderr or ""
    out = stdout + stderr
    print(out.rstrip())
    print(f"(exit={r.returncode})")
    print()
    return r.returncode, out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("chapter")
    p.add_argument("--strict", action="store_true",
                   help="treat length-bias findings as failure")
    p.add_argument("--no-length", action="store_true",
                   help="skip the length-bias report")
    args = p.parse_args()

    chapter = args.chapter
    failures: list[str] = []

    rc, _ = run(
        "VALIDATE (schema + TTS + display)",
        [PY, str(HERE / "_validate.py"), chapter],
    )
    if rc != 0:
        failures.append("_validate.py")

    rc, out = run(
        "CHOICE-REF CHECK (tts_explanation must not contain 選択肢N)",
        [PY, str(HERE / "_list_rewrite_targets.py"), chapter],
    )
    if "targets=0/" not in out:
        failures.append("_list_rewrite_targets.py")

    rc, _ = run(
        "DISPLAY AUDIT (to_display(tts_*) == display)",
        [PY, str(HERE / "_audit_display.py"), chapter],
    )
    if rc != 0:
        failures.append("_audit_display.py")

    if not args.no_length:
        rc, out = run(
            "LENGTH BIAS REPORT",
            [PY, str(HERE / "_length_report.py"), chapter],
        )
        if args.strict:
            if "Length-biased (diff>=10): 0 questions" not in out:
                failures.append("_length_report.py (strict)")

    print("=" * 60)
    if failures:
        print(f"FAILED checks for {chapter}: {', '.join(failures)}")
        print("Fix the errors above before proceeding.")
        return 1

    print(f"ALL CHECKS PASSED for {chapter}.")
    if not args.strict:
        print("(Length-bias warnings above are informational; use "
              "--strict to gate on them.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
