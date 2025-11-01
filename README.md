# Optimizing Data Placement

A simulation system for optimizing data placement and storage strategies in cloud environments. This project provides tools for analyzing and comparing different data placement strategies using both synthetic and real-world datasets.

## Project Overview

This project implements a simulation system for evaluating data placement strategies in cloud environments. It includes:

- Simulation of cloud-based storage systems
- Analysis of response times and network usage
- Support for both synthetic and real-world datasets
- Tools for comparing different placement strategies
- Hotness level calculation for files based on access patterns

## Features

- Static placement agent for initial data placement
- Migration agent for dynamic data movement
- Network cost consideration for file migrations
- Performance metrics tracking:
  - Response time distributions
  - Median and mean response times
  - Network usage analysis
- Support for file hotness level calculation
- Cloud storage integration capabilities

## Project Structure

```
.
├── src/
│   ├── Algorithms/     # Implementation of placement algorithms
│   ├── DataObject/     # Data structure definitions
│   ├── Simulation/     # Simulation environment
│   ├── Storage/        # Storage system implementation
│   └── utils/          # Utility functions
├── data/              # Dataset storage
├── logs/              # Simulation logs
└── requirements.txt   # Project dependencies
```

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Dependencies

- numpy
- torch
- matplotlib
- tensorflow

## Usage

[Usage instructions will be added as the project develops]

## Contributing

This project is currently under development. The code will be made publicly available once the associated paper is accepted.

## License

[License information to be added]
