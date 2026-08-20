#!/usr/bin/env python3
"""Ground state energy of the interacting spinless fermion chain, benchmarked
against the Bethe ansatz.

At V = 2t the spinless fermion chain is the isotropic Heisenberg chain, whose
bulk ground state energy per bond is known exactly:

    e0 / J = 1/4 - ln 2 = -0.4431471805599...

This script runs the ALPS `dmrg` code on a series of open chains, converts each
energy into spin units, and extrapolates e0(L) = a + b/L + c/L^2 to recover
that value.

Open boundary conditions are used throughout, as they must be: DMRG on a ring
has to carry entanglement across two cuts rather than one, and the bond
dimension needed for a given accuracy grows sharply as a result.  The price of
open boundaries is a surface energy contributing at order 1/L, which is why the
fit carries a b/L term.  A finite-size energy at any single length is nowhere
near the Bethe ansatz value; only the extrapolated bulk term is.

Two conventions matter and are handled here.

1.  The model is entered as `hardcore boson`, not `spinless fermions`.  The
    legacy `dmrg` binary returns energies far below the true ground state for
    the fermionic model; the boson form is exactly the XXZ chain by the local
    Matsubara-Matsuda mapping, and `dmrg` handles it correctly.

2.  Writing Sz = n - 1/2 in the Jz Sz Sz term produces, on an open chain, a
    boundary field (Jz/2)(n_1 + n_L) that a uniform `mu` cannot represent.  It
    is a surface term, so it shifts b and leaves the bulk value a untouched.

With Jxy = Jz = J = 1 the parameters are t = J/2, V = J, mu = J.

Usage:
    python3 run_bethe_ansatz.py [--lengths 16 24 32 48 64 96 128]
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

J = 1.0                      # isotropic Heisenberg coupling
BETHE = 0.25 - math.log(2)   # exact bulk e0/J


def find_alps_bin(explicit=None):
    if explicit:
        return explicit
    if shutil.which("dmrg") and shutil.which("parameter2xml"):
        return ""
    guess = os.path.expanduser("~/alps-install/bin")
    if os.path.isfile(os.path.join(guess, "dmrg")):
        return guess
    sys.exit("Could not find the ALPS binaries. Pass --alps-bin /path/to/alps/bin.")


def write_parm(path, L, maxstates, sweeps):
    """Open chain of L sites at half filling, at the isotropic Heisenberg point."""
    with open(path, "w") as f:
        f.write(
            'LATTICE="open chain lattice"\n'
            'MODEL="hardcore boson"\n'
            'CONSERVED_QUANTUMNUMBERS="N"\n'
            f"N_total={L // 2}\n"
            f"t={J / 2}\n"                       # t  = Jxy/2
            f"V={J}\n"                           # V  = Jz     (so V = 2t)
            f"mu={J}\n"                          # mu = Jz
            f"L={L}\n"
            "NUMBER_EIGENVALUES=1\n"
            f"{{SWEEPS={sweeps}; MAXSTATES={maxstates}}}\n"
        )


def read_energy(xml_path):
    root = ET.parse(xml_path).getroot()
    for avg in root.iter("SCALAR_AVERAGE"):
        if avg.get("name") == "Energy":
            return float(avg.find("MEAN").text)
    raise RuntimeError(f"no Energy found in {xml_path}")


def solve3(rows, rhs):
    """Gaussian elimination on a 3x3 system, so numpy is not required."""
    m = [r[:] + [v] for r, v in zip(rows, rhs)]
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(m[r][i]))
        m[i], m[p] = m[p], m[i]
        for r in range(3):
            if r != i:
                f = m[r][i] / m[i][i]
                for c in range(i, 4):
                    m[r][c] -= f * m[i][c]
    return [m[i][3] / m[i][i] for i in range(3)]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lengths", type=int, nargs="+",
                    default=[16, 24, 32, 48, 64, 96, 128])
    ap.add_argument("--maxstates", type=int, default=300)
    ap.add_argument("--sweeps", type=int, default=8)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--alps-bin", default=None)
    args = ap.parse_args()

    for L in args.lengths:
        if L % 2:
            sys.exit(f"L={L} is odd; half filling needs an even length.")
    if len(args.lengths) < 3:
        sys.exit("Give at least three lengths so the surface term can be fitted.")

    bindir = find_alps_bin(args.alps_bin)
    exe = lambda name: os.path.join(bindir, name) if bindir else name
    workdir = args.workdir or tempfile.mkdtemp(prefix="alps_bethe_")
    os.makedirs(workdir, exist_ok=True)

    print(f"isotropic Heisenberg point: J = {J}, so t = {J/2}, V = {J}, mu = {J}")
    print(f"open chain, half filling, D = {args.maxstates}")
    print(f"working in {workdir}\n")

    print(f"{'L':>5} {'E (hardcore boson)':>21} {'E (XXZ)':>18} "
          f"{'e0 = E/(L-1)':>16} {'e0 - Bethe':>12}")
    pts = []
    for L in args.lengths:
        stem = f"parm_chain_L{L}"
        write_parm(os.path.join(workdir, stem), L, args.maxstates, args.sweeps)
        subprocess.run([exe("parameter2xml"), stem], cwd=workdir,
                       check=True, capture_output=True)
        subprocess.run([exe("dmrg"), "--write-xml", f"{stem}.in.xml"], cwd=workdir,
                       check=True, capture_output=True)
        e_hcb = read_energy(os.path.join(workdir, f"{stem}.task1.out.xml"))
        e_xxz = e_hcb + J * (L - 1) / 4.0     # L-1 bonds on an open chain
        e0 = e_xxz / (L - 1)                  # energy per bond
        print(f"{L:>5} {e_hcb:>21.10f} {e_xxz:>18.10f} {e0:>16.12f} {e0 - BETHE:>12.2e}")
        pts.append((L, e0))

    (l1, y1), (l2, y2), (l3, y3) = pts[-3], pts[-2], pts[-1]
    a, b, c = solve3([[1, 1 / l1, 1 / l1 ** 2],
                      [1, 1 / l2, 1 / l2 ** 2],
                      [1, 1 / l3, 1 / l3 ** 2]], [y1, y2, y3])
    print(f"\nfit e0(L) = a + b/L + c/L^2  using L = {l1}, {l2}, {l3}:")
    print(f"  a = {a:.10f}   bulk energy per bond")
    print(f"  Bethe ansatz 1/4 - ln2 = {BETHE:.10f}   (diff {a - BETHE:.2e})")
    print(f"  b = {b:+.6f}   surface energy of the two open ends")
    print("\nThe b/L term is what open boundaries cost in the extrapolation.")
    print("It is the price of the geometry DMRG actually converges on.")


if __name__ == "__main__":
    main()
