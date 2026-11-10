#!/usr/bin/env python3
"""Write README.md (manifest) and SHA256SUMS for the conservation record directory.
  make_record_readme.py <record_dir>"""
import csv, glob, hashlib, os, sys
import numpy as np
R = sys.argv[1]
SNAPY = "3c891cb20614260351944fb8007cbc9bd50d22a3"
BUILD = ("source rr326/vb/bin/activate; cd snapy@" + SNAPY[:7] + "; "
         "cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DNETCDF=ON -DBUILD_TESTS=ON -DFULL_TESTS=OFF "
         "-DSNAPY_TEST_PYTHONPATH=<venv purelib>; cmake --build build --config Release --parallel 8; "
         "pip install --no-build-isolation --no-deps .")


def rows(p):
    with open(p) as f:
        return sum(1 for _ in f) - 1


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


arms = []  # (family, arm, prec, scheme, integ, wb4, grid, dt, bubble result, twin result, twin ic, csv)
def st(p):
    if not os.path.exists(p):
        return "not saved", ""
    d = np.load(p)
    s = str(d["status"])
    n = len(d["dry"]) - 1
    return (f"ok, {n}/{int(d['nsteps'])} steps" if s == "ok" else f"stopped: {s} at step {int(d['fail_step'])} ({n} steps recorded)"), os.path.basename(str(d["ic"]))
G = {"uni": "uniform nx1=400 dz=25 m", "str": "stretched x1rat=1.05 nx1=62 dz 24.6-480 m"}
for g in ("uni", "str"):
    for dt in ("1.6", "0.8"):
        for prec, sfx in (("float64", ""), ("float32", "_f32")):
            b, _ = st(f"{R}/raw_npz/scheme9/{g}_dt{dt}_s9_bubble{sfx}.npz"); t, ic = st(f"{R}/raw_npz/scheme9/{g}_dt{dt}_s9_rest{sfx}.npz")
            arms.append(("scheme9", f"{g}_dt{dt}_s9", prec, 9, "rk3", "off", g, dt, b, t, ic, "csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv"))
        b, _ = st(f"{R}/raw_npz/scheme0/{g}_dt{dt}_s0_bubble.npz"); t, ic = st(f"{R}/raw_npz/scheme0/{g}_dt{dt}_s0_rest.npz")
        arms.append(("scheme0", f"{g}_dt{dt}_s0", "float64", 0, "rk3", "off", g, dt, b, t, ic, "csv/scheme0_long.csv"))
    for prec in ("float64", "float32"):
        b, _ = st(f"{R}/raw_npz/rk2_control/{g}_dt0.8_s9_bubble_rk2_{prec}.npz"); t, ic = st(f"{R}/raw_npz/rk2_control/{g}_dt0.8_s9_rest_rk2_{prec}.npz")
        arms.append(("rk2_control", f"{g}_dt0.8_s9_rk2", prec, 9, "rk2", "off", g, "0.8", b, t, ic, "csv/rk2_control_long.csv, csv/rk2_control_paired.csv"))
    b, _ = st(f"{R}/raw_npz/wb_ref4/{g}_dt0.8_s9_bubble.npz"); t, ic = st(f"{R}/raw_npz/wb_ref4/{g}_dt0.8_s9_rest.npz")
    arms.append(("wb_ref4", f"{g}_dt0.8_s9_wbref4", "float64", 9, "rk3", "SNAP_WB_REF4=1", g, "0.8", b, t, ic, "csv/wb_ref4_long.csv"))

files = sorted(p for p in glob.glob(f"{R}/**/*", recursive=True) if os.path.isfile(p) and os.path.basename(p) not in ("README.md", "SHA256SUMS"))
L = []
L.append("# Record of the combined conservation run: snapy 3c891cb, Bryan-Fritsch moist bubble\n")
L.append("This archive packages the files behind the run; it contains no new runs. "
         "The CSVs are exports of the per-step series saved by `scripts/run_arm.py` (the `raw_npz/` files).\n")
