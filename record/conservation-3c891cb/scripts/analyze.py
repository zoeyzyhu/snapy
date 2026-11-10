#!/usr/bin/env python3
"""Analyse the per-step records of run_arm.py.

For each arm (bubble run + its rest twin) and quantity q_n (n = step):
  (a) rest residual of the twin: max|w| [m/s], max|p/p0-1|, max|rho/rho0-1|
  (b) E+PE drift of the bubble run: (E+PE)_n / (E+PE)_0 - 1, PE = snapy's own (corrected) PE
  (c) dry-air mass drift and total-water drift: M_n / M_0 - 1
  (d) tracer: max |r/r0 - 1| of the bubble run
final value  = q at the last recorded step
rate         = slope of a least-squares line q_n = a + s n over all recorded steps
               (absolute, and in eps units, eps = machine epsilon of the arm's dtype)
exponent     = slope of log|q_n| vs log n over steps with |q_n| > 0 (n >= 1);
               ~1 means linear growth, ~0.5 random walk, ~0 bounded
flags: |final| >= 1e-10 (relative quantities), exponent > 1.2 (super-linear),
       or the run did not reach tlim.  'onset' = first step where |q_n| exceeds
       100 eps (or 1e-10), reported for flagged quantities.

  python analyze.py runs/ > table.md
"""
import glob
import os
import sys

import numpy as np

D = sys.argv[1]
EPS = {"float64": np.finfo(np.float64).eps, "float32": np.finfo(np.float32).eps}


def fit(q):
    q = np.asarray(q, float)
    n = np.arange(len(q))
    if len(q) < 3 or not np.all(np.isfinite(q)):
        return np.nan, np.nan
    s = np.polyfit(n, q, 1)[0]
    m = (n >= 1) & (np.abs(q) > 0)
    if m.sum() < 3:
        return s, np.nan
    e = np.polyfit(np.log(n[m]), np.log(np.abs(q[m])), 1)[0]
    return s, e


def onset(q, thr):
    idx = np.nonzero(np.abs(q) > thr)[0]
    return int(idx[0]) if len(idx) else -1


arms = sorted({os.path.basename(f).replace("_bubble", "").replace(".npz", "")
               for f in glob.glob(f"{D}/*_bubble*.npz")})
rows = []
for arm in arms:
    tag_b = arm.replace("_s9", "_s9_bubble").replace("_s0", "_s0_bubble")
    tag_r = tag_b.replace("_bubble", "_rest")
    fb, fr = f"{D}/{tag_b}.npz", f"{D}/{tag_r}.npz"
    if not (os.path.exists(fb) and os.path.exists(fr)):
        continue
    B, R = np.load(fb), np.load(fr)
    dtype = str(B["dtype"]) if "dtype" in B.files else "float64"
    eps = EPS[dtype]
    q = {}
    q["a_w"] = R["wmax"]
    q["a_p"] = R["dp"]
    q["a_rho"] = R["drho"]
    epe = B["E"] + B["PE"]
    q["b_EPE"] = epe / epe[0] - 1.
    q["c_dry"] = B["dry"] / B["dry"][0] - 1.
    q["c_water"] = B["water"] / B["water"][0] - 1.
    q["d_tracer"] = B["tracer"]
    # twin conservation too (not in the table, reported as a check)
    epr = R["E"] + R["PE"]
    q["twin_EPE"] = epr / epr[0] - 1.
    q["twin_dry"] = R["dry"] / R["dry"][0] - 1.
    q["twin_water"] = R["water"] / R["water"][0] - 1.
    q["twin_tracer"] = R["tracer"]
    res = {"arm": arm, "dtype": dtype, "eps": eps,
           "status_b": f'{B["status"]}@{int(B["fail_step"])}' if str(B["status"]) != "ok" else "ok",
           "status_r": f'{R["status"]}@{int(R["fail_step"])}' if str(R["status"]) != "ok" else "ok",
           "steps_b": len(B["dry"]) - 1, "steps_r": len(R["dry"]) - 1, "nsteps": int(B["nsteps"]),
           "Cv": float(B["courant_v"]), "Ch": float(B["courant_h"]), "ratio": float(B["max_ratio"]),
           "dzH": float(B["max_dz_over_H"]), "dt": float(B["dt"]),
           "wall_b": float(B["wall"]), "wall_r": float(R["wall"])}
    for k, v in q.items():
        s, e = fit(v)
        fin = float(v[-1])
        thr = 1e-10 if k != "a_w" else np.inf
        flag = []
        if k != "a_w" and abs(fin) >= 1e-10:
            flag.append("near/above 1e-10")
        if np.isfinite(e) and e > 1.2 and abs(fin) > 100 * eps:
            flag.append("super-linear")
        res[k] = dict(final=fin, rate=s, rate_eps=s / eps, exp=e, flag=flag,
                      onset=onset(v, min(thr, 100 * eps)) if flag else None,
                      maxabs=float(np.nanmax(np.abs(v))))
    rows.append(res)

np.save(f"{D}/analysis.npy", rows, allow_pickle=True)


def f3(x):
    return "nan" if not np.isfinite(x) else f"{x:.2e}"


def cell(r, k):
    x = r[k]
    return f'{f3(x["final"])} / {f3(x["rate"])} ({x["rate_eps"]:.2g}ε) / {x["exp"]:.2f}' if np.isfinite(x["exp"]) \
        else f'{f3(x["final"])} / {f3(x["rate"])} ({x["rate_eps"]:.2g}ε) / –'


print("| arm | dtype | run (bubble, twin) | steps | (a) max|w| m/s | (a) max|p/p0-1| | (a) max|ρ/ρ0-1| "
      "| (b) E+PE | (c) dry mass | (c) water | (d) tracer |")
print("|" + "---|" * 11)
for r in rows:
    print(f'| {r["arm"]} | {r["dtype"]} | {r["status_b"]}, {r["status_r"]} | {r["steps_b"]}/{r["nsteps"]} | '
          + " | ".join(cell(r, k) for k in ["a_w", "a_p", "a_rho", "b_EPE", "c_dry", "c_water", "d_tracer"]) + " |")
print()
print("Grid/Courant: " + "; ".join(
    f'{r["arm"]}: dt={r["dt"]} Cv={r["Cv"]:.2f} Ch={r["Ch"]:.3f} ratio={r["ratio"]:.4f} dz/H={r["dzH"]:.4f}'
    for r in rows))
print()
print("Twin conservation (final / rate / exponent):")
for r in rows:
    print(f'- {r["arm"]}: ' + "; ".join(f'{k}: {cell(r, k)}' for k in ["twin_EPE", "twin_dry", "twin_water", "twin_tracer"]))
print()
print("Flags:")
for r in rows:
    for k, v in r.items():
        if isinstance(v, dict) and v["flag"]:
            print(f'- {r["arm"]} {k}: {", ".join(v["flag"])}; final {f3(v["final"])}, max {f3(v["maxabs"])}, '
                  f'exponent {v["exp"]:.2f}, first step above threshold {v["onset"]}')
