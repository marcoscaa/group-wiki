# Installation Overview

This section covers how to install and compile the codes used in the group on HPC clusters.

## Available Guides

| Guide | Target machine | Notes |
|---|---|---|
| [MACE](mace.md) | Tuolumne/LLNL (AMD GPU) | Standalone Python install |
| [MACE + LAMMPS](mace_lammps.md) | Tuolumne/LLNL (AMD GPU) | Full ML-MD stack with Kokkos/HIP |
| [PLUMED for ASE](plumed_ase.md) | Tuolumne/LLNL (AMD GPU) | PLUMED with Python bindings for ASE-based MD |

## General Tips

!!! note "Virtual environments"
    Always install Python packages inside a virtual environment (`python -m venv`).
    This keeps your installs isolated and reproducible across group members.

!!! warning "Module conflicts"
    Run `module purge` before loading any modules to avoid conflicts from
    previously loaded environments.