L.append("## Code, versions, build\n")
L.append(f"- **snapy:** chengcli/snapy `{SNAPY}`, a clean checkout with `git status --porcelain` empty. Every arm below ran on this one build. main has since moved, to bd40fd2 at 2026-11-10 01:38Z; these files are for 3c891cb only.")
L.append("- **snapy build:** CPU Release source build. GCC 13.3.0, cmake 3.30.0.")
L.append("- **Exact snapy build line** (from `scripts/build_snapy.sh`, run as `build_snapy.sh b`):")
L.append("  ```")
L.append("  cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DNETCDF=ON -DBUILD_TESTS=ON -DFULL_TESTS=OFF -DSNAPY_TEST_PYTHONPATH=\"$(python -c 'import sysconfig; print(sysconfig.get_path(\"purelib\"))')\"")
L.append("  cmake --build build --config Release --parallel 8")
L.append("  pip install --no-build-isolation --no-deps .")
L.append("  ```")
L.append("  The resulting CMakeCache has `CMAKE_BUILD_TYPE=Release, CUDA=OFF, NETCDF=ON, PNETCDF=ON, UCX=ON, BUILD_TESTS=ON, FULL_TESTS=OFF`; PNETCDF and UCX are the Linux defaults and were not passed explicitly. "
         "The IC binary `bryan.release` comes from the same build tree (`build/bin/bryan.release`). The examples directory is always built at this commit.")
