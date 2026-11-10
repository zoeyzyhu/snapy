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
