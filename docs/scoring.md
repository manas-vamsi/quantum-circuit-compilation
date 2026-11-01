# How the competition is scored

Source: the official verifier files in the competition data, plus the Kaggle overview page.
Raw task scores are **lower is better**. Verification and costs come from the `kickmix`
simulator.

## Overall score

Each task's raw score is turned into a ratio (baseline / yours, our reading of "improvement
relative to a baseline"). The leaderboard score is the **geometric mean of the three ratios**.

Check against a public entrant's numbers: ratios 1.2648, 1.1034 and 1.0 give a geometric
mean of about 1.1175, matching the 1.11751 that entrant reports. An unchanged task counts as 1.0.

## invsqrt (fusion energy): score = Q x C

- Phase `beta / sqrt(x)` for every `x` in `[1, 3,133,452]` (22-bit `x` register, `beta = 1`),
  within `2^-24 * beta / sqrt(x)` relative tolerance.
- `x` must be restored and all scratch qubits must return to |0>.
- `Q` = qubits. `C` = Toffoli-like gates (`CCX`, `CCZ`, `CSWAP`) per shot + T-cost / 4.
- Rotations (`Z_POW`): Clifford angles are free, a T angle costs 1 T, other angles cost
  `0.56 log2(1/eps) + 5.3` T. The verifier gives rotations the largest `eps` that fits in the
  tolerance left over by the circuit's own error. A more accurate circuit makes rotations cheaper.
- Default check: 64 shots per `x` (about 200 million shots). Shots must be a multiple of the batch size (256).

## dqi (combinatorial optimization): score = R(eps) x Q^2 x T

- Reed-Solomon syndrome decoder over GF(2^b), with m = 4095, n = 70, degree 12, r = 2016.
- `S0..S{n-1}` restored, everything else returns to |0>, global phase multiplied by
  `(-1)^(sum_j popcount(e_j & M_j))`. `Z_POW` gates are not allowed.
- A one-sided Clopper-Pearson upper bound `eps_plus` on the failure rate (confidence
  `1 - 2^-128`) must be below 1/16. `R(eps) = ln 2 / -ln(1/2 + 2 sqrt(eps))`, so more failures cost more.
- `Q` enters **squared**: cutting qubits by 10% cuts this score by about 19%.
- Test inputs and measurement outcomes are seeded from the SHA-256 of the circuit file
  (merged with a salt), so results are deterministic per file but vary a little with the salt.
- Default 102,400 shots.

## dfthcsos (quantum chemistry): score = lambda_eff x T_total x Q_total

- FeMoCo76o113e: 76 orbitals, 113 electrons. Baseline factorization shape `R, B, C = 65, 60, 60`.
- `lambda_eff = sqrt(E_gap (2 Lambda - E_gap))`, `T_total` = ANGLES Toffolis + heuristic costs of
  the state preparations and Givens rotations, `Q_total` = persistent + temporary qubits.
- Rejected if: any ANGLE circuit uses more than 128 qubits; `error_1` or `error_2` exceed 20 mHa;
  the gap fails `0 < E_gap < 2 Lambda`; `Lambda <= 49.0`; or `E_gap <= 3.914898` Ha.
- Baseline (README): 13,757 Toffolis, 90 persistent and 544 temporary qubits at `brot = 12`.

## Practical consequences

- A failed verification means no score for that task: always keep a passing version.
- Qubits are the strongest lever for `dqi` (squared) and a direct factor for the other two.
- Leave a small margin on `dqi` for the salt-dependent variation.
