#!/bin/bash
# build_snapy.sh <h|b> : CI-equivalent CPU Release build of tree head|base into venv v<h|b>
set -e
R=/mnt/data1/ai_workspace/worker1/rr326; N=$1; T=$([ $N = h ] && echo head || echo base)
source $R/v$N/bin/activate
cd $R/$T
PP=$(python -c 'import sysconfig; print(sysconfig.get_path("purelib"))')
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCUDA=OFF -DNETCDF=ON -DBUILD_TESTS=ON -DFULL_TESTS=OFF -DSNAPY_TEST_PYTHONPATH="$PP" > $R/${T}_cmake.log 2>&1
cmake --build build --config Release --parallel ${JOBS:-8} > $R/${T}_build.log 2>&1
pip install --no-build-isolation --no-deps . > $R/${T}_pip.log 2>&1
echo BUILD_OK $T
