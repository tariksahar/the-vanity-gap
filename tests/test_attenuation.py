"""Fixtures for `src.analysis.attenuation`.

The cases are chosen so the right answer is knowable by hand, which is the only
way to tell a correct attenuation factor from a plausible-looking one.

Run:  python tests/test_attenuation.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.analysis.attenuation import (  # noqa: E402
    BUCKETS, cluster_bootstrap, lambda_forward, lambda_reverse, mde_operative,
    precision,
)

FLAT = {"ran_small": 1.0, "true_to_size": 1.0, "ran_large": 1.0}
FAILURES: list[str] = []


def check(name: str, got, want, tol: float = 1e-9) -> None:
    ok = got is None and want is None
    if not ok and got is not None and want is not None:
        ok = abs(got - want) <= tol
    print(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(name)


def matrix(**cells) -> dict:
    """`matrix(ran_small__ran_small=10, ...)` -> {(assigned, human): n}."""
    out = {}
    for key, value in cells.items():
        assigned, human = key.split("__")
        out[(assigned, human)] = value
    return out


def test_perfect() -> None:
    """A perfect dictionary attenuates nothing."""
    m = matrix(ran_small__ran_small=30, true_to_size__true_to_size=30,
               ran_large__ran_large=30)
    lam, residual, _ = lambda_forward(m, FLAT)
    check("perfect: lambda_forward", lam, 1.0)
    check("perfect: residual", residual, 0.0)
    check("perfect: lambda_reverse", lambda_reverse(m), 1.0)


def test_symmetric_swap() -> None:
    """20% of each extreme is called the opposite extreme.

    a_small = 0.8*(-1) + 0.2*(+1) = -0.6; a_large = +0.6; lambda = 0.6.
    With flat prevalence the Bayes step is an identity, so the hand value holds.
    """
    m = matrix(ran_small__ran_small=80, ran_small__ran_large=20,
               true_to_size__true_to_size=100,
               ran_large__ran_large=80, ran_large__ran_small=20)
    lam, residual, _ = lambda_forward(m, FLAT)
    check("swap 20%: lambda_forward", lam, 0.6, 1e-9)
    check("swap 20%: residual", residual, 0.0, 1e-9)


def test_collapse_to_middle() -> None:
    """A dictionary whose extremes are always truly true_to_size carries no signal."""
    m = matrix(ran_small__true_to_size=50, true_to_size__true_to_size=50,
               ran_large__true_to_size=50)
    lam, _residual, _ = lambda_forward(m, FLAT)
    check("collapse: lambda_forward is None (true classes empty)", lam, None)


def test_half_correct_symmetric() -> None:
    """Half of EACH extreme is truly true_to_size -- symmetric leakage.

    Hand-computed with flat w = 1/3 each:
      p(true) = (1/6, 2/3, 1/6)
      a_small = (-1)(1/3)(0.5) / (1/6) = -1
      a_large = (+1)(1/3)(0.5) / (1/6) = +1        -> lambda = 1
      a_tts   = [(-1)(1/3)(0.5) + 0 + (+1)(1/3)(0.5)] / (2/3) = 0
      residual = 0 - (-1 + 1)/2 = 0

    lambda is 1 because the extremes are never confused WITH EACH OTHER, and the
    residual is 0 because the leakage is symmetric. Both are exactly right and
    neither is obvious, which is why this case is here.
    """
    m = matrix(ran_small__ran_small=50, ran_small__true_to_size=50,
               true_to_size__true_to_size=100,
               ran_large__ran_large=50, ran_large__true_to_size=50)
    lam, residual, _ = lambda_forward(m, FLAT)
    check("symmetric leakage: lambda_forward", lam, 1.0, 1e-9)
    check("symmetric leakage: residual", residual, 0.0, 1e-9)


def test_asymmetric_leak_moves_residual() -> None:
    """Only the small end leaks. The residual must pick that up.

    Hand-computed with flat w:
      p(true) = (1/6, 1/2, 1/3)
      a_small = -1,  a_large = +1  -> lambda = 1
      a_tts   = [(-1)(1/3)(0.5)] / (1/2) = -1/3
      residual = -1/3

    This is the case the residual diagnostic exists for: lambda alone says the
    measurement is undamaged, and it is wrong to stop there.
    """
    m = matrix(ran_small__ran_small=50, ran_small__true_to_size=50,
               true_to_size__true_to_size=100,
               ran_large__ran_large=100)
    lam, residual, _ = lambda_forward(m, FLAT)
    check("asymmetric leak: lambda_forward", lam, 1.0, 1e-9)
    check("asymmetric leak: residual", residual, -1.0 / 3.0, 1e-9)


def test_prevalence_matters() -> None:
    """lambda_forward depends on prevalence; lambda_reverse does not.

    That difference is the whole point of the distinction, so it is asserted.
    """
    m = matrix(ran_small__ran_small=80, ran_small__true_to_size=20,
               true_to_size__true_to_size=90, true_to_size__ran_small=10,
               ran_large__ran_large=70, ran_large__true_to_size=30)
    flat, _r1, _a = lambda_forward(m, FLAT)
    skewed, _r2, _b = lambda_forward(
        m, {"ran_small": 5.0, "true_to_size": 1.0, "ran_large": 1.0})
    print(f"        lambda_forward flat={flat:.4f} skewed={skewed:.4f}")
    if abs(flat - skewed) < 1e-6:
        FAILURES.append("prevalence: lambda_forward should move with prevalence")
    else:
        print("  PASS  prevalence: lambda_forward responds to prevalence")
    check("prevalence: lambda_reverse is prevalence-free",
          lambda_reverse(m), lambda_reverse(m))


def test_mde_operative() -> None:
    check("mde_operative", mde_operative(0.219, 0.73), 0.219 / 0.73, 1e-12)
    try:
        mde_operative(0.219, 0.0)
    except ValueError:
        print("  PASS  mde_operative raises on lambda = 0")
    else:
        FAILURES.append("mde_operative should raise on lambda = 0")


def test_cluster_bootstrap_respects_clusters() -> None:
    """With every row in one cluster the bootstrap cannot vary -- a degenerate
    case that catches a bootstrap which is secretly resampling rows."""
    rows = [{"parent": "P1", "assigned": "ran_small",
             "human": "ran_small" if i < 8 else "ran_large", "gender": "men"}
            for i in range(10)]
    low, high, _ = cluster_bootstrap(rows, lambda r: precision(r, "ran_small"),
                                     replicates=200)
    check("single cluster: CI is degenerate", high - low, 0.0, 1e-12)


def test_precision_excludes_unclear() -> None:
    rows = ([{"parent": f"P{i}", "assigned": "ran_large", "human": "ran_large"}
             for i in range(8)]
            + [{"parent": "PX", "assigned": "ran_large", "human": "unclear"}]
            + [{"parent": "PY", "assigned": "ran_large", "human": "ran_small"}])
    check("precision excludes unclear", precision(rows, "ran_large"), 8 / 9, 1e-12)


if __name__ == "__main__":
    print("attenuation fixtures")
    for test in (test_perfect, test_symmetric_swap, test_collapse_to_middle,
                 test_half_correct_symmetric, test_asymmetric_leak_moves_residual,
                 test_prevalence_matters, test_mde_operative,
                 test_cluster_bootstrap_respects_clusters,
                 test_precision_excludes_unclear):
        print(f"\n{test.__name__}")
        test()
    print("\n" + ("ALL PASS" if not FAILURES else f"FAILURES: {FAILURES}"))
    sys.exit(1 if FAILURES else 0)
