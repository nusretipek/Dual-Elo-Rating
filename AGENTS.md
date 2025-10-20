# Repository Guidelines

## Project Structure & Module Organization
- `Dual Elo/src` hosts the C++17 implementation; headers live in `Dual Elo/include`; release binaries `DualEloRating` and `DualEloRatingWindows.exe` sit beside source for quick CLI access.
- `DomArchive/Data` and `Simulation/Data` store CSV interaction logs; corresponding `Results` folders capture stdout from batch runs.
- `Simulation/Code` delivers Python generators (`mixtureDataGeneration.py`, etc.) and plotting helpers; confirm new scripts declare dependencies in `Simulation/Code/requirements.txt`.

## Build, Test, and Development Commands
- Build locally on Linux/macOS: `g++ src/*.cpp -o DualEloRating -ldlib -lpthread -Iinclude -std=c++17 -O2 -Wall` from `Dual Elo`; update flags only when new libs are required.
- Windows cross-compile (MinGW): `x86_64-w64-mingw32-g++-posix src/*.cpp -o DualEloRatingWindows.exe -L<dlib_path> -ldlib -static-libgcc -static-libstdc++ -static -lwinpthread -I<dlib_path>/dlib -I<dlib_path>/include -std=c++17 -flto -O2 -Wall`.
- Inspect CLI usage: `./DualEloRating -h`. Batch-run archival datasets: `bash DomArchive/runDomArchive.sh`; simulations: `bash Simulation/runExperiments.sh`.
- Python tooling: `pip install -r Simulation/Code/requirements.txt`; run generators with `python Simulation/Code/mixtureDataGeneration.py`.

## Coding Style & Naming Conventions
- Keep C++ to C++17, 4-space indents, snake_case filenames, lowerCamelCase helpers (`mergedIndices`), and include guards (`#ifndef CALCULATION_H`). Prefer `<vector>` plus STL algorithms over raw arrays.
- Python scripts mix CamelCase domain helpers (`GetHierarchy`) with snake_case modules; follow the existing file pattern and comment non-obvious math.
- Log CLI flags at the top of new shell scripts; use `set -euo pipefail` when extending them.
- User-visible logs should describe parameters as `k(g)` and `k(c)`; keep internal identifiers as-is unless the interface changes.

## Testing Guidelines
- No automated suite exists yet; validate changes by rerunning `./DualEloRating -f sample.csv -opt 2 -n 30 -t 10 -v 2` on both archival and simulated datasets.
- When adjusting optimizers, compare `Results/*.txt` before/after and retain timing deltas in PR notes.
- For Python data generators, seed reproducibility via `numpy.random.seed(...)` and refresh the matching CSV plus TXT outputs.

## Commit & Pull Request Guidelines
- Match history's concise, imperative subject lines (`Update runExperiments.sh`); keep under 72 characters and explain the change.
- In PRs, provide: 1) short summary of behaviour change, 2) datasets or commands used for validation, 3) linked issues, and 4) screenshots when plot outputs change.

## Data & Reproducibility Tips
- Keep large CSVs out of version control; document provenance in README updates and store derived artefacts in the appropriate `Results` folder.
- When sharing new binaries, note compiler, flags, and target OS so the release pair stays aligned.

## System
- When editing code, always read the current file content fully.
- Never revert or modify lines that differ from Codex's last generation.
- Assume user-edited lines are intentional and correct.
