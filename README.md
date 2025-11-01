# SimBench-HSS

A comprehensive simulation benchmark for optimizing data placement in Hierarchical Storage Systems (HSS). This project provides tools for analyzing and comparing different data placement strategies using both synthetic and real-world datasets.

## Project Overview

SimBench-HSS is a simulation system designed for evaluating data placement strategies in hierarchical storage environments. It enables researchers and practitioners to:

- Simulate cloud-based hierarchical storage systems with multiple tiers (Fast, Medium, Slow)
- Compare various placement algorithms (heuristic-based)
- Analyze performance metrics including response times and network usage
- Work with both synthetic and real-world datasets
- Evaluate placement strategies before deploying to cloud environments

## Features

### Core Capabilities

- **Multi-Tier Storage Simulation**: Simulates hierarchical storage systems with configurable tiers
- **Multiple Placement Algorithms**: TimeGreedy, SpaceGreedy, CostGreedy, HybridGreedy, LoadBalancingGreedy, RandomSelection, GeneticAlgorithm
- **File Hotness Calculation**: Automatically calculates file hotness levels from access patterns
- **Static Placement**: Initial data placement based on file characteristics and access patterns
- **Dynamic Migration**: Support for file migration with network cost considerations
- **Comprehensive Metrics**:
  - Response time distributions
  - Median and mean response times
  - Network usage analysis
  - Storage utilization statistics
- **Dataset Support**: Works with both synthetic datasets and real-world traces (e.g., Berkeley Auspex Traces)

## Project Structure

```
.
├── src/
│   ├── Algorithms/           # Placement and migration algorithms
│   │   └── Heuristic/        # Heuristic-based algorithms
│   ├── DataObject/          # Data structure definitions (File, Replica)
│   ├── Simulation/          # Simulation environment and configuration
│   ├── Storage/             # Storage system implementation
│   │   └── HierarchicalStorage/  # Hierarchical storage components
│   └── utils/               # Utility functions and helpers
├── data/
│   ├── train/               # Training datasets (JSONL format)
│   ├── test/                # Test datasets
│   └── Berkeley Auspex Traces - converted/  # Real-world traces
├── docs/                    # Documentation
│   ├── architecture.md      # System architecture
│   ├── getting-started.md   # Quick start guide
│   └── simulation.md        # Simulation system details
├── logs/                    # Simulation logs and results
├── requirements.txt         # Python dependencies
└── LICENSE                  # MIT License
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/SimBench-HSS.git
cd SimBench-HSS
```

2. Create a virtual environment:

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

## Dependencies

- **Core Scientific Computing**: numpy (≥1.20.0), matplotlib (≥3.4.0)
- **Data Analysis**: pandas (≥1.2.0), seaborn (≥0.11.0)
- **Utilities**: tqdm (≥4.60.0) for progress bars

## Usage

### Basic Usage

1. Prepare your data:

   - Place training data in `data/train/` directory (JSONL format)
   - Place test data in `data/test/` directory

2. Run the simulation:

```bash
python src/main.py
```

The simulation will process the access pattern file specified in `src/main.py` and generate results in the `logs/` directory.

### Configuration

The simulation system can be configured through:

- `src/Simulation/sim_config.py` - Simulation parameters
- `src/Storage/storage_config.py` - Storage system configuration

Key configuration options include:

- Storage tier capacities and costs
- Network latency and bandwidth settings
- Replication factor
- Algorithm-specific parameters

### Available Algorithms

#### Heuristic Algorithms

- **TimeGreedy**: Optimizes based on access time patterns
- **SpaceGreedy**: Optimizes storage space utilization
- **CostGreedy**: Minimizes storage costs
- **HybridGreedy**: Combines multiple greedy strategies
- **LoadBalancingGreedy**: Distributes load across storage tiers
- **RandomSelection**: Random placement baseline
- **GeneticAlgorithm**: Evolutionary optimization approach

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Getting Started Guide](docs/getting-started.md) - Installation and basic usage
- [Architecture Documentation](docs/architecture.md) - System design and components
- [Simulation Guide](docs/simulation.md) - Detailed simulation configuration

## Performance Metrics

The simulator tracks and reports:

- **Response Time Metrics**: Mean, median, and distribution of response times
- **Network Usage**: Data transfer volumes and costs
- **Storage Utilization**: Capacity usage across tiers
- **Access Patterns**: File hotness and access frequency

Results are saved in CSV format in the `logs/` directory for further analysis.

## Contributing

This project is currently under active development. The code will be made publicly available once the associated paper is accepted. Contributions and feedback are welcome.

For questions or issues, please open an issue on the GitHub repository.

## Citation

If you use SimBench-HSS in your research, please cite our paper (citation to be added upon publication).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Berkeley Auspex Traces for providing real-world dataset examples
- Inspired by research in hierarchical storage systems and data placement optimization
