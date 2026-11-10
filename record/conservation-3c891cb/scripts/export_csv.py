#!/usr/bin/env python3
"""Export the per-step series of the scheme-9 arms (float32 and float64) as CSV.

  python export_csv.py <runs_dir> <out_dir>

Reads <runs_dir>/{grid}_dt{dt}_s9_{bubble,rest}[_f32].npz (written by run_arm.py)
and writes:
  conservation_long.csv    one row per (arm, precision, step)
  conservation_paired.csv  one row per (arm, step), float32 and float64 side by side
  rates.csv                per (arm, precision, quantity): fitted per-step rate and end value
Drifts and deviations are given as absolute (dimensionless relative) values and in
units of the run's own machine epsilon (eps64 = 2^-52, eps32 = 2^-23).
"""
import csv
import os
import sys

import numpy as np

RUNS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
EPS = {"float64": float(np.finfo(np.float64).eps), "float32": float(np.finfo(np.float32).eps)}
ARMS = [(g, dt) for g in ("uni", "str") for dt in ("1.6", "0.8")]
GRID = {"uni": "uniform", "str": "stretched"}
# quantity name -> (source run, function of the npz); 'eps' says whether an eps column is written
QTY = [
    ("twin_wmax_ms", "rest", lambda d: d["wmax"], False),
    ("twin_max_dp_over_p0", "rest", lambda d: d["dp"], True),
    ("twin_max_drho_over_rho0", "rest", lambda d: d["drho"], True),
    ("EPE_rel_drift", "bubble", lambda d: (d["E"] + d["PE"]) / (d["E"][0] + d["PE"][0]) - 1., True),
    ("dry_mass_rel_drift", "bubble", lambda d: d["dry"] / d["dry"][0] - 1., True),
    ("water_rel_drift", "bubble", lambda d: d["water"] / d["water"][0] - 1., True),
    ("tracer_max_abs_r_over_r0_m1", "bubble", lambda d: d["tracer"], True),
]


def cols():
    c = []
    for name, _, _, e in QTY:
        c.append(name)
        if e:
            c.append(name + "_eps")
    return c


series = {}  # (arm, prec) -> dict
for g, dt in ARMS:
    arm = f"{g}_dt{dt}_s9"
    for prec, sfx in (("float64", ""), ("float32", "_f32")):
        B = np.load(f"{RUNS}/{arm}_bubble{sfx}.npz")
        R = np.load(f"{RUNS}/{arm}_rest{sfx}.npz")
        assert str(B["status"]) == "ok" and str(R["status"]) == "ok", arm
        assert str(B["dtype"]) == prec and str(R["dtype"]) == prec, (arm, prec)
        assert str(R["ic"]).endswith("_rest_uniform.pt"), R["ic"]  # clean twin
        n = len(B["dry"])
        assert len(R["dry"]) == n
        eps = EPS[prec]
        s = {"steps": np.arange(n), "time": np.arange(n) * float(B["dt"])}
        for name, src, f, e in QTY:
            v = np.asarray(f(B if src == "bubble" else R), float)
            s[name] = v
            if e:
                s[name + "_eps"] = v / eps
        series[(arm, prec)] = s

fmt = lambda x: repr(float(x))
rows_long = 0
with open(f"{OUT}/conservation_long.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["arm", "grid", "dt", "precision", "step", "time"] + cols())
    for (arm, prec), s in series.items():
        g, dt = arm.split("_")[0], arm.split("_")[1][2:]
        for i in s["steps"]:
            w.writerow([arm, GRID[g], dt, prec, int(i), fmt(s["time"][i])] + [fmt(s[c][i]) for c in cols()])
            rows_long += 1

rows_pair = 0
with open(f"{OUT}/conservation_paired.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    pc = []
    for c in cols():
        pc += [c + "_f32", c + "_f64"]
    w.writerow(["arm", "grid", "dt", "step", "time"] + pc)
    for g, dt in ARMS:
        arm = f"{g}_dt{dt}_s9"
        a, b = series[(arm, "float32")], series[(arm, "float64")]
        for i in a["steps"]:
            w.writerow([arm, GRID[g], dt, int(i), fmt(a["time"][i])]
                       + sum(([fmt(a[c][i]), fmt(b[c][i])] for c in cols()), []))
            rows_pair += 1

rows_rate = 0
with open(f"{OUT}/rates.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["arm", "grid", "dt", "precision", "quantity", "end_step", "end_time",
                "end_value", "end_value_eps", "rate_per_step", "rate_eps_per_step", "loglog_exponent"])
    for (arm, prec), s in series.items():
        g, dt = arm.split("_")[0], arm.split("_")[1][2:]
        n = s["steps"]
        for name, _, _, e in QTY:
            v = s[name]
            rate = np.polyfit(n, v, 1)[0]
            m = (n >= 1) & (np.abs(v) > 0)
            ex = np.polyfit(np.log(n[m]), np.log(np.abs(v[m])), 1)[0] if m.sum() > 2 else float("nan")
            w.writerow([arm, GRID[g], dt, prec, name, int(n[-1]), fmt(s["time"][-1]), fmt(v[-1]),
                        fmt(v[-1] / EPS[prec]) if e else "", fmt(rate),
                        fmt(rate / EPS[prec]) if e else "", fmt(ex)])
            rows_rate += 1
print(f"conservation_long.csv rows={rows_long}; conservation_paired.csv rows={rows_pair}; rates.csv rows={rows_rate}")
