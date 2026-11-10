# Per-step float32 vs float64 series: snapy conservation run, scheme 9

Bryan-Fritsch moist bubble from snapy's own `examples/bryan.yaml`, run to t = 1000 s with:
- passive tracer r0 = 1e-3, started uniform;
- `implicit-scheme: 9` (vic-full), rk3, limiter on, well-balanced x1 reconstruction (on with gravity);
- default (second-order, key 2) conversion: `dynamics/conversion-order` does not exist at this commit.

Fixed dt per arm. Each arm has a bubble run and a rest twin. The twin is the `balance_column` rest state, with column 0 copied to every column (the clean twin).

## Commit and versions
- **chengcli/snapy:** `3c891cb20614260351944fb8007cbc9bd50d22a3`, CPU Release source build (`CUDA=OFF`, `NETCDF=ON`). main has since moved, to `bd40fd25af4b8d9cac8ccb70e0499768c69a5fc3` at 2026-11-10 01:36Z. These series are from 3c891cb.
- **kintera:** 2.6.9, source build of chengcli/kintera `b8e726ce2fb1538aa15f0787fdcef732d9cdc997`.
- **Others:** torch 2.10.0+cu128 (run on CPU), pyharp 2.7.6, Python 3.12.3.

## Arms
| arm | grid | nx1 x nx2 | dz | dt (s) | steps | vertical acoustic Courant |
|---|---|---|---|---|---|---|
| uni_dt1.6_s9 | uniform | 400 x 25 | 25 m | 1.6 | 625 | 21.68 |
| uni_dt0.8_s9 | uniform | 400 x 25 | 25 m | 0.8 | 1250 | 10.84 |
| str_dt1.6_s9 | stretched, x1rat 1.05 | 62 x 25 | 24.6-480 m | 1.6 | 625 | 21.24 |
| str_dt0.8_s9 | stretched, x1rat 1.05 | 62 x 25 | 24.6-480 m | 0.8 | 1250 | 10.62 |

- dx = 800 m on both grids.
- Max adjacent width ratio: 1.0500 (stretched), 1.0000 (uniform).
- Max dz/H: 0.0769 (stretched), 0.0039 (uniform).

Each arm was run in float64 and in float32: the whole MeshBlock was moved to that dtype. Diagnostics are summed in float64 from the run's state.

## Files
- `conservation_long.csv`: one row per (arm, precision, step). Step 0 is the initialised state.
- `conservation_paired.csv`: one row per (arm, step). Each quantity column appears twice, as `<col>_f32` and `<col>_f64`.
- `rates.csv`: per (arm, precision, quantity):
  - `end_value` at the last step (t = 1000 s);
  - `rate_per_step`: least-squares slope over all steps;
  - `rate_eps_per_step`: the same rate in eps units;
  - `loglog_exponent`: slope of log|q| vs log(step) for step >= 1.
- `scripts/`: the drivers, deck generator, twin builder, exporter and decks used.

## Columns
- **Identifiers:** `arm`, `grid`, `dt` (s), `precision` (float64 or float32), `step`, `time` (= step × dt, in s).
- **(a) Rest twin** (twin run, interior cells):
  - `twin_wmax_ms`: max |velocity component| over the three components, in m/s.
  - `twin_max_dp_over_p0`: max |p/p0 - 1|.
  - `twin_max_drho_over_rho0`: max |rho/rho0 - 1|, where rho is the total density.
  - p0 and rho0 are the initialised state. Primitives come from snapy's EOS `U->W`, so step 0 already shows the round-trip error (a few eps).
- **(b) E+PE** (bubble run): `EPE_rel_drift` = (E+PE)_n / (E+PE)_0 - 1.
  - E = sum of the conserved energy u[IPR] dV.
  - PE is snapy's own corrected PE: rho g z dV with the centroid correction of `gravity_work_radial.hpp`. It matches `print_cycle_info`'s `pe=` to all 14 printed digits.
- **(c) Mass** (bubble run):
  - `dry_mass_rel_drift` = M_dry,n / M_dry,0 - 1, with M_dry = sum of u[IDN] dV.
  - `water_rel_drift`: the same for total water, H2O + H2O(l).
- **(d) Tracer** (bubble run): `tracer_max_abs_r_over_r0_m1` = max |r/r0 - 1|, where r = scalar_s / u[IDN].
- **eps columns:** every `*_eps` column is the value divided by the run's own machine epsilon:
  - eps64 = 2^-52 = 2.220446049250313e-16;
  - eps32 = 2^-23 = 1.1920928955078125e-07.
- **Formatting:** all values are written with Python `repr` (full double precision).

## Note on the drift
The E+PE, dry mass and water drift is linear: about -0.26 eps64/step in float64 and +0.26 eps32/step in float32. It comes from the rk3 stage-3 weights fl(1/3) and fl(2/3), whose exact sum is 1 - eps64/4 in float64 and 1 + eps32/4 in float32. With rk2 the drift was <= 0.006 eps/step (earlier report).

## Reproduce
See `scripts/README_order.txt`. Then run:

    python scripts/export_csv.py runs out/
