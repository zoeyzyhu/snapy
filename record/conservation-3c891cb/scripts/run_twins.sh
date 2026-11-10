#!/bin/bash
# run_twins.sh: the rest twins of all arms from the horizontally uniform balance_column rest state
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R
L=()
for g in uni str; do for dt in 1.6 0.8; do for s in 9 0; do L+=("$g $dt $s float64 rest"); done; L+=("$g $dt 9 float32 rest_f32"); done; done
printf '%s\n' "${L[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; ty=$3; sfx=$4; tag=${g}_dt${dt}_s${s}_${sfx}
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_rest_uniform.pt \
  --dt $dt --tlim 1000 --threads 2 --dtype $ty --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
