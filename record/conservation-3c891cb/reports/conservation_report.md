# Combined conservation run: snapy main 3c891cb, Bryan–Fritsch moist bubble

Read and run only. Nothing was pushed or posted.

## Pins, build, versions

- **Pin:** `git ls-remote https://github.com/chengcli/snapy refs/heads/main` returned `3c891cb20614260351944fb8007cbc9bd50d22a3` both at the start (2026-11-09 19:19:48Z) and at the end (19:48:01Z). Main did not move.
- **Build:** I reused an existing **source build** at exactly 3c891cb, made earlier today for my #326 leg. The tree is clean (`git status --porcelain` is empty) and the commit is `3c891cb2…a3`. It is a CPU build: `CMAKE_BUILD_TYPE=Release`, `CUDA=OFF`, `NETCDF=ON`, built with `cmake --build` and then `pip install --no-build-isolation --no-deps .` into its own venv. Example binary used: `bryan.release` from that build.
- **Versions:** Python 3.12.3, torch 2.10.0+cu128 (run on CPU), snapy 2.13.1 (the source build above), kintera 2.6.9 (source build of chengcli/kintera `b8e726ce2fb1538aa15f0787fdcef732d9cdc997`, tag v2.6.9), pyharp 2.7.6 (pip).
- **Conversion, "default conversion, key 2":** the option is `dynamics/conversion-order`, but it does **not exist at 3c891cb**. `check_keys` in `src/hydro/hydro_options.cpp:50-52@3c891cb` lists only `equation-of-state, reconstruct, riemann-solver, verbose, disable-flux-x1/2/3, wb-wall-clamp`, so the key would be rejected. The key appears only in a later tree (`hydro.hpp: ADD_ARG(int, conversion_order) = 2`). At 3c891cb the only cell-average↔point conversion is the second-order one, which is key 2. **I left it unset; that is the default and equals key 2.**
- **Well-balanced reference:** this is always engaged when gravity is on. See `src/hydro/hydro_forward.cpp:354-355@3c891cb` (`wb_x1 = grav1 && w.size(0) > IPR && eos != shallow-water`), with `wb-wall-clamp: true` as the default. The optional fourth-order density reference `SNAP_WB_REF4` (off by default) was run as a supplementary check (see below).
- **Vertically implicit scheme:** `integration/implicit-scheme: 9` (vic-full). Scheme 0 means "none", which is explicit.
- **Limiter:** `dynamics/equation-of-state/limiter: true`, the single limiter switch, read by reconstruct, hydro and scalar.
- **Integrator:** rk3 (the example's default), with gravity-work `face` (the default).

## Float32 (one line)

**Yes, snapy 3c891cb runs float32 end to end on CPU.** After `MeshBlock.to(cpu, float32)`, every buffer is float32 (including the kintera thermo submodules), and 3 steps of the scheme-9 Bryan deck ran finite in float32 (`check_fp32.py`). The VIC assemble/solve/redistribute kernels (`src/implicit/implicit_dispatch.cpp:26,85,141,183@3c891cb`), the moist EOS (`src/eos/eos_dispatch.cpp:61`) and kintera's saturation adjustment (`thermo_dispatch.cpp:42,114`) all dispatch with `AT_DISPATCH_FLOATING_TYPES`. Only diagnostic meters (`hydro_forward.cpp:884-885`) and kintera's SVP coefficient table (`log_svp.cpp:37`) stay float64. **So I added float32 copies of the four scheme-9 arms.**

## Case

- **Deck:** snapy's own `examples/bryan.yaml` (Bryan & Fritsch 2002; moist neutral, θ_e = const, q_t = 0.0196; dT = 2 K bubble at (x, z) = (10, 2) km with radius 2 km). Domain 20 km × 10 km, reflecting walls, ideal-moist EOS with H2O ⇌ H2O(l), WENO5 and LMARS. **Standard end time 1000 s**, which all scheme-9 arms reached.
- **IC:** written by `bryan.release` (the example's own `initialize_block`), restart at t = 0.
- **Passive tracer:** `scalar: {names: [tracer]}` (WENO5), started at r0 = 1e-3 everywhere. It is per unit dry mass, so r = scalar_s / u[IDN].
- **Twin:** the `balance_column` rest state comes from `bryan.release` with `dT: 0, balance-ic: true`: 8 saturation + `balance_column` passes, final residual 1.2e-14 and saturation |dp/p| 6e-14. One column of it is then copied horizontally (see finding F3). Twins use the same grid, deck and dt as their arm.
- **Grids:** horizontal nx2 = 25 (dx = 800 m) in both, so that the horizontal Courant number is < 1 while the vertical one is ≥ 10.
  - uniform: nx1 = 400, dz = 25 m.
  - stretched: `cells/x1rat: 1.05`, nx1 = 62, dz from 24.6 m to 480 m. **Measured max adjacent width ratio 1.0500** and **max dz/H = 0.0769**, with H = p/(ρg) per cell. The uniform grid has ratio 1.0000 and dz/H = 0.0039.
- **dt:** fixed (no `max_time_step`). dt = 1.6 s (625 steps) and dt/2 = 0.8 s (1250 steps).
  - **Vertical acoustic Courant** max c_s·dt/dz at t = 0: uniform 21.68 (dt) / 10.84 (dt/2), stretched 21.24 / 10.62. All are ≥ 10.
  - Horizontal Courant: 0.678 / 0.339.

## Table (8 arms + 4 float32 arms)

Each cell is final value / per-step rate from a linear fit (in ε units) / log-log growth exponent. ε = 2.22e-16 for float64 and 1.19e-7 for float32.

- (a) is the twin: max|w| over all velocity components (m/s; absolute rate per step), max|p/p0−1| and max|ρ/ρ0−1|.
- (b) is the relative drift of E+PE, using snapy's own corrected PE. It agrees with `print_cycle_info`'s `pe=` and `ie=` to all 14 printed digits (`check_pe.py`).
- (c) is the relative drift of total dry-air mass and of total water (vapor + liquid).
- (d) is max|r/r0−1| of the tracer in the bubble run.

| arm | (a) max\|w\| | (a) max\|δp/p\| | (a) max\|δρ/ρ\| | (b) E+PE | (c) dry mass | (c) water | (d) tracer |
|---|---|---|---|---|---|---|---|
| uni, dt, s9 | 4.7e-13 / −3.8e-15 / −0.62 | 6.4e-14 / −0.15ε / −0.07 | 6.8e-14 / −0.002ε / −0.02 | −3.56e-14 / −0.26ε / 1.02 | −3.61e-14 / −0.26ε / 0.95 | −3.53e-14 / −0.25ε / 0.92 | 1.75e-14 / 0.11ε / 0.56 |
| uni, dt/2, s9 | 4.5e-13 / −3.2e-15 / −0.74 | 1.0e-13 / 0.11ε / 0.07 | 1.1e-13 / 0.23ε / 0.19 | −7.14e-14 / −0.26ε / 1.02 | −7.19e-14 / −0.26ε / 0.97 | −7.07e-14 / −0.25ε / 0.94 | 3.00e-14 / 0.11ε / 0.65 |
| str, dt, s9 | 4.6e-13 / −2.1e-15 / −0.47 | 5.1e-14 / −0.06ε / −0.06 | 4.4e-14 / −0.04ε / −0.05 | −3.59e-14 / −0.26ε / 0.98 | −3.63e-14 / −0.26ε / 0.99 | −3.53e-14 / −0.25ε / 0.95 | 1.13e-14 / 0.05ε / 0.43 |
| str, dt/2, s9 | 4.9e-13 / −1.8e-15 / −0.55 | 8.4e-14 / 0.13ε / 0.12 | 7.5e-14 / 0.15ε / 0.18 | −7.15e-14 / −0.26ε / 0.98 | −7.23e-14 / −0.26ε / 1.01 | −7.09e-14 / −0.25ε / 0.96 | 1.40e-14 / 0.03ε / 0.41 |
| uni, dt, s0 | **DIVERGED**: twin redo at step 4; max\|w\| 7.0e-2 at step 3, exp 14.9 | 3.1e-4 | 2.5e-4 | −1.1e-16 (to step 2) | −2.2e-16 | −3.3e-16 | 8.9e-16 |
| uni, dt/2, s0 | **DIVERGED**: twin redo at step 6; 67 m/s at step 5, exp 15.5 | 0.23 | 0.18 | 0 (to step 3) | −4.4e-16 | −1.1e-16 | 8.9e-16 |
| str, dt, s0 | **DIVERGED**: twin redo at step 5; 28 m/s at step 4, exp 17.0 | 7.7e-2 | 6.4e-2 | −2.2e-16 (to step 2) | 0 | −1.1e-16 | 8.9e-16 |
| str, dt/2, s0 | **DIVERGED**: twin redo at step 6; 2.1 m/s at step 5, exp 14.6 | 1.1e-2 | 9.3e-3 | −2.2e-16 (to step 3) | −2.2e-16 | −1.1e-16 | 1.1e-15 |
| uni, dt, s9, f32 | 2.1e-4 / −1.5e-9 / 0.03 | 2.3e-5 / 0.23ε / 0.42 | 2.6e-5 / 0.34ε / 0.76 | 1.92e-5 / +0.26ε / 1.01 | 1.93e-5 / +0.26ε / 1.01 | 1.80e-5 / +0.25ε / 1.25† | 9.5e-6 / 0.12ε / 0.61 |
| uni, dt/2, s9, f32 | 2.2e-4 / 6.9e-9 / 0.03 | 4.0e-5 / 0.23ε / 0.54 | 5.0e-5 / 0.33ε / 0.82 | 3.83e-5 / +0.26ε / 1.01 | 3.81e-5 / +0.26ε / 1.02 | 3.63e-5 / +0.25ε / 1.16 | 1.8e-5 / 0.12ε / 0.68 |
| str, dt, s9, f32 | 2.7e-4 / 2.7e-9 / 0.04 | 2.0e-5 / 0.20ε / 0.41 | 2.0e-5 / 0.24ε / 0.68 | 1.93e-5 / +0.26ε / 0.99 | 1.95e-5 / +0.26ε / 1.01 | 1.80e-5 / +0.25ε / 1.21† | 6.3e-6 / 0.05ε / 0.43 |
| str, dt/2, s9, f32 | 2.7e-4 / 1.1e-8 / 0.03 | 3.5e-5 / 0.21ε / 0.54 | 3.2e-5 / 0.21ε / 0.75 | 3.83e-5 / +0.26ε / 0.99 | 3.82e-5 / +0.26ε / 0.99 | 3.63e-5 / +0.25ε / 1.11 | 6.5e-6 / 0.03ε / 0.43 |

† These exponents are a fit artifact: the drift is offset-linear. The water rate over steps 1…n/2 and over n/2…n is +0.242/+0.250 ε (str, dt) and +0.245/+0.247 ε (uni, dt). It is constant, so the growth is linear, not super-linear.

- In the scheme-0 rows, conservation quantities are given up to the last step that passed `check_redo`. The bubble runs of those arms stopped one or two steps earlier (redo at step 3 for dt, step 4 for dt/2).
- Scheme-9 twins also conserve: E+PE, dry mass and water drift at −0.18…−0.26 ε/step (exponent 0.91–1.04), and the tracer stays ≤ 4.4e-14.
- Bubble max|w| at 1000 s is 9.3 m/s (dt) and 10.4–10.5 m/s (dt/2) on both grids. Float32 matches float64 to 2 decimals.

## Findings

**F1. All scheme-0 arms diverged (8 of 8 runs, 4 arms × bubble/twin).** snapy's `check_redo` flagged each run at step 3–6, after max|w| in the rest twin grew with exponents of 15–17 (0.07–67 m/s). This is expected: scheme 0 is "none", which means fully explicit (`implicit_hydro.cpp:71-79@3c891cb`). It cannot run at the required vertical acoustic Courant of 10.6–21.7. Up to the failing step, mass, water, E+PE and tracer stayed at ≤ 1 ε. **No scheme-0 result exists at Courant ≥ 10.** A scheme-0 comparison would need its own dt with Courant < 1, which is outside this spec.

**F2. In every scheme-9 arm, E+PE, dry mass and water drift linearly at −0.25 to −0.26 ε/step (float64).** The drift has the same sign and size in uniform and stretched, dt and dt/2, bubble and twin. The relative E+PE drift equals the mass drift. That is about 2.5× the "~0.1 ε/step" expectation: it is round-off with linear growth (exponents 0.92–1.02), but it is systematic, not a random walk. At 1250 steps it is −7.1e-14, nowhere near 1e-10; extrapolated, it reaches 1e-10 after about 1.8 million steps. In float32 the same drift is **+0.25 to +0.26 ε₃₂/step** (2–4e-5 at 625–1250 steps). **Cause, tested:** stage 3 of SSP-RK3 uses fl(1/3) and fl(2/3) (`IntegratorWeight` 0.3333…, 0.6666…). Their exact sum is 1 − 2⁻⁵⁴ = 1 − ε/4 in float64 and 1 + 2⁻²⁵ = 1 + ε₃₂/4 in float32. This matches both the sign and the size of the drift in each dtype. Rerunning the dt/2 scheme-9 arms with `integration/type: rk2`, whose weights ½, ½ are exact, removes it. Float64 drift falls to ≤ 0.003 ε/step (finals ≤ 1.1e-15), and float32 drift to ≤ 0.006 ε₃₂/step (finals 1e-7…1e-6). The bias is in the stage-weight arithmetic, not in the fluxes, the VIC solve or the thermo. The tracer is not affected, because r = s/ρ_d sees the same factor in both.

**F3 (setup, not snapy dynamics). The first-pass twin was not horizontally uniform.** `bryan.cpp` runs its virtual-temperature bisection inside the bubble disk even with dT = 0 (`examples/bryan.cpp`, `solve_virtual_temperature_perturbation`, 32 iterations). That left a horizontal spread of 1.3e-12 in ρ and 4.9e-13 in p in the `balance_column` rest state. The twin then developed a linear-in-time flow centred on the old bubble (max|w| 4.7–5.2e-9 m/s at 1000 s, the same at dt and dt/2). I rebuilt the twin by copying the balanced column at x2 index 0 (outside the disk) to all columns, which gives a spread of 0. With that, the rest residual is round-off and bounded: max|w| is 1.7–3.4e-12 at step 1 and decays to 4.5–4.9e-13 m/s (exponent −0.5 to −0.7), and |δp/p| and |δρ/ρ| are ≤ 1.1e-13 (exponent −0.07 to 0.19). The table uses the rebuilt twins. Hypothesis, not tested: a rest IC from `bryan.release` with `dT: 0` is not a clean twin unless the bisection is skipped for zero amplitude.

**F4. Float32 rest residual.** |δp/p| and |δρ/ρ| reach 2–5e-5 (170–420 ε₃₂). Most of this is the uniform +ε₃₂/4-per-step mass gain from F2 (dry-mass drift 1.9–3.8e-5 over the same steps), not a hydrostatic imbalance. max|w| stays flat at about 2–3e-4 m/s (exponent 0.03). There is no super-linear growth in any float32 quantity (see † above).

**Pass/fail against the criterion** (round-off, growth at most linear, about 0.1 ε/step):
- (a) and (d) pass in all scheme-9 arms in both dtypes.
- (b) and (c) are round-off and linear, but at **0.25 ε/step, not 0.1 ε/step**, because of F2.
- Nothing in float64 is near 1e-10. Float32 values are above 1e-10 only because ε₃₂ = 1.2e-7.
- **All 4 scheme-0 arms failed to run (diverged).**

## Supplementary

- **`SNAP_WB_REF4=1`** (dt/2, scheme 9, float64):
  - Twin max|w|: 6.2e-13 (str) and 5.5e-13 (uni). |δp/p| 8.5e-14 and 1.0e-13.
  - E+PE, dry mass and water: −0.19…−0.26 ε/step.
  - Tracer: ≤ 4.6e-14.
  - Same picture as the default WB.
- **Unchecked:** CUDA, multi-block decomposition, other integrators beyond the rk2 attribution test, and the float32 scheme-0 arms. The scheme-0 float32 arms were not run, because scheme 0 already diverges in float64.

## How it was run

Fixed-dt Python driver (`run_arm.py`) on the snapy MeshBlock API: `initialize`, then `inc_cycle` and the rk3 stages `forward`, then `check_redo`. It records (a)–(d) after every step from `hydro_u` and `scalar_s`, with interior sums computed in float64. A redo or a non-finite state stops the run and is recorded. 24 main runs were done with 2 torch threads each, 6 in parallel on 12 CPUs (wall time 10–58 s per run).

## Appendix A: full table output of analyze.py (runs/)

| arm | dtype | run (bubble, twin) | steps | (a) max|w| m/s | (a) max|p/p0-1| | (a) max|ρ/ρ0-1| | (b) E+PE | (c) dry mass | (c) water | (d) tracer |
|---|---|---|---|---|---|---|---|---|---|---|
| str_dt0.8_s0 | float64 | redo@4, redo@6 | 3/1250 | 2.14e+00 / 3.06e-01 (1.4e+15ε) / 14.58 | 1.11e-02 / 1.58e-03 (7.1e+12ε) / 15.01 | 9.27e-03 / 1.33e-03 (6e+12ε) / 15.01 | -2.22e-16 / -7.77e-17 (-0.35ε) / – | -2.22e-16 / -8.88e-17 (-0.4ε) / – | -1.11e-16 / -4.44e-17 (-0.2ε) / – | 1.11e-15 / 3.55e-16 (1.6ε) / 0.81 |
| str_dt0.8_s9 | float64 | ok, ok | 1250/1250 | 4.93e-13 / -1.79e-15 (-8.1ε) / -0.55 | 8.42e-14 / 2.97e-17 (0.13ε) / 0.12 | 7.49e-14 / 3.26e-17 (0.15ε) / 0.18 | -7.15e-14 / -5.71e-17 (-0.26ε) / 0.98 | -7.23e-14 / -5.77e-17 (-0.26ε) / 1.01 | -7.09e-14 / -5.65e-17 (-0.25ε) / 0.96 | 1.40e-14 / 7.44e-18 (0.034ε) / 0.41 |
| str_dt0.8_s9_f32 | float32 | ok, ok | 1250/1250 | 2.73e-04 / 1.10e-08 (0.092ε) / 0.03 | 3.51e-05 / 2.51e-08 (0.21ε) / 0.54 | 3.23e-05 / 2.49e-08 (0.21ε) / 0.75 | 3.83e-05 / 3.06e-08 (0.26ε) / 0.99 | 3.82e-05 / 3.06e-08 (0.26ε) / 0.99 | 3.63e-05 / 2.96e-08 (0.25ε) / 1.11 | 6.54e-06 / 4.03e-09 (0.034ε) / 0.43 |
| str_dt1.6_s0 | float64 | redo@3, redo@5 | 2/625 | 2.82e+01 / 5.64e+00 (2.5e+16ε) / 17.03 | 7.72e-02 / 1.54e-02 (7e+13ε) / 17.44 | 6.40e-02 / 1.28e-02 (5.8e+13ε) / 17.43 | -2.22e-16 / -1.11e-16 (-0.5ε) / – | 0.00e+00 / 0.00e+00 (0ε) / – | -1.11e-16 / -5.55e-17 (-0.25ε) / – | 8.88e-16 / 4.44e-16 (2ε) / – |
| str_dt1.6_s9 | float64 | ok, ok | 625/625 | 4.57e-13 / -2.12e-15 (-9.6ε) / -0.47 | 5.14e-14 / -1.43e-17 (-0.064ε) / -0.06 | 4.41e-14 / -8.03e-18 (-0.036ε) / -0.05 | -3.59e-14 / -5.73e-17 (-0.26ε) / 0.98 | -3.63e-14 / -5.78e-17 (-0.26ε) / 0.99 | -3.53e-14 / -5.61e-17 (-0.25ε) / 0.95 | 1.13e-14 / 1.16e-17 (0.052ε) / 0.43 |
| str_dt1.6_s9_f32 | float32 | ok, ok | 625/625 | 2.72e-04 / 2.65e-09 (0.022ε) / 0.04 | 1.96e-05 / 2.34e-08 (0.2ε) / 0.41 | 1.95e-05 / 2.87e-08 (0.24ε) / 0.68 | 1.93e-05 / 3.08e-08 (0.26ε) / 0.99 | 1.95e-05 / 3.12e-08 (0.26ε) / 1.01 | 1.80e-05 / 2.95e-08 (0.25ε) / 1.21 | 6.33e-06 / 6.39e-09 (0.054ε) / 0.43 |
| uni_dt0.8_s0 | float64 | redo@4, redo@6 | 3/1250 | 6.71e+01 / 9.59e+00 (4.3e+16ε) / 15.45 | 2.26e-01 / 3.24e-02 (1.5e+14ε) / 15.69 | 1.77e-01 / 2.53e-02 (1.1e+14ε) / 15.67 | 0.00e+00 / 0.00e+00 (0ε) / – | -4.44e-16 / -1.33e-16 (-0.6ε) / 0.56 | -1.11e-16 / -5.55e-17 (-0.25ε) / 0.17 | 8.88e-16 / 2.89e-16 (1.3ε) / 0.63 |
| uni_dt0.8_s9 | float64 | ok, ok | 1250/1250 | 4.53e-13 / -3.22e-15 (-14ε) / -0.74 | 1.02e-13 / 2.46e-17 (0.11ε) / 0.07 | 1.14e-13 / 5.01e-17 (0.23ε) / 0.19 | -7.14e-14 / -5.73e-17 (-0.26ε) / 1.02 | -7.19e-14 / -5.74e-17 (-0.26ε) / 0.97 | -7.07e-14 / -5.62e-17 (-0.25ε) / 0.94 | 3.00e-14 / 2.50e-17 (0.11ε) / 0.65 |
| uni_dt0.8_s9_f32 | float32 | ok, ok | 1250/1250 | 2.20e-04 / 6.85e-09 (0.057ε) / 0.03 | 3.97e-05 / 2.75e-08 (0.23ε) / 0.54 | 4.95e-05 / 3.89e-08 (0.33ε) / 0.82 | 3.83e-05 / 3.07e-08 (0.26ε) / 1.01 | 3.81e-05 / 3.05e-08 (0.26ε) / 1.02 | 3.63e-05 / 2.95e-08 (0.25ε) / 1.16 | 1.80e-05 / 1.47e-08 (0.12ε) / 0.68 |
| uni_dt1.6_s0 | float64 | redo@3, redo@4 | 2/625 | 7.03e-02 / 2.11e-02 (9.5e+13ε) / 14.87 | 3.07e-04 / 9.22e-05 (4.2e+11ε) / 15.17 | 2.51e-04 / 7.53e-05 (3.4e+11ε) / 15.17 | -1.11e-16 / -5.55e-17 (-0.25ε) / – | -2.22e-16 / -1.11e-16 (-0.5ε) / – | -3.33e-16 / -1.67e-16 (-0.75ε) / – | 8.88e-16 / 4.44e-16 (2ε) / – |
| uni_dt1.6_s9 | float64 | ok, ok | 625/625 | 4.71e-13 / -3.77e-15 (-17ε) / -0.62 | 6.43e-14 / -3.32e-17 (-0.15ε) / -0.07 | 6.76e-14 / -3.92e-19 (-0.0018ε) / -0.02 | -3.56e-14 / -5.73e-17 (-0.26ε) / 1.02 | -3.61e-14 / -5.74e-17 (-0.26ε) / 0.95 | -3.53e-14 / -5.60e-17 (-0.25ε) / 0.92 | 1.75e-14 / 2.47e-17 (0.11ε) / 0.56 |
| uni_dt1.6_s9_f32 | float32 | ok, ok | 625/625 | 2.09e-04 / -1.47e-09 (-0.012ε) / 0.03 | 2.32e-05 / 2.75e-08 (0.23ε) / 0.42 | 2.55e-05 / 4.01e-08 (0.34ε) / 0.76 | 1.92e-05 / 3.07e-08 (0.26ε) / 1.01 | 1.93e-05 / 3.09e-08 (0.26ε) / 1.01 | 1.80e-05 / 2.95e-08 (0.25ε) / 1.25 | 9.53e-06 / 1.46e-08 (0.12ε) / 0.61 |

Grid/Courant: str_dt0.8_s0: dt=0.8 Cv=10.62 Ch=0.339 ratio=1.0500 dz/H=0.0769; str_dt0.8_s9: dt=0.8 Cv=10.62 Ch=0.339 ratio=1.0500 dz/H=0.0769; str_dt0.8_s9_f32: dt=0.8 Cv=10.62 Ch=0.339 ratio=1.0500 dz/H=0.0769; str_dt1.6_s0: dt=1.6 Cv=21.24 Ch=0.678 ratio=1.0500 dz/H=0.0769; str_dt1.6_s9: dt=1.6 Cv=21.24 Ch=0.678 ratio=1.0500 dz/H=0.0769; str_dt1.6_s9_f32: dt=1.6 Cv=21.24 Ch=0.678 ratio=1.0500 dz/H=0.0769; uni_dt0.8_s0: dt=0.8 Cv=10.84 Ch=0.339 ratio=1.0000 dz/H=0.0039; uni_dt0.8_s9: dt=0.8 Cv=10.84 Ch=0.339 ratio=1.0000 dz/H=0.0039; uni_dt0.8_s9_f32: dt=0.8 Cv=10.84 Ch=0.339 ratio=1.0000 dz/H=0.0039; uni_dt1.6_s0: dt=1.6 Cv=21.68 Ch=0.678 ratio=1.0000 dz/H=0.0039; uni_dt1.6_s9: dt=1.6 Cv=21.68 Ch=0.678 ratio=1.0000 dz/H=0.0039; uni_dt1.6_s9_f32: dt=1.6 Cv=21.68 Ch=0.678 ratio=1.0000 dz/H=0.0039

Twin conservation (final / rate / exponent):
- str_dt0.8_s0: twin_EPE: -2.22e-16 / -4.12e-17 (-0.19ε) / 0.41; twin_dry: -2.22e-16 / -3.81e-17 (-0.17ε) / –; twin_water: -3.33e-16 / -8.56e-17 (-0.39ε) / 0.00; twin_tracer: 6.66e-16 / 1.08e-16 (0.49ε) / 0.20
- str_dt0.8_s9: twin_EPE: -5.67e-14 / -4.49e-17 (-0.2ε) / 0.94; twin_dry: -5.21e-14 / -4.09e-17 (-0.18ε) / 0.94; twin_water: -5.40e-14 / -4.18e-17 (-0.19ε) / 0.92; twin_tracer: 2.51e-14 / 1.74e-17 (0.078ε) / 0.67
- str_dt0.8_s9_f32: twin_EPE: 2.51e-05 / 2.01e-08 (0.17ε) / 1.03; twin_dry: 2.11e-05 / 1.68e-08 (0.14ε) / 1.00; twin_water: 2.32e-05 / 1.87e-08 (0.16ε) / 1.16; twin_tracer: 2.06e-05 / 1.73e-08 (0.15ε) / 0.89
- str_dt1.6_s0: twin_EPE: -2.22e-16 / -4.44e-17 (-0.2ε) / -0.00; twin_dry: 0.00e+00 / -4.44e-17 (-0.2ε) / 0.00; twin_water: -3.33e-16 / -7.77e-17 (-0.35ε) / 1.48; twin_tracer: 8.88e-16 / 2.00e-16 (0.9ε) / 0.45
- str_dt1.6_s9: twin_EPE: -2.95e-14 / -4.63e-17 (-0.21ε) / 0.92; twin_dry: -2.71e-14 / -4.20e-17 (-0.19ε) / 0.93; twin_water: -2.75e-14 / -4.22e-17 (-0.19ε) / 0.91; twin_tracer: 1.60e-14 / 2.11e-17 (0.095ε) / 0.61
- str_dt1.6_s9_f32: twin_EPE: 1.42e-05 / 2.27e-08 (0.19ε) / 1.03; twin_dry: 1.26e-05 / 2.02e-08 (0.17ε) / 1.01; twin_water: 1.25e-05 / 2.08e-08 (0.17ε) / 1.29; twin_tracer: 1.03e-05 / 1.68e-08 (0.14ε) / 0.79
- uni_dt0.8_s0: twin_EPE: -2.22e-16 / -5.71e-17 (-0.26ε) / -0.24; twin_dry: -4.44e-16 / -6.34e-17 (-0.29ε) / 0.28; twin_water: -4.44e-16 / -6.34e-17 (-0.29ε) / 0.56; twin_tracer: 1.11e-15 / 2.16e-16 (0.97ε) / 0.56
- uni_dt0.8_s9: twin_EPE: -6.77e-14 / -5.42e-17 (-0.24ε) / 0.99; twin_dry: -6.48e-14 / -5.17e-17 (-0.23ε) / 0.96; twin_water: -6.35e-14 / -4.98e-17 (-0.22ε) / 0.92; twin_tracer: 4.40e-14 / 3.43e-17 (0.15ε) / 0.81
- uni_dt0.8_s9_f32: twin_EPE: 3.44e-05 / 2.75e-08 (0.23ε) / 1.00; twin_dry: 3.16e-05 / 2.54e-08 (0.21ε) / 1.01; twin_water: 2.99e-05 / 2.40e-08 (0.2ε) / 1.09; twin_tracer: 2.67e-05 / 2.17e-08 (0.18ε) / 0.86
- uni_dt1.6_s0: twin_EPE: -3.33e-16 / -1.11e-16 (-0.5ε) / –; twin_dry: -2.22e-16 / -8.88e-17 (-0.4ε) / –; twin_water: -1.11e-16 / -3.33e-17 (-0.15ε) / 0.00; twin_tracer: 6.66e-16 / 2.22e-16 (1ε) / 0.39
- uni_dt1.6_s9: twin_EPE: -3.43e-14 / -5.44e-17 (-0.24ε) / 0.99; twin_dry: -3.28e-14 / -5.19e-17 (-0.23ε) / 0.94; twin_water: -3.15e-14 / -4.90e-17 (-0.22ε) / 0.91; twin_tracer: 2.52e-14 / 3.81e-17 (0.17ε) / 0.74
- uni_dt1.6_s9_f32: twin_EPE: 1.79e-05 / 2.86e-08 (0.24ε) / 1.00; twin_dry: 1.67e-05 / 2.68e-08 (0.22ε) / 1.01; twin_water: 1.50e-05 / 2.44e-08 (0.2ε) / 1.18; twin_tracer: 1.38e-05 / 2.20e-08 (0.18ε) / 0.78

Flags:
- str_dt0.8_s0 a_w: super-linear; final 2.14e+00, max 2.14e+00, exponent 14.58, first step above threshold 1
- str_dt0.8_s0 a_p: near/above 1e-10, super-linear; final 1.11e-02, max 1.11e-02, exponent 15.01, first step above threshold 1
- str_dt0.8_s0 a_rho: near/above 1e-10, super-linear; final 9.27e-03, max 9.27e-03, exponent 15.01, first step above threshold 1
- str_dt0.8_s9_f32 a_p: near/above 1e-10; final 3.51e-05, max 3.51e-05, exponent 0.54, first step above threshold 0
- str_dt0.8_s9_f32 a_rho: near/above 1e-10; final 3.23e-05, max 3.33e-05, exponent 0.75, first step above threshold 0
- str_dt0.8_s9_f32 b_EPE: near/above 1e-10; final 3.83e-05, max 3.83e-05, exponent 0.99, first step above threshold 1
- str_dt0.8_s9_f32 c_dry: near/above 1e-10; final 3.82e-05, max 3.82e-05, exponent 0.99, first step above threshold 1
- str_dt0.8_s9_f32 c_water: near/above 1e-10; final 3.63e-05, max 3.63e-05, exponent 1.11, first step above threshold 1
- str_dt0.8_s9_f32 d_tracer: near/above 1e-10; final 6.54e-06, max 7.50e-06, exponent 0.43, first step above threshold 0
- str_dt0.8_s9_f32 twin_EPE: near/above 1e-10; final 2.51e-05, max 2.51e-05, exponent 1.03, first step above threshold 1
- str_dt0.8_s9_f32 twin_dry: near/above 1e-10; final 2.11e-05, max 2.11e-05, exponent 1.00, first step above threshold 1
- str_dt0.8_s9_f32 twin_water: near/above 1e-10; final 2.32e-05, max 2.32e-05, exponent 1.16, first step above threshold 1
- str_dt0.8_s9_f32 twin_tracer: near/above 1e-10; final 2.06e-05, max 2.06e-05, exponent 0.89, first step above threshold 0
- str_dt1.6_s0 a_w: super-linear; final 2.82e+01, max 2.82e+01, exponent 17.03, first step above threshold 1
- str_dt1.6_s0 a_p: near/above 1e-10, super-linear; final 7.72e-02, max 7.72e-02, exponent 17.44, first step above threshold 1
- str_dt1.6_s0 a_rho: near/above 1e-10, super-linear; final 6.40e-02, max 6.40e-02, exponent 17.43, first step above threshold 1
- str_dt1.6_s9_f32 a_p: near/above 1e-10; final 1.96e-05, max 2.00e-05, exponent 0.41, first step above threshold 0
- str_dt1.6_s9_f32 a_rho: near/above 1e-10; final 1.95e-05, max 1.99e-05, exponent 0.68, first step above threshold 0
- str_dt1.6_s9_f32 b_EPE: near/above 1e-10; final 1.93e-05, max 1.93e-05, exponent 0.99, first step above threshold 1
- str_dt1.6_s9_f32 c_dry: near/above 1e-10; final 1.95e-05, max 1.95e-05, exponent 1.01, first step above threshold 1
- str_dt1.6_s9_f32 c_water: near/above 1e-10, super-linear; final 1.80e-05, max 1.80e-05, exponent 1.21, first step above threshold 1
- str_dt1.6_s9_f32 d_tracer: near/above 1e-10; final 6.33e-06, max 6.33e-06, exponent 0.43, first step above threshold 0
- str_dt1.6_s9_f32 twin_EPE: near/above 1e-10; final 1.42e-05, max 1.42e-05, exponent 1.03, first step above threshold 1
- str_dt1.6_s9_f32 twin_dry: near/above 1e-10; final 1.26e-05, max 1.26e-05, exponent 1.01, first step above threshold 1
- str_dt1.6_s9_f32 twin_water: near/above 1e-10, super-linear; final 1.25e-05, max 1.25e-05, exponent 1.29, first step above threshold 1
- str_dt1.6_s9_f32 twin_tracer: near/above 1e-10; final 1.03e-05, max 1.03e-05, exponent 0.79, first step above threshold 0
- uni_dt0.8_s0 a_w: super-linear; final 6.71e+01, max 6.71e+01, exponent 15.45, first step above threshold 1
- uni_dt0.8_s0 a_p: near/above 1e-10, super-linear; final 2.26e-01, max 2.26e-01, exponent 15.69, first step above threshold 1
- uni_dt0.8_s0 a_rho: near/above 1e-10, super-linear; final 1.77e-01, max 1.77e-01, exponent 15.67, first step above threshold 1
- uni_dt0.8_s9_f32 a_p: near/above 1e-10; final 3.97e-05, max 3.98e-05, exponent 0.54, first step above threshold 0
- uni_dt0.8_s9_f32 a_rho: near/above 1e-10; final 4.95e-05, max 4.95e-05, exponent 0.82, first step above threshold 0
- uni_dt0.8_s9_f32 b_EPE: near/above 1e-10; final 3.83e-05, max 3.83e-05, exponent 1.01, first step above threshold 1
- uni_dt0.8_s9_f32 c_dry: near/above 1e-10; final 3.81e-05, max 3.81e-05, exponent 1.02, first step above threshold 1
- uni_dt0.8_s9_f32 c_water: near/above 1e-10; final 3.63e-05, max 3.63e-05, exponent 1.16, first step above threshold 1
- uni_dt0.8_s9_f32 d_tracer: near/above 1e-10; final 1.80e-05, max 1.89e-05, exponent 0.68, first step above threshold 0
- uni_dt0.8_s9_f32 twin_EPE: near/above 1e-10; final 3.44e-05, max 3.44e-05, exponent 1.00, first step above threshold 1
- uni_dt0.8_s9_f32 twin_dry: near/above 1e-10; final 3.16e-05, max 3.16e-05, exponent 1.01, first step above threshold 1
- uni_dt0.8_s9_f32 twin_water: near/above 1e-10; final 2.99e-05, max 2.99e-05, exponent 1.09, first step above threshold 1
- uni_dt0.8_s9_f32 twin_tracer: near/above 1e-10; final 2.67e-05, max 2.67e-05, exponent 0.86, first step above threshold 0
- uni_dt1.6_s0 a_w: super-linear; final 7.03e-02, max 7.03e-02, exponent 14.87, first step above threshold 1
- uni_dt1.6_s0 a_p: near/above 1e-10, super-linear; final 3.07e-04, max 3.07e-04, exponent 15.17, first step above threshold 1
- uni_dt1.6_s0 a_rho: near/above 1e-10, super-linear; final 2.51e-04, max 2.51e-04, exponent 15.17, first step above threshold 1
- uni_dt1.6_s9_f32 a_p: near/above 1e-10; final 2.32e-05, max 2.33e-05, exponent 0.42, first step above threshold 0
- uni_dt1.6_s9_f32 a_rho: near/above 1e-10; final 2.55e-05, max 2.55e-05, exponent 0.76, first step above threshold 0
- uni_dt1.6_s9_f32 b_EPE: near/above 1e-10; final 1.92e-05, max 1.92e-05, exponent 1.01, first step above threshold 1
- uni_dt1.6_s9_f32 c_dry: near/above 1e-10; final 1.93e-05, max 1.93e-05, exponent 1.01, first step above threshold 1
- uni_dt1.6_s9_f32 c_water: near/above 1e-10, super-linear; final 1.80e-05, max 1.80e-05, exponent 1.25, first step above threshold 1
- uni_dt1.6_s9_f32 d_tracer: near/above 1e-10; final 9.53e-06, max 1.01e-05, exponent 0.61, first step above threshold 0
- uni_dt1.6_s9_f32 twin_EPE: near/above 1e-10; final 1.79e-05, max 1.79e-05, exponent 1.00, first step above threshold 1
- uni_dt1.6_s9_f32 twin_dry: near/above 1e-10; final 1.67e-05, max 1.67e-05, exponent 1.01, first step above threshold 1
- uni_dt1.6_s9_f32 twin_water: near/above 1e-10; final 1.50e-05, max 1.50e-05, exponent 1.18, first step above threshold 1
- uni_dt1.6_s9_f32 twin_tracer: near/above 1e-10; final 1.38e-05, max 1.39e-05, exponent 0.78, first step above threshold 0

## Appendix B: scripts and decks

### scripts/README_order.txt

```text
Order of execution (all from the run directory, venv with snapy built from 3c891cb):
 1. python scripts/make_decks.py <snapy@3c891cb>/examples/bryan.yaml decks
 2. for each of ic_{uni,str}_{bubble,rest}.yaml: <build>/bin/bryan.release -i decks/<deck>  (in ic/<grid>_<kind>/)
 3. python scripts/make_twin_uniform.py ic/<g>_rest/ic_<g>_rest.00000.restart ic/<g>_rest_uniform.pt
 4. scripts/run_all.sh     (bubble runs of the 8 float64 + 4 float32 arms; its twins are superseded by step 5)
 5. scripts/run_twins.sh   (rest twins from the horizontally uniform balance_column rest state)
 6. python scripts/analyze.py runs > table.md
 7. scripts/run_checks.sh  (rk2 attribution, SNAP_WB_REF4=1);  scripts/check_pe.py, scripts/check_fp32.py
```

### scripts/make_decks.py

```python
#!/usr/bin/env python3
"""Write the input decks of the combined conservation run (snapy main 3c891cb).

Base: snapy's own examples/bryan.yaml (Bryan & Fritsch 2002 moist bubble), with
  * x1 (vertical, 0..10 km): uniform dz = 25 m (nx1 = 400) or geometric stretch
    x1rat = 1.05 with nx1 = 62 (dz 24.6 m at the ground .. 480 m at the top)
  * x2 (horizontal, 0..20 km): nx2 = 25 (dx = 800 m) so the horizontal acoustic
    Courant number stays < 1 at the long dt while the vertical one is >= 10
  * limiter on (dynamics/equation-of-state/limiter: true, as in the example)
  * well-balanced x1 reconstruction: engaged by gravity (hydro_forward.cpp:354)
  * conversion: dynamics/conversion-order does not exist at 3c891cb (check_keys
    in hydro_options.cpp:50-52 rejects it); the only conversion there is the
    second-order one, i.e. key 2. Not set.

Decks written:
  ic_<grid>_bubble.yaml  bryan.release IC: dT = 2 K bubble, balance-ic false (standard)
  ic_<grid>_rest.yaml    bryan.release IC: dT = 0, balance-ic true -> balance_column rest state
  run_<grid>_s<scheme>.yaml   the Python driver's deck (adds the passive tracer)
"""
import copy
import os
import sys

import yaml

SRC = sys.argv[1]  # examples/bryan.yaml of the 3c891cb checkout
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)

base = yaml.safe_load(open(SRC))

GRIDS = {
    "uni": {"nx1": 400, "nx2": 25, "nx3": 1, "nghost": 3},
    "str": {"nx1": 62, "nx2": 25, "nx3": 1, "nghost": 3, "x1rat": 1.05},
}

for g, cells in GRIDS.items():
    for kind in ("bubble", "rest"):
        d = copy.deepcopy(base)
        d["geometry"]["cells"] = dict(cells)
        d["integration"]["nlim"] = 0
        d["integration"]["implicit-scheme"] = 0
        d["integration"]["ncycle_out"] = 1
        d["outputs"] = [{"type": "restart", "dt": 1.e9}]
        if kind == "rest":
            d["problem"]["dT"] = 0.0
            d["problem"]["balance-ic"] = True
            d["problem"]["balance-ic-passes"] = 40
        with open(f"{OUT}/ic_{g}_{kind}.yaml", "w") as f:
            yaml.safe_dump(d, f, sort_keys=False)

    for scheme in (0, 9):
        d = copy.deepcopy(base)
        d["geometry"]["cells"] = dict(cells)
        d["integration"]["implicit-scheme"] = scheme
        d["integration"]["nlim"] = -1
        d["integration"]["tlim"] = 1000.
        d["integration"]["ncycle_out"] = 0
        d["outputs"] = []
        d["scalar"] = {"names": ["tracer"], "reconstruct": {"type": "weno5", "shock": False}}
        with open(f"{OUT}/run_{g}_s{scheme}.yaml", "w") as f:
            yaml.safe_dump(d, f, sort_keys=False)
print("decks written to", OUT)
```

### scripts/make_twin_uniform.py

```python
#!/usr/bin/env python3
"""Horizontally uniform rest twin: take the balance_column rest state that
bryan.release wrote (problem/dT = 0, balance-ic: true; 8 saturation+balance
passes), keep its interior column at x2 index 0 (outside the old bubble disk,
where bryan.cpp's bisection is not applied), and copy it to every x2 cell.
Every column is then bitwise the balanced column 0.

  make_twin_uniform.py <restart> <out.pt>
"""
import sys
import torch
import snapy

w = snapy.load_restart(sys.argv[1], 0)["hydro_w"].clone()
ng = 3
col = w[:, :, ng:ng + 1, :].clone()
w[:] = col.expand_as(w)
torch.save({"hydro_w": w}, sys.argv[2])
wi = w[:, :, ng:-ng, ng:-ng]
print(sys.argv[2], "max horizontal spread of p:", float((wi[4].max(1).values - wi[4].min(1).values).abs().max()))
```

### scripts/run_arm.py

```python
#!/usr/bin/env python3
"""One arm of the combined conservation run: snapy main 3c891cb, CPU, float64.

  python run_arm.py --deck run_<grid>_s<scheme>.yaml --ic <restart> --dt DT
                    --tlim 1000 --out arm.npz [--threads N]

Runs MeshBlock (in --dtype; diagnostics are summed in float64) with a fixed dt (no max_time_step) from the given IC restart
(written by snapy's own bryan.release, examples/bryan.cpp), adds a passive
tracer r = r0 = 1e-3 kg/kg dry air everywhere, and records after EVERY step:

  dry      total dry-air mass       sum u[IDN] dV
  water    total water              sum (u[H2O] + u[H2O(l)]) dV
  E        total energy             sum u[IPR] dV           (u[IPR] = ie + ke)
  PE       snapy's own PE           as print_cycle_diagnostics (meshblock.cpp:1140-1156):
           rho g x1v dV minus the corrected-PE term of gravity_work_radial.hpp
           (corrected_pe_work_seam, cartesian: grav1 * h^2/12 * centroid slope of rho)
  tracer   max |r/r0 - 1| over interior, r = scalar_s / u[IDN]
  wmax     max |v| over all three velocity components (interior)
  dp, drho max |p/p_0 - 1|, max |rho/rho_0 - 1| (interior, rho = total density)

Step 0 is the initialised state. A non-finite state or an exception stops the
run and is recorded (status, step).
"""
import argparse
import math
import time

import numpy as np
import torch
import snapy
from snapy import MeshBlock, MeshBlockOptions, kIDN, kIPR

kIVX = 1

p = argparse.ArgumentParser()
p.add_argument("--deck", required=True)
p.add_argument("--ic", required=True)
p.add_argument("--dt", type=float, required=True)
p.add_argument("--tlim", type=float, default=1000.)
p.add_argument("--out", required=True)
p.add_argument("--threads", type=int, default=2)
p.add_argument("--r0", type=float, default=1.e-3)
p.add_argument("--save-final", default="")
p.add_argument("--dtype", choices=("float64", "float32"), default="float64")
a = p.parse_args()

torch.set_num_threads(a.threads)
torch.set_default_dtype(torch.float64)

b = MeshBlock(MeshBlockOptions.from_yaml(a.deck))
DT = getattr(torch, a.dtype)
b.to(torch.device("cpu"), DT)

ic = torch.load(a.ic) if a.ic.endswith(".pt") else snapy.load_restart(a.ic, 0)
w0 = ic["hydro_w"].clone().to(DT)
eos = dict(b.named_modules())["hydro.eos"]
grav1 = -9.81  # forcing/const-gravity/grav1 of the deck (checked below)

x1f = b.buffer("coord.x1f").double()
x2f = b.buffer("coord.x2f").double()
x3f = b.buffer("coord.x3f").double()
x1v = 0.5 * (x1f[1:] + x1f[:-1])
assert w0.shape[-1] == x1v.numel(), (w0.shape, x1v.shape)

scal = torch.full((1,) + tuple(w0.shape[1:]), a.r0, dtype=DT)
vars_, _ = b.initialize({"hydro_w": w0, "scalar_r": scal})

sl = b.part((0, 0, 0), False)  # interior, leading var axis included
I3 = tuple(sl[1:])
ng = (x1f.numel() - 1 - (w0.shape[-1] - 2 * 3)) // 2
il, iu = 3, w0.shape[-1] - 3  # [il, iu) interior x1 cells (nghost = 3)
h1 = (x1f[1:] - x1f[:-1])
h2 = (x2f[1:] - x2f[:-1])
h3 = (x3f[1:] - x3f[:-1])
vol = (h3.view(-1, 1, 1) * h2.view(1, -1, 1) * h1.view(1, 1, -1))[I3]

# ---- corrected PE (gravity_work_radial.hpp, cartesian = plain measure) ----
xs = x1v[il:iu]
n = xs.numel()
hm = xs[1:n - 1] - xs[0:n - 2]
hp = xs[2:n] - xs[1:n - 1]
A = xs[1] - xs[0]; B = xs[2] - xs[1]; C = xs[n - 2] - xs[n - 3]; D = xs[n - 1] - xs[n - 2]
wt0 = torch.cat([(-(2. * A + B) / (A * (A + B))).view(1), -hp / (hm * (hm + hp)), (D / (C * (C + D))).view(1)])
wt1 = torch.cat([((A + B) / (A * B)).view(1), (hp - hm) / (hm * hp), (-((C + D) / (C * D))).view(1)])
wt2 = torch.cat([(-(A / ((A + B) * B))).view(1), hm / (hp * (hm + hp)), ((C + 2. * D) / ((C + D) * D)).view(1)])
j = torch.arange(n).clamp(1, n - 2) - 1
gvar = grav1 * (h1[il:iu] ** 2) / 12.


def pe_total(u):
    u = u.double()
    ui = u[(slice(None),) + I3]
    rho = ui[kIDN] + ui[5:].sum(0)
    pe = rho * (-grav1 * xs)
    slope = wt0 * rho[..., j] + wt1 * rho[..., j + 1] + wt2 * rho[..., j + 2]
    pe = pe - gvar * slope
    return float((pe * vol).sum())


def diag(vars_):
    u = vars_["hydro_u"].double()
    ui = u[(slice(None),) + I3]
    rho = ui[kIDN] + ui[5:].sum(0)
    out = {}
    out["dry"] = float((ui[kIDN] * vol).sum())
    out["water"] = float((ui[5:].sum(0) * vol).sum())
    out["E"] = float((ui[kIPR] * vol).sum())
    out["PE"] = pe_total(u)
    out["ke"] = float(((0.5 * (ui[1:4] ** 2).sum(0) / rho) * vol).sum())
    s = vars_["scalar_s"].double()[(slice(None),) + I3]
    r = s / ui[kIDN]
    out["tracer"] = float((r / a.r0 - 1.).abs().max())
    w = eos.compute("U->W", [vars_["hydro_u"].clone()]).double()
    wi = w[(slice(None),) + I3]
    out["wmax"] = float(wi[1:4].abs().max())
    out["dp"] = float((wi[kIPR] / P0 - 1.).abs().max())
    out["drho"] = float((wi[kIDN] / R0 - 1.).abs().max())
    out["finite"] = bool(torch.isfinite(vars_["hydro_u"]).all())
    return out


wi0 = vars_["hydro_w"].double()[(slice(None),) + I3].clone()
P0 = wi0[kIPR].clone()
R0 = wi0[kIDN].clone()

# vertical / horizontal acoustic Courant numbers at t = 0
gam = eos.compute("W->A", [vars_["hydro_w"]])
cs = eos.compute("WA->L", [vars_["hydro_w"], gam])[I3].double()
courant_v = float((cs * a.dt / h1[il:iu]).max())
courant_h = float((cs * a.dt / h2[I3[1]].view(1, -1, 1)).max())
dz = h1[il:iu]
ratio = torch.maximum(dz[1:] / dz[:-1], dz[:-1] / dz[1:]).max().item() if n > 1 else 1.
Rgas_over_g = None  # scale height from p/(rho g): H = p / (rho g)
H = (wi0[kIPR] / (wi0[kIDN] * (-grav1)))
dz_over_H = float((dz / H).max())

rec = [diag(vars_)]
nsteps = int(round(a.tlim / a.dt))
status, fail_step, msg = "ok", -1, ""
stages = len(b.intg.stages)
redo_count = 0
t0 = time.time()
t = 0.
for step in range(1, nsteps + 1):
    try:
        b.inc_cycle()
        for st in range(stages):
            b.forward(vars_, a.dt, st)
        redo = b.check_redo(vars_)
        if redo != 0:
            redo_count += 1
            status, fail_step, msg = "redo", step, f"check_redo returned {redo}"
            break
    except Exception as e:  # noqa: BLE001
        status, fail_step, msg = "exception", step, str(e).splitlines()[0][:300]
        break
    t += a.dt
    d = diag(vars_)
    rec.append(d)
    if not d["finite"]:
        status, fail_step, msg = "nonfinite", step, "non-finite hydro_u"
        break

if a.save_final:
    torch.save({"w": vars_["hydro_w"].double()[(slice(None),) + I3].clone(), "w0": wi0, "x1v": xs, "t": t}, a.save_final)

keys = ["dry", "water", "E", "PE", "ke", "tracer", "wmax", "dp", "drho"]
np.savez(a.out, **{k: np.array([r[k] for r in rec]) for k in keys},
         dt=a.dt, nsteps=nsteps, status=status, fail_step=fail_step, msg=msg,
         courant_v=courant_v, courant_h=courant_h, max_ratio=ratio,
         max_dz_over_H=dz_over_H, nx1=n, dz_min=float(dz.min()), dz_max=float(dz.max()),
         wall=time.time() - t0, dtype=a.dtype, deck=a.deck, ic=a.ic)
print(f"{a.out}: status={status} step={fail_step} steps_done={len(rec)-1}/{nsteps} "
      f"Cv={courant_v:.2f} Ch={courant_h:.3f} ratio={ratio:.4f} dz/H={dz_over_H:.4f} "
      f"wall={time.time()-t0:.0f}s {msg}")
```

### scripts/run_all.sh

```bash
#!/bin/bash
# run_all.sh: 8 arms {uni,str} x {dt=1.6, dt/2=0.8} x {scheme 0, 9}, each a bubble run and a rest twin
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R
jobs_list=()
for g in uni str; do for dt in 1.6 0.8; do for s in 9 0; do for k in bubble rest; do
  jobs_list+=("$g $dt $s $k")
done; done; done; done
printf '%s\n' "${jobs_list[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; k=$3; tag=${g}_dt${dt}_s${s}_${k}
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_${k}/ic_${g}_${k}.00000.restart \
  --dt $dt --tlim 1000 --threads 2 --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
# float32 arms (scheme 9 only; scheme 0 cannot run at these Courant numbers)
fl=()
for g in uni str; do for dt in 1.6 0.8; do for k in bubble rest; do fl+=("$g $dt 9 $k"); done; done; done
printf '%s\n' "${fl[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; k=$3; tag=${g}_dt${dt}_s${s}_${k}_f32
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_${k}/ic_${g}_${k}.00000.restart \
  --dt $dt --tlim 1000 --threads 2 --dtype float32 --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
```

### scripts/run_twins.sh

```bash
#!/bin/bash
# run_twins.sh: the rest twins of all arms from the horizontally uniform balance_column rest state
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R
L=()
for g in uni str; do for dt in 1.6 0.8; do for s in 9 0; do L+=("$g $dt $s float64 rest"); done; L+=("$g $dt 9 float32 rest_f32"); done; done
printf '%s\n' "${L[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; ty=$3; sfx=$4; tag=${g}_dt${dt}_s${s}_${sfx}
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_rest_uniform.pt \
  --dt $dt --tlim 1000 --threads 2 --dtype $ty --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
```

### scripts/run_checks.sh

```bash
#!/bin/bash
# run_checks.sh: the two supplementary checks of the report
#  1) integrator attribution: the scheme-9 dt/2 arms with integration/type rk2 (weights 1/2, 1/2 exact)
#     (twins here are the bryan.release dT=0 restart, i.e. before the uniform-twin fix; used for (b)-(c) only)
#  2) SNAP_WB_REF4=1 (fourth-order WB density reference) on the scheme-9 dt/2 arms, uniform twins
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R; mkdir -p runs_rk2 runs_wb4
for g in str uni; do sed 's/type: rk3/type: rk2/' decks/run_${g}_s9.yaml > decks/run_${g}_s9_rk2.yaml; done
for g in str uni; do for d in float64 float32; do
  python scripts/run_arm.py --deck decks/run_${g}_s9_rk2.yaml --ic ic/${g}_rest/ic_${g}_rest.00000.restart --dt 0.8 --dtype $d --out runs_rk2/${g}_dt0.8_s9_rest_rk2_$d.npz
  python scripts/run_arm.py --deck decks/run_${g}_s9_rk2.yaml --ic ic/${g}_bubble/ic_${g}_bubble.00000.restart --dt 0.8 --dtype $d --out runs_rk2/${g}_dt0.8_s9_bubble_rk2_$d.npz
done; done
for g in str uni; do
  SNAP_WB_REF4=1 python scripts/run_arm.py --deck decks/run_${g}_s9.yaml --ic ic/${g}_bubble/ic_${g}_bubble.00000.restart --dt 0.8 --out runs_wb4/${g}_dt0.8_s9_bubble.npz
  SNAP_WB_REF4=1 python scripts/run_arm.py --deck decks/run_${g}_s9.yaml --ic ic/${g}_rest_uniform.pt --dt 0.8 --out runs_wb4/${g}_dt0.8_s9_rest.npz
done
```

### scripts/analyze.py

```python
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
```

### scripts/check_pe.py

```python
#!/usr/bin/env python3
"""Cross-check run_arm.py's E and PE against snapy's own print_cycle_info
(meshblock.cpp:1103-1215 @3c891cb): runs 2 steps of a deck copy with
ncycle_out: 1 and prints both.   check_pe.py <deck> <ic> <dt>"""
import subprocess, sys, tempfile, os
deck, ic, dt = sys.argv[1:4]
txt = open(deck).read().replace("ncycle_out: 0", "ncycle_out: 1")
tmp = tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, dir=".")
tmp.write(txt); tmp.close()
here = os.path.dirname(os.path.abspath(__file__))
src = open(f"{here}/run_arm.py").read().replace(
    "rec.append(d)",
    'rec.append(d); b.print_cycle_info(vars_, t, a.dt); '
    'print("mine E=%.16e pe=%.16e ke=%.16e dry=%.16e" % (d["E"], d["PE"], d["ke"], d["dry"]), flush=True)')
sys.argv = ["run_arm.py", "--deck", tmp.name, "--ic", ic, "--dt", dt, "--tlim", str(2 * float(dt)), "--out", tmp.name + ".npz"]
try:
    exec(compile(src, "run_arm.py", "exec"), {"__name__": "__main__"})
finally:
    os.unlink(tmp.name)
    if os.path.exists(tmp.name + ".npz"): os.unlink(tmp.name + ".npz")
```

### scripts/check_fp32.py

```python
#!/usr/bin/env python3
"""Float32 end-to-end check: the scheme-9 Bryan deck, moved to float32, 3 steps.
usage: check_fp32.py deck ic dt"""
import sys, torch, snapy
from snapy import MeshBlock, MeshBlockOptions
deck, ic, dt = sys.argv[1], sys.argv[2], float(sys.argv[3])
torch.set_num_threads(2)
b = MeshBlock(MeshBlockOptions.from_yaml(deck))
b.to(torch.device("cpu"), torch.float32)
w = snapy.load_restart(ic, 0)["hydro_w"].float()
r = torch.full((1,) + tuple(w.shape[1:]), 1.e-3, dtype=torch.float32)
try:
    v, _ = b.initialize({"hydro_w": w, "scalar_r": r})
    print("init ok; dtypes:", {k: str(t.dtype) for k, t in v.items() if hasattr(t, "dtype")})
    for step in range(3):
        b.inc_cycle()
        for st in range(len(b.intg.stages)):
            b.forward(v, dt, st)
        print("step", step + 1, "hydro_u", v["hydro_u"].dtype, "finite", bool(torch.isfinite(v["hydro_u"]).all()))
    print("buffer dtypes:", sorted({str(t.dtype) for _, t in b.named_buffers()}))
except Exception as e:
    print("FP32 FAILED:", type(e).__name__, str(e).splitlines()[0][:400])
```

### decks/run_uni_s9.yaml

```yaml
reference-state:
  Tref: 0.0
  Pref: 1.e5
species:
- name: dry
  composition:
    O: 0.4200039819342909
    N: 1.560014790041652
    Ar: 0.01
  cv_R: 2.5
- name: H2O
  composition:
    H: 2
    O: 1
  cv_R: 3.08424
  u0_R: 0.0
- name: H2O(l)
  composition:
    H: 2
    O: 1
  cv_R: 9.070249
  u0_R: -6778.6962
geometry:
  type: cartesian
  bounds:
    x1min: 0.0
    x1max: 10.e3
    x2min: 0.0
    x2max: 20.e3
    x3min: -0.5
    x3max: 0.5
  cells:
    nx1: 400
    nx2: 25
    nx3: 1
    nghost: 3
distribute:
  layout: slab
dynamics:
  equation-of-state:
    type: ideal-moist
    density-floor: 1.0e-10
    pressure-floor: 1.0e-10
    limiter: true
    max-iter: 20
    ftol: 1.0e-08
  reconstruct:
    vertical:
      type: weno5
      scale: false
      shock: false
    horizontal:
      type: weno5
      scale: false
      shock: false
  riemann-solver:
    type: lmars
boundary-condition:
  external:
    x1-inner: reflecting
    x1-outer: reflecting
    x2-inner: reflecting
    x2-outer: reflecting
    x3-inner: periodic
    x3-outer: periodic
integration:
  type: rk3
  cfl: 0.9
  implicit-scheme: 9
  nlim: -1
  tlim: 1000.0
  ncycle_out: 0
outputs: []
forcing:
  const-gravity:
    grav1: -9.81
reactions:
- equation: H2O <=> H2O(l)
  type: nucleation
  rate-constant:
    formula: h2o_bryan
problem:
  dT: 2.0
  xc: 10.e3
  zc: 2.e3
  xr: 2.e3
  zr: 2.e3
  p0: 1.e5
  Ts: 289.85
  qt: 0.0196
  balance-ic: false
  balance-ic-passes: 8
scalar:
  names:
  - tracer
  reconstruct:
    type: weno5
    shock: false
```

### Other decks (differences from decks/run_uni_s9.yaml)

```diff
--- run_uni_s9.yaml vs run_str_s9.yaml
33c33
<     nx1: 400
---
>     nx1: 62
36a37
>     x1rat: 1.05
--- run_uni_s9.yaml vs run_uni_s0.yaml
69c69
<   implicit-scheme: 9
---
>   implicit-scheme: 0
--- run_uni_s9.yaml vs ic_uni_bubble.yaml
69,70c69,70
<   implicit-scheme: 9
<   nlim: -1
---
>   implicit-scheme: 0
>   nlim: 0
72,73c72,75
<   ncycle_out: 0
< outputs: []
---
>   ncycle_out: 1
> outputs:
> - type: restart
>   dt: 1000000000.0
93,98d94
< scalar:
<   names:
<   - tracer
<   reconstruct:
<     type: weno5
<     shock: false
--- run_uni_s9.yaml vs ic_uni_rest.yaml
69,70c69,70
<   implicit-scheme: 9
<   nlim: -1
---
>   implicit-scheme: 0
>   nlim: 0
72,73c72,75
<   ncycle_out: 0
< outputs: []
---
>   ncycle_out: 1
> outputs:
> - type: restart
>   dt: 1000000000.0
83c85
<   dT: 2.0
---
>   dT: 0.0
91,98c93,94
<   balance-ic: false
<   balance-ic-passes: 8
< scalar:
<   names:
<   - tracer
<   reconstruct:
<     type: weno5
<     shock: false
---
>   balance-ic: true
>   balance-ic-passes: 40
(run_str_s0 = run_str_s9 with implicit-scheme: 0; ic_str_* = ic_uni_* with nx1: 62, x1rat: 1.05; run_*_s9_rk2 = run_*_s9 with integration/type: rk2)
```
