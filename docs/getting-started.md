# Getting Started

This guide will help you set up and start using the Optimizing Data Placement project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/optimizing_data_placement.git
cd optimizing_data_placement
```

2. Create and activate a virtual environment:

```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On Unix or MacOS
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

1. Prepare your data:

   - Place your training data in the `data/train` directory
   - Place your test data in the `data/test` directory
   - Data should be in JSONL format for training traces

2. Run the simulation:

```bash
python src/main.py
```

## Configuration

The simulation system can be configured through the `src/Simulation/sim_config.py` file. Key configuration options include:

- Storage system parameters
- Network configuration
- Simulation parameters
- Performance metrics collection settings

## Project Structure

```
optimizing_data_placement/
├── src/
│   ├── Algorithms/     # Placement and migration algorithms
│   ├── DataObject/     # Data structure definitions
│   ├── Simulation/     # Simulation environment
│   ├── Storage/        # Storage system implementation
│   └── utils/          # Utility functions
├── data/
│   ├── train/         # Training datasets
│   └── test/          # Test datasets
├── docs/              # Documentation
├── logs/              # Simulation logs
└── requirements.txt   # Project dependencies
```

## Next Steps

- Read the [Architecture](./architecture.md) documentation to understand the system design
- Check out the [Examples](./examples.md) for usage patterns
- Review the [API Reference](./api-reference.md) for detailed information about available classes and methods
