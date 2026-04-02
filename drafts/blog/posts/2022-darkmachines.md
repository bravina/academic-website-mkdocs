---
date: 2022-01-15
categories:
  - Machine learning
---

# Dark Machines anomaly detection challenge published

![Dark Machines results](https://inspirehep.net/files/3b04b7a8ecb9c2b3dbdc31ef12f2b4e4){ .blog-hero }

The results of our community-wide anomaly detection challenge are out in [SciPost Physics](https://doi.org/10.21468/SciPostPhys.12.1.043). We benchmarked hundreds of unsupervised ML models on over 1 billion simulated LHC events.

<!-- more -->

The Dark Machines initiative brought together physicists and machine learning researchers to tackle a fundamental question: can we find new physics at the LHC without knowing what we're looking for?

We generated a large benchmark dataset corresponding to 10 fb$^{-1}$ of 13 TeV $pp$ collisions and tested a wide range of algorithms — auto-encoders, normalising flows, deep sets, variational approaches, and more — in realistic analysis environments.

## Key takeaways

- No single model dominates across all signal types.
- Ensemble approaches and normalising flows performed consistently well.
- The benchmark dataset and code are publicly available for future studies.

The benchmark data is available at [phenoMLdata.org](https://www.phenoMLdata.org) and the analysis code at [GitHub](https://github.com/bostdiek/DarkMachines-UnsupervisedChallenge).

**Links:** [arXiv:2105.14027](https://arxiv.org/abs/2105.14027) · [CERN Courier coverage](https://cerncourier.com/a/whats-in-the-box/)
