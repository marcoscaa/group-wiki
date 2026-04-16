module purge
module load python/3.10.8
module load PrgEnv-gnu gcc/12.2.1-magic craype-accel-amd-gfx942 cray-mpich/9.0.1 cmake/3.24.2 rocm/6.2.4hangfix
export CC=mpicc
export CXX=hipcc
export KOKKOS_HOST_COMPILER=mpicxx

python -m venv venvs/allegro_env
source venvs/allegro_env/bin/activate
#pip install --upgrade pip setuptools wheel


pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/rocm6.2.4

pip install cython pybind11 
git clone https://github.com/ACEsuit/mace.git
pip install ./mace
mkdir mylammps
cd mylammps
git clone -b release https://github.com/lammps/lammps
git clone --recursive https://github.com/wcwitt/symmetrix
# Helpful: show where torch & pybind11 CMake files are
python - <<'PY'
import torch, pybind11, sys, site, pathlib
print("Torch CMake:", pathlib.Path(torch.__file__).parent/"share/cmake")
print("pybind11 CMake:", pathlib.Path(pybind11.__file__).parent/"share/cmake/pybind11")
print("Python site-packages:", site.getsitepackages())
PY
cd symmetrix/pair_symmetrix
./install.sh ../../lammps
cd ../symmetrix
pip install .
cd ../..
cd lammps

mkdir build
cd build

# Where CMake should find Torch & pybind11
TORCH_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/torch/share/cmake"
PYBIND11_CMAKE_DIR="$VIRTUAL_ENV/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"
export CMAKE_PREFIX_PATH="${TORCH_CMAKE_DIR}:${PYBIND11_CMAKE_DIR}"

# Install path (adjust as you like)
PREFIX="${PWD}/install"

export CC=mpicc
export CXX=hipcc
export KOKKOS_HOST_COMPILER=mpicxx
module load cmake/3.29.2 
cmake ../cmake \
  -D CMAKE_BUILD_TYPE=Release \
  -D CMAKE_C_COMPILER="${CC}" \
  -D CMAKE_CXX_COMPILER="$(which hipcc)" \
  -D CMAKE_CXX_STANDARD=20 \
  -D BUILD_SHARED_LIBS=ON \
  -D PKG_KOKKOS=ON \
  -D BUILD_MPI=ON \
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
  -D PKG_RIGID=YES \
  -D PKG_ML-MACE=ON \
  -D PKG_USER-MISC=YES \
  -D CRAYPE_LINK_TYPE=dynamic \
  -D CMAKE_PREFIX_PATH="$VIRTUAL_ENV/lib/python3.10/site-packages/torch/share/cmake;$VIRTUAL_ENV/lib/python3.10/site-packages/pybind11/share/cmake/pybind11"
make -j 96
make install-python
