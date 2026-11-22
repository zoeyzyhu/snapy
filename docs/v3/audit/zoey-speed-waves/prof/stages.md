| stage | `730b3500` | `6007eaa9` | `deeabfee` | `d3178f20` | d3178f20 − 730b3500 | wave 2 (deeabfee − 6007eaa9) |
|---|---|---|---|---|---|---|
| flux register (FluxRegister::*, supply_prescribed) | 0.00 (0.0%) | 0.00 (0.0%) | 2.90 (8.7%) | 2.94 (8.9%) | +2.94 ± 0.12 | +2.90 ± 0.12 |
| positivity limiter (PositivityLimiter / flux_positivity_theta) | 0.64 (2.2%) | 0.56 (1.9%) | 1.26 (3.8%) | 1.16 (3.5%) | +0.52 ± 0.10 | +0.70 ± 0.10 |
| scalar transport (ScalarImpl::forward, incl. its reconstruction) | 9.32 (31.5%) | 9.58 (32.3%) | 8.77 (26.4%) | 8.84 (26.8%) | -0.48 ± 0.26 | -0.81 ± 0.26 |
| Riemann solve (HLLC, perturbation path) | 3.53 (11.9%) | 3.52 (11.9%) | 4.46 (13.4%) | 4.06 (12.3%) | +0.53 ± 0.19 | +0.94 ± 0.19 |
| hydro reconstruction (ReconstructImpl::forward) | 4.70 (15.9%) | 4.74 (16.0%) | 4.66 (14.0%) | 5.22 (15.8%) | +0.52 ± 0.21 | -0.08 ± 0.21 |
| x1 hydrostatic reference (_hydro_ref_x1 / X1Reference / WellBalancedX1) | 3.94 (13.3%) | 3.88 (13.1%) | 4.61 (13.9%) | 4.56 (13.8%) | +0.62 ± 0.20 | +0.73 ± 0.20 |
| EOS (cons2prim, perturbations, compute) | 1.73 (5.8%) | 1.75 (5.9%) | 1.96 (5.9%) | 1.58 (4.8%) | -0.15 ± 0.13 | +0.21 ± 0.14 |
| coordinate (divergence, vec raise) | 0.75 (2.5%) | 1.04 (3.5%) | 0.61 (1.8%) | 0.42 (1.3%) | -0.33 ± 0.08 | -0.43 ± 0.09 |
| ghost exchange and boundaries | 0.40 (1.3%) | 0.41 (1.4%) | 0.43 (1.3%) | 0.60 (1.8%) | +0.20 ± 0.07 | +0.02 ± 0.07 |
| rest of HydroImpl::forward | 3.33 (11.3%) | 3.07 (10.3%) | 2.66 (8.0%) | 2.57 (7.8%) | -0.75 ± 0.17 | -0.41 ± 0.17 |
| rest of MeshBlock step (advance_local, integrator, executor) | 0.93 (3.1%) | 0.79 (2.7%) | 0.63 (1.9%) | 0.69 (2.1%) | -0.23 ± 0.09 | -0.16 ± 0.09 |
| outside snap (python/pybind/torch dispatch only) | 0.30 (1.0%) | 0.30 (1.0%) | 0.23 (0.7%) | 0.29 (0.9%) | -0.01 ± 0.06 | -0.06 ± 0.05 |
| total (unprofiled 1-thread ms/step) | 29.56 | 29.65 | 33.20 | 32.96 | +3.40 | +3.55 |
| samples in step() | 5573 | 5493 | 6379 | 6171 | | |
