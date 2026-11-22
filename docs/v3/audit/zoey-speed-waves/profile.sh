#!/bin/bash
# py-spy --native sampling of Straka CPU 1 rank (bench.py unchanged), OMP/torch threads = 1 so the sampled main thread does all work
S=/mnt/data1/ai_workspace/worker2/spd; P=$S/prof; mkdir -p $P; E=/mnt/data1/ai_workspace/worker2/ef8
for t in 730b3500 6007eaa9 deeabfee d3178f20; do
  echo "$(date -u +%T) $t load=$(cut -d' ' -f1-3 /proc/loadavg)" >> $P/state.log
  (cd /tmp && OMP_NUM_THREADS=1 DEVICE_ID=0 PYTHONPATH=$S/pkg-$t:$E/py $S/tools/bin/py-spy record --native -r 100 -f raw -o $P/straka_cpu1.$t.collapsed -- \
     python $S/bench.py --tree $S/t-$t --device cpu --out $P/straka_cpu1.$t.json --warmup 3 --steps 1500 --threads 1 \
     --deck straka_hllc --init straka --nb2 1 --precision float64 > $P/straka_cpu1.$t.log 2>&1)
  echo "$(date -u +%T) $t rc=$? $(grep -h '^rank 0' $P/straka_cpu1.$t.log | tail -1)" >> $P/state.log
done
for t in 730b3500 d3178f20 730b3500 d3178f20; do  # unprofiled 1-thread reference, 2 runs each
  (cd /tmp && OMP_NUM_THREADS=1 PYTHONPATH=$S/pkg-$t:$E/py python $S/bench.py --tree $S/t-$t --device cpu --out /tmp/ref.json --warmup 3 --steps 60 --threads 1 --deck straka_hllc --init straka --nb2 1 --precision float64 2>&1 | grep '^rank 0' | sed "s/^/unprofiled $t: /") >> $P/state.log
done
echo PROFILE_DONE >> $P/state.log
