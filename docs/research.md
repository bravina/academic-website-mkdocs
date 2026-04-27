---
title: Research
description: Research themes and ongoing projects
---


My research sits at the intersection of precision top quark physics, quantum information science, and machine learning — all within the [ATLAS experiment](https://atlas.cern) at the [Large Hadron Collider](https://home.cern/science/accelerators/large-hadron-collider).
I am also interested in the future of particle physics, especially at the [FCC-ee](https://fcc.web.cern.ch/), for which I am studying simulation and reconstruction algorithms for tile calorimeters.

## Quantum information science at colliders

The top quark is unique among quarks: it decays before hadronising, so its spin information is directly accessible through the angular distributions of its decay products. This makes $t\bar{t}$ production a natural laboratory for probing quantum correlations at the highest energies.

I contributed to the [first observation of quantum entanglement in top quark pairs](https://doi.org/10.1038/s41586-024-07824-z), published in *Nature* in 2024 — the highest-energy observation of entanglement to date. Building on this, I am pursuing a broad programme of quantum information measurements at colliders, along several lines:

**Spin density matrix and quantum observables.** We need precise differential measurements of the $t\bar{t}$ spin density matrix that we can interpret in terms of quantum information observables: entanglement, quantum discord, quantum magic, etc. The aim is to characterise the full quantum state of the top quark pair as a function of kinematics.

**Hierarchy of quantum correlations.** In a [recent paper](https://arxiv.org/abs/2602.15115), we established the full hierarchy of quantum correlations in top quark pairs, from separable to Bell-correlated states, providing the most complete experimental characterisation of a two-qubit state at collider energies to date.

**Higgs sector.** Quantum information studies in the $H \to WW^*$ and $H \to ZZ^*$ processes would benefit from Monte Carlo simulations of the polarised final states, especially beyond leading-order accuracy. I am exploring these prospects with MadGraph and Sherpa. There is much to be done with such simulations, including also fundamental tests of the Standard Model (such as the _Goldstone Equivalence Theorem_).

**Community engagement.** These developments fed into a [community white paper](https://doi.org/10.1140/epjp/s13360-025-06752-9) submitted as input to the update of the European Strategy for Particle Physics, making the case for quantum information science as a core component of the future collider physics programme.

The precision tools developed in this programme played a central role in the [observation of a cross-section enhancement consistent with toponium formation](https://arxiv.org/abs/2601.11780), an unexpected discovery at the LHC.

## Top quark electroweak couplings

Rare processes such as $t\bar{t}Z$, $tZq$, $tWZ$, and $t\bar{t}\gamma$ directly probe the electroweak couplings of the top quark. I have led several ATLAS measurements of these processes, most recently the [legacy Run 2 $t\bar{t}Z$ analysis](https://doi.org/10.1007/JHEP07(2024)163), which includes the first measurement of spin correlations in $t\bar{t}Z$ and a comprehensive SMEFT interpretation of differential cross sections.

I also performed the first joint unfolding and EFT interpretation of two distinct top+X processes simultaneously, $t\bar{t}Z$ and $t\bar{t}\gamma$, in the [combined $t\bar{t}\gamma$ measurement](https://doi.org/10.1007/JHEP10(2024)191), demonstrating a coherent treatment of systematics and correlations across final states and yielding competitive limits on a large set of dimension-6 SMEFT operators.

Looking ahead, I contributed to the [HL-LHC physics projections](https://arxiv.org/abs/2504.00672) for the top quark sector on behalf of ATLAS and CMS, and to a [dedicated sensitivity study](https://cds.cern.ch/record/2927962) for $t\bar{t}\gamma$ and $t\bar{t}Z$ at the High-Luminosity LHC. I also prepared the [roadmap for future ATLAS+CMS combinations](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PUBNOTES/ATL-PHYS-PUB-2023-030/) of top+X results in the EFT framework. These efforts will define the legacy strategy for the HL-LHC and inform the precision top programme at future colliders.

## Machine learning & anomaly detection

As part of the [Dark Machines](https://darkmachines.org/) initiative, I contributed to a [large-scale benchmark](https://doi.org/10.21468/SciPostPhys.12.1.043) of anomaly detection algorithms for LHC collisions, testing hundreds of unsupervised models (auto-encoders, normalising flows, deep sets) on simulated datasets with the goal of enabling model-independent searches for new physics in LHC Run 3 data.

Beyond anomaly detection, I am actively investigating novel neural network architectures motivated directly by the physics of the final states I study. In particular, I am interested in Lorentz-equivariant architectures and in designing physically motivated objectives and loss functions for the reconstruction of challenging final states: semi-leptonic and di-leptonic $t\bar{t}$ (including neutrino momentum inference), $t\bar{t}+X$, and other multi-object topologies. Improved reconstruction is critical to achieving the precision goals of the quantum information and threshold measurements described above.

## Analysis software for Run 3

The physics results described on this page all rely on [TopCPToolkit](https://topcptoolkit.docs.cern.ch/), a modular analysis framework that I created and continue to develop. It provides a flexible, well-documented pipeline for producing analysis-ready ntuples and is now the most widely used analysis framework in the ATLAS Collaboration, supporting a wide range of measurements, searches, and calibration efforts in Run 3.

!!! tip "Get started with TopCPToolkit"
    Get the code [on Gitlab](https://gitlab.cern.ch/atlas/amg/software/TopCPToolkit) and check out our [documentation](https://topcptoolkit.docs.cern.ch/latest/)!
    You can cite us as
    {% raw %}
     ```tex
     @software{TopCPToolkit,
         author      = {{ATLAS Collaboration}},
         title       = {TopCPToolkit},
         publisher   = {Zenodo},
         doi         = {10.5281/zenodo.19683083},
         url         = {https://doi.org/10.5281/zenodo.19683083},
     }
     ```
     {% endraw %}

I am also developing [iTopCPToolkit](https://itopcptoolkit.web.cern.ch/), a web application that provides automation and AI-assisted analysis development tools to reduce time spent on routine coding and let physicists focus on physics. Because TopCPToolkit reads PHYSLITE directly, it is also well positioned to support analyses of [ATLAS Open Data](https://opendata.cern.ch/search?experiment=ATLAS), broadening access to LHC physics beyond the collaboration.
