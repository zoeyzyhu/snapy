#!/usr/bin/env python3
"""Export the saved per-step series (run_arm.py .npz) of the non-headline runs as CSV.
No runs are made; this only converts saved files.

  python export_extra_csv.py <cons3c8 dir> <out_dir>

Families (one long CSV each; one row per (arm, precision, step); step 0 = initial state):
  scheme0_long.csv            scheme 0 (explicit), rk3, float64, 4 arms; series end at the
                              last step that passed check_redo (bubble and twin stop separately;
                              cells are empty after a run stopped)
  rk2_control_long.csv        scheme 9, integration/type rk2, dt/2, float32 + float64, both grids
                              (twin IC = the first-pass bryan.release dT=0 restart, NOT the
                              clean-column twin; see README)
  rk2_control_paired.csv      the same, float32 and float64 side by side per (arm, step)
  wb_ref4_long.csv            scheme 9, rk3, SNAP_WB_REF4=1, dt/2, float64, both grids, clean twin
  superseded_twin_bisect_ic_long.csv
                              first-pass rest twins (bryan.release dT=0 restart with the bisection
                              residue), all 8 float64 arms + 4 float32; twin columns only.
                              Superseded by the clean-column twins; kept for finding F3.
  extra_rates.csv             per (family, arm, precision, quantity): end value, fitted
                              per-step rate (abs and eps), log-log exponent
"""
import csv
import glob
import os
import sys

import numpy as np

D, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
EPS = {"float64": float(np.finfo(np.float64).eps), "float32": float(np.finfo(np.float32).eps)}
GRID = {"uni": "uniform", "str": "stretched"}
TWIN_Q = [("twin_wmax_ms", lambda d: d["wmax"], False),
          ("twin_max_dp_over_p0", lambda d: d["dp"], True),
          ("twin_max_drho_over_rho0", lambda d: d["drho"], True)]
BUB_Q = [("EPE_rel_drift", lambda d: (d["E"] + d["PE"]) / (d["E"][0] + d["PE"][0]) - 1., True),
         ("dry_mass_rel_drift", lambda d: d["dry"] / d["dry"][0] - 1., True),
         ("water_rel_drift", lambda d: d["water"] / d["water"][0] - 1., True),
         ("tracer_max_abs_r_over_r0_m1", lambda d: d["tracer"], True)]
fmt = lambda x: repr(float(x))


def qcols(qs):
    c = []
    for n, _, e in qs:
        c += [n] + ([n + "_eps"] if e else [])
    return c


META = ["family", "arm", "grid", "dt", "scheme", "integrator", "wb_ref4", "precision", "twin_ic",
        "bubble_status", "twin_status", "step", "time"]


def status(d):
    if d is None:
        return ""
    s = str(d["status"])
    return "ok" if s == "ok" else f"{s} at step {int(d['fail_step'])} ({str(d['msg'])})"


def series(d, qs, prec):
    out = {}
    if d is None:
        return out
    for n, f, e in qs:
        v = np.asarray(f(d), float)
        out[n] = v
        if e:
            out[n + "_eps"] = v / EPS[prec]
    return out


rate_rows = []


def emit(path, family, entries, qs_bub=True):
    """entries: list of dicts arm, grid, dt, scheme, integrator, wb4, prec, bubble npz|None, rest npz"""
    cols = qcols(TWIN_Q) + (qcols(BUB_Q) if qs_bub else [])
    n_rows = 0
    store = {}
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(META + cols)
        for e in entries:
            B, R, prec = e["bubble"], e["rest"], e["prec"]
            sb = series(B, BUB_Q, prec) if qs_bub else {}
            sr = series(R, TWIN_Q, prec)
            s = {**sr, **sb}
            store[(e["arm"], prec)] = s
            dt = float((B if B is not None else R)["dt"])
            nmax = max(len(v) for v in s.values())
            twin_ic = os.path.basename(str(R["ic"]))
            for i in range(nmax):
                row = [family, e["arm"], GRID[e["arm"][:3]], f"{dt:g}", e["scheme"], e["integrator"],
                       e["wb4"], prec, twin_ic, status(B) if qs_bub else "", status(R), i, fmt(i * dt)]
                row += [fmt(s[c][i]) if i < len(s[c]) else "" for c in cols]
                w.writerow(row)
                n_rows += 1
            for c in cols:
                if c.endswith("_eps"):
                    continue
                v = s[c]
                n = np.arange(len(v))
                if len(v) < 3:
                    continue
                r = np.polyfit(n, v, 1)[0]
                m = (n >= 1) & (np.abs(v) > 0)
                ex = np.polyfit(np.log(n[m]), np.log(np.abs(v[m])), 1)[0] if m.sum() > 2 else float("nan")
                ep = c != "twin_wmax_ms"
                rate_rows.append([family, e["arm"], prec, c, int(n[-1]), fmt(v[-1]),
                                  fmt(v[-1] / EPS[prec]) if ep else "", fmt(r),
                                  fmt(r / EPS[prec]) if ep else "", fmt(ex)])
    print(f"{os.path.basename(path)} rows={n_rows}")
    return store, cols


