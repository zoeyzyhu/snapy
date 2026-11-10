#!/bin/bash
set -e
R=/mnt/data1/ai_workspace/worker1/rr326
source $R/vh/bin/activate
cd $R/kintera
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DNETCDF=ON -DBUILD_TESTS=OFF > $R/kin_cmake.log 2>&1
cmake --build build --parallel 10 > $R/kin_build.log 2>&1
pip install --no-build-isolation --no-deps . > $R/kin_pip_h.log 2>&1
deactivate; source $R/vb/bin/activate
pip install --no-build-isolation --no-deps . > $R/kin_pip_b.log 2>&1
echo KIN_OK
