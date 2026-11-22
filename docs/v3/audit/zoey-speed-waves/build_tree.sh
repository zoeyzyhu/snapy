# usage: build_tree.sh <sha8> : same command for all four trees (CUDA, Release, NETCDF/PNETCDF/UCX off, no tests)
set -e
C=$1; S=/mnt/data1/ai_workspace/worker2/spd; T=$S/t-$C; P=$S/pkg-$C; E=/mnt/data1/ai_workspace/worker2/ef8
export PATH=/usr/local/cuda-12.9/bin:$PATH CUDA_HOME=/usr/local/cuda-12.9
export PYTHONPATH=$E/py
cd $T; echo "tree $(git rev-parse HEAD) dirty=$(git status --porcelain | wc -l)"; t0=$(date +%s)
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=ON -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.9/bin/nvcc \
  -DNETCDF=OFF -DPNETCDF=OFF -DUCX=OFF -DBUILD_TESTS=OFF > $S/logs/cmake-$C.log 2>&1
echo "CONFIGURE_DONE $(( $(date +%s)-t0 ))s"
cmake --build build --parallel 12 > $S/logs/make-$C.log 2>&1
echo "BUILD_DONE $(( $(date +%s)-t0 ))s"
rm -rf $P
PYTHONPATH=$E/py:$E/buildtools MAX_JOBS=12 python -m pip install --no-deps --no-build-isolation --target $P . > $S/logs/pip-$C.log 2>&1
echo "INSTALL_DONE $(( $(date +%s)-t0 ))s"
