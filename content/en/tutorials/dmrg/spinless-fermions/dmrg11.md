---
title: DMRG-11 Particle-Number Sectors
weight: 5
math: true
toc: true
---

Every parameter file in this series has carried the line `CONSERVED_QUANTUMNUMBERS="N"`, and every one has then pinned a single value of `N_total` and moved on. This module makes the sector itself the variable: the same Hamiltonian, run in three different fixed-$N$ blocks, with the energy and the density profile of each read off side by side.

The three lowest blocks are chosen deliberately. They are the only ones on the whole ladder whose answers are known in closed form, which turns them from a physics calculation into a calibration: whatever DMRG returns here can be checked against arithmetic rather than against another simulation.

## Phenomena of interest

The particle number $\hat N = \sum_i \hat n_i$ commutes with the $t$–$V$ Hamiltonian, so $H$ is block diagonal in $N$ and each block can be diagonalised on its own. Declaring `N` as a conserved quantum number is what tells ALPS to build those blocks; `N_total` then selects one of them. Several `{ N_total=... }` blocks in one parameter file therefore run several independent DMRG calculations whose energies are directly comparable, because they are eigenvalues of one operator.

At the dilute end of the ladder the physics is stripped down to almost nothing, and that is the point:

- **$N=0$** is the empty chain. The block is one-dimensional, the state is the vacuum, and $E = 0$ exactly, for any $t$ and any $V$.
- **$N=1$** is one particle in a box. There is nothing for the interaction to act on — $V$ couples *pairs* of neighbouring sites — so the energy and the density profile are those of a free particle no matter how strong $V$ is. Both are known analytically.
- **$N=2$** is the first sector in which $V$ does anything at all. Two particles on an open chain is the smallest problem that is genuinely interacting, and the difference between its energy and the free-fermion value is the entire interaction energy of the chain.

That last point is the physical content of this module. The step from $N=1$ to $N=2$ is where a non-interacting problem becomes an interacting one, and both the energy shift and the rearrangement of the density can be measured cleanly, without a thermodynamic-limit extrapolation standing in the way.

In spin language the same three sectors sit at the bottom of the magnetisation ladder. With $S^z_i = \hat n_i - \tfrac12$ the dictionary of [DMRG-07](../dmrg07) gives $S^z_{\text{tot}} = N - L/2$, so for $L=32$ the sectors $N = 0, 1, 2$ are $S^z_{\text{tot}} = -16, -15, -14$: the fully polarised state, and the one- and two-magnon states built on top of it. Read that way, $\langle n_i \rangle$ is the *magnon density*, and the profiles below are magnon wavefunctions. This is the fermionic counterpart of the magnetisation sectors studied in [DMRG-05](../../dmrg05), with one difference worth keeping in mind: there the sectors were counted from the middle of the ladder and the interesting structure was at the chain edges, here they are counted from the bottom and the structure is in the bulk.

## The model

The $t$–$V$ chain of [DMRG-08](../dmrg08), on an open chain of $L$ sites, with no chemical potential:

$$
\hat H \;=\; -t\sum_{j=1}^{L-1}\Big(\hat c^{\dagger}_j \hat c_{j+1} + \hat c^{\dagger}_{j+1}\hat c_j\Big)
\;+\; V \sum_{j=1}^{L-1} \hat n_j\, \hat n_{j+1} .
$$

