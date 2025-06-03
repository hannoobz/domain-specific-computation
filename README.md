# An Agent-Based Model of Mycobacterium tuberculosis Drug Resistance Evolution

A comprehensive computational model simulating the evolution of MTb drug resistance in spatially constrained multi-drug treatment environments.

## Overview

This agent-based model investigates the complex interplay between drug pharmacodynamics, spatial constraints, and bacterial adaptation in Mycobacterium tuberculosis (MTb) drug resistance evolution. The simulation incorporates realistic pharmacokinetic parameters, bacterial replication dynamics, mutation rates, and persister cell behavior within discrete spatial grids.

## Key Features

- Multi-drug simulation with four first-line anti-TB drugs (RIF, INH, PZA, EMB)
- Spatial constraints modeling tissue-level limitations
- Persister cell dynamics with phenotypic switching
- Realistic pharmacodynamics using Hill equation-based drug effects
- Stochastic mutation with drug-specific resistance rates
- Interactive visualization with Solara GUI

### UI Preview
![ScreencastFrom2025-06-0403-41-41-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/e7ba9366-6710-4aff-a9a4-51a6587fede6)


## Installation

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hannoobz/domain-specific-computation.git
cd domain-specific-computation
```

2. Create and activate virtual environment:
```bash
virtualenv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode (Interactive Visualization)

Launch the interactive Solara interface:
```bash
solara run app_viz.py
```

This provides a web-based interface to:
- Adjust simulation parameters in real-time
- Visualize bacterial population dynamics
- Monitor resistance evolution patterns
- Analyze spatial distribution

### Command Line Mode

Run simulations programmatically:
```bash
python app.py --start 21 --days 180 --interval 2 --drug-type "RIF INH"
```

#### Command Line Arguments

- `--start`: Treatment start day (required)
- `--days`: Total simulation duration (required)
- `--interval`: Days between drug administrations (default: 1)
- `--drug-type`: Drug types as space-separated string (default: "RIF PZA INH EMB")
- `--seed`: Random seed for reproducibility (default: 0)

#### Examples

```bash
# Single drug simulation
python app.py --start 10 --days 100 --interval 3 --drug-type "RIF"

# Multi-drug combination therapy
python app.py --start 5 --days 180 --interval 1 --drug-type "RIF INH PZA EMB"

# Delayed treatment with specific seed
python app.py --start 50 --days 200 --interval 7 --drug-type "RIF INH" --seed 42
```

## Authors

| **NIM**  |           **Name**             |
| :------: | :--------------------------:   |
| 13522024 |        Kristo Anugrah          |
| 13522038 |    Francesco Michael Kusuma    |
| 13522100 |  M. Hanief Fatkhan Nashrullah  |
