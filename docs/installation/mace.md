# Install MACE (standalone)

This guide installs the [MACE](https://github.com/ACEsuit/mace) machine-learning interatomic potential framework
on a machine with AMD GPUs (ROCm), such as **Frontier at ORNL**.

## Prerequisites

- Access to an AMD GPU node
- The following modules available: `python/3.10.8`, `PrgEnv-gnu`, `gcc/12.2.1-magic`,
  `craype-accel-amd-gfx942`, `cray-mpich/9.0.1`, `cmake/3.24.2`, `rocm/6.2.4hangfix`

## Steps

### 1. Load modules

```bash
module purge
module load python/3.10.8
module load PrgEnv-gnu gcc/12.2.1-magic craype-accel-amd-gfx942 cray-mpich/9.0.1 cmake/3.24.2 rocm/6.2.4hangfix
export CC=mpicc
export CXX=hipcc
```

### 2. Create and activate a virtual environment

```bash
python -m venv venvs/mace_env
source venvs/mace_env/bin/activate
pip install --upgrade pip setuptools wheel
```

### 3. Install PyTorch with ROCm support

```bash
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/rocm6.2.4
```

### 4. Install MACE

```bash
pip install cython pybind11
git clone https://github.com/ACEsuit/mace.git
pip install ./mace
```

## Verification

```python
import mace
import torch
print("MACE version:", mace.__version__)
print("CUDA/ROCm available:", torch.cuda.is_available())
```
