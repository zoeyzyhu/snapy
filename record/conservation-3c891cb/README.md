# Record of the combined conservation run: snapy 3c891cb, Bryan-Fritsch moist bubble

**Provenance of this branch:** the record is for chengcli/snapy `3c891cb20614260351944fb8007cbc9bd50d22a3`; the parent of the commit that adds it on this branch is the fork's own main (zoeyzyhu/snapy `117e449a620bd7fd50abe19239ab660a56d5d4cb`), not that sha. The record is data only; check out chengcli/snapy at 3c891cb to rebuild.

This archive packages the files behind the run; it contains no new runs. The CSVs are exports of the per-step series saved by `scripts/run_arm.py` (the `raw_npz/` files).

## Code, versions, build

- **snapy:** chengcli/snapy `3c891cb20614260351944fb8007cbc9bd50d22a3`, a clean checkout with `git status --porcelain` empty. Every arm below ran on this one build. main has since moved, to bd40fd2 at 2026-11-10 01:38Z; these files are for 3c891cb only.
- **snapy build:** CPU Release source build. GCC 13.3.0, cmake 3.30.0.
- **Exact snapy build line** (from `scripts/build_snapy.sh`, run as `build_snapy.sh b`):
  ```
  cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DNETCDF=ON -DBUILD_TESTS=ON -DFULL_TESTS=OFF -DSNAPY_TEST_PYTHONPATH="$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
  cmake --build build --config Release --parallel 8
  pip install --no-build-isolation --no-deps .
  ```
  The resulting CMakeCache has `CMAKE_BUILD_TYPE=Release, CUDA=OFF, NETCDF=ON, PNETCDF=ON, UCX=ON, BUILD_TESTS=ON, FULL_TESTS=OFF`; PNETCDF and UCX are the Linux defaults and were not passed explicitly. The IC binary `bryan.release` comes from the same build tree (`build/bin/bryan.release`). The examples directory is always built at this commit.
- **kintera:** 2.6.9, source build of chengcli/kintera `b8e726ce2fb1538aa15f0787fdcef732d9cdc997` (tag v2.6.9), from `scripts/build_kintera.sh`:
  ```
  cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DNETCDF=ON -DBUILD_TESTS=OFF
  cmake --build build --parallel 10
  pip install --no-build-isolation --no-deps .
  ```
- **Python environment:** pyharp 2.7.6 (pip), torch 2.10.0+cu128 (pip, run on CPU), numpy 2.5.4, Python 3.12.3. The venv was created by `scripts/setup_env.sh`.
- **Common settings:** conversion is the hard-wired second-order one, i.e. key 2 (`dynamics/conversion-order` does not exist at 3c891cb). Limiter on (`equation-of-state/limiter: true`). The well-balanced x1 reconstruction is on, as it always is with gravity. gravity-work is `face`, the passive tracer starts at r0 = 1e-3, and t_end = 1000 s. dt is fixed (no `max_time_step`). nx2 = 25 (dx = 800 m) on both grids.
- **Grids:** max adjacent width ratio is 1.0500 (stretched) and 1.0000 (uniform). Max dz/H is 0.0769 and 0.0039. The vertical acoustic Courant number at dt = 1.6 / 0.8 s is 21.68 / 10.84 (uniform) and 21.24 / 10.62 (stretched).

## Arms (every run in this record)

