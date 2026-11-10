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
