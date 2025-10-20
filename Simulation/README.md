# Simulation

This folder contains simulated datasets, results, and code used to evaluate the Dual Elo rating.

## Folder Structure

### 1. Data

The `Data` folder contains interaction datasets in CSV format. Each file is structured as follows:

- **First Column**: Represents the winner of the interaction.
- **Second Column**: Represents the loser of the interaction.

The naming convention for these CSV files is: `dataset_type_alpha_index.csv`, where:

- `dataset_type` indicates the type of simulated dataset (sudden, mixture and null hypothesis).
- `alpha` is an alphabetical identifier.
- `index` is a numerical index that starts from 0.

**Note:** In the associated paper, the indices start from 1. To match the indices with the paper, simply add 1 to the file index.

### 2. Results

The `Results` folder contains the standard outputs (STDOUT) from the Dual Elo rating, saved as text files. These files are generated using:

- **Optimization Level**: 2
- **Verbosity**: 2

Each TXT file also includes:

- Execution time for each module.
- Overall execution time at the end.

> The simulation results provided here were generated with the Linux `DualEloRating` binary to ensure consistency with the published benchmarks.

### 3. Code

The `Code` folder contains library and scripts to:
- Generate simulated datasets using directed acyclic graphs (DAGs).
- Produce the figures used in the associated paper.