| family | arm | precision | implicit scheme | integrator | WB_REF4 | grid | dt (s) | bubble run | rest twin | twin IC | CSV |
|---|---|---|---|---|---|---|---|---|---|---|---|
| scheme9 | uni_dt1.6_s9 | float64 | 9 | rk3 | off | uniform nx1=400 dz=25 m | 1.6 | ok, 625/625 steps | ok, 625/625 steps | uni_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme9 | uni_dt1.6_s9 | float32 | 9 | rk3 | off | uniform nx1=400 dz=25 m | 1.6 | ok, 625/625 steps | ok, 625/625 steps | uni_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme0 | uni_dt1.6_s0 | float64 | 0 | rk3 | off | uniform nx1=400 dz=25 m | 1.6 | stopped: redo at step 3 (2 steps recorded) | stopped: redo at step 4 (3 steps recorded) | uni_rest_uniform.pt | csv/scheme0_long.csv |
| scheme9 | uni_dt0.8_s9 | float64 | 9 | rk3 | off | uniform nx1=400 dz=25 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | uni_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme9 | uni_dt0.8_s9 | float32 | 9 | rk3 | off | uniform nx1=400 dz=25 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | uni_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme0 | uni_dt0.8_s0 | float64 | 0 | rk3 | off | uniform nx1=400 dz=25 m | 0.8 | stopped: redo at step 4 (3 steps recorded) | stopped: redo at step 6 (5 steps recorded) | uni_rest_uniform.pt | csv/scheme0_long.csv |
| rk2_control | uni_dt0.8_s9_rk2 | float64 | 9 | rk2 | off | uniform nx1=400 dz=25 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | ic_uni_rest.00000.restart | csv/rk2_control_long.csv, csv/rk2_control_paired.csv |
| rk2_control | uni_dt0.8_s9_rk2 | float32 | 9 | rk2 | off | uniform nx1=400 dz=25 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | ic_uni_rest.00000.restart | csv/rk2_control_long.csv, csv/rk2_control_paired.csv |
| wb_ref4 | uni_dt0.8_s9_wbref4 | float64 | 9 | rk3 | SNAP_WB_REF4=1 | uniform nx1=400 dz=25 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | uni_rest_uniform.pt | csv/wb_ref4_long.csv |
| scheme9 | str_dt1.6_s9 | float64 | 9 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 1.6 | ok, 625/625 steps | ok, 625/625 steps | str_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme9 | str_dt1.6_s9 | float32 | 9 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 1.6 | ok, 625/625 steps | ok, 625/625 steps | str_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme0 | str_dt1.6_s0 | float64 | 0 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 1.6 | stopped: redo at step 3 (2 steps recorded) | stopped: redo at step 5 (4 steps recorded) | str_rest_uniform.pt | csv/scheme0_long.csv |
| scheme9 | str_dt0.8_s9 | float64 | 9 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | str_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme9 | str_dt0.8_s9 | float32 | 9 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | str_rest_uniform.pt | csv/conservation_long.csv, csv/conservation_paired.csv, csv/rates.csv |
| scheme0 | str_dt0.8_s0 | float64 | 0 | rk3 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | stopped: redo at step 4 (3 steps recorded) | stopped: redo at step 6 (5 steps recorded) | str_rest_uniform.pt | csv/scheme0_long.csv |
| rk2_control | str_dt0.8_s9_rk2 | float64 | 9 | rk2 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | ic_str_rest.00000.restart | csv/rk2_control_long.csv, csv/rk2_control_paired.csv |
| rk2_control | str_dt0.8_s9_rk2 | float32 | 9 | rk2 | off | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | ic_str_rest.00000.restart | csv/rk2_control_long.csv, csv/rk2_control_paired.csv |
| wb_ref4 | str_dt0.8_s9_wbref4 | float64 | 9 | rk3 | SNAP_WB_REF4=1 | stretched x1rat=1.05 nx1=62 dz 24.6-480 m | 0.8 | ok, 1250/1250 steps | ok, 1250/1250 steps | str_rest_uniform.pt | csv/wb_ref4_long.csv |

Twin IC:
- `*_rest_uniform.pt` is the clean-column twin: the balance_column rest state from `bryan.release` with `dT: 0, balance-ic: true`, with its x2 column 0 copied to all columns by `scripts/make_twin_uniform.py`.
- `ic_*_rest.00000.restart` is the first-pass twin. It still carries the bisection residue inside the old bubble disk: a 1.3e-12 horizontal spread in density. This affects the rk2-control twins and the superseded twins. Their (a) rest residual includes the resulting ~5e-9 m/s flow. Their conservation columns (b)-(d) come from the bubble runs and are unaffected.

All runs are by the same driver, `scripts/run_arm.py`, and the same build. Only `run_arm.py` options and the deck differ.

## Directory layout

- **`decks/`:** all decks.
  - `run_{uni,str}_s{0,9}.yaml`: the run decks.
  - `run_*_s9_rk2.yaml`: the rk2 control.
  - `ic_{uni,str}_{bubble,rest}.yaml`: the `bryan.release` IC decks. The rest deck has dT = 0 and balance-ic true.
- **`ic/`:** IC states fed to the driver.
  - `ic_*.00000.restart`: written by `bryan.release`.
  - `*_rest_uniform.pt`: the clean-column twins.
