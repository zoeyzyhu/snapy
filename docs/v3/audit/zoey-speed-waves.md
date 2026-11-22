# V3 speed by wave: where the extra eager time went (v2.14.1 → wave 1 → wave 2 → waves 3–5)

Asked by Xi (2026-11-22, 1795373905), as a follow-up to chen sihe's `speed.md` (cshsgy/snapy `v3/audit-speed` `80619cbcb4ef3173c1889bd0d9c803d8701036ad`). That audit shows V3 eager at 0.69–0.88× of v2.14.1. This note is measurement only.

The four trees are timed on one quiet machine with the same flags and the same kintera and pyharp packages:

| label | commit | tag |
|---|---|---|
| v2.14.1 | `730b35007d16389c64116e4bf9d2fe93707e29e9` | v2.14.1 |
| wave 1 | `6007eaa9f1f3a66fdfd929616ca219ee3f560bd2` | v2.14.2 |
| wave 2 | `deeabfee597cd83f68f4586d245b01f6091eaa6e` | v2.14.3 |
| waves 3–5 | `d3178f207b60663ff966b7c7ef20025821ef52fa` | v3/wave3, the #313 head |

Numbers are wall time per time step (all RK3 stages) after warm-up. Each value is the median of 3 independent runs, with the spread of the 3 run medians in parentheses. Lower is better.

## Tables

| case | v2.14.1 `730b3500` | wave 1 `6007eaa9` | wave 2 `deeabfee` | waves 3–5 `d3178f20` | v2.14.1 / d3178f20 |
|---|---|---|---|---|---|
| 1. Straka 2-D (HLLC, ideal-moist dry, 64×256), CPU 1 rank, FP64 | 29.50 ms (29.30–29.76) | 29.75 ms (29.71–29.85) | 32.65 ms (32.51–32.85) | 32.62 ms (32.60–33.24) | 0.90× |
| 1. Straka 2-D, CUDA FP64 eager | 7.36 ms (7.34–7.42) | 7.37 ms (7.32–7.47) | 9.18 ms (9.13–9.33) | 9.26 ms (9.23–9.30) | 0.80× |
| 2. cart3d_pert 64³ (moist 3-D), CPU 1 rank | 1393.92 ms (1389.01–1400.10) | 1481.09 ms (1452.47–1481.60) | 1685.18 ms (1675.95–1693.90) | 1657.22 ms (1653.48–1676.94) | 0.84× |

Per-wave deltas (median − median of the previous tree):

| case | wave 1 (730b3500 → 6007eaa9) | wave 2 (6007eaa9 → deeabfee) | waves 3–5 (deeabfee → d3178f20) | total |
|---|---|---|---|---|
| 1. Straka CPU 1 rank | +0.25 ms | **+2.89 ms** | −0.03 ms | +3.12 ms |
| 1. Straka CUDA FP64 eager | +0.00 ms | **+1.81 ms** | +0.08 ms | +1.90 ms |
| 2. cart3d_pert 64³ CPU 1 rank | +87.2 ms | **+204.1 ms** | −28.0 ms | +263.3 ms |

