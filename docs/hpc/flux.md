# Flux Job Scheduler

[Flux](https://flux-framework.org/) is the workload manager used on **Frontier** (ORNL).

## Submission script template

```bash
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
```

### Key directives

| Directive | Meaning |
|---|---|
| `-N` | Number of nodes |
| `--time-limit` | Wall-clock limit (e.g. `24h`, `30m`) |
| `--bank` | Allocation account |
| `--queue` | Partition/queue name |
| `--cores-per-task` | CPU cores assigned per MPI rank |
| `--gpus-per-task` | GPUs assigned per MPI rank |

## Common commands

```bash
# Submit a job
flux batch my_script.sh

# Check job status
flux jobs

# Cancel a job
flux cancel <jobid>

# View job output in real time
flux job attach <jobid>

# Check allocation/bank info
flux account info
```

## Running interactively

```bash
flux alloc -N 1 --time-limit=1h --bank=pr4ccc --queue=pbatch
```

This drops you into an interactive shell on the allocated node.
