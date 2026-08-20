---
title: DMRG-09 Ground State Energy and the Bethe Ansatz
weight: 3
math: true
toc: true
---

[DMRG-08](dmrg08) benchmarked the chain where it is free. Here we turn the interaction on.
[DMRG-07](dmrg07) showed that the XXZ chain and the spinless fermion chain are the same system written in two languages.
That equivalence has a practical payoff: the XXZ chain is Bethe-ansatz integrable, so the interacting fermion problem inherits an exact answer to check DMRG against.
This module computes the ground state energy of the half-filled fermion chain at the interaction strength where the mapping lands on the isotropic Heisenberg point, and extrapolates it to the Bethe ansatz value $e_0/J = 1/4 - \ln 2$.

## The model and the interaction strength that matters

The spinless fermion chain is:

$$
H = -t\sum_{i}\big(c^\dagger_i c_{i+1} + c^\dagger_{i+1} c_i\big) \;+\; V\sum_{i} n_i n_{i+1} \;-\; \mu\sum_{i} n_i ,
$$

with $n_i = c^\dagger_i c_i \in \{0,1\}$.
Substituting $S^z_i = n_i - \tfrac12$ and the Jordan-Wigner strings of [DMRG-07](dmrg07) into the XXZ chain:

$$
H_{\text{XXZ}} = \sum_i \Big[ J_{xy}\big(S^x_iS^x_{i+1} + S^y_iS^y_{i+1}\big) + J_z S^z_iS^z_{i+1} \Big] ,
$$

identifies the two sets of couplings as:

$$
t = \frac{J_{xy}}{2}, \qquad V = J_z .
$$

