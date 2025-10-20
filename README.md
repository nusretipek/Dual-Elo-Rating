# Dual Elo Rating

Elo rating and its variants are widely employed to characterize the social (dominance) hierarchies within animal groups. These ranking methods are considered the state-of-the-art for analyzing sequential dyadic agonistic interaction data. However, they have been criticized for adapting slowly to rare but abrupt and important changes in the dominance hierarchy. In this paper, we show that this delayed response can be overcome by making the update parameter of the Elo rating time-dependent. By distinguishing between two types of interactions, i.e. low-impact and high-impact interactions each with an associated update parameter, a simple parametrization of a time-dependent update parameter can be obtained. We refer to this innovation as Dual Elo. Building on Optimized Elo, we propose a computationally efficient maximum-likelihood-based algorithm to fit Dual Elo to an observed sequence of interactions. The result is an extension of Elo rating that can handle a mix of gradual and sudden changes in the hierarchy, leading to a model that is more responsive with more robust estimates of the temporal evolution of the Elo scores. An extensive evaluation of the Dual Elo rating on both simulated and publicly available datasets demonstrates its robustness, even when the observations of the outcomes of interactions are noisy.

## Repository Structure

### 1. Dual Elo Rating

This folder contains:

- **Source Code**: The C++ implementation of the Dual Elo rating.
- **Compiled Binaries**: Pre-compiled binaries for Linux, macOS, and Windows.

> We ship executables for every platform, but only the Linux build is thoroughly tested. Native MSVC (Windows) and Clang (macOS) builds can yield small numerical deltas because their standard libraries use different floating-point reductions. For reproducible results, run the Linux executable directly (or via WSL/Docker on other platforms).

### 2. DomArchive

This folder includes:

- **Publicly Available Datasets**: Sourced from the [DomArchive](https://github.com/DomArchive/DomArchive) repository.
- **Dual Elo Rating Results**: Results of applying the Dual Elo rating system to these datasets.

### 3. Simulation

This folder provides:

- **Python Code**: Scripts to generate simulated data.
- **Dual Elo Rating Results**: Results generated from the simulated data using the Dual-K Elo rating.
- **Plotting Scripts**: Code to generate the plots that are used in the paper.

For build instructions, CMake options, and compiler flags, refer to `Dual Elo/README.md`.

## Demo

You can try out the Dual Elo system via our online demo: [Dual Elo Demo](https://dual-elo-rating.streamlit.app).
Please note that, the demo does not come with any uptime or performance guarantee. For the best performance, we recommend compiling the source code provided in this repository.

![Demo](demo.gif)

## Cite This Work

**[Citation Here]**

## License

This code is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.html).