- **`scripts/`:** the deck generator, twin builder, driver, batch scripts, fit/table script (`analyze.py`), CSV exporters, PE and float32 checks, and the build and env scripts. `README_order.txt` gives the execution order. Scripts contain the original absolute paths of the run directory.
- **`csv/`:** per-step CSVs. Column definitions are in `reports/fp32_fp64_csv_README.md` and the docstring of `scripts/export_extra_csv.py`.
  - `conservation_long.csv`, `conservation_paired.csv`, `rates.csv`: the headline scheme-9 arms, float32 and float64.
  - `scheme0_long.csv`, `rk2_control_long.csv`, `rk2_control_paired.csv`, `wb_ref4_long.csv`, `superseded_twin_bisect_ic_long.csv`, `extra_rates.csv`: the other runs.
  - Every relative quantity has an absolute column and an `_eps` column, in units of the run's own eps (eps64 = 2^-52, eps32 = 2^-23).
- **`raw_npz/`:** the per-step series as saved by the driver; the CSVs are exports of these.
- **`logs/`:** driver logs per run, batch outputs, and the `bryan.release` IC logs, including the balance-ic pass residuals.
- **`reports/`:** the original report (table, findings, appendix), the `analyze.py` table, and the README of the float32/float64 CSV export.

## Missing (never saved, not regenerated)

- **Plot script:** none exists, because no plot was ever made for this run. The reported numbers come from `scripts/analyze.py` and `scripts/export_csv.py`, which do the linear and log-log fits.
- **rk2 control at dt = 1.6 s and in scheme 0:** never run. The control covers only the dt = 0.8 s scheme-9 arms, in float32 and float64.
- **rk2 control with the clean-column twin:** never run. Its twins used the first-pass twin IC (see above).
- **WB_REF4 at dt = 1.6 s and in float32:** never run.
- **Float32 scheme-0 arms:** never run, because scheme 0 already diverges in float64.
- **Scheme-0 series after the redo stop:** these do not exist. The redo check stops the run, so the series end there (bubble at step 3/4, twin at step 4-6).
- **The original first-pass bubble series:** superseded. They were rerun bitwise-identical with the final driver for the CSV export; the copies here are the final-driver ones.
- **The two probe runs** used to locate the contaminated twin's flow: not included. They are one-off diagnostics duplicating `superseded_twin_bisect_ic` series.

## Files, sizes, CSV row counts, sha256

Row counts are data rows, excluding the header. `SHA256SUMS` covers every file, including this README.

