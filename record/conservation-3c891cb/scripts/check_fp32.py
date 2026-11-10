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
