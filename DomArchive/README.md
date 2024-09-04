# DomArchive

This folder contains datasets and results used to evaluate the Dual-K Elo rating, sourced and derived from the [DomArchive](https://github.com/DomArchive/DomArchive).

## Folder Structure

### 1. Data

The `Data` folder contains interaction datasets in CSV format. Each file is structured as follows:

- **First Column**: Represents the winner of the interaction.
- **Second Column**: Represents the loser of the interaction.

The CSV file names follow this format: `Author_Year[Sequence].csv`, where "Sequence" is an alphabetical identifier to differentiate multiple datasets from the same author and year.
For more detailed information on these datasets, please refer to the [DomArchive repository](https://github.com/DomArchive/DomArchive).

### 2. Results

The `Results` folder contains the standard outputs (STDOUT) from the Dual-K Elo rating system, saved as text files. These files are generated using:

- **Optimization Level**: 2
- **Verbosity**: 2

Each TXT file also includes:

- Execution time for each module.
- Overall execution time at the end.