| file | bytes | CSV rows | sha256 |
|---|---|---|---|
| csv/conservation_long.csv | 2109684 | 7508 | d7a45c77375ba70e4c5c33ac79d03943ac6cfa93bbefadeb1154a6f97e910c4d |
| csv/conservation_paired.csv | 1894355 | 3754 | 82ac035b864b4d33b917cb54e0f639858c77ee0e2e8db97f772e3860e03b364d |
| csv/extra_rates.csv | 15701 | 106 | f2ce8bb5391eb61bebef42a95c07f00b3453f7c2493b9d58118639bc415afac1 |
| csv/rates.csv | 8989 | 56 | 7694a30707d99295d29c2cffaf7fcc8a84b7a1055947d32f65c22370146fdfe2 |
| csv/rk2_control_long.csv | 1644437 | 5004 | 6154e51f654a1f673faf6317a460e285986767018f95c73634f08b7616e0d57f |
| csv/rk2_control_paired.csv | 1220527 | 2502 | 510ba18f70a3e52df106199949e4bd0c807d58e6039a194a06d8eef41a4887c6 |
| csv/scheme0_long.csv | 6598 | 21 | 6aa68b7047260be175b0f1e6ba982e3d799fb7160b4149db4836c108d0e2f380 |
| csv/superseded_twin_bisect_ic_long.csv | 1568023 | 7529 | f11263e6fafde30eac28b38f8bf22103b0d82e214a3292b0730da146710b32b9 |
| csv/wb_ref4_long.csv | 769492 | 2502 | 51ccacdad69a4ff92f44f08f1151c56744776eb1cd1a87233140d977da3b4f59 |
| decks/ic_str_bubble.yaml | 1501 |  | 0cd999a9ca1b2d2192654110d96ce5d782e7b1ef8bb095b29ad36256197bec98 |
| decks/ic_str_rest.yaml | 1501 |  | 221a1030e825de9c35109382809aa611fc4d8fce7c13ba1ab5a277effaa38be2 |
| decks/ic_uni_bubble.yaml | 1486 |  | 2d3674f0ca192fc208a7f1e9c1177c9902337c45901d2d9f705e32235dc8a227 |
| decks/ic_uni_rest.yaml | 1486 |  | 57405d00a0017db7d43990f24cfe7fbee502640388344de099723799bcf1109f |
| decks/run_str_s0.yaml | 1546 |  | 6316b2662b852ab7f139d639f0d1e3c8afd0d708fe9e82f97ac9f4c0a812e8f7 |
| decks/run_str_s9.yaml | 1546 |  | 22624af19f506a782de5678e192a898a1d7182b1d40462565d4b8b618b9ae14c |
| decks/run_str_s9_rk2.yaml | 1546 |  | 36d9b638261ccf23d2ebdc1f97d4948930bdc9b06db869488281c22198a9f1d2 |
| decks/run_uni_s0.yaml | 1531 |  | 6106f265243a43079f1bdeba4c630229d46440bd12fa41c32f1a8f5fb65f1bf3 |
| decks/run_uni_s9.yaml | 1531 |  | ce70ba5d47b91ebbf8c70e4fc6a0db44185faa770b0c03c2ead8c2d505dd0dc5 |
| decks/run_uni_s9_rk2.yaml | 1531 |  | 49b5bfe65d9e5ce1ff26f2326fc9ba0eaeb629440f7def809fdae615d69c6c9c |
| ic/ic_str_bubble.00000.restart | 240105 |  | 75050bce2e37d737bef2c16240123dda76e8fc8a43790ca4891c3f9f86c6b662 |
| ic/ic_str_rest.00000.restart | 240077 |  | 0fc6ffccd226aa95d2419876c3542db02c156023baecf0841764f75f9aa1ffab |
| ic/ic_uni_bubble.00000.restart | 1413737 |  | 67a3b5d5af38d94db5018f9e75e59065fab40440926d6ae16b8392f6d3fc9417 |
| ic/ic_uni_rest.00000.restart | 1413709 |  | b99422f5209476c15e3346e1b6138a72674049d054dd70157cd7042d3bbaca58 |
| ic/str_rest_uniform.pt | 119720 |  | 71481de9ba96045729947e3db30a99e5fcd842bfbab633654a95332fcb44c9e6 |
| ic/uni_rest_uniform.pt | 706472 |  | 902e6fc83f16f4e386e9f5e86b0ee9db1d2c21da2d9055d720e0e931ffd10302 |
| logs/ic/bryan_ic_str_bubble.log | 305 |  | 66585308f215be30bc939fe1eab6b0e3d83d2016b8731b1740c47950c4f0f53e |
| logs/ic/bryan_ic_str_rest.log | 1470 |  | fd150b8adeb24c0eb15741d14796482d58722061c91eb77fa25c4f7c2ff96505 |
| logs/ic/bryan_ic_uni_bubble.log | 305 |  | 3d5d0289233c77d28fc6f480f9036b905f2b9ee08ce7258c6b42d900e9c3e42d |
| logs/ic/bryan_ic_uni_rest.log | 1179 |  | 868cf49437d4f2d86aa5822c7ac0bbde0186de3d8b215acf754539e0b1f56f81 |
| logs/runs/run_all.out | 3716 |  | 2eb552cb92cb97926b5a8aff195568f9e642090a0028368ad6f9861253432018 |
| logs/runs/run_all_first_pass.out | 2484 |  | ea09d8fdcff947a68dd55e312e246e3b75bb248cdb74bb8e1b53960566e536b1 |
| logs/runs/run_twins.out | 1834 |  | 98b9c7e070d546e668a9b3b30af1d28940a8136a9711087ba3929d0901f45774 |
| logs/runs/str_dt0.8_s0_bubble.log | 6834 |  | 76be82f2d95da741df470beba048a4e1bfcc4e9abbe77532706764b629caf1e5 |
| logs/runs/str_dt0.8_s0_rest.log | 3708 |  | 25855f8cad38691abc42aed8af1cdc6ac76b831284cd94590a0bac8b41d7bfd1 |
| logs/runs/str_dt0.8_s9_bubble.log | 277 |  | 589ae1089883f2c027806473e73b6bdeabea45d96b3f5e892adee67b439295cd |
| logs/runs/str_dt0.8_s9_bubble_f32.log | 166531 |  | 6a560c4161e7c8dfb9425a7542721161cd798ddb8abcbf24f15926c96b090206 |
| logs/runs/str_dt0.8_s9_rest.log | 275 |  | 614d08caf15199d910ca9fe8cc68d40d9d1cdb56faaf92eca7f4201197f4faf3 |
| logs/runs/str_dt0.8_s9_rest_f32.log | 166529 |  | 5df3e2749a6baa23d0303a6a60ae8e33842032426722906a8d1702999be40c6e |
| logs/runs/str_dt1.6_s0_bubble.log | 5578 |  | de02259d33227328935936d984c28403412c28910d0f3767a01bdf228943d7dd |
| logs/runs/str_dt1.6_s0_rest.log | 6179 |  | e1a9c7c613a2b91923ed6d6af9cb7333e3a470f7eeb49c715710974e21a00663 |
| logs/runs/str_dt1.6_s9_bubble.log | 275 |  | 2f4c608ed8e53114735dffc3b107a5408e007efe5a965fe0342c4f908c4db372 |
| logs/runs/str_dt1.6_s9_bubble_f32.log | 83404 |  | 26541b9ad624a6aba66ecec7dbe15fe627c6eebd2b3374058360400ec57b93b1 |
| logs/runs/str_dt1.6_s9_rest.log | 273 |  | e98c43789a1ad0fad665263ac7447a5de7308ba26f4835fcaa3f1116fc4fd4b5 |
| logs/runs/str_dt1.6_s9_rest_f32.log | 83402 |  | 8690783587f02dfe807c06d963f1406b747532a9e97ddf0cc9d7ca7863c817fe |
| logs/runs/uni_dt0.8_s0_bubble.log | 13160 |  | b3ef613cd7aafd17cc0bc41d9be4a42a7ae49344a4aec2faae5995b870055ee2 |
| logs/runs/uni_dt0.8_s0_rest.log | 142256 |  | 6bc2fbfdccff259434081f92e2694a99200792cf2c23e5bfdd56ecaf3b779b9f |
| logs/runs/uni_dt0.8_s9_bubble.log | 277 |  | 840b5cb6967cfee6841d507e1cf17706ff9294f4ab9fd5280440fe2ea8a92a85 |
| logs/runs/uni_dt0.8_s9_bubble_f32.log | 166531 |  | 93aa6b9986059a6fae9bae9b9e3e175f8ff01c6a55f3ca5d045fc3b94510518f |
| logs/runs/uni_dt0.8_s9_rest.log | 275 |  | fb27781865ecc77b65acbb6ccd1601ba47eb376ad8d2ffd99feade217196482d |
| logs/runs/uni_dt0.8_s9_rest_f32.log | 166529 |  | 2a3314313dc592d9e536597add5fe825041e040d9cfaaf730336db2a578ef304 |
| logs/runs/uni_dt1.6_s0_bubble.log | 9988 |  | facb10f71e88eb7bcd726bfd7d6aee0a131f6e4fd0efcf80667b7466a0d93463 |
| logs/runs/uni_dt1.6_s0_rest.log | 608 |  | 9e0e2d64bb0d06e7b39398ad815e757af7c3b6fb2127a5f259064bcbea779211 |
| logs/runs/uni_dt1.6_s9_bubble.log | 275 |  | a81a2d16e08b1692ee91ca13e72c6ae5a3a3e03c8ac0648cbe7cf9c7708ad33f |
| logs/runs/uni_dt1.6_s9_bubble_f32.log | 83404 |  | 70c07834462a165a8ff1029370d2d0688c251dacb89aa0f1b7bf970455826008 |
| logs/runs/uni_dt1.6_s9_rest.log | 273 |  | ee506ba8d475c14b6b38ad9e013a159a7e8e58c6cff16da5d9429bd9d96b8d06 |
| logs/runs/uni_dt1.6_s9_rest_f32.log | 83402 |  | 11070c18d794e2974e3c51a6f64a51eaa32ad19e4ce46f17ec6dcab498f4737d |
| raw_npz/rk2_control/str_dt0.8_s9_bubble_rk2_float32.npz | 96536 |  | 6a2b21030370d3df6954119ee01a65023fe997b9b50338b1995ef538377b10d2 |
| raw_npz/rk2_control/str_dt0.8_s9_bubble_rk2_float64.npz | 96536 |  | 2dca17db6d32fb34e405358436c0db15a36294c514ff47e657f072be40e6faa7 |
| raw_npz/rk2_control/str_dt0.8_s9_rest_rk2_float32.npz | 96520 |  | 34899f86cc9e57ff68fbff7ac9461f85f0256c61d5a1bcf37704fb4b04b47a19 |
| raw_npz/rk2_control/str_dt0.8_s9_rest_rk2_float64.npz | 96520 |  | 50160a18fd17db2e181fa01c475cc8672652064ff0c8cd7e73a8ccd9e8d367d9 |
| raw_npz/rk2_control/uni_dt0.8_s9_bubble_rk2_float32.npz | 96536 |  | 946b7677336933c1c789b09616233c9ac75130ae4c349baa2ef02c3b68ab8d9f |
| raw_npz/rk2_control/uni_dt0.8_s9_bubble_rk2_float64.npz | 96536 |  | 861a4426454c4630179354744396c30d23744d65a491d414b39685b5d7c428ce |
| raw_npz/rk2_control/uni_dt0.8_s9_rest_rk2_float32.npz | 96520 |  | 96335fc7be2919f955a5bcc2d00e4fcc55b2dc6b4167c4f2c0490c89feaebea5 |
| raw_npz/rk2_control/uni_dt0.8_s9_rest_rk2_float64.npz | 96520 |  | 0498db923c4a60dfdcd47238dd73fb5b3910d7b94c9e68c9bdf601943e5bb615 |
| raw_npz/scheme0/str_dt0.8_s0_bubble.npz | 6824 |  | 2b10a474fdf1178f83a11a1bb221f60143da91a41f79beaeae4a82d3f8925fca |
| raw_npz/scheme0/str_dt0.8_s0_rest.npz | 6892 |  | e788148905ef66db7c521e34766ee814acbeab65c47c6e132e3f4a0244f7fa52 |
| raw_npz/scheme0/str_dt1.6_s0_bubble.npz | 6752 |  | cabf8558da572e52181ce10e122c03c8b1b18b822ab19ebb90bc7ad8167bbbfc |
| raw_npz/scheme0/str_dt1.6_s0_rest.npz | 6820 |  | a7553e84c1957defe0fd65ad274b942de87a1e83208e0c84241568e6831ef93a |
| raw_npz/scheme0/uni_dt0.8_s0_bubble.npz | 6824 |  | 9cedce333d68a9b8c7ad91afe63ab5802a729bb8f1c8bf8f3f5e07a33708578d |
| raw_npz/scheme0/uni_dt0.8_s0_rest.npz | 6892 |  | 25fbc10f02d7fc649a12e1155b161644e9d4cb445b0593c8cd8b5aad9d36a0b7 |
| raw_npz/scheme0/uni_dt1.6_s0_bubble.npz | 6752 |  | 525b5dc63b84e6ae4b8667ddc42dda1e7d6e57ae03e1eb7f60be085b473424d8 |
| raw_npz/scheme0/uni_dt1.6_s0_rest.npz | 6748 |  | f5885252a83ce8b8765f3345b733e83e1222f9a5d8881afba1b19528a1cfee17 |
| raw_npz/scheme9/str_dt0.8_s9_bubble.npz | 96520 |  | db603a06cf3f06f6e26996130f7e2319220a0ef41dd82eacfec08fdd91639376 |
| raw_npz/scheme9/str_dt0.8_s9_bubble_f32.npz | 96520 |  | 00890b54ac8f581cbf79d0bcf0e1cc3ae908cc22352aa75850ef70fbe189717c |
| raw_npz/scheme9/str_dt0.8_s9_rest.npz | 96444 |  | 3d2f0e6c543beaa5c46d2376128e72e672ead175518e8eab77db126c34d63393 |
| raw_npz/scheme9/str_dt0.8_s9_rest_f32.npz | 96444 |  | 95bab3c8a4ce8281287c0571b60be61758c28fdd11f2167b3779700269b7245b |
| raw_npz/scheme9/str_dt1.6_s9_bubble.npz | 51520 |  | 6367e5acde4e836978186dacd5cc5c0dbc6f0c0a3154767df061fdfc218d124c |
| raw_npz/scheme9/str_dt1.6_s9_bubble_f32.npz | 51520 |  | 1cdebd985b6c69d416615709d2c8ce9b5c798a8f6b4d16f829f76403a4f84ad0 |
| raw_npz/scheme9/str_dt1.6_s9_rest.npz | 51444 |  | 1b6ca3b5563d0dd223f44d4ccc5851d731eaad3c87d30d4940efe958080bfb5a |
| raw_npz/scheme9/str_dt1.6_s9_rest_f32.npz | 51444 |  | 56b1fb299a031ae0930b5480fdc96060a65e1852569cf3a93d826b3e27dedfd4 |
| raw_npz/scheme9/uni_dt0.8_s9_bubble.npz | 96520 |  | a91c84361cc97c6c074867cb31f879d8a8dde5f7a7113d1d43692ee7ae5b7c10 |
| raw_npz/scheme9/uni_dt0.8_s9_bubble_f32.npz | 96520 |  | 47c7214c529ad246c2fe8d6d35158598d6091e712028b43a59052c99c96fbb2b |
| raw_npz/scheme9/uni_dt0.8_s9_rest.npz | 96444 |  | e0c6c09bdf97d3c58c9afef1e8ebd97d99edde89981ef7c24201faabb3613471 |
| raw_npz/scheme9/uni_dt0.8_s9_rest_f32.npz | 96444 |  | b18a81506e9395c27d8432070d4eff6ad70e0c42c8c5e835d990685c5a704044 |
| raw_npz/scheme9/uni_dt1.6_s9_bubble.npz | 51520 |  | 5a77a7dcbeb9ef985623e695252a17402e9853862ae4e054da39d1cc4fabea26 |
| raw_npz/scheme9/uni_dt1.6_s9_bubble_f32.npz | 51520 |  | 0f0baefa7c14078a3a755b741d46a3a9c959daa270330341c3d10f358b5a1656 |
| raw_npz/scheme9/uni_dt1.6_s9_rest.npz | 51444 |  | 6795d08e1199ed2f0428990d40e93981e3b01b89a2367dea067a06cec2e90293 |
| raw_npz/scheme9/uni_dt1.6_s9_rest_f32.npz | 51444 |  | 6ff2b1cafcf8e558970d497168bd07b077fc9317db7562cc223945bb5ad71ccc |
| raw_npz/superseded_twin_bisect_ic/str_dt0.8_s0_rest.npz | 6952 |  | 5ff767221e510034d6ec07d847f145367876f543da35b63f041c5a51bb7b47db |
| raw_npz/superseded_twin_bisect_ic/str_dt0.8_s9_rest.npz | 96504 |  | 18196fd978733aac62ff1200c5e6a434b9781982da64b6c10b78fad084a656ea |
| raw_npz/superseded_twin_bisect_ic/str_dt0.8_s9_rest_f32.npz | 96504 |  | 3dfd6c2dcb0ee594cf02c33b66141844c843f9b5157777cf2166be3643bc2320 |
| raw_npz/superseded_twin_bisect_ic/str_dt1.6_s0_rest.npz | 6880 |  | d30c2ae283d4e4079fcc9cabc2b8a125a0fbfec93da255fb3eaf2b208c7aba22 |
| raw_npz/superseded_twin_bisect_ic/str_dt1.6_s9_rest.npz | 51504 |  | b8313f9a621a60c53a61ffb9a8e231640afd2a98120fc6c9bc8cb0a8b7f6a2c5 |
| raw_npz/superseded_twin_bisect_ic/str_dt1.6_s9_rest_f32.npz | 51504 |  | 3e11ab4a2124ffc59712f04af04cca1fb93b5433990e94461e24fa8112afeee2 |
| raw_npz/superseded_twin_bisect_ic/uni_dt0.8_s0_rest.npz | 6952 |  | 38888962a991602418bdd9cd73e93a3ef90df8cb0066ed03e642050e613af788 |
| raw_npz/superseded_twin_bisect_ic/uni_dt0.8_s9_rest.npz | 96504 |  | 5d0d96a52fa801187eb7ed11ebe7b684101113c58d9d13bdfe6766f50f41e26e |
| raw_npz/superseded_twin_bisect_ic/uni_dt0.8_s9_rest_f32.npz | 96504 |  | 59cbf00caf96001e833857038b09a4bb8f40f16754f58c733c5cc9fd5aeddeff |
| raw_npz/superseded_twin_bisect_ic/uni_dt1.6_s0_rest.npz | 6808 |  | 1e2d824d23f4b97fc8307d3ad717adaa6a6bb2deb4006dfb47480c5081e951ac |
| raw_npz/superseded_twin_bisect_ic/uni_dt1.6_s9_rest.npz | 51504 |  | cb3fd4fe444f810fea9a93190a6e19d0bc67b352850fb2770d33e75bdb8ee33b |
| raw_npz/superseded_twin_bisect_ic/uni_dt1.6_s9_rest_f32.npz | 51504 |  | f78d62977438fd31d41573e2365fe11a2e8dbad5af243f1920cde53ad44b4de9 |
| raw_npz/wb_ref4/str_dt0.8_s9_bubble.npz | 96520 |  | d73afde99af6db59a7eaecb080a01f454a23254153420ce2c8b794bad42ad2e9 |
| raw_npz/wb_ref4/str_dt0.8_s9_rest.npz | 96444 |  | e7027cdf2b1ec69f69f2aa5827073b9191bc59895aba8b302b0c5663bcdd306c |
| raw_npz/wb_ref4/uni_dt0.8_s9_bubble.npz | 96520 |  | 330612acf41f42839658b4bde8d38a2b50038b6eeddb4360b71c9936abba977c |
| raw_npz/wb_ref4/uni_dt0.8_s9_rest.npz | 96444 |  | 06bd04c77578a342beeed8f33ba3b91ce1807aefbad22198a1d92c35845ebcfc |
| reports/analyze_table.md | 13840 |  | 88e210c29b92e1c250ffdd5a516ac085f70069f347aeff7ec9afed3f978b8b7b |
| reports/conservation_report.md | 52187 |  | 1d768403a4bf4faeeda62af5a66064dc6a2d07b0eee9b48b4f317d7af50cae93 |
| reports/fp32_fp64_csv_README.md | 4085 |  | eaf0cade403c165652580a2c876da34002682d80dfc88f268511c2d724da17b7 |
| scripts/README_order.txt | 735 |  | 203fde08c2e88f4b68d5eaae468c07aed62d10c080284dea324eaed3cd5a8b30 |
| scripts/analyze.py | 5337 |  | 525230fa2ef7f5d9aa14a7415b7d47e0056a729763329b61dd54cff59f8f0cc1 |
| scripts/build_kintera.sh | 446 |  | 6b29c0398248e91bcc7effa888293e434dbea6a5b12572960f661e8254e4ec7a |
| scripts/build_snapy.sh | 632 |  | ae4b30bdd4d0b0d6798e5e9f236d6682e14d64c399aabaddc27a8069c27de025 |
| scripts/check_fp32.py | 1077 |  | 8272786e6c2bd5987bf6a2585ba2738c5c8a378969a2a90d5d9f8dfbf3f3e9e2 |
| scripts/check_pe.py | 1063 |  | ff13abb94be7eaabf51f331e8894523ab3e93aa47282fe12c10148d47e41bd0f |
| scripts/export_csv.py | 4688 |  | fe927f4365737391cdb07c817e1e8804058510135ff89fe1a7af547a8f338d32 |
| scripts/export_extra_csv.py | 7452 |  | 8be17fda35c9612d21857fbc2f536d2c3b98a26975de746680eaab5118055478 |
| scripts/make_decks.py | 2621 |  | 93e9e2d679f01a4f1d29c24ed2c4b80068ed17ec446bdee7f605f8aad3d296c1 |
| scripts/make_record_readme.py | 10369 |  | 97e487c6a1e4ad8c6156ac0cb45aaac11fd24c4ce3f8da4eff48460d2d75bd0c |
| scripts/make_twin_uniform.py | 772 |  | d9f014b1a04ded4442921ea800c346719ef35bd684ff41fcfe2609f572ae18f4 |
| scripts/run_all.sh | 1283 |  | 99fe09e3ce4dedda3e7431bfbcb7d9a27a9aa7cea91a2cb16815c7b613f0b130 |
| scripts/run_arm.py | 7041 |  | cc697a036864e1b426fac93dd3c4f6425779176edea80a7b603dfe4c4855dde4 |
| scripts/run_checks.sh | 1387 |  | cf9b25bd205e3fb06d4706cb0aa6c5f99a45cc1004a15475edf9ee54a97e9551 |
| scripts/run_twins.sh | 719 |  | 07706749f76e23f797d788732c396fe538084253d356e40f7bb1738bca441208 |
| scripts/setup_env.sh | 420 |  | 671cedfb7f56d10cf4d38a5d4ec0a5b26525d5bbea6877b3fd0845e35d6b72c5 |
