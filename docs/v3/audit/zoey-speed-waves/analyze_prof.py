"""Summarize py-spy --native raw (collapsed) stacks of bench.py's step loop.
usage: analyze_prof.py <collapsed> <ms_per_step_unprofiled> [topn]
Frames are kept from bench.py's step() inward; a frame name is the function
without its argument list and template arguments. Self = leaf samples,
inclusive = samples whose stack contains the function (counted once per sample).
"""
import re, sys, json, collections

def name(frame):
    f = frame.rsplit(" (", 1)[0]
    f = re.sub(r"\(anonymous namespace\)", "anon", f)
    # strip template args and argument lists repeatedly
    prev = None
    while prev != f:
        prev = f
        f = re.sub(r"<[^<>]*>", "", f)
        f = re.sub(r"\([^()]*\)", "", f)
    f = re.sub(r"\{lambda#\d+\}", "{lambda}", f)
    f = f.replace("::::", "::").strip()
    if f.startswith("0x"):
        lib = re.search(r"\(([^)]*)\)\s*$", frame)
        f = "[" + (lib.group(1) if lib else "?") + "]"
    return f[:140]

def load(path):
    total = 0; selfc = collections.Counter(); incl = collections.Counter(); outside = 0; deep = collections.Counter()
    for line in open(path):
        line = line.rstrip("\n")
        if not line: continue
        stack, cnt = line.rsplit(" ", 1); cnt = int(cnt)
        frames = stack.split(";")
        idx = next((i for i, fr in enumerate(frames) if fr.startswith("main.<locals>.step (")), None)
        if idx is None:
            outside += cnt; continue
        fr = [name(f) for f in frames[idx + 1:]] or ["step (python)"]
        total += cnt
        selfc[fr[-1]] += cnt
        for f in set(fr):
            incl[f] += cnt
        snapf = [f for f in fr if f.startswith("snap::")]
        deep[snapf[-1] if snapf else "(no snap frame)"] += cnt
    return total, outside, selfc, incl, deep

if __name__ == "__main__":
    path, ms = sys.argv[1], float(sys.argv[2]); topn = int(sys.argv[3]) if len(sys.argv) > 3 else 25
    total, outside, selfc, incl, deep = load(path)
    print(f"# {path}: {total} samples in step(), {outside} outside; {ms:.2f} ms/step (unprofiled, 1 thread)")
    print("## self (leaf)")
    for f, c in selfc.most_common(topn):
        print(f"{100*c/total:6.2f}%  {ms*c/total:7.3f} ms  {f}")
    print("## self by deepest snap:: frame (all time below it, torch included, charged to it)")
    for f, c in deep.most_common(topn):
        print(f"{100*c/total:6.2f}%  {ms*c/total:7.3f} ms  {f}")
    print("## inclusive, snap:: frames")
    for f, c in [(f, c) for f, c in incl.most_common() if f.startswith("snap::")][:topn]:
        print(f"{100*c/total:6.2f}%  {ms*c/total:7.3f} ms  {f}")