The model is integrable: through the [Jordan–Wigner transformation](https://doi.org/10.1007/BF01331938) it is the XXZ chain solved exactly by [Yang and Yang](https://doi.org/10.1103/PhysRev.150.321), and its critical phase is the standard lattice realisation of the [Luttinger liquid](https://doi.org/10.1088/0022-3719/14/19/010).

Setting $\mu = 0$ is deliberate. A chemical potential shifts every sector by $-\mu N$, which is exactly the term that would make energies from different $N$ incomparable; dropping it means the numbers in the table below can be subtracted from one another directly.

The interaction is run at $V = 2t$, the isotropic Heisenberg point used throughout this series ($J_{xy} = J_z$, see [DMRG-10](../dmrg10)), and at $V=0$ for the free reference.

### The exact answers

**$N=0$.** The vacuum $|0\rangle$ is annihilated by every term in $\hat H$, so $E_0(N{=}0) = 0$ and $\langle n_i \rangle = 0$ on every site.

**$N=1$.** With one particle the interaction term $V\hat n_j \hat n_{j+1}$ has no support at all, so the problem is a single particle hopping in a box of $L$ sites with hard walls. The eigenstates are standing waves,

$$
\varepsilon_n = -2t\,\cos\!\left(\frac{n\pi}{L+1}\right), \qquad n = 1,\dots,L ,
$$

so the ground state energy is $\varepsilon_1$ and the density profile is a half wavelength:

$$
E_0(N{=}1) = -2t\cos\!\frac{\pi}{L+1}, \qquad
\langle n_i \rangle = \frac{2}{L+1}\sin^2\!\frac{\pi i}{L+1} .
$$

Both are independent of $V$. This is the sharpest single check in the module: running $N=1$ at $V=0$ and at $V=2t$ must give *identical* numbers, and any difference is a bug rather than physics.

**$N=2$.** At $V=0$ the two particles fill the two lowest standing waves, $E_0 = \varepsilon_1 + \varepsilon_2$, and the density is the sum of the two, $\langle n_i \rangle = |\psi_1(i)|^2 + |\psi_2(i)|^2$ — a two-lobed profile with a dip in the middle, which is the hardcore constraint alone keeping the particles apart. At $V>0$ there is no closed form, but the sector holds only $\binom{L}{2}$ states and is exactly diagonalisable, so an exact reference is still available.

## Parameters

| Parameter | Meaning | Value |
|---|---|---|
| `LATTICE` | built-in open chain, no lattice file needed (see the [ALPS lattice library](../../../../documentation/intro/latticehowtos)) | `open chain lattice` |
| `MODEL` | hardcore-boson $t$–$V$ model, the usable form of the fermion chain (see [DMRG-09](../dmrg09)) | `hardcore boson` |
| `CONSERVED_QUANTUMNUMBERS` | quantum number held fixed; this is what builds the fixed-$N$ blocks | `N` |
| `N_total` | the block selected — one DMRG run per value | 0, 1, 2 |
| `L` | chain length | 32 |
| `t` | nearest-neighbour hopping amplitude | 1 |
| `V` | nearest-neighbour repulsion | 2 (isotropic point); 0 (free reference) |
| `mu` | chemical potential, omitted so sectors stay comparable | — |
| `SWEEPS` | number of DMRG finite-size sweeps | 6 |
| `NUMBER_EIGENVALUES` | eigenstates requested per sector | 1 |
| `MAXSTATES` | bond dimension $D$ kept after truncation | 100 |
| `MEASURE_LOCAL[...]` | site-resolved observable to record | `n` |

There is no `Sz_total` anywhere: a spinless fermion has no spin to project, and the sector is fixed by `N_total` instead — the parameter-file face of $S^z_{\text{tot}} = N - L/2$.

## Lattice

The built-in `open chain lattice` is all that is needed. Every site is equivalent and every bond carries the same $t$ and $V$:

```
      t,V     t,V     t,V                 t,V     t,V
  o-------o-------o-------o  . . .  o-------o-------o
  1       2       3       4         30      31      32

  every bond:  hopping t, interaction V
  every site:  no chemical potential (mu = 0)

  N particles distributed over these 32 sites; N is what N_total fixes
```

Open boundaries are the geometry DMRG converges on ([DMRG-01](../../dmrg01)), and they are what make the single-particle levels the clean $\cos(n\pi/(L+1))$ standing waves used as the reference above — on a ring they would be plane waves with a two-fold degeneracy, and the $N=2$ ground state would not be unique. No lattice file is required.

## Choice of method

The dilute sectors are tiny by the standards of this series:

| sector | $\dim \mathcal{H}_N = \binom{L}{N}$ at $L=32$ |
|---|---|
| $N=0$ | 1 |
| $N=1$ | 32 |
| $N=2$ | 496 |
| $N=16$ (half filling, for contrast) | $6.0\times10^{8}$ |

Six orders of magnitude separate $N=2$ from the half-filled sector that forced DMRG on us in [DMRG-08](../dmrg08). That inversion is what makes this module useful: because exact diagonalisation is instant here, `sparsediag` can be run on exactly the same parameter file and its answer used as ground truth for the DMRG one. Everything below — energies and density profiles alike — comes from `dmrg`; `sparsediag` only ever appears as the check. Each `dmrg` run takes a few seconds at $D=100$.

{{< callout type="info" >}}
The site-resolved measurement machinery in the `dmrg` application was reworked in 2026 (local observables are now accumulated as `dmtk::Term` objects rather than wrapped Hamiltonians). On builds predating that work, `MEASURE_LOCAL` returns a vector that is nonzero only on the two central sites and does not satisfy $\sum_i \langle n_i \rangle = N_{\text{total}}$. Energies are unaffected either way. If the sum rule below fails on your build, update ALPS and rebuild rather than chasing a convergence problem that is not there.
{{< /callout >}}

## Parameter files

The whole module is one parameter file. Each `{ ... }` line is one fixed-$N$ block, and the six blocks below cover both couplings, giving six independent runs from a single `dmrg` invocation — `parm_sectors`:

```
LATTICE="open chain lattice"
MODEL="hardcore boson"
CONSERVED_QUANTUMNUMBERS="N"
L=32
t=1
NUMBER_EIGENVALUES=1
SWEEPS=6
MAXSTATES=100
MEASURE_LOCAL[Local density]=n
{ V=2; N_total=0 }
{ V=2; N_total=1 }
{ V=2; N_total=2 }
{ V=0; N_total=0 }
{ V=0; N_total=1 }
{ V=0; N_total=2 }
```

or equivalently from Python, with `sectors.py`:

```python
import pyalps
parms = []
for V in [2, 0]:
    for N in [0, 1, 2]:
        parms.append( {
            'LATTICE'                   : 'open chain lattice',
            'MODEL'                     : 'hardcore boson',
            'CONSERVED_QUANTUMNUMBERS'  : 'N',
            'N_total'                   : N,
            'L'                         : 32,
            't'                         : 1,
            'V'                         : V,
            'SWEEPS'                    : 6,
            'NUMBER_EIGENVALUES'        : 1,
            'MAXSTATES'                 : 100,
            'MEASURE_LOCAL[Local density]' : 'n'
        } )
input_file = pyalps.writeInputFiles('parm_sectors',parms)
pyalps.runApplication('dmrg',input_file,writexml=True)
```

## Running the simulation

With the ALPS binaries on your `PATH`:

```bash
parameter2xml parm_sectors
dmrg --write-xml parm_sectors.in.xml
```

This produces six output files `parm_sectors.task1.out.xml` … `parm_sectors.task6.out.xml`, one per block, in the order the blocks appear in the file. Because the sectors are small, the very same input can be pushed through exact diagonalisation to obtain reference values:

```bash
sparsediag --write-xml parm_sectors.in.xml
```

The script <a class="alps-download" href="../run_number_sectors.py" data-filename="run_number_sectors.py" target="_blank" rel="noopener">`run_number_sectors.py`</a> runs the sectors, prints the tables below and draws the figure; `--check` adds the `sparsediag` column:

```bash
python3 run_number_sectors.py --L 32 --sectors 0 1 2 --check --plot sectors.png
```

Pass `--alps-bin /path/to/alps/bin` if the ALPS executables are not on your `PATH`.

## Evaluating the results

Reading the energies and profiles back:

```python
import numpy as np, matplotlib.pyplot as plt, pyalps

data = pyalps.loadEigenstateMeasurements(
    pyalps.getResultFiles(prefix='parm_sectors'))
for run in data:
    N = int(run[0].props['N_total'])
    V = float(run[0].props['V'])
    for s in run:
        if s.props['observable'] == 'Energy':
            print('V = %g, N = %d:  E = %.12f' % (V, N, s.y[0]))
        if s.props['observable'] == 'Local density' and V == 2:
            y = np.real(np.asarray(s.y).flatten())
            plt.plot(np.arange(1, len(y)+1), y, marker='o', ms=3,
                     label='$N = %d$' % N)
plt.xlabel('site $i$'); plt.ylabel(r'$\langle n_i \rangle$')
plt.legend(); plt.show()
```

A useful check on any of these runs is that $\sum_i \langle n_i \rangle$ recovers `N_total`; here it does so to about $5\times10^{-7}$, the accuracy of the measurement itself rather than of the energy. A gross failure of that sum rule means either an unconverged run or the outdated build noted above.

### Energies

$L = 32$, $t = 1$, $D = 100$, six sweeps:

| $V$ | $N$ | $\dim\mathcal{H}_N$ | $E_0$ (`dmrg`) | $E_0$ (`sparsediag`) | difference | $E_0$ free, exact |
|---|---|---|---|---|---|---|
| $2t$ | 0 | 1 | $0.000000000000$ | $0.000000000000$ | $0$ | $0$ |
| $2t$ | 1 | 32 | $-1.990943845146$ | $-1.990943845146$ | $4\times10^{-15}$ | $-1.990943845146$ |
| $2t$ | 2 | 496 | $-3.953402017692$ | $-3.953402017692$ | $6\times10^{-15}$ | $-3.954801239672$ |
| $0$ | 0 | 1 | $0.000000000000$ | $0.000000000000$ | $0$ | $0$ |
| $0$ | 1 | 32 | $-1.990943845146$ | $-1.990943845146$ | $2\times10^{-16}$ | $-1.990943845146$ |
| $0$ | 2 | 496 | $-3.954801239672$ | $-3.954801239672$ | $2\times10^{-15}$ | $-3.954801239672$ |

Three things are worth reading off this table.

**The blocks are genuinely independent.** Six runs came out of one file, and each converged to the ground state *of its own sector* rather than to the global ground state, which lies far below all of these at half filling ($E_0 \approx -22$, see [DMRG-08](../dmrg08)). Without `CONSERVED_QUANTUMNUMBERS="N"` there would be no blocks and no way to ask the question.

**$N=1$ does not know about $V$.** The two $N=1$ rows agree to $10^{-14}$ across a change of the interaction from $0$ to $2t$, and both reproduce $-2t\cos(\pi/33) = -1.990943845146$ to twelve digits. A nearest-neighbour interaction needs two particles, and the code reproduces that exactly rather than approximately.

**$N=2$ is where the interaction turns on.** The free value is $\varepsilon_1 + \varepsilon_2 = -3.954801239672$, and switching on $V=2t$ raises the energy to $-3.953402017692$:

$$
E_0(V{=}2t) - E_0(V{=}0) \;=\; +0.0013992220 .
$$

That number is the entire interaction energy of the chain in this sector. It is positive, as a repulsion must be, and it is small — about $10^{-3}$ of the kinetic energy — because two particles spread over 32 sites are rarely adjacent. It is also, importantly, not zero to within any tolerance that matters: DMRG resolves it against a background of $\sim 4$ with fourteen digits of agreement with exact diagonalisation.

### Density profiles

![Local density in the N=0, 1 and 2 particle-number sectors of a 32-site chain](/figs/dmrg/dmrg11_number_sectors.png)

**Figure 1.** Open chain, $L=32$, $t=1$, $D=100$, all data from `dmrg`. (a) $\langle n_i \rangle$ in the three particle-number sectors at $V=2t$, with the exact one-particle standing wave $\tfrac{2}{L+1}\sin^2\tfrac{\pi i}{L+1}$ drawn underneath in grey. (b) The $N=2$ profile at $V=0$ and $V=2t$ over the central region: the repulsion pushes weight out of the middle of the chain and into the two lobes.

The three sectors in panel (a) are exactly the three pictures the algebra predicts:

- $N=0$ is flat at zero. The block has a single state and there is nothing to measure.
- $N=1$ is one half wavelength, peaking at $\langle n_i \rangle = 0.0605$ in the middle and vanishing at the walls. Laid over the analytic $\tfrac{2}{L+1}\sin^2\tfrac{\pi i}{L+1}$, the two are indistinguishable — the largest deviation anywhere on the chain is $1.8\times10^{-7}$.
- $N=2$ has two lobes with a dip between them, the signature of the second standing wave $\psi_2$, which has a node at the chain centre. The two particles are already avoiding each other at $V=0$, purely because they are hardcore.

Panel (b) isolates what the interaction adds to that. Comparing $V=0$ with $V=2t$ in the same sector, the central density falls from $0.061016$ to $0.057045$ and the lobe maxima rise correspondingly, a rearrangement of at most $4.0\times10^{-3}$ per site. The particles were already kept apart by the hardcore constraint; $V$ widens the gap. Note that the total is conserved throughout — $\sum_i \langle n_i \rangle = 1.99999999$ in both runs — so every particle pushed out of the centre reappears in the lobes.

This is the same physics that becomes the charge-density-wave transition at $V > 2t$ once the chain is at half filling and there are enough particles for the avoidance to organise into a pattern. At $N=2$ it is visible in its simplest possible form: two particles, one dip, and an energy shift of $1.4\times10^{-3}$.

## Summary

Declaring `N` conserved turns one Hamiltonian into a ladder of independent blocks, and stacking `{ N_total=... }` lines in a parameter file runs as many of them as you like from a single invocation. In the three dilute blocks the answers are known in closed form, and DMRG reproduces them: $E=0$ in the vacuum, the exact standing-wave energy and profile at $N=1$ for any $V$ (to twelve and seven digits respectively), and at $N=2$ the first sector where the interaction acts at all — worth $+1.4\times10^{-3}$ in energy and a $4\times10^{-3}$ redistribution of the density.

## Questions

1. Continue up the ladder: add `{ V=2; N_total=3 }` and `{ V=2; N_total=4 }`. The interaction energy $E_0(V{=}2t) - E_0(V{=}0)$ grows with $N$ — does it grow like $N$, like $N^2$, or like something else, and what does that say about how often two particles are adjacent?
2. Build the chemical potential back in. The addition energy $\mu(N) = E_0(N) - E_0(N-1)$ is what it costs to put one more particle on the chain. Compute it for $N = 1, 2, 3$ and check that at $V=0$ it reproduces the single-particle levels $\varepsilon_N$ exactly.
3. Make $V$ attractive. Set $V = -2t$ at $N=2$: two particles now gain energy by sitting next to each other. Does the density profile develop a *peak* at the chain centre instead of a dip, and can you find the threshold $|V|$ at which a two-particle bound state forms?
4. Check the spin dictionary directly. Run the same three sectors as `MODEL="spin"` with `Sz_total` $= N - L/2$ at $J_{xy}=2t$, $J_z=V$, and confirm that the energies differ from the ones above only by the constant $J_z N_b/4$ derived in [DMRG-10](../dmrg10).
5. Push the sector until DMRG has to work. Repeat at $N = L/4$ and $N = L/2$ with $D = 20$ and $D = 100$: at which filling does the $D=20$ energy first fail to match `sparsediag`, and how does that compare with the Hilbert-space dimensions in the table above?
