# VASP Input Files

A VASP calculation requires four input files in the same directory.

## File overview

| File | Role |
|---|---|
| `INCAR` | Calculation parameters (what to compute, how) |
| `POSCAR` | Crystal structure (cell + atomic positions) |
| `KPOINTS` | k-point sampling |
| `POTCAR` | Pseudopotentials / PAW datasets (concatenated) |

---

## INCAR

Controls every aspect of the calculation.

```
# Basic SCF
SYSTEM  = Si bulk
ISTART  = 0       # 0 = new calculation
ICHARG  = 2       # 2 = superposition of atomic charges

# Electronic minimization
ENCUT   = 520     # plane-wave cutoff in eV
EDIFF   = 1E-6    # SCF convergence criterion (eV)
ALGO    = Fast    # RMM-DIIS + Davidson
NELM    = 100     # max SCF steps

# k-point smearing (metals)
ISMEAR  = 1       # Methfessel-Paxton
SIGMA   = 0.2     # smearing width in eV

# Output
LORBIT  = 11      # write DOSCAR and projected DOS
LWAVE   = .FALSE. # do not write WAVECAR
LCHARG  = .FALSE. # do not write CHGCAR
```

### Common INCAR tags

| Tag | Values | Description |
|---|---|---|
| `ENCUT` | (eV) | Plane-wave cutoff |
| `EDIFF` | 1E-5 to 1E-8 | SCF energy tolerance |
| `EDIFFG` | negative (eV/Å) | Force tolerance for relaxation |
| `NSW` | integer | Max ionic steps (0 = single-point) |
| `IBRION` | 2 | Ionic relaxation algorithm (2 = CG) |
| `ISIF` | 2/3 | 2 = relax ions; 3 = relax ions + cell |
| `ISMEAR` | 1/-5 | 1 = MP smearing (metals); -5 = tetrahedron (insulators) |
| `SIGMA` | (eV) | Smearing width |
| `GGA` | `PE` | PBE functional |
| `LDAU` | `.TRUE.` | Enable DFT+U |
| `NPAR` | integer | Parallelization over bands |

---

## POSCAR

```
Si FCC bulk
1.0
  2.715  2.715  0.000
  0.000  2.715  2.715
  2.715  0.000  2.715
Si
2
Direct
  0.000  0.000  0.000
  0.250  0.250  0.250
```

Line-by-line:

1. Comment / system name
2. Universal scale factor
3–5. Lattice vectors (Å)
6. Element names (must match POTCAR order)
7. Number of atoms per species
8. `Direct` (fractional) or `Cartesian`
9+. Atomic positions

---

## KPOINTS

=== "Automatic Monkhorst-Pack"
    ```
    Automatic mesh
    0
    Monkhorst-Pack
    8 8 8
    0 0 0
    ```

=== "Gamma-centered"
    ```
    Gamma-centered mesh
    0
    Gamma
    8 8 8
    0 0 0
    ```

=== "Explicit k-path (band structure)"
    ```
    k-path
    10
    Line-mode
    Reciprocal
      0.000  0.000  0.000   ! Γ
      0.500  0.000  0.500   ! X
      0.500  0.000  0.500   ! X
      0.500  0.250  0.750   ! W
    ```

---

## POTCAR

Concatenate PAW datasets for each species **in the same order as POSCAR**:

```bash
cat $VASP_PP_PATH/PAW_PBE/Si/POTCAR > POTCAR
# for binary: cat .../Cu/POTCAR .../O/POTCAR > POTCAR
```

!!! warning "Order matters"
    The species order in POTCAR must exactly match POSCAR line 6.
