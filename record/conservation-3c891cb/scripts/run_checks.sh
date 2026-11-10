#!/bin/bash
# run_checks.sh: the two supplementary checks of the report
#  1) integrator attribution: the scheme-9 dt/2 arms with integration/type rk2 (weights 1/2, 1/2 exact)
#     (twins here are the bryan.release dT=0 restart, i.e. before the uniform-twin fix; used for (b)-(c) only)
#  2) SNAP_WB_REF4=1 (fourth-order WB density reference) on the scheme-9 dt/2 arms, uniform twins
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R; mkdir -p runs_rk2 runs_wb4
for g in str uni; do sed 's/type: rk3/type: rk2/' decks/run_${g}_s9.yaml > decks/run_${g}_s9_rk2.yaml; done
for g in str uni; do for d in float64 float32; do
  python scripts/run_arm.py --deck decks/run_${g}_s9_rk2.yaml --ic ic/${g}_rest/ic_${g}_rest.00000.restart --dt 0.8 --dtype $d --out runs_rk2/${g}_dt0.8_s9_rest_rk2_$d.npz
  python scripts/run_arm.py --deck decks/run_${g}_s9_rk2.yaml --ic ic/${g}_bubble/ic_${g}_bubble.00000.restart --dt 0.8 --dtype $d --out runs_rk2/${g}_dt0.8_s9_bubble_rk2_$d.npz
done; done
for g in str uni; do
  SNAP_WB_REF4=1 python scripts/run_arm.py --deck decks/run_${g}_s9.yaml --ic ic/${g}_bubble/ic_${g}_bubble.00000.restart --dt 0.8 --out runs_wb4/${g}_dt0.8_s9_bubble.npz
  SNAP_WB_REF4=1 python scripts/run_arm.py --deck decks/run_${g}_s9.yaml --ic ic/${g}_rest_uniform.pt --dt 0.8 --out runs_wb4/${g}_dt0.8_s9_rest.npz
done
