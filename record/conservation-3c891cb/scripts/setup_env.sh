#!/bin/bash
# setup_env.sh <name>: venv v<name> following CI deps
set -e
R=/mnt/data1/ai_workspace/worker1/rr326; N=$1
export PIP_CACHE_DIR=/mnt/data1/ai_workspace/worker1/j326/pipcache
python3 -m venv $R/v$N; source $R/v$N/bin/activate
pip install -q -U pip
pip install -q wheel numpy pyyaml pytest netcdf4 'torch==2.10.0' setuptools-scm 'pyharp>=2.2.0' 'commux>=0.1.4' 'pinc>=0.2.0' 'cmake<=3.30' ninja
echo ENV_OK $N
