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
