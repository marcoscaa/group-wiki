# Install MACE + LAMMPS + PLUMED (with Kokkos/HIP)

This guide builds LAMMPS with the `PKG_ML-MACE`, `PKG_PLUMED`, and Kokkos/HIP packages for AMD GPU
acceleration, using the [symmetrix](https://github.com/wcwitt/symmetrix) pair style and a
[PLUMED](https://www.plumed.org/) installation built from source for enhanced-sampling/free-energy
simulations.
Target machine: **Tuolumne at LLNL** (AMD MI300A, `gfx942`).

This is an extension of the [MACE + LAMMPS](mace_lammps.md) guide. The key difference is that PLUMED
is compiled separately and linked into LAMMPS in **runtime mode**, so you can run biased MD with
MACE potentials on GPU.

!!! tip "Download the full script"
    The complete build script is available here:
    [`compile_mace_lammps_plumed.sh`](../assets/scripts/compile_mace_lammps_plumed.sh).
    Save it to your working directory and run it, or follow the steps below manually.

## Prerequisites

- Access to a GPU node on Tuolumne
- The following modules available: `StdEnv`, `python/3.10.8`, `PrgEnv-gnu`, `gcc/12.2.1-magic`,
  `craype-accel-amd-gfx942`, `cray-mpich/9.0.1`, `cmake/3.29.2`, `rocm/6.2.4hangfix`

## Full install script

You can run the steps below manually, or save them as a script and execute it from your working directory.

```bash
#!/bin/bash
set -euo pipefail

ROOT="$PWD"
```

### 1. Load modules and set compilers

```bash
module --force purge
module load StdEnv
module load python/3.10.8
module load PrgEnv-gnu
module load gcc/12.2.1-magic
module load craype-accel-amd-gfx942
module load cray-mpich/9.0.1
module load cmake/3.29.2
module load rocm/6.2.4hangfix

export CC=mpicc
export CXX=hipcc
export KOKKOS_HOST_COMPILER=mpicxx
export CRAYPE_LINK_TYPE=dynamic
```

### 2. Create virtual environment and install dependencies

```bash
mkdir -p "${ROOT}/venvs"
python -m venv "${ROOT}/venvs/mace_env"
source "${ROOT}/venvs/mace_env/bin/activate"

python -m pip install --upgrade pip setuptools wheel

pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/rocm6.2.4

pip install cython pybind11 scikit-build-core ninja
```

### 3. Install MACE

```bash
git clone https://github.com/ACEsuit/mace.git
pip install ./mace
```

### 4. Clone LAMMPS and symmetrix

```bash
mkdir -p "${ROOT}/mylammps"
cd "${ROOT}/mylammps"

git clone -b release https://github.com/lammps/lammps
git clone --recursive https://github.com/wcwitt/symmetrix
```

### 5. Find CMake paths (helper)

Run this inside your activated environment to confirm the correct paths:

```bash
python - <<'PY'
import torch, pybind11, pathlib, site
print("Torch CMake:", pathlib.Path(torch.__file__).parent / "share/cmake")
print("pybind11 CMake:", pathlib.Path(pybind11.__file__).parent / "share/cmake/pybind11")
print("Python site-packages:", site.getsitepackages())
PY
```

### 6. Install symmetrix into LAMMPS source

```bash
cd symmetrix/pair_symmetrix
./install.sh ../../lammps

cd ../symmetrix

export TORCH_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/torch/share/cmake"
export PYBIND11_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"
export CMAKE_PREFIX_PATH="${TORCH_CMAKE_DIR}:${PYBIND11_CMAKE_DIR}"

export CMAKE_GENERATOR="Unix Makefiles"
export CMAKE_ARGS="-DKokkos_ENABLE_HIP=ON \
  -DSYMMETRIX_KOKKOS=ON \
  -DKokkos_ARCH_AMD_GFX942=ON \
  -DCMAKE_HIP_ARCHITECTURES=gfx942 \
  -DCMAKE_C_COMPILER=$(which mpicc) \
  -DCMAKE_CXX_COMPILER=$(which hipcc) \
  -DCMAKE_CXX_STANDARD=20 \
  -DCMAKE_CXX_SCAN_FOR_MODULES=OFF \
  -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}"

pip install --no-build-isolation . 2>&1 | tee "${ROOT}/symmetrix_build.log"
```

### 7. Build PLUMED from source

PLUMED is built with the host MPI C++ compiler (`mpicxx`), **not** `hipcc`, since it is plain
CPU/C++ code. It is installed to its own prefix so the LAMMPS CMake build can locate it later via
`pkg-config`.

```bash
PLUMED_PREFIX="${ROOT}/plumed-install"

cd "${ROOT}"
git clone https://github.com/plumed/plumed2.git
cd plumed2

./configure \
  --prefix="${PLUMED_PREFIX}" \
  --enable-mpi \
  CC=mpicc \
  CXX=mpicxx

make -j 96 2>&1 | tee "${ROOT}/plumed_make.log"
make install 2>&1 | tee "${ROOT}/plumed_install.log"

# Make this PLUMED installation discoverable by LAMMPS' CMake (pkg-config) and at runtime.
export PKG_CONFIG_PATH="${PLUMED_PREFIX}/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export PATH="${PLUMED_PREFIX}/bin:${PATH}"
export LD_LIBRARY_PATH="${PLUMED_PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PLUMED_KERNEL="${PLUMED_PREFIX}/lib/libplumedKernel.so"
```

!!! note "Why runtime mode?"
    The LAMMPS build below uses `PLUMED_MODE=runtime`: LAMMPS only embeds the small PLUMED wrapper
    at compile time and `dlopen()`s the kernel at runtime. This avoids C++ ABI mismatches between
    `hipcc` (clang-based) and `gcc`/`mpicxx`, and only requires the PLUMED kernel to be findable at
    runtime via `LD_LIBRARY_PATH` / `PLUMED_KERNEL`.

### 8. Configure and build LAMMPS

```bash
cd "${ROOT}/mylammps/lammps"
mkdir -p build && cd build

export TORCH_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/torch/share/cmake"
export PYBIND11_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"
export CMAKE_PREFIX_PATH="${TORCH_CMAKE_DIR}:${PYBIND11_CMAKE_DIR}"

PREFIX="${PWD}/install"

cmake ../cmake \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_C_COMPILER="${CC}" \
  -D CMAKE_CXX_COMPILER="$(which hipcc)" \
  -D CMAKE_CXX_STANDARD=20 \
  -D BUILD_SHARED_LIBS=ON \
  -D BUILD_MPI=ON \
  -D PKG_KOKKOS=ON \
  -D PKG_PYTHON=ON \
  -D PKG_EXTRA-FIX=YES \
  -D FFT=KISS \
  -D Kokkos_ENABLE_OPENMP=ON \
  -D Kokkos_ENABLE_HIP=ON \
  -D SYMMETRIX_KOKKOS=ON \
  -D Kokkos_ENABLE_AGGRESSIVE_VECTORIZATION=ON \
  -D Kokkos_ARCH_AMD_GFX942=ON \
  -D CMAKE_HIP_ARCHITECTURES=gfx942 \
  -D Kokkos_HOST_COMPILER="${KOKKOS_HOST_COMPILER}" \
  -D HIP_HIPCC_EXECUTABLE="$(which hipcc)" \
  -D PKG_MISC=YES \
  -D PKG_DIPOLE=YES \
  -D PKG_REPLICA=YES \
  -D PKG_EXTRA-COMMAND=YES \
  -D PKG_EXTRA-COMPUTE=YES \
  -D PKG_EXTRA-DUMP=YES \
  -D PKG_EXTRA-MOLECULE=YES \
  -D PKG_EXTRA-PAIR=YES \
  -D PKG_DIELECTRIC=YES \
  -D PKG_RIGID=YES \
  -D MKL_INCLUDE_DIR=/tmp \
  -D PKG_ML-MACE=ON \
  -D PKG_PLUMED=yes \
  -D DOWNLOAD_PLUMED=no \
  -D PLUMED_MODE=runtime \
  -D PKG_USER-MISC=YES \
  -D CRAYPE_LINK_TYPE=dynamic \
  -D CMAKE_INSTALL_PREFIX="${PREFIX}" \
  -D CMAKE_PREFIX_PATH="${TORCH_CMAKE_DIR};${PYBIND11_CMAKE_DIR}"

make -j 96 2>&1 | tee "${ROOT}/lammps_make.log"
make install-python 2>&1 | tee "${ROOT}/lammps_install_python.log"
```

The PLUMED-specific flags here are:

| Flag | Purpose |
|---|---|
| `PKG_PLUMED=yes` | Enable the LAMMPS PLUMED package (`fix plumed`). |
| `DOWNLOAD_PLUMED=no` | Use the PLUMED we built in step 7 instead of downloading one. |
| `PLUMED_MODE=runtime` | Embed only the wrapper; load the kernel at runtime via `dlopen()`. |

!!! tip "Parallel build cores"
    Adjust `-j 96` to the number of CPU cores available on your build node.

### 9. Verify the build

After a successful build you should see:

```
Build complete
VENV: /path/to/venvs/mace_env
LAMMPS binary: .../lammps/build/lmp
LAMMPS shared lib: .../lammps/build/liblammps.so.0
```

Build logs are saved in `${ROOT}/symmetrix_build.log`, `${ROOT}/plumed_make.log`,
`${ROOT}/plumed_install.log`, `${ROOT}/lammps_make.log`, and `${ROOT}/lammps_install_python.log`
for debugging.

## Running PLUMED-biased MD

PLUMED is loaded at runtime, so make sure the kernel is on your library path before running LAMMPS
(this is also needed in your job script):

```bash
export PLUMED_PREFIX="${ROOT}/plumed-install"
export PATH="${PLUMED_PREFIX}/bin:${PATH}"
export LD_LIBRARY_PATH="${PLUMED_PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PLUMED_KERNEL="${PLUMED_PREFIX}/lib/libplumedKernel.so"
```

In your LAMMPS input, enable PLUMED with the `fix plumed` command:

```lammps
fix bias all plumed plumedfile plumed.dat outfile plumed.out
```

!!! warning "Kernel not found at runtime"
    If LAMMPS reports that it cannot load `libplumedKernel.so`, confirm that `LD_LIBRARY_PATH` and
    `PLUMED_KERNEL` point at your `plumed-install` directory. These must be set in the same
    environment (and job script) where you launch `lmp`.
