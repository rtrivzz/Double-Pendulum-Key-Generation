# MPNG: Multi Pendulum Based Random Number Generator

**A Novel Approach to Random Key Generation Using Chaotic Double Pendulum Dynamics**

[![Paper](https://img.shields.io/badge/IEEE-ICCCNP%202025-blue)](https://doi.org/10.1109/ICCCNP63914.2025.11233414)
---

## Abstract

This repository provides the reference implementation of **MPNG (Multi Pendulum based Random Number Generator)**, a cryptographic key generation framework that exploits the chaotic dynamics of double pendulum systems. The proposed system digitally simulates ten double pendulums instantiated with randomized physical parameters, extracts their angular state into a shared queue, and processes the resulting entropy stream through XOR decorrelation, circulant matrix randomness extraction, and MD5 hashing to yield **128-bit cryptographic keys**.

The generated keys satisfy the full **NIST Statistical Test Suite (SP 800-22)**, with results that match or exceed those of Python's `secrets` library — a widely adopted cryptographic-grade PRNG — across multiple statistical measures.

**Published at:** *2025 IEEE International Conference on Compute, Control, Network & Photonics (ICCCNP)*  
**DOI:** [10.1109/ICCCNP63914.2025.11233414](https://doi.org/10.1109/ICCCNP63914.2025.11233414)

**Authors:** John Tony, Pratik Senapati, Raghav Trivedi, Ramani Selvanambi\* — Vellore Institute of Technology, India

---

## Table of Contents

1. [Motivation](#motivation)
2. [System Architecture](#system-architecture)
3. [Mathematical Foundation](#mathematical-foundation)
4. [Getting Started](#getting-started)
5. [NIST Statistical Test Results](#nist-statistical-test-results)
6. [Analysis and Evaluation](#analysis-and-evaluation)
7. [Design Rationale](#design-rationale)
8. [Practical Applications](#practical-applications)
9. [Repository Structure](#repository-structure)
10. [Citation](#citation)
11. [Future Directions](#future-directions)
12. [Contact](#contact)
13. [License](#license)

---

## Motivation

Conventional pseudorandom number generators (PRNGs) are inherently deterministic: exposure of the underlying seed or algorithm renders their output reproducible and cryptographically compromised. The double pendulum — a simple mechanical system of two pendulums coupled end-to-end — is governed by non-linear differential equations that exhibit extreme sensitivity to initial conditions. Infinitesimal perturbations in starting parameters (mass, length, angle, angular velocity) produce rapidly diverging trajectories, a property formalized by positive Lyapunov exponents.

This characteristic makes the double pendulum an entropy-rich source whose evolution is, in practice, computationally infeasible to predict without exact knowledge of the initial state. MPNG leverages this property to construct a key generation pipeline grounded in deterministic physical laws yet resistant to the predictability inherent in algorithmic PRNGs.

---

## System Architecture

The MPNG pipeline consists of six sequential stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                  10 Double Pendulums                            │
│         (randomized l₁, l₂, m₁, m₂, g, θ₁, θ₂, θ̇₁, θ̇₂)       │
└──────────────────────┬──────────────────────────────────────────┘
                       │  θ values computed at each timestep
                       ▼
              ┌─────────────────┐
              │   Shared Queue  │
              └────────┬────────┘
                       │  Dequeue two values
                       ▼
              ┌─────────────────┐
              │  XOR Operation  │
              └────────┬────────┘
                       │
                       ▼
            ┌───────────────────┐
            │ Circulant Matrix  │
            │ Randomness        │
            │ Extractor         │
            └────────┬──────────┘
                     │  128-bit intermediate
                     ▼
              ┌─────────────────┐
              │   MD5 Hashing   │
              └────────┬────────┘
                       │
                       ▼
            ┌───────────────────┐
            │ Circulant Matrix  │
            │ Extractor (2nd)   │
            └────────┬──────────┘
                     │
                     ▼
           ┌────────────────────┐
           │  128-bit Random    │
           │  Cryptographic Key │
           └────────────────────┘
```

**Stage 1 — Simulation.** Ten double pendulums are instantiated with randomized physical parameters: string lengths (*l*₁, *l*₂), bob masses (*m*₁, *m*₂), gravitational acceleration (*g*), initial angular positions (*θ*₁, *θ*₂), and initial angular velocities (*θ̇*₁, *θ̇*₂).

**Stage 2 — State Extraction.** At each timestep, the angular positions of every pendulum are computed by numerically integrating the Euler-Lagrange derived ODEs, and the resulting values are pushed to a shared FIFO queue.

**Stage 3 — XOR Decorrelation.** Two values are dequeued and combined via bitwise XOR to eliminate statistical correlations between paired bitstreams.

**Stage 4 — First Randomness Extraction.** The XOR output is passed through a circulant matrix extractor — a structured transformation where each row is a cyclic shift of the previous — to amplify entropy and suppress residual bias.

**Stage 5 — MD5 Hashing.** The resulting 128-bit intermediate value is hashed using the MD5 algorithm, providing uniform distribution and serving as a computational one-way function.

**Stage 6 — Second Randomness Extraction.** The hash digest undergoes a second pass through the circulant matrix extractor, yielding the final 128-bit cryptographic key.

---

## Mathematical Foundation

The motion of each double pendulum is derived from the **Euler-Lagrange formulation**, producing two coupled second-order ordinary differential equations (ODEs). For numerical integration, these are decomposed into four first-order ODEs over the following state variables:

| Symbol | Description |
|--------|-------------|
| *θ*₁, *θ*₂ | Angular positions of the upper and lower bobs |
| *θ̇*₁, *θ̇*₂ | Angular velocities |
| *l*₁, *l*₂ | String lengths |
| *m*₁, *m*₂ | Bob masses |
| *g* | Gravitational acceleration |

The system of ODEs is integrated at each timestep independently for all ten pendulums. The resulting angular position values constitute the raw entropy stream fed into the key generation pipeline.

---

## Getting Started

### Prerequisites

- Python 3.8 or later
- NumPy
- SciPy
- Matplotlib (for visualization and analysis plots)

### Installation

```bash
git clone https://github.com/rtrivzz/Double-Pendulum-Key-Generation.git
cd Double-Pendulum-Key-Generation
pip install -r requirements.txt
```

### Usage

```bash
# Run the MPNG key generation pipeline
python main.py

# Generate keys with custom parameters
python main.py --num_pendulums 10 --num_keys 100

# Execute NIST SP 800-22 statistical tests on generated bitstreams
python nist_tests.py

# Reproduce analysis plots (phase-space, bifurcation, trajectory, etc.)
python plots.py
```

---

## NIST Statistical Test Results

The MPNG system was evaluated using the complete **NIST SP 800-22** statistical test suite on **100 sequences of 1,000,000 bits each**. A p-value above 0.01 indicates the sequence is considered random; the Proportion column denotes the number of sequences (out of 100) that passed each test. Results are presented alongside Python's `secrets` library (a cryptographic-grade PRNG) and the historically flawed RANDU linear congruential generator:

| Statistical Test | RANDU | Python `secrets` | **MPNG (Ours)** |
|---|:---:|:---:|:---:|
| Frequency | 100/100 | 100/100 | **99/100** |
| Block Frequency | 0/100 | 100/100 | **98/100** |
| Cumulative Sums | 100/100 | 98/100 | **99/100** |
| Runs | 100/100 | 98/100 | **98/100** |
| Longest Run of Ones | 34/100 | 99/100 | **98/100** |
| Rank | 95/100 | 98/100 | **97/100** |
| DFT (FFT) | 0/100 | 94/100 | **96/100** |
| Non-Overlapping Templates | 59/118 | 148/148 | **146/148** |
| Overlapping Template | 0/100 | 100/100 | **97/100** |
| Maurer's Universal | 5/100 | 100/100 | **100/100** |
| Approximate Entropy | 0/100 | 100/100 | **99/100** |
| Random Excursions | 5/8 | 7/8 | **8/8** |
| Random Excursions Variant | 18/18 | 18/18 | **18/18** |
| Serial | 100/100 | 100/100 | **99/100** |
| Linear Complexity | 99/100 | 99/100 | **100/100** |

MPNG passes all 15 NIST tests and demonstrates a measurable advantage over Python's `secrets` on several metrics, including Discrete Fourier Transform, Random Excursions, Linear Complexity, and Maurer's Universal Statistical Test.

---

## Analysis and Evaluation

The repository includes scripts to reproduce all analytical results presented in the paper. A summary of each evaluation method follows.

### Scalability Analysis

The Approximate Entropy test from the NIST suite was executed on 100 bitstreams of 1,000,000 bits each, generated by systems ranging from 5 to 200 pendulums. The computed entropy values remain above the 0.01 significance threshold across all configurations, with no discernible correlation between pendulum count and randomness quality. This confirms that the system scales without degradation of its statistical properties.

### Phase-Space Plot

Angular position (*θ*₁) is plotted against angular velocity (*ż*₁) for multiple pendulums. The resulting trajectories are intricate and non-repeating, with overlapping paths confirming the presence of chaotic attractors — a defining characteristic of systems exhibiting deterministic chaos.

### Trajectory Plot

The time evolution of *θ*₁ and *θ*₂ is visualized for both nominal and slightly perturbed initial conditions. Minor perturbations produce rapidly diverging trajectories, directly demonstrating the sensitive dependence on initial conditions that underpins the system's entropy generation capability.

### Lyapunov Exponent

The mean Lyapunov exponent is computed across 20 distinct initial conditions by measuring the rate of separation of initially proximate trajectories over time. Consistently positive values with high variance confirm operation in the chaotic regime and quantify the exponential rate of trajectory divergence.

### Bifurcation Diagrams

Four bifurcation diagrams (*θ*₁, *θ*₂, *θ̇*₁, *θ̇*₂ plotted against driving force amplitude) reveal the classical transition from stable periodic motion at low driving forces to fully chaotic behavior at higher amplitudes. The progressive emergence of dense branching structures is a hallmark of non-linear dynamical systems.

### Poincaré Section

The Poincaré section samples the system state at discrete intervals. The wide scatter of points across the section space confirms the breadth of accessible states, reinforcing both the chaotic nature of the system and its suitability as an entropy source for cryptographic applications.

---

## Design Rationale

| Decision | Justification |
|----------|---------------|
| **10 pendulums** | Balances entropy diversity with computational efficiency; scalability analysis confirms no degradation up to 200 pendulums |
| **Shared FIFO queue** | Interleaves outputs from independent pendulums, disrupting temporal patterns inherent to any individual source |
| **XOR decorrelation** | Eliminates pairwise statistical dependencies between bitstreams drawn from the queue |
| **Circulant matrix extractor (applied twice)** | Structured cyclic-shift transformations uniformize the output distribution and suppress residual bias |
| **MD5 hashing** | Provides avalanche-effect mixing and acts as a one-way function between extraction stages |
| **128-bit output** | Standard symmetric key length, directly compatible with AES-128 and comparable ciphers |

---

## Practical Applications

The MPNG framework is applicable to a range of domains where high-quality, non-reproducible key material is required:

- **Secure communications** — Key generation for encrypted data transmission across energy grids, autonomous vehicle networks, and military communication systems.
- **Wireless sensor networks (WSNs)** — Lightweight key generation for secure node authentication and data transmission in resource-constrained, adversarial environments.
- **Financial systems** — Continuous generation of non-reproducible session keys for high-frequency trading platforms and decentralized finance (DeFi) protocols.
- **IoT security** — Runtime key refreshment for devices where key reuse and hardware-level attacks pose significant threats.
- **General-purpose cryptography** — Drop-in entropy source for any pipeline requiring cryptographically secure random number generation.

---

## Repository Structure

```
Double-Pendulum-Key-Generation/
├── main.py                  # Main MPNG key generation pipeline
├── pendulum.py              # Double pendulum simulation (ODE integration)
├── queue_manager.py         # Shared queue implementation
├── randomness_extractor.py  # Circulant matrix randomness extractor
├── key_generator.py         # XOR, hashing, and key assembly
├── nist_tests.py            # NIST SP 800-22 test execution
├── plots.py                 # Visualization and analysis scripts
├── requirements.txt         # Python dependencies
├── results/                 # Pre-computed results and figures
│   ├── nist_results/
│   ├── phase_space.png
│   ├── trajectory.png
│   ├── bifurcation_theta1.png
│   ├── bifurcation_theta2.png
│   ├── lyapunov.png
│   └── poincare.png
└── README.md
```

> **Note:** The directory listing above is representative. Consult the repository contents for exact filenames and organization.


---

## Future Directions

- **Three-dimensional pendulum simulation** using hardware accelerators to expand the accessible state space and increase entropy throughput.
- **Extended statistical evaluation** beyond NIST STS, incorporating additional test suites such as Dieharder and TestU01.
- **End-to-end cryptosystem integration** — embedding MPNG into lightweight, performant encryption pipelines suitable for deployment across heterogeneous environments.
- **FPGA-based hardware implementation** for real-time key generation, building on prior work with sensor-seeded double pendulum systems.
- **Improved entropy extraction** — investigating alternative extraction methods to maximize bitrate from chaos-based sources.
