#!/bin/sh
#FLUX: --job-name=example
#FLUX: --output='flux.{{id}}.out'
#FLUX: --error='flux.{{id}}.err'
#FLUX: -N 1
#FLUX: --time-limit=24h
#FLUX: --bank=pr4ccc
#FLUX: --queue=pbatch

echo "Starting job at $(date)"

CORES_PER_TASK="${CORES_PER_TASK:-24}"

flux run -N 1 -n 1 \
  --cores-per-task="${CORES_PER_TASK}" \
  --gpus-per-task=4 \
  YOUR_CODE_HERE


echo "Finishing job at $(date)"
