#!/bin/bash
# run_all.sh: 8 arms {uni,str} x {dt=1.6, dt/2=0.8} x {scheme 0, 9}, each a bubble run and a rest twin
R=/mnt/data1/ai_workspace/worker1/cons3c8
source /mnt/data1/ai_workspace/worker1/rr326/vb/bin/activate
cd $R
jobs_list=()
for g in uni str; do for dt in 1.6 0.8; do for s in 9 0; do for k in bubble rest; do
  jobs_list+=("$g $dt $s $k")
done; done; done; done
printf '%s\n' "${jobs_list[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; k=$3; tag=${g}_dt${dt}_s${s}_${k}
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_${k}/ic_${g}_${k}.00000.restart \
  --dt $dt --tlim 1000 --threads 2 --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
# float32 arms (scheme 9 only; scheme 0 cannot run at these Courant numbers)
fl=()
for g in uni str; do for dt in 1.6 0.8; do for k in bubble rest; do fl+=("$g $dt 9 $k"); done; done; done
printf '%s\n' "${fl[@]}" | xargs -P ${PAR:-6} -L1 bash -c '
g=$0; dt=$1; s=$2; k=$3; tag=${g}_dt${dt}_s${s}_${k}_f32
python scripts/run_arm.py --deck decks/run_${g}_s${s}.yaml --ic ic/${g}_${k}/ic_${g}_${k}.00000.restart \
  --dt $dt --tlim 1000 --threads 2 --dtype float32 --out runs/$tag.npz > runs/$tag.log 2>&1
echo "$tag exit=$? $(grep status= runs/$tag.log)"'
