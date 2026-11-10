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
