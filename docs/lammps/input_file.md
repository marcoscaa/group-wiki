# LAMMPS Input File Structure

A LAMMPS input script is read top-to-bottom. Commands fall into a few logical sections.

## Minimal example

```lammps
# ── 1. Initialization ─────────────────────────────────────────────────────────
units           metal          # eV, Å, ps, bar
dimension       3
boundary        p p p          # periodic in x, y, z
atom_style      atomic

# ── 2. Geometry ───────────────────────────────────────────────────────────────
read_data       structure.lammps

# ── 3. Interatomic potential ──────────────────────────────────────────────────
pair_style      mace no_domain_decomposition
pair_coeff      * * my_model.model Cu

# ── 4. Settings ───────────────────────────────────────────────────────────────
neighbor        2.0 bin
neigh_modify    every 1 delay 0 check yes

# ── 5. Output ─────────────────────────────────────────────────────────────────
thermo          100
thermo_style    custom step temp press etotal vol

dump            1 all custom 100 dump.lammpstrj id type x y z

# ── 6. Run ────────────────────────────────────────────────────────────────────
timestep        0.001          # 1 fs in metal units

fix             1 all nvt temp 300.0 300.0 0.1
run             10000
```

## Section reference

### 1. Initialization

| Command | Purpose |
|---|---|
| `units` | Sets unit system (`metal`, `real`, `si`, `lj`, …) |
| `boundary` | Periodic (`p`) or non-periodic (`f`/`s`) per axis |
| `atom_style` | Atom attributes (`atomic`, `charge`, `full`, …) |

### 2. Geometry

| Command | Purpose |
|---|---|
| `read_data` | Read atom positions from a `.lammps` data file |
| `lattice` + `region` + `create_atoms` | Build a lattice from scratch |

### 3. Interatomic potential

| Command | Purpose |
|---|---|
| `pair_style` | Functional form of the potential |
| `pair_coeff` | Parameters / model file |
| `kspace_style` | Long-range electrostatics (Ewald, PPPM) |

### 4. Settings

| Command | Purpose |
|---|---|
| `neighbor` | Skin distance for neighbor list |
| `neigh_modify` | How often to rebuild the neighbor list |
| `group` | Define atom groups for selective fixes/dumps |

### 5. Output

| Command | Purpose |
|---|---|
| `thermo` | Print thermodynamic data every N steps |
| `thermo_style custom` | Choose which quantities to print |
| `dump` | Write trajectory file |
| `restart` | Write binary restart files |

### 6. Run

| Command | Purpose |
|---|---|
| `timestep` | Integration time step |
| `fix` | Apply integrators, thermostats, constraints |
| `minimize` | Energy minimization instead of dynamics |
| `run` | Number of MD steps to execute |

## Common `units` reference

| System | Energy | Length | Time | Force |
|---|---|---|---|---|
| `metal` | eV | Å | ps | eV/Å |
| `real` | kcal/mol | Å | fs | kcal/(mol·Å) |
| `si` | J | m | s | N |
| `lj` | ε | σ | — | — |
