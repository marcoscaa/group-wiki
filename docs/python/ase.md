# ASE Tutorial

[ASE](https://wiki.fysik.dtu.dk/ase/) (Atomic Simulation Environment) is a Python library for setting up, running, and analyzing atomistic simulations.

## Installation

```bash
pip install ase
```

## Building structures

```python
from ase.build import bulk, molecule, surface
from ase.io import read, write

# FCC bulk crystal
cu = bulk("Cu", "fcc", a=3.615)

# Simple molecule
h2o = molecule("H2O")

# FCC (111) surface, 4 layers, 10 Å vacuum
slab = surface("Cu", (1, 1, 1), layers=4, vacuum=10.0)

# Read from file (POSCAR, xyz, cif, lammps data, …)
atoms = read("POSCAR")
atoms = read("structure.xyz")

# Write to file
write("out.xyz", atoms)
write("POSCAR", atoms)
write("structure.lammps", atoms, specorder=["Cu", "O"])
```

## Inspecting structures

```python
print(atoms)                       # summary
print(atoms.get_positions())       # Nx3 array, Å
print(atoms.get_chemical_symbols())
print(atoms.get_cell())            # 3x3 cell matrix
print(atoms.get_volume())          # Å³
print(len(atoms))                  # number of atoms

# Access a single atom
atoms[0].symbol
atoms[0].position
atoms[0].mass
```

## Manipulating structures

```python
from ase.build import make_supercell
import numpy as np

# Supercell
supercell = make_supercell(cu, [[2, 0, 0],
                                [0, 2, 0],
                                [0, 0, 2]])

# Repeat shorthand
supercell = cu.repeat([2, 2, 2])

# Rotate
atoms.rotate(45, "z", center="COP")

# Translate
atoms.translate([1.0, 0.0, 0.0])

# Add / remove atoms
from ase import Atom
atoms.append(Atom("H", position=(0, 0, 5)))
del atoms[0]
```

## Attaching a calculator

```python
# EMT (built-in, for quick tests with metals)
from ase.calculators.emt import EMT

atoms.calc = EMT()
e = atoms.get_potential_energy()    # eV
f = atoms.get_forces()              # eV/Å
s = atoms.get_stress()              # Voigt, eV/Å³

# LAMMPS calculator
from ase.calculators.lammpsrun import LAMMPS
calc = LAMMPS(pair_style="eam/alloy",
              pair_coeff=["* * Cu.eam.alloy Cu"])
atoms.calc = calc
```

## Structure optimization

```python
from ase.optimize import BFGS, FIRE

opt = BFGS(atoms, trajectory="relax.traj")
opt.run(fmax=0.01)    # converge forces below 0.01 eV/Å

# Or with FIRE
opt = FIRE(atoms)
opt.run(fmax=0.01)
```

## Reading trajectories

```python
from ase.io import read

# Read all frames
traj = read("relax.traj", index=":")   # returns a list of Atoms

for frame in traj:
    print(frame.get_potential_energy())

# Read last frame only
last = read("relax.traj")
```

## Visualisation

```python
from ase.visualize import view

view(atoms)               # opens ASE GUI
view(traj)                # animate trajectory
```

!!! tip "Headless servers"
    On HPC clusters without a display, use `write("out.png", atoms)` or
    `write("out.html", atoms)` to produce static/interactive images.
