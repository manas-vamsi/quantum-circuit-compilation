"""Does an invsqrt circuit actually work? A small, readable test on 64 inputs (takes seconds).

For every chosen x the circuit is run on the basis state |x>|0...0> and three things are checked:

  1. x is restored (the circuit must not change its input),
  2. every scratch qubit is back to 0 (leftover garbage would ruin quantum interference),
  3. the phase the circuit applied equals 1/sqrt(x) turns, within the tolerance 2^-24 relative.

This uses the official verifier's own helpers, so "working" means the same thing here as on Kaggle,
but only for 64 inputs. The full check over all 3,133,452 inputs is the official verifier.

  python check_works.py path/to/invsqrt.kmb       # test one circuit
  python check_works.py --selftest                # prove the test passes a good and fails a broken circuit

Exit code 0 = all 64 inputs fine, 1 = something failed. Run inside WSL with the competition data
unpacked in ~/gq-compilation/data.
"""

import argparse
import sys
from pathlib import Path

import numpy as np

VERIFIER_DIR = Path.home() / "gq-compilation" / "data" / "verifiers" / "invsqrt"
sys.path.insert(0, str(VERIFIER_DIR))
import kickmix as km  # noqa: E402
import nr_reference_circuit as nr  # noqa: E402
import verify_submission_invsqrt as v  # noqa: E402

BATCH = 64
N_P = 10
# Edge cases first (smallest x, powers of two, the largest x), then seeded random inputs.
SPECIAL_X = [1, 2, 3, 4, 5, 9, 100, 1023, 65536, 1046655, 2588411, 3133452]


def pick_inputs(spec, seed=2026):
    rng = np.random.default_rng(seed)
    specials = [x for x in SPECIAL_X if x <= spec.max_x]
    rest = rng.integers(1, spec.max_x + 1, size=BATCH - len(specials)).tolist()
    return np.array(specials + rest, dtype=np.uint64)


def run_check(circuit, spec, xs):
    """Run the circuit once per input in `xs` and return per-input results."""
    x_reg, scratch = v.validate_registers(circuit, spec)
    target, tol = v.reference_values(spec, xs)
    sim = km.Simulator(batch_size=len(xs), debug_print=False, counting_operations=False, seed=1)
    sim.clear_for_shot()
    sim.write_across_shots(x_reg, v.to_bits(xs, spec.width))
    sim.do(circuit)

    restored = v.from_bits(sim.read_across_shots(x_reg)) == xs
    # read_across_shots returns (qubits, shots): a shot is clean if none of its scratch qubits is 1.
    clean = ~sim.read_across_shots(scratch).any(axis=0) if len(scratch) else np.ones(len(xs), dtype=bool)
    theta = np.array([v.half_turns_to_units(sim.read_shot_phase(i)) for i in range(len(xs))],
                     dtype=np.uint64)
    error = (theta - target).view(np.int64)             # signed, in units of 2^-64 turns
    used = np.abs(error).view(np.uint64)
    phase_ok = used <= tol
    return {
        "x": xs, "restored": restored, "clean": clean, "phase_ok": phase_ok,
        "expected": target.astype(np.float64) / 2.0**64,
        "got": theta.astype(np.float64) / 2.0**64,
        "error": error.astype(np.float64) / 2.0**64,
        "ratio": used.astype(np.float64) / np.maximum(tol.astype(np.float64), 1.0),
    }


def report(name, res, rows=14):
    ok = res["restored"] & res["clean"] & res["phase_ok"]
    print(f"\n=== {name}")
    print(f"{'x':>9}  {'expected phase':>15}  {'circuit phase':>15}  {'error (turns)':>13}  "
          f"{'error/limit':>11}  restored  clean  phase")
    for i in range(min(rows, len(ok))):
        print(f"{int(res['x'][i]):>9}  {res['expected'][i]:>15.9f}  {res['got'][i]:>15.9f}  "
              f"{res['error'][i]:>13.2e}  {res['ratio'][i]:>11.3f}  "
              f"{'yes' if res['restored'][i] else 'NO':^8}  {'yes' if res['clean'][i] else 'NO':^5}  "
              f"{'ok' if res['phase_ok'][i] else 'FAIL'}")
    if len(ok) > rows:
        print(f"... ({len(ok) - rows} more inputs not shown)")
    print(f"restored: {int(res['restored'].sum())}/{len(ok)}   scratch clean: {int(res['clean'].sum())}/{len(ok)}   "
          f"phase within limit: {int(res['phase_ok'].sum())}/{len(ok)}   "
          f"worst error/limit: {res['ratio'].max():.3f}")
    verdict = bool(ok.all())
    print("RESULT:", "WORKS on all 64 inputs" if verdict else "BROKEN")
    return verdict


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("circuit", nargs="?", help="path to a .kmb or .kmx circuit")
    ap.add_argument("--selftest", action="store_true", help="check the test itself on a good and a broken circuit")
    args = ap.parse_args()
    spec = v.ProblemSpecInvSqrt.for_n_p(N_P)
    xs = pick_inputs(spec)

    if args.selftest:
        good = report("reference circuit (should WORK)", run_check(nr.build_nr_circuit(N_P), spec, xs))
        # Too few bits in the first-guess polynomial: a circuit that builds and runs but is not accurate.
        broken_prec = nr.Precision(delta_bits=5)
        bad = report("deliberately broken circuit, delta_bits=5 (should be BROKEN)",
                     run_check(nr.build_nr_circuit(N_P, prec=broken_prec), spec, xs))
        passed = good and not bad
        print("\nSELFTEST:", "OK - the test passes a good circuit and catches a broken one" if passed
              else "PROBLEM - the test did not behave as expected")
        sys.exit(0 if passed else 1)

    if not args.circuit:
        ap.error("give a circuit file, or use --selftest")
    circuit = km.Circuit.from_file(args.circuit, format="auto")
    sys.exit(0 if report(args.circuit, run_check(circuit, spec, xs)) else 1)


if __name__ == "__main__":
    main()