L.append("- **kintera:** 2.6.9, source build of chengcli/kintera `b8e726ce2fb1538aa15f0787fdcef732d9cdc997` (tag v2.6.9), from `scripts/build_kintera.sh`:")
L.append("  ```")
L.append("  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DNETCDF=ON -DBUILD_TESTS=OFF")
L.append("  cmake --build build --parallel 10")
L.append("  pip install --no-build-isolation --no-deps .")
L.append("  ```")
L.append("- **Python environment:** pyharp 2.7.6 (pip), torch 2.10.0+cu128 (pip, run on CPU), numpy 2.5.4, Python 3.12.3. The venv was created by `scripts/setup_env.sh`.")
L.append("- **Common settings:** conversion is the hard-wired second-order one, i.e. key 2 (`dynamics/conversion-order` does not exist at 3c891cb). Limiter on (`equation-of-state/limiter: true`). The well-balanced x1 reconstruction is on, as it always is with gravity. gravity-work is `face`, the passive tracer starts at r0 = 1e-3, and t_end = 1000 s. dt is fixed (no `max_time_step`). nx2 = 25 (dx = 800 m) on both grids.")
L.append("- **Grids:** max adjacent width ratio is 1.0500 (stretched) and 1.0000 (uniform). Max dz/H is 0.0769 and 0.0039. The vertical acoustic Courant number at dt = 1.6 / 0.8 s is 21.68 / 10.84 (uniform) and 21.24 / 10.62 (stretched).\n")
L.append("## Arms (every run in this record)\n")
L.append("| family | arm | precision | implicit scheme | integrator | WB_REF4 | grid | dt (s) | bubble run | rest twin | twin IC | CSV |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
for a in arms:
    L.append("| " + " | ".join([a[0], a[1], a[2], str(a[3]), a[4], a[5], G[a[6]], a[7], a[8], a[9], a[10], a[11]]) + " |")
L.append("\nTwin IC:")
L.append("- `*_rest_uniform.pt` is the clean-column twin: the balance_column rest state from `bryan.release` with `dT: 0, balance-ic: true`, with its x2 column 0 copied to all columns by `scripts/make_twin_uniform.py`.")
L.append("- `ic_*_rest.00000.restart` is the first-pass twin. It still carries the bisection residue inside the old bubble disk: a 1.3e-12 horizontal spread in density. This affects the rk2-control twins and the superseded twins. Their (a) rest residual includes the resulting ~5e-9 m/s flow. Their conservation columns (b)-(d) come from the bubble runs and are unaffected.")
L.append("\nAll runs are by the same driver, `scripts/run_arm.py`, and the same build. Only `run_arm.py` options and the deck differ.\n")
L.append("## Directory layout\n")
L.append("- **`decks/`:** all decks.")
L.append("  - `run_{uni,str}_s{0,9}.yaml`: the run decks.")
L.append("  - `run_*_s9_rk2.yaml`: the rk2 control.")
L.append("  - `ic_{uni,str}_{bubble,rest}.yaml`: the `bryan.release` IC decks. The rest deck has dT = 0 and balance-ic true.")
L.append("- **`ic/`:** IC states fed to the driver.")
L.append("  - `ic_*.00000.restart`: written by `bryan.release`.")
L.append("  - `*_rest_uniform.pt`: the clean-column twins.")
L.append("- **`scripts/`:** the deck generator, twin builder, driver, batch scripts, fit/table script (`analyze.py`), CSV exporters, PE and float32 checks, and the build and env scripts. `README_order.txt` gives the execution order. Scripts contain the original absolute paths of the run directory.")
L.append("- **`csv/`:** per-step CSVs. Column definitions are in `reports/fp32_fp64_csv_README.md` and the docstring of `scripts/export_extra_csv.py`.")
L.append("  - `conservation_long.csv`, `conservation_paired.csv`, `rates.csv`: the headline scheme-9 arms, float32 and float64.")
L.append("  - `scheme0_long.csv`, `rk2_control_long.csv`, `rk2_control_paired.csv`, `wb_ref4_long.csv`, `superseded_twin_bisect_ic_long.csv`, `extra_rates.csv`: the other runs.")
L.append("  - Every relative quantity has an absolute column and an `_eps` column, in units of the run's own eps (eps64 = 2^-52, eps32 = 2^-23).")
L.append("- **`raw_npz/`:** the per-step series as saved by the driver; the CSVs are exports of these.")
L.append("- **`logs/`:** driver logs per run, batch outputs, and the `bryan.release` IC logs, including the balance-ic pass residuals.")
L.append("- **`reports/`:** the original report (table, findings, appendix), the `analyze.py` table, and the README of the float32/float64 CSV export.\n")
L.append("## Missing (never saved, not regenerated)\n")
L.append("- **Plot script:** none exists, because no plot was ever made for this run. The reported numbers come from `scripts/analyze.py` and `scripts/export_csv.py`, which do the linear and log-log fits.")
L.append("- **rk2 control at dt = 1.6 s and in scheme 0:** never run. The control covers only the dt = 0.8 s scheme-9 arms, in float32 and float64.")
L.append("- **rk2 control with the clean-column twin:** never run. Its twins used the first-pass twin IC (see above).")
L.append("- **WB_REF4 at dt = 1.6 s and in float32:** never run.")
L.append("- **Float32 scheme-0 arms:** never run, because scheme 0 already diverges in float64.")
L.append("- **Scheme-0 series after the redo stop:** these do not exist. The redo check stops the run, so the series end there (bubble at step 3/4, twin at step 4-6).")
L.append("- **The original first-pass bubble series:** superseded. They were rerun bitwise-identical with the final driver for the CSV export; the copies here are the final-driver ones.")
L.append("- **The two probe runs** used to locate the contaminated twin's flow: not included. They are one-off diagnostics duplicating `superseded_twin_bisect_ic` series.\n")
L.append("## Files, sizes, CSV row counts, sha256\n")
L.append("Row counts are data rows, excluding the header. `SHA256SUMS` covers every file, including this README.\n")
L.append("| file | bytes | CSV rows | sha256 |")
L.append("|---|---|---|---|")
for p in files:
    rel = os.path.relpath(p, R)
    L.append(f"| {rel} | {os.path.getsize(p)} | {rows(p) if p.endswith('.csv') else ''} | {sha(p)} |")
open(f"{R}/README.md", "w").write("\n".join(L) + "\n")
with open(f"{R}/SHA256SUMS", "w") as f:
    for p in files + [f"{R}/README.md"]:
        f.write(f"{sha(p)}  {os.path.relpath(p, R)}\n")
print("README.md and SHA256SUMS written;", len(files) + 1, "files hashed")