The isotropic point $J_{xy} = J_z = J$ is therefore **$V = 2t$** — which is simultaneously the critical interaction strength at which the chain opens a charge-density-wave gap.
This is the one interaction strength where the Bethe ansatz hands us a closed-form energy, established for the Heisenberg chain by [Bethe (1931)](https://doi.org/10.1007/BF01341708) and extended to the anisotropic chain by [Yang and Yang (1966)](https://doi.org/10.1103/PhysRev.150.321):

$$
\frac{e_0}{J} = \frac{1}{4} - \ln 2 = -0.4431471805599\ldots
$$

quoted per bond in the thermodynamic limit, the convention used in [DMRG-02](../dmrg02) and throughout [DMRG-03](../dmrg03).
The DMRG algorithm itself is due to [White (1992)](https://doi.org/10.1103/PhysRevLett.69.2863).

## Boundary conditions

Open boundaries, as in every other module of this series, and for the usual reason: DMRG on a ring must carry entanglement across two cuts rather than one, and the bond dimension needed for a given accuracy grows sharply as a result.
The results below reach $L=128$ at $D=300$; a ring needs $D=600$ to manage $L=32$.

Open boundaries do cost something in the comparison, and it is worth being explicit about what.
Expanding the interaction with $S^z = n - \tfrac12$:

$$
J_z\sum_{\langle ij\rangle} S^z_iS^z_j = J_z\sum_{\langle ij\rangle} n_in_j \;-\; \frac{J_z}{2}\sum_i z_i n_i \;+\; \frac{J_z N_b}{4} ,
$$

where $z_i$ counts the bonds touching site $i$ and $N_b = L-1$.
In the bulk $z_i = 2$ and the middle term is $-J_z\hat N$, a constant at fixed filling.
At the two ends $z_i = 1$, leaving a boundary field $\tfrac{J_z}{2}(n_1 + n_L)$ that ALPS's uniform `mu` cannot represent.

This is a *surface* term: it leaves the bulk energy density untouched and contributes at order $1/L$.
That does not make it harmless.
It costs a full order in the finite-size scaling, and the cost is severe.
A ring has $z_i = 2$ everywhere, no surface at all, and its leading correction is the conformal $1/L^2$; the open chain converges only as $1/L$.
Measured against the same Bethe ansatz value, at equal length:

| $L$ | ring, $\|e_0 - e_\infty\|$ | open chain, $\|e_0 - e_\infty\|$ | ratio |
|---|---|---|---|
| 16 | $3.25\times10^{-3}$ | $6.07\times10^{-2}$ | 19× |
| 24 | $1.44\times10^{-3}$ | $4.00\times10^{-2}$ | 28× |
| 32 | $8.07\times10^{-4}$ | $2.99\times10^{-2}$ | 37× |

The ratio *grows* with $L$, as two different powers must.
Reaching the raw accuracy of a $32$-site ring would take an open chain of roughly $1200$ sites.

The benchmark survives this for two reasons, and it is worth being clear that the extrapolation is doing the work, not the raw data.
First, the $1/L$ form is known in advance, so the surface term can be fitted out rather than waited out.
Second, open boundaries are cheap enough to reach $L=128$ at $D=300$, where a ring needs $D=600$ to manage $L=32$ — so the fit has a long, clean lever arm to work with.
The extrapolated bulk values end up comparable either way ($4.9\times10^{-6}$ open, $3.1\times10^{-6}$ ring), but only because the open chain compensates in length for what it gives up in convergence order.

## Parameters

With $J = 1$, so $t = J/2$, $V = J$, $\mu = J$:

| Parameter | Meaning | Value |
|---|---|---|
| `LATTICE` | built-in open chain | `open chain lattice` |
| `MODEL` | see [Choice of method](#choice-of-method) | `hardcore boson` |
| `L` | chain length | 16, 24, 32, 48, 64, 96, 128 |
| `CONSERVED_QUANTUMNUMBERS` | quantum numbers held fixed | `N` |
| `N_total` | particle-number sector; $L/2$ is half filling $\Leftrightarrow S^z_{\text{tot}} = 0$ | $L/2$ |
| `t` | hopping, $=J_{xy}/2$ | 0.5 |
| `V` | nearest-neighbor repulsion, $=J_z$; note $V = 2t$ | 1 |
| `mu` | chemical potential, $=J_z$, cancelling the $-J_z\hat N$ term | 1 |
| `SWEEPS` | finite-size sweeps | 8 |
| `NUMBER_EIGENVALUES` | eigenstates requested | 1 |
| `MAXSTATES` | bond dimension $D$ | 300 |

There is no `Sz_total` anywhere: a spinless fermion has no spin to project, and the sector is fixed by `N_total` instead.
That substitution is the parameter-file face of $\hat S^z_{\text{tot}} = \hat N - L/2$ from [DMRG-07](dmrg07).

## Parameter file

```
LATTICE="open chain lattice"
MODEL="hardcore boson"
CONSERVED_QUANTUMNUMBERS="N"
N_total=64
t=0.5
V=1
mu=1
L=128
NUMBER_EIGENVALUES=1
{SWEEPS=8; MAXSTATES=300}
```

## Lattice

An open chain of $L$ sites with $L-1$ bonds, every site carrying $-\mu\, n_i$ and every bond the same $t$ and $V$:

```
   -mu       -mu       -mu                       -mu       -mu
    o---------o---------o------- ... -------------o---------o
    1         2         3                        L-1        L
       t, V      t, V         t, V         t, V

    ^                                                       ^
    z = 1                                                   z = 1     <- boundary field lives here
              z = 2 everywhere in between
```

The two end sites touch one bond instead of two, which is the origin of the surface term discussed above.
`open chain lattice` is built in, so no lattice file is needed — see the [ALPS lattice library](../../../documentation/intro/latticehowtos).

## Choice of method

DMRG reaches chain lengths far past exact diagonalization: already at $L=32$ the half-filled sector holds $\binom{32}{16}\approx6.0\times10^{8}$ states, and the runs below go to $L=128$.
With open boundaries a bond dimension of $D=300$ is enough across that whole range, because the chain has a single cut to carry entanglement across.
At $L=16$ the result reproduces exact diagonalization to $4\times10^{-15}$.

**On the model name.**
The parameter file sets `MODEL="hardcore boson"`, not `MODEL="spinless fermions"`.
Running the fermionic model through the legacy `dmrg` binary returns energies far *below* the exact ground state — variationally impossible, so the matrix being diagonalized is not the intended Hamiltonian.
At $L=8$, $N=4$, $V=0$, where the exact answer is $-4.758770483$:

| Model | `sparsediag` | `dmrg` |
|---|---|---|
| `spinless fermions` | $-4.7587704831436346$ | $-467.3$ |
| `hardcore boson` | $-4.7587704831436346$ | $-4.7587704831436337$ |

`sparsediag` handles the fermionic model correctly, so the model definition is sound and the fault lies in `dmrg`.
The hard-core boson form is exactly the XXZ chain under the local Matsubara-Matsuda mapping, which needs no strings and holds on any lattice, so nothing is lost by using it.

## Running the simulation

```
parameter2xml parm_chain
dmrg --write-xml parm_chain.in.xml
```

The script <a class="alps-download" href="../run_bethe_ansatz.py" data-filename="run_bethe_ansatz.py" target="_blank" rel="noopener">`run_ground_state.py`</a> sweeps the whole length series, converts each energy to spin units, and performs the extrapolation:

```
python3 run_bethe_ansatz.py --lengths 16 24 32 48 64 96 128 --maxstates 300
```

Pass `--alps-bin /path/to/alps/bin` if the ALPS executables are not on your `PATH`.

## Results

Each DMRG energy is converted to spin units by adding the constant derived above, $E_{\text{XXZ}} = E_{\text{hcb}} + J_z(L-1)/4$, and divided by the $L-1$ bonds:

| $L$ | $E$ (hardcore boson) | $E$ (XXZ) | $e_0 = E/(L-1)$ | $e_0 - (1/4-\ln 2)$ |
|---|---|---|---|---|
| 16 | $-11.3074087080$ | $-7.5574087080$ | $-0.503827247202$ | $-6.07\times10^{-2}$ |
| 24 | $-16.8632093523$ | $-11.1132093523$ | $-0.483183015316$ | $-4.00\times10^{-2}$ |
| 32 | $-22.4142204664$ | $-14.6642204664$ | $-0.473039369885$ | $-2.99\times10^{-2}$ |
| 48 | $-33.5108427370$ | $-21.7608427370$ | $-0.462996653979$ | $-1.98\times10^{-2}$ |
| 64 | $-44.6045271479$ | $-28.8545271479$ | $-0.458008367427$ | $-1.49\times10^{-2}$ |
| 96 | $-66.7887264214$ | $-43.0387264214$ | $-0.453039225488$ | $-9.89\times10^{-3}$ |
| 128 | $-88.9712527981$ | $-57.2212527981$ | $-0.450561045654$ | $-7.41\times10^{-3}$ |

No single length is close to the Bethe ansatz value — even at $L=128$ the energy is still $7\times10^{-3}$ away, and the gap shrinks only as $1/L$.
That slow approach is the surface energy discussed above, and it is the dominant error in this calculation by four orders of magnitude: the DMRG truncation error at these bond dimensions is around $10^{-14}$, while the finite-size deviation is $10^{-2}$.
Nothing is gained here by pushing $D$ higher; everything depends on the extrapolation.
Note how cleanly the last column halves as $L$ doubles: $-1.49\times10^{-2}$ at $L=64$ against $-7.41\times10^{-3}$ at $L=128$.
That is the signature of a pure $1/L$ surface term rather than a bulk error.

Fitting $e_0(L) = a + b/L + c/L^2$ to the three longest chains gives:

$$
a = -0.4431520707 \quad\text{against}\quad \tfrac14 - \ln 2 = -0.4431471806 ,
$$

a difference of $4.9\times10^{-6}$, with a surface coefficient:

$$
b = -0.945895 .
$$

The bulk energy is recovered to six digits from data whose raw finite-size error is four orders of magnitude larger.
The residual is not DMRG truncation error — at $L=16$ the energy matched exact diagonalization to $4\times10^{-15}$ — but the logarithmic corrections peculiar to the isotropic point, which decay more slowly than any power and make $\Delta=1$ the hardest place on the XXZ line to extrapolate.

## Summary and outlook

Tuning the fermion interaction to $V = 2t$ puts the chain at the isotropic Heisenberg point, where the Bethe ansatz supplies an exact energy.
Open-boundary DMRG up to $L=128$, extrapolated against a $1/L$ surface term, reproduces the bulk value $1/4-\ln 2$ to $4.9\times10^{-6}$.

1. Add a logarithmic correction to the fit, $e_0(L) = a + b/L + c/(L\ln^3 L)$. How much of the $4.9\times10^{-6}$ residual does it absorb?
2. Move off the isotropic point to $V = t$ ($\Delta = 1/2$), still inside the gapless phase. The Bethe ansatz energy is available for all $|\Delta|<1$ — does the extrapolation converge faster once the logarithmic corrections are gone?
3. Repeat at $V = 3t$ ($\Delta = 3/2$), inside the gapped CDW phase. How does the finite-size scaling change once the chain is no longer critical?
4. Measure the surface energy directly. The fitted $b$ should match $E_0(L) - L\,e_0(\infty)$ as $L\to\infty$ — check that it does, and see how much of it comes from the boundary field rather than the open ends themselves.
