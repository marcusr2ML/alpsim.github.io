---
title: DMRG-09 Model
weight: 3
math: true
toc: true
---

[DMRG-07](../dmrg07) derived the Jordan-Wigner mapping, and [DMRG-08](../dmrg07-simulations) used it to justify running the fermion chain as `MODEL="hardcore boson"`: on an open chain with nearest-neighbor hopping the strings cancel between adjacent sites, so the two models are the same Hamiltonian. That is a physical argument, and it is correct.

This module demonstrates it by simulation instead — runs both models through both codes and compares the energies and the convergence. The equivalence appears exactly where the physical argument says it must. What the numbers add is a second finding the argument cannot supply: the legacy `dmrg` binary does not reproduce the fermionic model at all, which turns the substitution from permitted into mandatory.

## The two models

The spinless fermion chain with nearest-neighbor hopping and nearest-neighbor repulsion is:

$$
H = -t\sum_{i=1}^{L-1}\big(c^\dagger_i c_{i+1} + c^\dagger_{i+1} c_i\big) \;+\; V\sum_{i=1}^{L-1} n_i n_{i+1} \;-\; \mu\sum_{i=1}^{L} n_i ,
$$

with $n_i = c^\dagger_i c_i \in \{0,1\}$.
This is the built-in `spinless fermions` model of the ALPS model library.
It is the fermionic image of the anisotropic Heisenberg chain solved by [Lieb, Schultz, and Mattis (1961)](https://doi.org/10.1016/0003-4916(61)90115-4), reached through the transformation of [Jordan and Wigner (1928)](https://doi.org/10.1007/BF01331938); the DMRG algorithm itself is due to [White (1992)](https://doi.org/10.1103/PhysRevLett.69.2863).

The hard-core boson chain is the same expression with $c^\dagger_i \to b^\dagger_i$, where the $b$ commute on different sites but $(b^\dagger_i)^2 = 0$ still admits at most one particle per site.
This is the built-in `hardcore boson` model, and it takes the same parameters `t`, `V`, `mu` and the same conserved quantum number `N`.

The two models differ *only* in the exchange statistics — that is, only through the Jordan-Wigner strings.
On an open chain with nearest-neighbor hopping those strings cancel between adjacent sites, leaving $\hat S^+_j\hat S^-_{j+1} = \hat c^\dagger_j \hat c_{j+1}$ with no residual sign, so the two share every eigenvalue, sector by sector in $N$.
Note the limits of the substitution: it is exact only for nearest-neighbor hopping on an open chain.
Add periodic boundaries or hopping beyond nearest neighbors and the strings no longer cancel, at which point hard-core bosons and spinless fermions are genuinely different models — a point [DMRG-10](../dmrg09) returns to when it puts the chain on a ring.

At $V=0$ the chain is exactly solvable.
On an open chain the single-particle levels are:

$$
\varepsilon_k = -2t\cos\!\left(\frac{k\pi}{L+1}\right), \qquad k = 1,\dots,L ,
$$

and the ground state energy at $N$ particles is the sum of the $N$ lowest of them.
That closed form is the exact reference both models are measured against below.

## Where the two models disagree: the `dmrg` binary

The substitution is not cosmetic.
Running the fermionic model through the legacy `dmrg` binary returns energies far below the true ground state — a variational impossibility, and a clear sign the matrix being diagonalized is not the intended Hamiltonian.
On an $L=8$, $N=4$ chain at $V=0$, where the exact answer is $-4.758770483$:

| Model | `sparsediag` | `dmrg` |
|---|---|---|
| `spinless fermions` | $-4.7587704831436346$ | $-467.3$ |
| `hardcore boson` | $-4.7587704831436346$ | $-4.7587704831436337$ |

Read the table by column and by row.
Down the `sparsediag` column the two models agree to sixteen digits: this is the Jordan-Wigner equivalence of [DMRG-07](../dmrg07) confirmed numerically rather than argued, and it is the demonstration this module exists to provide.
Down the `dmrg` column they do not agree at all.
Across the `hardcore boson` row both codes agree, so the two codes are not the problem either.
Only one cell of the table is wrong, and isolating it that way is what makes the diagnosis possible: since `sparsediag` reproduces the fermionic spectrum correctly, the model *definition* in the ALPS library is sound, and the failure lies in what `dmrg` does with it.

The size of the discrepancy rules out an accuracy problem before any mechanism need be considered.
The single-particle levels above give the whole many-body spectrum at $V=0$: any eigenvalue is a sum of a subset of the eight $\varepsilon_k$, so the extreme values are obtained by filling all the negative levels or all the positive ones, and the entire spectrum — every state, in every particle-number sector — lies within

$$
-4.758770483 \;\le\; E \;\le\; +4.758770483 .
$$

The reported $-467.3$ is not merely below the ground state; it is roughly $98\times$ below the smallest eigenvalue the Hamiltonian possesses. No amount of truncation error, sweep count, or bond dimension can produce that. DMRG is variational: with a correct operator, the energy is a Rayleigh quotient $\langle\psi|H|\psi\rangle/\langle\psi|\psi\rangle$ over some trial state, and such a quotient is bounded below by the lowest eigenvalue no matter how bad the state is. A number outside the spectrum therefore proves the matrix being diagonalized is not $H$.

### Why spinless fermions fail here

The words "fermion sign" point naturally toward the sign problem, which is not what is happening.

The [sign problem](../../../../documentation/models/sfm) is a pathology of *stochastic* methods: negative or complex weights in a Monte Carlo sampling cause the statistical error to grow exponentially with system size and inverse temperature. It degrades precision at fixed cost; it never returns an energy outside the spectrum, and it never appears in a deterministic calculation. DMRG performs no sampling at all, so it cannot have one — which is also why exact diagonalization handles the fermionic model here without difficulty.

What fermions demand of DMRG is bookkeeping, not sampling. Anticommutation means $c^\dagger_i c_j$ acting across a partition of the chain carries a Jordan-Wigner string $\prod_{l<i}(1-2n_l)$ over every site in between, and those string factors must be inserted when the Hamiltonian is expressed in the renormalized block bases that DMRG builds and rebuilds each sweep. Get them right and the fermionic calculation is as well behaved as the bosonic one. Omit or misapply them and the assembled matrix is a different operator — one with no reason to be Hermitian, and hence no variational floor at all, which is consistent with a Lanczos iteration wandering a hundredfold below the true ground state. The exact defect in the legacy code is not something these two numbers can pin down; what they do establish is the category of failure, and that it is not statistical.

The practical consequence is the same either way. The hard-core boson form is exactly the XXZ chain under the local Matsubara-Matsuda mapping, which needs no strings and holds on any lattice, so nothing is lost by using it — and on the open chain of this series, nothing is approximated either. The boson form is the one to use with `dmrg` throughout.

## Parameters

| Parameter | Meaning | Value |
|---|---|---|
| `LATTICE` | built-in open chain, no lattice file required | `open chain lattice` |
| `MODEL` | the boson form, for the reason established above | `hardcore boson` |
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
This is the parameter-file face of the dictionary $\hat S^z_{\text{tot}} = \hat N - L/2$ derived in [DMRG-07](../dmrg07): zero magnetization is half filling.
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

To reproduce the comparison table above, the same file with `MODEL="spinless fermions"` and `L=8`, `N_total=4` is run through both `sparsediag` and `dmrg`.

## Lattice

An open chain of $L=32$ sites, every bond carrying the same hopping $t$ and repulsion $V$, every site the same chemical potential $\mu$:

```
   -mu          -mu          -mu                     -mu
    o------------o------------o----- ... ------------o
    1            2            3                      L=32
       t, V         t, V                    t, V
```

The chain is the natural geometry here: DMRG is at its most accurate in one dimension, and the open ends are what make the Jordan-Wigner strings cancel, so the model equivalence tested on this page holds exactly.
The `open chain lattice` is built in, so no lattice file is needed — see the [ALPS lattice library](../../../../documentation/intro/latticehowtos) for the other chain variants.
What the open ends cost in return is the subject of [DMRG-10](../dmrg09).

## Choice of method

DMRG is the right tool for a 1D chain of this length: the half-filled sector holds about $6\times10^{8}$ states, far beyond exact diagonalization, yet the ground state is only lightly entangled and a bond dimension of a few hundred suffices.

The $L=8$ comparison above is the exception, and deliberately so: at that length the full Hilbert space is small enough for `sparsediag` to diagonalize exactly, which is what makes it possible to attribute the discrepancy to the `dmrg` binary rather than to the model definition. Benchmarking one method against another only works where a third, exact method can arbitrate.

## Running the simulation

From a parameter file named `parm_sf`:

```
parameter2xml parm_sf
dmrg --write-xml parm_sf.in.xml
```

Each task writes `parm_sf.taskN.out.xml`, containing the converged energy and truncation error.

The script <a class="alps-download" href="../run_free_theory.py" data-filename="run_free_theory.py" target="_blank" rel="noopener">`run_free_theory.py`</a> does all of the above and tabulates the result against the exact answer:

```
python3 run_free_theory.py --L 32
```

It writes the parameter files, calls `parameter2xml` and `dmrg` for each bond dimension, parses the energies out of the XML, and prints the comparison table below.
Pass `--alps-bin /path/to/alps/bin` if the ALPS executables are not on your `PATH`.

## Results

With the model question settled, the boson form converges as it should.
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

Every entry in that table approaches the exact energy *from above* and stops there, which is the variational principle doing its job — and the contrast with the failure above is the point.
A broken operator does not announce itself by converging slowly to a slightly wrong number; it converges to an impossible one.
That is the check worth building into any fermionic DMRG run: compare against a bound rather than against an expectation. Here the free-fermion closed form supplies the bound exactly, but even a crude one is enough, since the failure mode overshoots it by a factor of a hundred rather than a percent.

The intensive quantities are:

$$
\frac{E_0}{L} = -0.625512122, \qquad \frac{E_0}{L-1} = -0.645689932 ,
$$

against the thermodynamic-limit value $-2t/\pi = -0.636619772$ per site for the half-filled chain with periodic boundaries.
Neither finite-$L$ number has converged to it yet, and the gap between the two is itself a boundary effect: dividing by $L$ or by $L-1$ should not matter in the thermodynamic limit, and at $L=32$ it matters in the second digit. That $O(1/L)$ discrepancy is exactly what [DMRG-10](../dmrg09) takes apart.

## Summary

On an open chain with nearest-neighbor hopping, `spinless fermions` and `hardcore boson` are the same model, and `sparsediag` confirms it to sixteen digits — the physical argument of [DMRG-07](../dmrg07), demonstrated rather than asserted. The legacy `dmrg` binary reproduces that spectrum only in the boson form, returning an energy $98\times$ below the smallest eigenvalue the Hamiltonian has in the fermionic one. That is Jordan-Wigner string bookkeeping failing, not a sign problem — DMRG samples nothing and cannot have one — and it means the boson form is not a convenience but a requirement. In that form the half-filled non-interacting chain is reproduced to machine precision at $D=200$.

## Questions

1. Verify the equivalence yourself on a small chain: run `sparsediag` with `MODEL="spinless fermions"` and with `MODEL="hardcore boson"` for $L=8$, $N_{\text{total}}=4$, and confirm that the spectra coincide sector by sector, not just in the ground state.
2. Test the stated limit of the substitution: repeat that comparison on a *periodic* chain (`LATTICE="chain lattice"`) and confirm that the two energies now differ, as the surviving Jordan-Wigner string requires.
3. Test the other stated limit: add a next-nearest-neighbor hopping $t'$ on the open chain. At what value of $t'/t$ does the fermion-boson discrepancy become visible above the truncation error?
4. Does the fermionic `dmrg` failure depend on the sector? Repeat the $L=8$ run at $N_{\text{total}} = 1$, where a single particle has no other particle to exchange with, and at $N_{\text{total}} = 2$.
5. How does the energy per site approach $-2t/\pi$ as $L$ grows? Run $L = 16, 32, 64, 128$ and fit the finite-size correction — is it $O(1/L)$ or $O(1/L^2)$? Compare your answer with [DMRG-10](../dmrg09).
