"""One example on how to use ASE+MACE+PLUMED to run enhanced sampling MD"""
import argparse
import os
import time

import ase.io
import numpy as np
from ase import units
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
from ase.calculators.plumed import Plumed, restart_from_trajectory
from ase import Atoms

from mace.calculators.mace import MACECalculator

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to XYZ configurations", required=True)
    parser.add_argument(
        "--config_index", help="index of configuration", type=int, default=-1
    )
    parser.add_argument("--temperature_K", help="temperature", type=float, default=300)
    parser.add_argument("--nvt-q", type=float, default=43.06225052549201)
    parser.add_argument("--timestep", help="timestep", type=float, default=1)
    parser.add_argument("--nsteps", help="number of steps", type=int, default=1000)
    parser.add_argument(
        "--nprint", help="number of steps between prints", type=int, default=10
    )
    parser.add_argument(
        "--nsave", help="number of steps between saves", type=int, default=10
    )
    parser.add_argument(
        "--max_seconds", help="Maximum wall time to run the code", type=int, default=43000
    )

    parser.add_argument(
        "--model",
        help="path to model. Use wildcards to add multiple models as committee eg "
        "(`mace_*.model` to load mace_1.model, mace_2.model) ",
        required=True,
    )
    parser.add_argument("--output", help="output path", required=True)
    parser.add_argument(
        "--device",
        help="select device",
        type=str,
        choices=["cpu", "cuda"],
        default="cuda",
    )
    parser.add_argument(
        "--default_dtype",
        help="set default dtype",
        type=str,
        choices=["float32", "float64"],
        default="float64",
    )
    parser.add_argument(
        "--compute_stress",
        help="compute stress",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--info_prefix",
        help="prefix for energy, forces and stress keys",
        type=str,
        default="MACE_",
    )
    return parser.parse_args()

def change_hydrogen_mass(atom):
    masses=atom.get_masses()
    atomic_index=np.array(atom.get_atomic_numbers(),dtype=int)
    masses[atomic_index==1]=2.016
    atom.set_masses(masses)
    return atom

def printenergy(dyn, start_time=None):  # store a reference to atoms in the definition.
    """Function to print the potential, kinetic and total energy."""
    a = dyn.atoms
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    if start_time is None:
        elapsed_time = 0
    else:
        elapsed_time = time.time() - start_time
    print(
        "%.1fs: Energy per atom: Epot = %.3feV  Ekin = %.3feV (T=%3.0fK)  "  # pylint: disable=C0209
        "Etot = %.3feV t=%.1ffs"
        % (
            elapsed_time,
            epot,
            ekin,
            ekin / (1.5 * units.kB),
            epot + ekin,
            dyn.get_time() / units.fs,
        ),
        flush=True,
    )

def save_config(dyn, fname):
    atomsi = dyn.atoms
    ens = atomsi.get_potential_energy()
    frcs = atomsi.get_forces()
    atoms_save = Atoms(symbols=atomsi.get_chemical_symbols(),
                       positions=atomsi.get_positions(),
                       cell=atomsi.get_cell(),
                       pbc=atomsi.get_pbc())

    atoms_restart = atoms_save.copy()
    atoms_restart.info.update({"time": np.round(dyn.get_time() / units.fs, 5)})
    atoms_restart.arrays.update(
        {
            "momenta": atomsi.get_momenta(),
        }
    )
    atoms_save.info.update(
        {
            "time": np.round(dyn.get_time() / units.fs, 5),
        }
    )

    ase.io.write("md.restart", atoms_restart, format="extxyz")
    ase.io.write(fname, atoms_save, append=True)

def plumed_input(restart=False):
    setup = []
    if restart:
        setup = ["RESTART"]

    setup.extend( 
            [f"UNITS LENGTH=A TIME={1/(1000 * units.fs)} ENERGY={units.mol/units.kJ}",
              "lq: COORDINATIONNUMBER SPECIES=2209-2256 SWITCH={EXP D_0=3.5 R_0=10.0}",
              "mat: CONTACT_MATRIX ATOMS=lq SWITCH={EXP D_0=3.5 R_0=10.0}",
              "dfs: DFSCLUSTERING MATRIX=mat",
              "clust1: CLUSTER_PROPERTIES CLUSTERS=dfs CLUSTER=1 SUM",
              "metad: METAD arg=clust1.sum sigma=5 height=1.0 BIASFACTOR=100 TEMP=400.0 PACE=100",
              "PRINT ARG=clust1.sum,metad.* STRIDE=100 FILE=COLVAR",
              "FLUSH STRIDE=100"] 
            )
    return setup

def stop_maxseconds(dyn, maxsec=None, start_time=None):
    if start_time is None:
        elapsed_time = 0
    else:
        elapsed_time = time.time() - start_time
    if maxsec is not None:
        if elapsed_time > maxsec:
            print("Simulation exceeded maximum allowed time", flush=True)
            dyn.max_steps = 0

def main():
    args = parse_args()

    mace_fname = args.model
    atoms_fname = args.config
    atoms_index = args.config_index

    mace_calc = MACECalculator(
        model_paths=mace_fname,
        device=args.device,
        default_dtype=args.default_dtype,
    )

    NSTEPS = args.nsteps

    if os.path.exists(args.output):
        print("Trajectory exists. Continuing from last step.")
        atoms = ase.io.read(args.output, index=-1)
        len_save = len(ase.io.read(args.output, ":"))
        #print("Last step: ", atoms.info["time"], "Number of configs: ", len_save)
        NSTEPS -= len_save * args.nsave
        restart=True

    else:
        atoms = ase.io.read(atoms_fname, index=atoms_index)
        MaxwellBoltzmannDistribution(atoms, temperature_K=args.temperature_K)
        restart=False


    change_hydrogen_mass(atoms)
    #Enhandec sampling with Plumed
    plumed_inp = plumed_input(restart=restart)
    plumed_calc = Plumed(calc=mace_calc,
                        input=plumed_inp,
                        timestep=args.timestep * units.fs,
                        atoms=atoms,
                        restart=restart,
                        log="plumed.log")

    atoms.calc = plumed_calc

    #Running NVT (Langevin thermostat)
    dyn = Langevin(
        atoms,
        timestep=args.timestep * units.fs,
        temperature_K=args.temperature_K,  # temperature in K
        friction=0.01 / units.fs,
    )

    dyn.attach(printenergy, interval=args.nsave, dyn=dyn, start_time=time.time())
    dyn.attach(save_config, interval=args.nsave, dyn=dyn, fname=args.output)
    dyn.attach(
        stop_maxseconds, interval=args.nsave, dyn=dyn, maxsec=args.max_seconds, start_time=time.time()
    )
    # Now run the dynamics
    dyn.run(NSTEPS)


if __name__ == "__main__":
    main()
