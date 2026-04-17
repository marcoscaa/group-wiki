# Install PLUMED for Python/ASE

This guide compiles PLUMED with Python bindings so it can be used with ASE-based MD simulations.
Target machine: **Tuolumne at LLNL**.

## Prerequisites

- An active Python virtual environment (see [MACE install guide](mace.md))
- The following modules available: `python/3.10.8`, `PrgEnv-gnu`, `gcc/12.2.1-magic`,
  `craype-accel-amd-gfx942`, `cray-mpich/9.0.1`, `cmake/3.24.2`, `rocm/6.2.4hangfix`

## 1. Clone and configure PLUMED

```bash
git clone https://github.com/plumed/plumed2.git
cd plumed2

module purge
module load python/3.10.8
module load PrgEnv-gnu gcc/12.2.1-magic craype-accel-amd-gfx942
module load cray-mpich/9.0.1 cmake/3.24.2 rocm/6.2.4hangfix

export CC=mpicc
export CXX=hipcc

source /path/to/your/venv/bin/activate  # activate your Python environment

./configure CC=mpicc CXX=mpicxx \
    --prefix=`realpath .` \
    --enable-python \
    --enable-modules=+adjmat:+crystalization
```

!!! note "Python environment"
    You must activate your virtual environment **before** running `./configure` so PLUMED links against the correct Python installation. If you don't have one yet, create it first:
    ```bash
    python -m venv /path/to/your/venv
    source /path/to/your/venv/bin/activate
    ```

## 2. Build and install

```bash
make -j 8
make install
```

## 3. Source the PLUMED environment

From the same directory where you compiled PLUMED, run:

```bash
source sourceme.sh
```

!!! warning "Submission scripts"
    You must source `sourceme.sh` in every job submission script that uses PLUMED, so the
    environment variables are set at runtime.

## 4. Install the PLUMED Python backend

```bash
pip install plumed
```

## 5. Run an MD simulation with MACE + ASE + PLUMED

Use the [`run_md_mace_ase_plumed.py`](../assets/scripts/run_md_mace_ase_plumed.py) script with the following arguments:

```bash
python run_md_mace_ase_plumed.py \
    --nsteps 10000000 \
    --max_seconds 86000 \
    --nsave 100 \
    --timestep 1.0 \
    --temperature_K 400 \
    --model "$model" \
    --output md.extxyz \
    --default_dtype "float32" \
    --config input.extxyz
```

Replace `$model` with the path to your MACE model file.

| Argument | Description |
|---|---|
| `--nsteps` | Total number of MD steps |
| `--max_seconds` | Wall-time limit in seconds |
| `--nsave` | Save trajectory every N steps |
| `--timestep` | Time step in fs |
| `--temperature_K` | Target temperature in Kelvin |
| `--model` | Path to the MACE model |
| `--output` | Output trajectory file |
| `--default_dtype` | Floating-point precision (`float32` or `float64`) |
| `--config` | Input structure file (extxyz format) |
