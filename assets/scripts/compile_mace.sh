module purge
module load python/3.10.8
module load PrgEnv-gnu gcc/12.2.1-magic craype-accel-amd-gfx942 cray-mpich/9.0.1 cmake/3.24.2 rocm/6.2.4hangfix
export CC=mpicc
export CXX=hipcc
#export KOKKOS_HOST_COMPILER=mpicxx
python -m venv venvs/mace_env
source venvs/mace_env/bin/activate
pip install --upgrade pip setuptools wheel
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/rocm6.2.4
pip install cython pybind11
#git clone --branch=mace --depth=1 https://github.com/ACEsuit/lammps mylammps
git clone https://github.com/ACEsuit/mace.git
pip install ./mace