L = lambda p: np.load(p) if os.path.exists(p) else None
ARMS = [(g, dt) for g in ("uni", "str") for dt in ("1.6", "0.8")]

# scheme 0
ent = [dict(arm=f"{g}_dt{dt}_s0", scheme=0, integrator="rk3", wb4="off", prec="float64",
            bubble=L(f"{D}/runs/{g}_dt{dt}_s0_bubble.npz"), rest=L(f"{D}/runs/{g}_dt{dt}_s0_rest.npz"))
       for g, dt in ARMS]
emit(f"{OUT}/scheme0_long.csv", "scheme0", ent)

# rk2 control
ent = [dict(arm=f"{g}_dt0.8_s9_rk2", scheme=9, integrator="rk2", wb4="off", prec=p,
            bubble=L(f"{D}/runs_rk2/{g}_dt0.8_s9_bubble_rk2_{p}.npz"),
            rest=L(f"{D}/runs_rk2/{g}_dt0.8_s9_rest_rk2_{p}.npz"))
       for g in ("uni", "str") for p in ("float64", "float32")]
store, cols = emit(f"{OUT}/rk2_control_long.csv", "rk2_control", ent)
n_rows = 0
with open(f"{OUT}/rk2_control_paired.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["arm", "grid", "dt", "step", "time"] + sum(([c + "_f32", c + "_f64"] for c in cols), []))
    for g in ("uni", "str"):
        arm = f"{g}_dt0.8_s9_rk2"
        a, b = store[(arm, "float32")], store[(arm, "float64")]
        for i in range(len(a["EPE_rel_drift"])):
            w.writerow([arm, GRID[g], "0.8", i, fmt(i * 0.8)] + sum(([fmt(a[c][i]), fmt(b[c][i])] for c in cols), []))
            n_rows += 1
print(f"rk2_control_paired.csv rows={n_rows}")

# SNAP_WB_REF4=1
ent = [dict(arm=f"{g}_dt0.8_s9_wbref4", scheme=9, integrator="rk3", wb4="SNAP_WB_REF4=1", prec="float64",
            bubble=L(f"{D}/runs_wb4/{g}_dt0.8_s9_bubble.npz"), rest=L(f"{D}/runs_wb4/{g}_dt0.8_s9_rest.npz"))
       for g in ("uni", "str")]
emit(f"{OUT}/wb_ref4_long.csv", "wb_ref4", ent)

# superseded first-pass twins
ent = []
for g, dt in ARMS:
    for s in (9, 0):
        ent.append(dict(arm=f"{g}_dt{dt}_s{s}", scheme=s, integrator="rk3", wb4="off", prec="float64", bubble=None,
                        rest=L(f"{D}/runs_twin_bisect_ic/{g}_dt{dt}_s{s}_rest.npz")))
    ent.append(dict(arm=f"{g}_dt{dt}_s9", scheme=9, integrator="rk3", wb4="off", prec="float32", bubble=None,
                    rest=L(f"{D}/runs_twin_bisect_ic/{g}_dt{dt}_s9_rest_f32.npz")))
emit(f"{OUT}/superseded_twin_bisect_ic_long.csv", "superseded_twin_bisect_ic", ent, qs_bub=False)

with open(f"{OUT}/extra_rates.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["family", "arm", "precision", "quantity", "end_step", "end_value", "end_value_eps",
                "rate_per_step", "rate_eps_per_step", "loglog_exponent"])
    w.writerows(rate_rows)
print(f"extra_rates.csv rows={len(rate_rows)}")
