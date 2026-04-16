# Quantum ESPRESSO Input File (pw.x)

The main QE executable `pw.x` reads a single input file divided into **namelists** and **cards**.

## Minimal SCF example

```fortran
&CONTROL
  calculation  = 'scf'
  prefix       = 'silicon'
  outdir       = './tmp'
  pseudo_dir   = './pseudos'
/

&SYSTEM
  ibrav        = 2
  celldm(1)    = 10.26        ! lattice parameter in Bohr
  nat          = 2
  ntyp         = 1
  ecutwfc      = 60.0         ! plane-wave cutoff in Ry
  ecutrho      = 480.0        ! charge-density cutoff in Ry
/

&ELECTRONS
  conv_thr     = 1.0e-8
/

ATOMIC_SPECIES
 Si  28.086  Si.pbe-n-rrkjus_psl.1.0.0.UPF

ATOMIC_POSITIONS {crystal}
 Si  0.00  0.00  0.00
 Si  0.25  0.25  0.25

K_POINTS {automatic}
 8 8 8  0 0 0
```

## Namelist reference

### `&CONTROL`

| Parameter | Description |
|---|---|
| `calculation` | `'scf'`, `'relax'`, `'vc-relax'`, `'nscf'`, `'bands'` |
| `prefix` | Label for output files |
| `outdir` | Directory for temporary files |
| `pseudo_dir` | Directory containing pseudopotential files |
| `tprnfor` | Print forces (`.true.`/`.false.`) |
| `tstress` | Print stress tensor |

### `&SYSTEM`

| Parameter | Description |
|---|---|
| `ibrav` | Bravais lattice index (0 = free, read from `CELL_PARAMETERS`) |
| `celldm(1)` | Lattice parameter in Bohr (used when `ibrav ≠ 0`) |
| `nat` | Number of atoms |
| `ntyp` | Number of atomic species |
| `ecutwfc` | Kinetic energy cutoff for wavefunctions (Ry) |
| `ecutrho` | Cutoff for charge density (Ry); typically `8–12 × ecutwfc` |
| `occupations` | `'smearing'` for metals; `'fixed'` for insulators |
| `smearing` | `'mp'` (Methfessel-Paxton), `'mv'`, `'gaussian'` |
| `degauss` | Smearing width in Ry |
| `nspin` | `1` non-spin, `2` spin-polarized |

### `&ELECTRONS`

| Parameter | Description |
|---|---|
| `conv_thr` | SCF convergence threshold on total energy (Ry) |
| `mixing_beta` | Charge mixing parameter (default 0.7; reduce for hard cases) |
| `diagonalization` | `'david'` (default) or `'cg'` |

### `&IONS` (for `relax` / `vc-relax`)

| Parameter | Description |
|---|---|
| `ion_dynamics` | `'bfgs'` (default) or `'damp'` |

### `&CELL` (for `vc-relax`)

| Parameter | Description |
|---|---|
| `cell_dynamics` | `'bfgs'` |
| `press` | Target pressure in kbar |

## Cards reference

| Card | Description |
|---|---|
| `ATOMIC_SPECIES` | Species name, mass, pseudopotential filename |
| `ATOMIC_POSITIONS` | Atom positions; units: `{crystal}`, `{angstrom}`, `{bohr}` |
| `K_POINTS` | k-point mesh; `{automatic}` for Monkhorst-Pack |
| `CELL_PARAMETERS` | Lattice vectors when `ibrav = 0`; units `{angstrom}` or `{bohr}` |
