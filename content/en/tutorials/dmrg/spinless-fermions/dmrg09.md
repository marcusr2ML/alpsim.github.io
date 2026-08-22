---
title: DMRG-9 Boundary Conditions
weight: 4
math: true
toc: true
---

Every simulation so far in this series has used an open chain, justified in passing as the geometry DMRG handles best. This module makes that choice the subject rather than the assumption, and puts a price on it.

Open and periodic boundaries give different answers at finite $L$, converge to the thermodynamic limit at different rates, and fail differently when the extrapolation is done carelessly. To measure any of that we need a known target, so we work at the one interaction strength where the Bethe ansatz supplies an exact bulk energy — $V = 2t$, the isotropic Heisenberg point — and compare the two geometries against it.

## The reference point

The spinless fermion chain is:

$$
H = -t\sum_{i}\big(c^\dagger_i c_{i+1} + c^\dagger_{i+1} c_i\big) \;+\; V\sum_{i} n_i n_{i+1} \;-\; \mu\sum_{i} n_i ,
$$

with $n_i = c^\dagger_i c_i \in \{0,1\}$, run in the `hardcore boson` form established in [DMRG-09](../dmrg08).
Substituting $S^z_i = n_i - \tfrac12$ and the Jordan-Wigner strings of [DMRG-07](../dmrg07) into the XXZ chain:

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

