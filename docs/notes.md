# Notes and results log

One line per experiment: date, task, what changed, measured score, verdict. Record failures too.

## 2026-11-01

- Environment: WSL2 Ubuntu 24.04, Python 3.12, Qualtran 0.7.0, kickmix 1.0.0 (installed and imports).
- Competition data unpacked to `~/gq-compilation/data` (995 MB). `dqi.kmb` baseline is 886 MB: memory-heavy.
- Baseline `invsqrt` verification (full default check, 200,540,928 shots, 18 min 36 s wall, 74 min CPU on 4 cores):
  **PASS**, score 2,076,774.23 = 260 qubits x 7,987.59 Toffoli-equivalents
  (7,735 Toffolis + 37 rotations, rotation eps 1.5e-12, 1 T gate). Worst error is 0.477 of the
  tolerance, so about half of the allowed error is unused: possible room to trade accuracy for cost.
  Circuit sha256 e2bf8eb6...ca321e1.
- A public repo quotes a different `invsqrt` starting point (237 qubits, 7,334 gates); our sample
  file is 260 qubits and 7,735 Toffolis, so compare against our own baseline only.
- Public information seen: top leaderboard scores around 27; a public repo claims 22.8 with a
  portfolio of public Apache-2.0 circuits; another reports 1.1175 with small gains.
  Check the Rules tab before reusing other people's code.

## 2026-11-02: dqi baseline

- `dqi.kmb` (886 MB) loads in 1.4 s and 858 MB peak memory (tested under a 4 GB cap): 1,893 qubits,
  86,051,014 operations, 5,725,461 Toffoli-like gates statically, 4,165 registers.
- Official verifier on the baseline: **PASS**, 102,400 shots, 0 value errors, 0 phase errors, error-rate
  upper bound 8.66e-4 (limit 1/16), repetition factor R = 1.1913, score 24,439,463,583,672.93.
  Wall time 4 min 54 s on 4 threads (15 min 44 s CPU). circuit sha256 959471d0...cc04995.
- Reading of the formula: score = R x Q^2 x T. R can only fall from 1.19 to 1.0, so qubits (squared) and
  Toffolis are the real levers; halving the qubit count alone would divide the score by about 4.

## Baseline scores

| Task | Baseline raw score | Source |
|---|---|---|
| invsqrt | 2,076,774.23 (Q=260, C=7,987.59) | local verifier, 2026-11-01 |
| dqi | 24,439,463,583,672.93 (R=1.1913, Q=1,893, T=5,725,108.4 Toffolis) | local verifier, 2026-11-02 |
| dfthcsos | TODO | local verifier |

## Experiments

| Date | Task | Change | Score | Verdict |
|---|---|---|---|---|
| 2026-11-02 | invsqrt | `tasks/invsqrt/sweep_precision.py`: coordinate descent on the five `Precision` bit-widths (14/17/28/28/29 -> 13/17/27/28/28) | estimated 1,989,316.5 (Q=258, 7,461 Toffolis, 36 rotations, error 0.789 of tolerance); baseline 2,076,774.2, so about 4.2% better | Estimator reproduces the official baseline exactly (3 s per evaluation vs 18 min). **Official verification: PASS**, score 1,989,316.54 (matches the estimate exactly; ratio vs baseline 1.0440; Q=258, 7,461 Toffolis, 36 rotations, rotation eps 9.1e-13, worst error 0.789 of tolerance, 200,540,928 shots, sha256 04b0c7bb...f8eda09). Wall time was 592 min but CPU time only 92 min: the laptop slept and paused the job, so keep it awake on AC power. Single-bit moves are exhausted; larger gains need structural changes. |