**Reading.**
- Wave 2 (`deeabfee`, #372: flux register, EOS and floors, reconstruction, cubed-sphere faces, MeshBlock split, implicit face work) adds the time in every cell: 93 % of the Straka CPU increase, 96 % of the Straka CUDA increase and 78 % of the cart3d increase.
- Wave 1 adds 87 ms (+6.3 %) on cart3d but nothing measurable on Straka.
- Waves 3–5 add nothing. On both CPU cells they are slightly faster than wave 2; on CUDA they are +0.08 ms, inside the spread.
- On this machine V3 is at 0.80–0.90× of v2.14.1, which is consistent with speed.md's 0.79–0.88× for the same cells.

## Profile: Straka CPU 1 rank at the four trees

**Tool.** perf could not be used here (`kernel.perf_event_paranoid = 4`, no root), and snapy has no stage timers or `RECORD_FUNCTION` markers. I used py-spy 0.4.4 instead, a sampling profiler that unwinds native C++ frames with symbols: `py-spy record --native -r 100 -f raw`.

**Setup.**
- py-spy samples only Python-attached threads, so the profiled runs use one torch/OpenMP thread (`OMP_NUM_THREADS=1 --threads 1`), and the main thread does all the work.
- Straka's ms/step is the same at 1 and 8 threads on this host: 29.56 vs 29.50 ms at 730b3500, and 32.96 vs 32.62 ms at d3178f20.
- Each profile covers 3 + 1500 steps, which gives 5,493–6,379 samples inside bench.py's `step()`.
- py-spy slows the target, so the sample fractions are converted to ms/step using unprofiled 1-thread runs of the same deck (2 runs each): 730b3500 29.56, 6007eaa9 29.65, deeabfee 33.20, d3178f20 32.96 ms/step.
- Errors are binomial 1-sigma sampling errors.

**Stage attribution.** Each sampled stack is charged to the first matching stage, in the row order below (`stages.py`):

| stage | `730b3500` | `6007eaa9` | `deeabfee` | `d3178f20` | d3178f20 − 730b3500 | wave 2 (deeabfee − 6007eaa9) |
|---|---|---|---|---|---|---|
| flux register (FluxRegister::*, supply_prescribed) | 0.00 (0.0%) | 0.00 (0.0%) | 2.90 (8.7%) | 2.94 (8.9%) | **+2.94 ± 0.12** | **+2.90 ± 0.12** |
| positivity limiter (PositivityLimiter / flux_positivity_theta) | 0.64 (2.2%) | 0.56 (1.9%) | 1.26 (3.8%) | 1.16 (3.5%) | +0.52 ± 0.10 | +0.70 ± 0.10 |
| scalar transport (ScalarImpl::forward, incl. its reconstruction) | 9.32 (31.5%) | 9.58 (32.3%) | 8.77 (26.4%) | 8.84 (26.8%) | −0.48 ± 0.26 | −0.81 ± 0.26 |
| Riemann solve (HLLC, perturbation path) | 3.53 (11.9%) | 3.52 (11.9%) | 4.46 (13.4%) | 4.06 (12.3%) | +0.53 ± 0.19 | +0.94 ± 0.19 |
| hydro reconstruction (ReconstructImpl::forward) | 4.70 (15.9%) | 4.74 (16.0%) | 4.66 (14.0%) | 5.22 (15.8%) | +0.52 ± 0.21 | −0.08 ± 0.21 |
| x1 hydrostatic reference (_hydro_ref_x1 / X1Reference / WellBalancedX1) | 3.94 (13.3%) | 3.88 (13.1%) | 4.61 (13.9%) | 4.56 (13.8%) | +0.62 ± 0.20 | +0.73 ± 0.20 |
| EOS (cons2prim, perturbations, compute) | 1.73 (5.8%) | 1.75 (5.9%) | 1.96 (5.9%) | 1.58 (4.8%) | −0.15 ± 0.13 | +0.21 ± 0.14 |
| coordinate (divergence, vec raise) | 0.75 (2.5%) | 1.04 (3.5%) | 0.61 (1.8%) | 0.42 (1.3%) | −0.33 ± 0.08 | −0.43 ± 0.09 |
| ghost exchange and boundaries | 0.40 (1.3%) | 0.41 (1.4%) | 0.43 (1.3%) | 0.60 (1.8%) | +0.20 ± 0.07 | +0.02 ± 0.07 |
| rest of HydroImpl::forward | 3.33 (11.3%) | 3.07 (10.3%) | 2.66 (8.0%) | 2.57 (7.8%) | −0.75 ± 0.17 | −0.41 ± 0.17 |
| rest of MeshBlock step (advance_local, integrator, executor) | 0.93 (3.1%) | 0.79 (2.7%) | 0.63 (1.9%) | 0.69 (2.1%) | −0.23 ± 0.09 | −0.16 ± 0.09 |
| outside snap (python/pybind/torch dispatch only) | 0.30 (1.0%) | 0.30 (1.0%) | 0.23 (0.7%) | 0.29 (0.9%) | −0.01 ± 0.06 | −0.06 ± 0.05 |
| total (unprofiled 1-thread ms/step) | 29.56 | 29.65 | 33.20 | 32.96 | +3.40 | +3.55 |
| samples in step() | 5573 | 5493 | 6379 | 6171 | | |

**Where the extra time is (Straka CPU, +3.40 ms/step from 730b3500 to d3178f20).**

1. **The flux register, +2.94 ± 0.12 ms/step.** This is the whole net increase within error; the other rows roughly cancel (+0.46 ms in sum, error about ±0.5 ms). All of it arrives in wave 2 (+2.90). Breakdown at d3178f20 (`prof/flux_register_breakdown.txt`):
   - `HydroImpl::forward → FluxRegister::apply_prescribed`: 2.08 ms/step. A further 0.21 ms/step comes in through `ScalarImpl::forward`.
   - `supply_prescribed`: 0.40 ms/step, from Hydro 0.23 and from Scalar 0.17.
   - `FluxRegister::end_stage`: 0.21 ms/step.
   - **The ATen ops underneath.**
     - `apply_prescribed` (`src/hydro/flux_register.cpp:390-404` @ d3178f20) runs `torch::where(mask, value, t)` over the whole face field, 0.95 ms/step. It then calls `overwrite_`.
     - `overwrite_` (`:300-316`) books `(area * (after − t)).sum({1,2,3})` over the whole face field. That is `mul` 0.50 ms/step plus `sub` 0.44 ms/step, then `copy_`. The `sum` is 0.06 ms/step.
     - `supply_prescribed` runs `repeat` (0.20 ms/step) and `zeros_like` (0.08 ms/step).
     - Nearly all of these samples are TensorIterator elementwise loops (`c10::function_ref::callback_fn`, 2.17 ms/step).
   - **Hypothesis (not tested):** the register prescribes only the wall faces, but `where`, `mul`, `sub` and `copy_` run over every face of every direction, every stage. Restricting them to the masked face planes, or skipping when the prescribed value already equals the total, would remove most of this.
2. **The remaining wave-2 rows.** The Riemann solve on the perturbation path (`riemann_solve → RiemannSolverImpl::solve`) is +0.94 ± 0.19 in wave 2. Waves 3–5 bring it back to +0.53 over v2.14.1. The positivity limiter (`PositivityLimiter::apply`, replacing `flux_positivity_theta`) is +0.70 ± 0.10, and the x1 reference (`X1Reference` / `WellBalancedX1`) is +0.73 ± 0.20. Scalar transport (−0.81), coordinate (−0.43) and the rest of `HydroImpl::forward` (−0.41) partly offset these.
3. **Waves 3–5** move time between rows but not in total. Reconstruction is +0.56 against deeabfee, Riemann −0.40, EOS −0.38, and ghost exchange +0.17 (`LayoutImpl::fill_corners`).

Per-function inclusive times for all four trees, sorted by the change (several functions were renamed in wave 2, e.g. `HLLCSolverImpl::forward_perturbations` → `RiemannSolverImpl::forward_perturbations`, `call_weno5_cpu`/`call_poly_cpu` → `recon_line_cpu`), are in `zoey-speed-waves/prof/compare_inclusive.txt`. The top self and inclusive lists per tree are in `prof/report.<tree>.txt`.

## Machine (quiet) and checks

- **Host:** AMD Ryzen 5 7600X (6 cores, 12 threads), 62 GB, NVIDIA GeForce RTX 5090 (32 GB, driver 580.178.04), Ubuntu 24.04.5 LTS.
- **Toolchain:** gcc 13.3.0, nvcc 12.9.86, cmake 3.30.0, Python 3.12.3, torch 2.10.0+cu128.
- **Packages:** kintera 2.6.11 (`431fd144`) and pyharp 2.8.1 (installed wheel), the same packages for all four builds.
- **Quiet machine:** no other user jobs. The GPU had no other compute process (`nvidia-smi --query-compute-apps` empty, 280 MiB used, 0 % before the runs).
  - Load average was 4.17 at the start (the end of my own builds, decaying) and 1.0–1.8 during the cart3d cells.
  - Load and GPU state before and after every run are in `zoey-speed-waves/runs/state.log`. The GPU utilisation printed there (≈ 57 %) is the sample taken right after a CUDA run, i.e. the run itself.
  - Cells ran 2026-11-22T19:36:27Z → 19:48:03Z. Profiles ran 19:50:57Z → 19:55:02Z, with the 1-thread references after them.
- **Same physics in every tree:** the built-in Straka deck reads each tree's own `examples/straka.yaml` and `tests/test_anomaly_storage.yaml`, which are byte-identical in all four trees. `dt0` is identical in all four trees for every case (Straka 0.2594361089829126, cart3d 0.023306639802554097). Every run ended finite.
- **Execution path:** the d3178f20 CUDA cells report `execution_report` captures 0 / eager 315, i.e. eager as intended.

## Builds

The same command for all four trees (`zoey-speed-waves/build_tree.sh`), one after another (505–560 s each):

```
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.9/bin/nvcc \
      -DNETCDF=OFF -DPNETCDF=OFF -DUCX=OFF -DBUILD_TESTS=OFF        # PYTHONPATH = the kintera 2.6.11 package
cmake --build build --parallel 12
pip install --no-deps --no-build-isolation --target pkg-<sha> .
```

- The CUDA architecture list is set by each tree's CMake. It is identical in all four: 60, 61, 70, 75, 80, 86, 89, 90, 120.
- Compiler warning lines: 38, 36, 35 and 35.
- Differences from speed.md's builds: `-DUCX=OFF`, and the GPU (sm_120 here, sm_90 there). That only matters for the multi-rank cells, which are not timed here.

## Decks and method

- **Harness:** chen sihe's `docs/v3/audit/speed/bench.py` at `80619cbc` (sha256 `8676ebb68563701c`), unchanged.
- **Decks:** its built-in `straka_hllc` deck with `--init straka --nb2 1`, and its `cart3d_pert_64.yaml` with the generic hydrostatic init. Both are described in speed.md.
- **Deck adaptation:** none needed. bench.py only writes `integration/execution` for non-eager runs, and every cell here is eager, so v2.14.1 (which rejects the key) runs the same decks unchanged.
- **Driver:** a single block in a single process, through `MeshBlock.forward`.
- **Steps and threads:** CPU 3 warm-up + 30 timed steps, CUDA 5 + 100. 8 threads (`torch.set_num_threads(8)`, `OMP_NUM_THREADS=8`). Fixed dt = `dt0`. CUDA is synchronised around each step.
- **Runs:** each cell is 3 independent processes, with the four trees interleaved within each rep (`run_cells.sh`).

Commands:

```
bash build_tree.sh <sha8>            # for 730b3500 6007eaa9 deeabfee d3178f20
bash run_cells.sh                     # all timing cells
bash profile.sh                       # py-spy profiles + unprofiled 1-thread references
python3 stages.py                     # stage table; analyze_prof.py <collapsed> <ms> for per-function lists
```

Raw data: `zoey-speed-waves/summary.json` (cells, per-wave deltas, profile stages, host, packages), `runs/*.json` (every per-step time for every run), `runs/state.log`, and `prof/` (gzipped collapsed stacks, per-tree reports, stage table, inclusive comparison and the flux-register breakdown).

## Caveats and not done

- **Profiles are CPU only, Straka only, 1 thread.** The CUDA wave-2 increase (+1.81 ms/step) and the cart3d increases (wave 1 +87 ms, wave 2 +204 ms) were not profiled. Whether the same register ops explain them is an untested hypothesis.
- **py-spy is a 100 Hz sampler.** The per-function numbers carry the sampling errors shown, and ms/step comes from separate unprofiled runs.
- Not run: CUDA FP32, cuda-graph, multi-rank, cubed-sphere, arm64, MPS.
- Timing is on a different, smaller machine than speed.md's, so the absolute values differ. The ratios agree.
- This audit changes no snapy source. It is documentation only, on a branch of `zoeyzyhu/snapy` based on d3178f20.
