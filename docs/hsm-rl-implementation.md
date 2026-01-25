# HSM-RL Implementation

This document describes the implementation of the HSM-RL (Hierarchical Storage Management using Reinforcement Learning) algorithm based on the paper by Zhang et al., 2022.

**Note:** All HSM-RL related files are now organized in the `src/Algorithms/RL/HSMRL/` folder. See the [README.md](../src/Algorithms/RL/HSMRL/README.md) in that folder for detailed documentation.

## File Organization

All HSM-RL implementation files are located in:
- `src/Algorithms/RL/HSMRL/`
  - `HSMRL.py` - Main algorithm class
  - `RLAgent.py` - RL agent for each tier
  - `FRBValueFunction.py` - Fuzzy Rule Based value function approximation
  - `README.md` - Detailed documentation
  - `__init__.py` - Module exports

## Quick Start

```python
from Algorithms.RL import HSMRL
# or
from Algorithms.RL.HSMRL import HSMRL

from Storage import HierarchicalStorageSystem

# Create storage system
sys = HierarchicalStorageSystem()

# Create HSM-RL algorithm
algorithm = HSMRL(
    sys=sys,
    num_state_variables=3,  # utilization, avg_temp, num_files
    learning_rate=0.1,
    discount_factor=0.9,
    lambda_trace=0.7
)

# Use in simulator
from Simulation import Simulator
sim = Simulator(access_pattern_path="access_pattern.json")
sim.run_algorithm(access_pattern_path, HSMRL)
```

## References

Zhang et al., 2022. "Reinforcement learning based policy for hierarchical storage management"
