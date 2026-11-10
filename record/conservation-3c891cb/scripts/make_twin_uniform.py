#!/usr/bin/env python3
"""Horizontally uniform rest twin: take the balance_column rest state that
bryan.release wrote (problem/dT = 0, balance-ic: true; 8 saturation+balance
passes), keep its interior column at x2 index 0 (outside the old bubble disk,
where bryan.cpp's bisection is not applied), and copy it to every x2 cell.
Every column is then bitwise the balanced column 0.

  make_twin_uniform.py <restart> <out.pt>
"""
import sys
import torch
import snapy

w = snapy.load_restart(sys.argv[1], 0)["hydro_w"].clone()
ng = 3
col = w[:, :, ng:ng + 1, :].clone()
w[:] = col.expand_as(w)
torch.save({"hydro_w": w}, sys.argv[2])
wi = w[:, :, ng:-ng, ng:-ng]
print(sys.argv[2], "max horizontal spread of p:", float((wi[4].max(1).values - wi[4].min(1).values).abs().max()))
