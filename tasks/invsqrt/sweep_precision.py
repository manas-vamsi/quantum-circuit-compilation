"""Search the bit-widths of the reference invsqrt circuit for cheaper circuits that still fit.

The reference generator (competition data, verifiers/invsqrt/nr_reference_circuit.py) has five
fixed-point bit-widths (`Precision`). Narrower registers mean fewer qubits and Toffolis but a
larger approximation error. This tool:

  1. measures the worst relative error over the whole input range with the generator's exact
     classical model (fast, no circuit simulation),
  2. counts qubits, Toffolis and rotations statically from the built circuit,
  3. estimates the score exactly the way the official verifier does:
        margin   = min over x of (2^-24 - rel_error(x)) / sqrt(x)        [turns]
        eps      = pi * margin / n_rot
        T_rot    = 0.56 * log2(1 / eps) + 5.3 per rotation
        C        = Toffolis + (t_gates + n_rot * T_rot) / 4
        score    = qubits * C                                            (lower is better)

Always confirm a chosen circuit with the official verifier before submitting.

  python sweep_precision.py --baseline-only
  python sweep_precision.py --rounds 6 --write best.kmb

Run inside WSL with the competition data unpacked in ~/gq-compilation/data.
"""

import argparse
import dataclasses
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

GENERATOR_DIR = Path.home() / "gq-compilation" / "data" / "verifiers" / "invsqrt"
sys.path.insert(0, str(GENERATOR_DIR))
import nr_reference_circuit as nr  # noqa: E402

N_P = 10
MAX_X = 3 * (2**N_P - 2) ** 2
REL_TOL = 2.0**-24
T_PER_TOFFOLI = 4
FIELDS = ["delta_bits", "coef_bits", "square_bits", "product_bits", "result_bits"]


def margin_stats(prec, chunk=200_000):
    """(worst relative error, smallest margin in turns) over x = 1..MAX_X, or None if unusable."""
    worst, min_margin = 0.0, math.inf
    for start in range(1, MAX_X + 1, chunk):
        xs = np.arange(start, min(start + chunk, MAX_X + 1))
        try:
            err = nr.relative_error(N_P, prec, xs)
        except (OverflowError, ValueError):
            return None  # a register would overflow
        worst = max(worst, float(err.max()))
        min_margin = min(min_margin, float(((REL_TOL - err) / np.sqrt(xs)).min()))
    return worst, min_margin


def static_counts(prec):
    circuit = nr.build_nr_circuit(N_P, prec=prec)
    stats = circuit.operation_statistics()
    n_rot = stats.num_z_pow(min_clifford_hierarchy_level=4)
    return circuit, circuit.num_qubits, stats.num_toffoli_like, stats.num_t_like, n_rot


def estimate(prec):
    ms = margin_stats(prec)
    if ms is None or ms[1] <= 0:
        return None
    worst, margin = ms
    circuit, qubits, toffolis, t_gates, n_rot = static_counts(prec)
    eps = math.pi * margin / n_rot
    rot_cost = 0.56 * math.log2(1 / eps) + 5.3
    cost = toffolis + (t_gates + n_rot * rot_cost) / T_PER_TOFFOLI
    return {
        "prec": dataclasses.asdict(prec),
        "qubits": qubits, "toffolis": toffolis, "t_gates": t_gates, "n_rot": n_rot,
        "worst_error_over_tol": worst / REL_TOL, "eps": eps,
        "cost": cost, "score": qubits * cost, "circuit": circuit,
    }


def show(tag, r):
    if r is None:
        print(f"{tag:<28} rejected (error too large or overflow)", flush=True)
        return
    print(f"{tag:<28} score {r['score']:>12,.1f}  Q={r['qubits']}  Tof={r['toffolis']:,}  "
          f"rot={r['n_rot']}  err/tol={r['worst_error_over_tol']:.3f}  {json.dumps(r['prec'])}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline-only", action="store_true")
    ap.add_argument("--rounds", type=int, default=6, help="coordinate-descent rounds")
    ap.add_argument("--write", type=Path, help="write the best circuit here (.kmb)")
    args = ap.parse_args()

    t0 = time.time()
    best = estimate(nr.Precision())
    show("baseline (reference)", best)
    print(f"  (one evaluation took {time.time() - t0:.0f} s)", flush=True)
    if args.baseline_only:
        return

    for rnd in range(1, args.rounds + 1):
        improved = False
        for field in FIELDS:
            current = best["prec"]
            trial = nr.Precision(**{**current, field: current[field] - 1})
            r = estimate(trial)
            show(f"round {rnd}: {field} -1", r)
            if r is not None and r["score"] < best["score"]:
                best, improved = r, True
        print(f"-- after round {rnd}: best score {best['score']:,.1f}  {json.dumps(best['prec'])}", flush=True)
        if not improved:
            break

    if args.write:
        best["circuit"].to_file(str(args.write), format="kmb")
        print(f"wrote {args.write}")


if __name__ == "__main__":
    main()
