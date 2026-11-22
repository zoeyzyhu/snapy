#!/bin/bash
# wave-boundary timings: Sihe's bench.py (80619cbc) unchanged; 3 reps, the four trees interleaved per rep
S=/mnt/data1/ai_workspace/worker2/spd; R=$S/runs; mkdir -p $R; E=/mnt/data1/ai_workspace/worker2/ef8
TREES="730b3500 6007eaa9 deeabfee d3178f20"
state() { echo "load=$(cut -d' ' -f1-3 /proc/loadavg) gpu=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader | tr -d ' ') apps=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"; }
run() {  # run CELL TREE REP DEV WARM STEPS args...
  cell=$1; t=$2; rep=$3; dev=$4; wm=$5; st=$6; shift 6
  out=$R/$cell.$t.r$rep
  echo "$(date -u +%T) $cell $t r$rep before: $(state)" >> $R/state.log
  (cd /tmp && OMP_NUM_THREADS=8 DEVICE_ID=0 PYTHONPATH=$S/pkg-$t:$E/py python $S/bench.py --tree $S/t-$t --device $dev \
     --out $out.rank0.json --warmup $wm --steps $st --threads 8 "$@" > $out.rank0.log 2>&1)
  echo "$(date -u +%T) $cell $t r$rep rc=$? after: $(state) | $(grep -h '^rank 0' $out.rank0.log | tail -1)" >> $R/state.log
}
STR="--deck straka_hllc --init straka --nb2 1"
echo "START $(date -u +%FT%TZ) $(state)" >> $R/state.log
for rep in 1 2 3; do for t in $TREES; do run c1_cpu_fp64 $t $rep cpu 3 30 $STR --precision float64; done; done
for rep in 1 2 3; do for t in $TREES; do run c1_cuda_fp64_eager $t $rep cuda 5 100 $STR --precision float64; done; done
for rep in 1 2 3; do for t in $TREES; do run c2_cpu_1rank $t $rep cpu 3 30 --deck $S/cart3d_pert_64.yaml; done; done
echo "DONE $(date -u +%FT%TZ) $(state)" >> $R/state.log
