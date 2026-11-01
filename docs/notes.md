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

## Baseline scores (fill in)

| Task | Baseline raw score | Source |
|---|---|---|
| invsqrt | 2,076,774.23 (Q=260, C=7,987.59) | local verifier, 2026-11-01 |
| dqi | TODO | local verifier |
| dfthcsos | TODO | local verifier |

## Experiments

| Date | Task | Change | Score | Verdict |
|---|---|---|---|---|
