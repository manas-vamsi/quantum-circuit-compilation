# Quantum circuit compilation (Kaggle: Google Quantum AI)

Working repository for the Kaggle competition
[Google Quantum AI - Verifiable Quantum Circuit Compilation](https://www.kaggle.com/competitions/google-verifiable-quantum-circuit-compilation/overview).
Goal: make three fault-tolerant quantum subroutines cheaper (fewer qubits and Toffoli gates)
while a classical verifier still accepts them. Final submission deadline: 2027-01-20, 23:59 UTC.

This repository is **public**. It contains our own scripts, notes and measurements only; the
competition data is not included. Check the competition Rules tab for what may be shared and
for the licence terms that apply to prize-winning submissions. No licence file has been chosen
yet, so by default all rights are reserved until one is added.

## What is here

- `docs/scoring.md`: how each task is scored, written from the official verifier files.
- `docs/notes.md`: a dated log of what was tried and the measured scores.
- `scripts/`: set-up and verification helpers (run inside WSL / Linux).
- `tasks/`: one folder per task (`invsqrt`, `dqi`, `dfthcsos`) for our own circuit generators.

## What is NOT here (on purpose)

The competition data is not committed. It is large (the baseline `dqi.kmb` is 886 MB, over
GitHub's 100 MB file limit) and belongs to the competition. Download it from the Kaggle
**Data** tab and unpack it to `~/gq-compilation/data` (inside WSL). Expected layout:

```text
~/gq-compilation/data/
  kickmix/            prebuilt kickmix and its licence
  sample_submission/  baseline circuits for all three tasks
  verifiers/          official verification and scoring code
```

## Set up (Windows + WSL2, Ubuntu 24.04)

1. Once, as root: `wsl -d Ubuntu -u root -- apt-get install -y python3.12-venv python3-pip`
2. In WSL: `bash scripts/setup_wsl.sh` (creates `~/gq-compilation/.venv`, installs Qualtran and kickmix).
3. Does an `invsqrt` circuit work? Quick test on 64 inputs (seconds), readable output:
   `python tasks/invsqrt/check_works.py path/to/invsqrt.kmb`
   Run `python tasks/invsqrt/check_works.py --selftest` to see that the test passes a good circuit
   and catches a deliberately broken one.
4. Full official check (all 3.1 million inputs, 18+ minutes of CPU, keep the laptop awake):
   `bash scripts/verify_invsqrt.sh path/to/invsqrt.kmb`
   To run it in the background (survives closing the window), type these three short lines one at a
   time. Do not paste one long command that wraps onto two lines: a line break inside it breaks the command.

   ```bash
   S=/mnt/c/Users/manas/quantum-circuit-compilation/scripts
   cd ~/gq-compilation
   setsid nohup bash $S/verify_invsqrt.sh work/invsqrt_sweep_best.kmb > logs/my_invsqrt.log 2>&1 &
   ```

   Then check `pgrep -af verify_submission` (running?) and, after about 20 minutes, `cat logs/my_invsqrt.log`.
   Adding `--max-x 65536` to the circuit path gives a 20-second smoke test; its score is NOT the real score.
5. Fast score estimate for bit-width changes (3 seconds): `python tasks/invsqrt/sweep_precision.py --baseline-only`

WSL clears `/tmp` on restart, so keep everything under `~/gq-compilation`.

## Submission rule to remember

The submission zip must contain all three tasks every time (`invsqrt`, `dqi`, and the
`dfthcsos` folder). Improve one task at a time and keep the other two at baseline until
they are done. Scoring on Kaggle takes about 45 minutes, so verify locally first.

## Status

See `docs/notes.md`.
