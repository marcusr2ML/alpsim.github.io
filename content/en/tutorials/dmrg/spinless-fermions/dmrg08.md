---
title: DMRG-08 Free Theory
weight: 2
math: true
toc: true
---

Having established in [DMRG-07](dmrg07) that the XXZ chain is a chain of spinless fermions in disguise, we now run the ALPS `dmrg` code on the fermionic form and compute the quantity every study starts from: the ground state energy.
We work at the free-fermion point $V=0$, where the answer is known in closed form, so that every digit the DMRG produces can be checked against an exact result rather than against another approximation.
Once that agreement is established, the same parameter file with $V\neq0$ takes us into genuinely interacting territory, which [DMRG-09](dmrg09) takes up against the Bethe ansatz.

## The model

The spinless fermion chain with nearest-neighbor hopping and nearest-neighbor repulsion is:

$$
H = -t\sum_{i=1}^{L-1}\big(c^\dagger_i c_{i+1} + c^\dagger_{i+1} c_i\big) \;+\; V\sum_{i=1}^{L-1} n_i n_{i+1} \;-\; \mu\sum_{i=1}^{L} n_i ,
$$

with $n_i = c^\dagger_i c_i \in \{0,1\}$.
This is the built-in `spinless fermions` model of the ALPS model library.
It is the fermionic image of the anisotropic Heisenberg chain solved by [Lieb, Schultz, and Mattis (1961)](https://doi.org/10.1016/0003-4916(61)90115-4), reached through the transformation of [Jordan and Wigner (1928)](https://doi.org/10.1007/BF01331938); the DMRG algorithm itself is due to [White (1992)](https://doi.org/10.1103/PhysRevLett.69.2863).

At $V=0$ the chain is exactly solvable.
On an open chain the single-particle levels are:

$$
\varepsilon_k = -2t\cos\!\left(\frac{k\pi}{L+1}\right), \qquad k = 1,\dots,L ,
$$

and the ground state energy at $N$ particles is the sum of the $N$ lowest of them.
That closed form is what we benchmark against below.

## Parameters

| Parameter | Meaning | Value |
|---|---|---|
| `LATTICE` | built-in open chain, no lattice file required | `open chain lattice` |
| `MODEL` | see [Choice of method](#choice-of-method) — entered as `hardcore boson` | `hardcore boson` |
| `L` | chain length | 32 |
| `CONSERVED_QUANTUMNUMBERS` | quantum numbers held fixed, used to block-diagonalize $H$ | `N` |
| `N_total` | particle-number sector; $N=L/2$ is half filling | 16 |
| `t` | nearest-neighbor hopping amplitude | 1 |
| `V` | nearest-neighbor repulsion; $V=0$ is the free-fermion point | 0 |
| `SWEEPS` | number of DMRG finite-size sweeps | 4 |
| `NUMBER_EIGENVALUES` | eigenstates requested | 1 |
| `MAXSTATES` | bond dimension $D$ kept after truncation | 20, 50, 100, 200 |

Note what has changed relative to the spin-chain modules.
There is no `Sz_total`, because a spinless fermion has no spin to project; the sector is fixed by `N_total` instead.
This is the parameter-file face of the dictionary $\hat S^z_{\text{tot}} = \hat N - L/2$ derived in [DMRG-07](dmrg07): zero magnetization is half filling.
Leaving `N_total` unset runs the calculation grand canonically over the full $2^L$-dimensional space, whereas fixing it restricts the calculation to the $\binom{32}{16} \approx 6.0\times10^{8}$ states of the half-filled sector.

## Parameter file

```
LATTICE="open chain lattice"
MODEL="hardcore boson"
CONSERVED_QUANTUMNUMBERS="N"
N_total=16
t=1
V=0
L=32
NUMBER_EIGENVALUES=1
{SWEEPS=4; MAXSTATES=20}
{SWEEPS=4; MAXSTATES=50}
{SWEEPS=4; MAXSTATES=100}
{SWEEPS=4; MAXSTATES=200}
```

## Lattice

An open chain of $L=32$ sites, every bond carrying the same hopping $t$ and repulsion $V$, every site the same chemical potential $\mu$:

```
   -mu          -mu          -mu                     -mu
    o------------o------------o----- ... ------------o
    1            2            3                      L=32
       t, V         t, V                    t, V
```

The chain is the natural geometry here: DMRG is at its most accurate in one dimension, and open boundaries (rather than periodic) keep the entanglement across any cut as small as possible, which is what lets a modest bond dimension reach machine precision below.
Open boundaries matter for a second reason specific to fermions, discussed next.
The `open chain lattice` is built in, so no lattice file is needed — see the [ALPS lattice library](../../../documentation/intro/latticehowtos) for the other chain variants.

## Choice of method

DMRG is the right tool for a 1D chain of this length: the half-filled sector holds about $6\times10^{8}$ states, far beyond exact diagonalization, yet the ground state is only lightly entangled and a bond dimension of a few hundred suffices.

**One important caveat about the model name.**
The parameter file above sets `MODEL="hardcore boson"`, not `MODEL="spinless fermions"`.
On an open chain with nearest-neighbor hopping the two are the *same Hamiltonian*, for exactly the reason derived in [DMRG-07](dmrg07): the Jordan-Wigner strings cancel between adjacent sites, leaving $\hat S^+_j\hat S^-_{j+1} = \hat c^\dagger_j \hat c_{j+1}$ with no residual sign.
Hard-core bosons and spinless fermions differ only through those strings, so on this geometry they share every eigenvalue.

The substitution is not cosmetic.
Running the fermionic model through the legacy `dmrg` binary returns energies far below the true ground state — a variational impossibility, and a clear sign the matrix being diagonalized is not the intended Hamiltonian.
On an $L=8$, $N=4$ chain, where the exact answer is $-4.758770483$:

| Model | `sparsediag` | `dmrg` |
|---|---|---|
| `spinless fermions` | $-4.7587704831436346$ | $-467.3$ |
| `hardcore boson` | $-4.7587704831436346$ | $-4.7587704831436337$ |

`sparsediag` handles the fermionic model correctly, so the model definition itself is sound; the failure is in `dmrg`.
The boson form is therefore the one to use with `dmrg` here.
Note the limits of the substitution: it is exact only for nearest-neighbor hopping on an open chain.
Add periodic boundaries or hopping beyond nearest neighbors and the strings no longer cancel, at which point hard-core bosons and spinless fermions are genuinely different models.

## Running the simulation

From a parameter file named `parm_sf`:

```
parameter2xml parm_sf
dmrg --write-xml parm_sf.in.xml
```

Each task writes `parm_sf.taskN.out.xml`, containing the converged energy and truncation error.

The script <a class="alps-download" href="../run_free_theory.py" data-filename="run_free_theory.py" target="_blank" rel="noopener">`run_ground_state.py`</a> does all of the above and tabulates the result against the exact answer:

```
python3 run_free_theory.py --L 32
```

It writes the parameter files, calls `parameter2xml` and `dmrg` for each bond dimension, parses the energies out of the XML, and prints the comparison table below.
Pass `--alps-bin /path/to/alps/bin` if the ALPS executables are not on your `PATH`.

## Results

Ground state energy of the half-filled $L=32$ chain at $t=1$, $V=0$:

| $D$ | $E_0$ (DMRG) | truncation error | $E_0 - E_{\text{exact}}$ |
|---|---|---|---|
| 20 | $-20.016369170590639$ | $5.232\times10^{-7}$ | $1.873\times10^{-5}$ |
| 50 | $-20.016387897889135$ | $5.161\times10^{-11}$ | $2.596\times10^{-9}$ |
| 100 | $-20.016387900483672$ | $3.235\times10^{-14}$ | $1.467\times10^{-12}$ |
| 200 | $-20.016387900485153$ | $1.732\times10^{-16}$ | $-1.421\times10^{-14}$ |
| exact | $-20.016387900485139$ | | |

By $D=200$ the DMRG energy agrees with the closed-form result to $1.4\times10^{-14}$, essentially machine precision.
The error tracks the truncation error closely across four orders of magnitude, which is the practical basis for the extrapolation used in later modules: the truncation error is a computable proxy for the error in the energy, even when no exact answer is available to compare against.

The intensive quantities are:

$$
\frac{E_0}{L} = -0.625512122, \qquad \frac{E_0}{L-1} = -0.645689932 ,
$$

against the thermodynamic-limit value $-2t/\pi = -0.636619772$ per site for the half-filled chain with periodic boundaries.
Neither finite-$L$ number has converged to it yet: the open chain's two missing bonds and its boundary effects are an $O(1/L)$ correction, which is what the next module extrapolates away.

## Summary and outlook

The half-filled, non-interacting spinless fermion chain is reproduced by ALPS DMRG to machine precision, once the model is entered in its hard-core boson form and the sector is fixed by `N_total` rather than `Sz_total`.
That gives a trustworthy baseline against which the interacting case can be judged.

1. How does the energy per site approach $-2t/\pi$ as $L$ grows? Run $L = 16, 32, 64, 128$ and fit the finite-size correction — is it $O(1/L)$ or $O(1/L^2)$?
2. Turn on the interaction. At what value of $V/t$ does the bond dimension needed for a fixed accuracy start to grow sharply, and how does that relate to the transition at $V = 2t$?
3. Away from half filling, does the convergence in $D$ improve or degrade? Compare $N = L/4$ with $N = L/2$ at fixed $L$.
4. Verify the claim above directly: run `spinless fermions` and `hardcore boson` through `sparsediag` on a *periodic* chain and confirm that the two energies now differ, as the surviving Jordan-Wigner string requires.
