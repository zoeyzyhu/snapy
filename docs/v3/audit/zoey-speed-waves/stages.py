"""Assign each sampled step() stack to one stage (first matching rule, in order) and convert to ms/step.
usage: stages.py  (reads prof/straka_cpu1.<tree>.collapsed; ms/step = unprofiled 1-thread medians)"""
import math, re, sys, json, collections
sys.path.insert(0, ".")
from analyze_prof import name
MS = {"730b3500": 29.56, "6007eaa9": 29.65, "deeabfee": 33.20, "d3178f20": 32.96}
RULES = [
    ("flux register (FluxRegister::*, supply_prescribed)", r"snap::FluxRegister::|snap::supply_prescribed"),
    ("positivity limiter (PositivityLimiter / flux_positivity_theta)", r"snap::PositivityLimiter::|snap::flux_positivity_theta"),
    ("scalar transport (ScalarImpl::forward, incl. its reconstruction)", r"snap::ScalarImpl::forward"),
    ("Riemann solve (HLLC, perturbation path)", r"snap::RiemannSolverImpl::|snap::HLLCSolverImpl::|snap::riemann_solve|snap::hllc_impl|snap::riemann_cpu|snap::call_hllc_cpu"),
    ("hydro reconstruction (ReconstructImpl::forward)", r"snap::ReconstructImpl::forward|snap::reconstruct_faces"),
    ("x1 hydrostatic reference (_hydro_ref_x1 / X1Reference / WellBalancedX1)", r"snap::HydroImpl::_hydro_ref_x1|snap::X1Reference::|snap::WellBalancedX1::|snap::HydroReferenceX1Operator"),
    ("EOS (cons2prim, perturbations, compute)", r"snap::EquationOfStateImpl::|snap::IdealMoistImpl::|snap::MoistEOSImpl::"),
    ("coordinate (divergence, vec raise)", r"snap::CoordinateImpl::|snap::coord_vec_raise_|snap::call_coord_vec_raise"),
    ("ghost exchange and boundaries", r"snap::MeshBlockImpl::exchange_ghost_zones|snap::MeshBlockImpl::_exchange_once|snap::LayoutImpl::|snap::BoundaryFuncOptions|apply_boundaries|snap::reflect"),
    ("rest of HydroImpl::forward", r"snap::HydroImpl::forward"),
    ("rest of MeshBlock step (advance_local, integrator, executor)", r"snap::"),
    ("outside snap (python/pybind/torch dispatch only)", r"."),
]
out = {}
for t, ms in MS.items():
    cnt = collections.Counter(); total = 0
    for line in open(f"prof/straka_cpu1.{t}.collapsed"):
        line = line.rstrip("\n")
        if not line: continue
        stack, c = line.rsplit(" ", 1); c = int(c)
        frames = stack.split(";")
        idx = next((i for i, fr in enumerate(frames) if fr.startswith("main.<locals>.step (")), None)
        if idx is None: continue
        joined = ";".join(name(f) for f in frames[idx + 1:])
        total += c
        for label, rx in RULES:
            if re.search(rx, joined):
                cnt[label] += c; break
    out[t] = {"samples": total, "ms_per_step": ms,
              "stages": {l: {"pct": 100 * cnt[l] / total, "ms": ms * cnt[l] / total,
                             "ms_sd": ms * math.sqrt(cnt[l] / total * (1 - cnt[l] / total) / total)} for l, _ in RULES}}
json.dump(out, open("prof/stages.json", "w"), indent=1)
T = list(MS)
print("| stage | " + " | ".join(f"`{t}`" for t in T) + " | d3178f20 − 730b3500 | wave 2 (deeabfee − 6007eaa9) |")
print("|---|" + "---|" * (len(T) + 2))
for l, _ in RULES:
    v = [out[t]["stages"][l] for t in T]
    d = v[3]["ms"] - v[0]["ms"]; dsd = math.hypot(v[3]["ms_sd"], v[0]["ms_sd"])
    w = v[2]["ms"] - v[1]["ms"]; wsd = math.hypot(v[2]["ms_sd"], v[1]["ms_sd"])
    print(f"| {l} | " + " | ".join(f"{x['ms']:.2f} ({x['pct']:.1f}%)" for x in v) + f" | {d:+.2f} ± {dsd:.2f} | {w:+.2f} ± {wsd:.2f} |")
print("| total (unprofiled 1-thread ms/step) | " + " | ".join(f"{MS[t]:.2f}" for t in T) + f" | {MS['d3178f20']-MS['730b3500']:+.2f} | {MS['deeabfee']-MS['6007eaa9']:+.2f} |")
print("| samples in step() | " + " | ".join(str(out[t]['samples']) for t in T) + " | | |")