quoted per bond in the thermodynamic limit, the convention used in [DMRG-02](../../dmrg02) and throughout [DMRG-03](../../dmrg03).
The DMRG algorithm itself is due to [White (1992)](https://doi.org/10.1103/PhysRevLett.69.2863).

Note that the ring is a genuinely different model here, not just a different lattice: as [DMRG-09](../dmrg08) noted, periodic boundaries leave a surviving Jordan-Wigner string, so `hardcore boson` on a ring is the XXZ chain but no longer the spinless-fermion chain. The comparison below is between two boundary conditions on the *spin* problem, which is what the Bethe ansatz value refers to.

## Where the surface term comes from

Expanding the interaction with $S^z = n - \tfrac12$:

$$
J_z\sum_{\langle ij\rangle} S^z_iS^z_j = J_z\sum_{\langle ij\rangle} n_in_j \;-\; \frac{J_z}{2}\sum_i z_i n_i \;+\; \frac{J_z N_b}{4} ,
$$

where $z_i$ counts the bonds touching site $i$ and $N_b$ is the number of bonds.
In the bulk $z_i = 2$ and the middle term is $-J_z\hat N$, a constant at fixed filling.

This is where the two geometries part company.
A ring has $z_i = 2$ everywhere and $N_b = L$: the middle term is a constant outright, and there is no surface at all.
An open chain has $N_b = L-1$ and $z_i = 1$ at the two ends, leaving a boundary field $\tfrac{J_z}{2}(n_1 + n_L)$ that ALPS's uniform `mu` cannot represent.

This is a *surface* term: it leaves the bulk energy density untouched and contributes at order $1/L$.
That does not make it harmless.
It costs a full order in the finite-size scaling, and the cost is severe.
The ring's leading correction is the conformal $1/L^2$; the open chain converges only as $1/L$.
Measured against the same Bethe ansatz value, at equal length:

| $L$ | ring, $\|e_0 - e_\infty\|$ | open chain, $\|e_0 - e_\infty\|$ | ratio |
|---|---|---|---|
| 16 | $3.25\times10^{-3}$ | $6.07\times10^{-2}$ | 19× |
| 24 | $1.44\times10^{-3}$ | $4.00\times10^{-2}$ | 28× |
| 32 | $8.07\times10^{-4}$ | $2.99\times10^{-2}$ | 37× |

The ratio *grows* with $L$, as two different powers must.
Reaching the raw accuracy of a $32$-site ring would take an open chain of roughly $1200$ sites.

## The cost of a ring

That table would seem to settle the matter in favor of periodic boundaries, and it does not, because it measures only one of the two costs involved.

DMRG on a ring must carry entanglement across two cuts rather than one, and the bond dimension needed for a given accuracy grows sharply as a result: the results below reach $L=128$ at $D=300$ with open boundaries, whereas a ring needs $D=600$ to manage $L=32$.
The two effects pull against each other — the ring converges in $L$ two orders faster, the open chain reaches lengths the ring cannot — and which one wins depends on whether you can fit the surface term out.

Here we can, for two reasons, and it is worth being clear that the extrapolation is doing the work, not the raw data.
First, the $1/L$ form is known in advance, so the surface term can be fitted out rather than waited out.
Second, open boundaries are cheap enough to reach $L=128$ at $D=300$, so the fit has a long, clean lever arm to work with.
The extrapolated bulk values end up comparable either way ($4.9\times10^{-6}$ open, $3.1\times10^{-6}$ ring), but only because the open chain compensates in length for what it gives up in convergence order — and, as [the closing section](#how-much-the-surface-term-really-costs) shows, only because the correct fit form was known going in.

## Parameters

With $J = 1$, so $t = J/2$, $V = J$, $\mu = J$:

| Parameter | Meaning | Value |
|---|---|---|
| `LATTICE` | the boundary condition under study | `open chain lattice` / `chain lattice` |
| `MODEL` | the boson form, established in [DMRG-09](../dmrg08) | `hardcore boson` |
| `L` | chain length | 16, 24, 32, 48, 64, 96, 128 (open); 16, 24, 32 (ring) |
| `CONSERVED_QUANTUMNUMBERS` | quantum numbers held fixed | `N` |
| `N_total` | particle-number sector; $L/2$ is half filling $\Leftrightarrow S^z_{\text{tot}} = 0$ | $L/2$ |
| `t` | hopping, $=J_{xy}/2$ | 0.5 |
| `V` | nearest-neighbor repulsion, $=J_z$; note $V = 2t$ | 1 |
| `mu` | chemical potential, $=J_z$, cancelling the $-J_z\hat N$ term | 1 |
| `SWEEPS` | finite-size sweeps | 8 |
| `NUMBER_EIGENVALUES` | eigenstates requested | 1 |
| `MAXSTATES` | bond dimension $D$ | 300 (open); 600 (ring) |

The only parameter that distinguishes the two runs is `LATTICE`; `MAXSTATES` then has to follow, for the entanglement reason above.

There is no `Sz_total` anywhere: a spinless fermion has no spin to project, and the sector is fixed by `N_total` instead.
That substitution is the parameter-file face of $\hat S^z_{\text{tot}} = \hat N - L/2$ from [DMRG-07](../dmrg07).

## Parameter files

The open chain, at the longest length of the series:

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

The ring, at the longest length it can reach for the same effort:

```
LATTICE="chain lattice"
MODEL="hardcore boson"
CONSERVED_QUANTUMNUMBERS="N"
N_total=16
t=0.5
V=1
mu=1
L=32
NUMBER_EIGENVALUES=1
{SWEEPS=8; MAXSTATES=600}
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

The two end sites touch one bond instead of two, which is the origin of the surface term.
The ring closes that gap, adding an $L$-th bond and making every site equivalent:

```
        t, V      t, V         t, V         t, V
    o---------o---------o------- ... -------------o
    |  -mu       -mu       -mu                -mu |
    1         2         3                         L
    |                  t, V                       |
    +---------------------------------------------+

    z = 2 everywhere, no surface, one extra cut for DMRG to carry
```

Both `open chain lattice` and `chain lattice` are built in, so no lattice file is needed — see the [ALPS lattice library](../../../../documentation/intro/latticehowtos).

## Choice of method

DMRG reaches chain lengths far past exact diagonalization: already at $L=32$ the half-filled sector holds $\binom{32}{16}\approx6.0\times10^{8}$ states, and the runs below go to $L=128$.
With open boundaries a bond dimension of $D=300$ is enough across that whole range, because the chain has a single cut to carry entanglement across.
At $L=16$ the result reproduces exact diagonalization to $4\times10^{-15}$, which matters for the argument below: it means every discrepancy in the tables is a boundary effect and not a truncation error.

The ring is run in the same `hardcore boson` form for the reason given in [DMRG-09](../dmrg08) — the fermionic model is not usable with the legacy `dmrg` binary — and on a ring that form is the XXZ chain rather than the fermion chain, which is the comparison intended here.

## Running the simulation

```
parameter2xml parm_chain
dmrg --write-xml parm_chain.in.xml
```

The script <a class="alps-download" href="../run_bethe_ansatz.py" data-filename="run_bethe_ansatz.py" target="_blank" rel="noopener">`run_bethe_ansatz.py`</a> sweeps the whole length series, converts each energy to spin units, and performs the extrapolation:

```
python3 run_bethe_ansatz.py --lengths 16 24 32 48 64 96 128 --maxstates 300
```

Pass `--alps-bin /path/to/alps/bin` if the ALPS executables are not on your `PATH`.

## Results

Each DMRG energy is converted to spin units by adding the constant derived above, $E_{\text{XXZ}} = E_{\text{hcb}} + J_z N_b/4$, and divided by the number of bonds — $N_b = L-1$ on the open chain, $N_b = L$ on the ring. The open-chain series:

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
That slow approach is the surface energy, and it is the dominant error in this calculation by four orders of magnitude: the DMRG truncation error at these bond dimensions is around $10^{-14}$, while the finite-size deviation is $10^{-2}$.
Nothing is gained here by pushing $D$ higher; everything depends on the extrapolation.
Note how cleanly the last column halves as $L$ doubles: $-1.49\times10^{-2}$ at $L=64$ against $-7.41\times10^{-3}$ at $L=128$.
That is the signature of a pure $1/L$ surface term rather than a bulk error — and the ring column of the earlier table, which falls by a factor of four rather than two over the same doubling, is the signature of $1/L^2$.

Fitting $e_0(L) = a + b/L + c/L^2$ to the three longest open chains gives:

$$
a = -0.4431520707 \quad\text{against}\quad \tfrac14 - \ln 2 = -0.4431471806 ,
$$

a difference of $4.9\times10^{-6}$, with a surface coefficient:

$$
b = -0.945895 .
$$

The bulk energy is recovered to six digits from data whose raw finite-size error is four orders of magnitude larger.
The residual is not DMRG truncation error — at $L=16$ the energy matched exact diagonalization to $4\times10^{-15}$ — but the logarithmic corrections peculiar to the isotropic point, which decay more slowly than any power and make $\Delta=1$ the hardest place on the XXZ line to extrapolate.

## How much the surface term really costs

The extrapolated answer above is about as accurate as one obtained from rings, which invites the wrong conclusion — that the boundary term is bookkeeping.
It is not, but the cost is not where one might first look.

**It is not in the stability of the fit.**
Refitting over every choice of lengths, the extrapolated bulk value moves by:

| | spread in $a$ across fit windows |
|---|---|
| open chain, $a + b/L + c/L^2$, all 3-point windows | $1.70\times10^{-4}$ |
| ring, $a + b/L^2$, all 2-point windows | $1.45\times10^{-4}$ |

Essentially the same. Having a surface term to fit does not make the fit noticeably more fragile against which lengths you feed it.

**It is in the consequence of getting the fit form wrong.**
The two geometries are not equally forgiving:

| Data | Fit form used | Extrapolated $a$ | Error |
|---|---|---|---|
| open | $a + b/L + c/L^2$ (correct) | $-0.4431521$ | $4.9\times10^{-6}$ |
| open | $a + b/L^2$ (surface term omitted) | $-0.4473748$ | $4.2\times10^{-3}$ |
| ring | $a + b/L^2$ (correct) | $-0.4431440$ | $3.1\times10^{-6}$ |
| ring | $a + b/L + c/L^2$ (spurious surface term) | $-0.4431593$ | $1.2\times10^{-5}$ |

Omitting a surface term that is really there costs a factor of $850$.
Including one that is not there costs a factor of $4$.

That asymmetry is the real price of open boundaries.
On a ring, translational symmetry *guarantees* there is no surface contribution — the leading correction is the conformal $1/L^2$ and you cannot get the form wrong.
On an open chain the correct form is something you must know in advance and put in by hand.
Here we knew it, because we knew the answer we were extrapolating toward and could check.
In a calculation where the answer is not known ahead of time — which is the only kind worth doing — that assurance is absent, and the $4.2\times10^{-3}$ column is the size of the mistake available to anyone who assumes the conformal form without asking whether the geometry has a surface.

## Summary

Open and periodic boundaries are not interchangeable. The open chain carries a $1/L$ surface term from its two singly-coordinated end sites, converging an order slower than the ring's conformal $1/L^2$ — 37× worse at $L=32$, and widening. It is used anyway because a single entanglement cut buys $L=128$ at $D=300$ where a ring needs $D=600$ for $L=32$, and because a known $1/L$ form can be fitted out: extrapolated that way, open-boundary DMRG reproduces the bulk value $1/4-\ln 2$ to $4.9\times10^{-6}$. The asymmetry in the last table is the warning that comes with it — the fit form is an input on an open chain, and a guarantee only on a ring.

## Questions

1. Reproduce the ring column directly. Run `LATTICE="chain lattice"` at $L = 16, 24, 32$ with $D = 600$ and confirm both the energies and that $D=300$ is *not* enough — where does the ring's truncation error sit relative to the open chain's at equal $D$?
2. Measure the surface energy directly. The fitted $b$ should match $E_0(L) - L\,e_0(\infty)$ as $L\to\infty$ — check that it does, and see how much of it comes from the boundary field $\tfrac{J_z}{2}(n_1+n_L)$ rather than the missing bond itself.
3. Cancel the surface term instead of fitting it. Use the special-edge lattice of [DMRG-08](../dmrg07-simulations) to set $\mu_j = \tfrac{V}{2}z_j$ site by site, which removes the boundary field exactly. Does the open chain now converge as $1/L^2$, and how close does a two-point fit get?
4. Add a logarithmic correction to the fit, $e_0(L) = a + b/L + c/(L\ln^3 L)$. How much of the $4.9\times10^{-6}$ residual does it absorb, and does the ring benefit equally?
5. Repeat the boundary comparison off the isotropic point, at $V = t$ ($\Delta = 1/2$) inside the gapless phase and at $V = 3t$ ($\Delta = 3/2$) inside the gapped CDW phase. Once the chain is no longer critical the correlation length is finite — does the open-chain penalty survive?
