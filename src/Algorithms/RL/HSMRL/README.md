# HSM-RL Implementation

This document describes the implementation of the HSM-RL (Hierarchical Storage Management using Reinforcement Learning) algorithm based on the paper by Zhang et al., 2022.

## Overview

The HSM-RL framework implements a reinforcement learning-based policy for hierarchical storage management. It uses:
- RL agents for each storage tier
- Fuzzy Rule Based (FRB) value function approximation
- TD(λ) algorithm for value function updates
- Migration policy based on cost value functions and average temperature

## Components

### 1. FRBValueFunction (`FRBValueFunction.py`)

Implements the Fuzzy Rule Based value function approximation:
- Uses two fuzzy categories: {Small, Large} for each state variable
- Membership functions: μLarge(xj) = 1/(1 + aj * e^(-bj * xj))
- Value function: v̂(s) = Σ(pi * wi(s)) / Σ(wi(s))

### 2. RLAgent (`RLAgent.py`)

Implements an RL agent for each tier:
- Uses TD(λ) algorithm for value function updates
- Tracks eligibility traces: En(s) = λγ * En-1(s) + 1(s = sn)
- Calculates rewards: Rn = (1/Xn) * Σ(ri * e^(-(tn,i - tn)))
- Updates value function: v̂(s) = v̂(s) + α * (Rn + γ * v̂(sn+1) - v̂(sn)) * En(s)

### 3. HSMRL (`HSMRL.py`)

Main algorithm class that:
- Creates an RL agent for each tier (FAST, MEDIUM, SLOW)
- Implements the migration policy:
  - File F in tier i is upgraded to tier i+1 if:
    v_i_up * t̄_i_up + v_{i+1}_up * t̄_{i+1}_up < v_i_not * t̄_i_not + v_{i+1}_not * t̄_{i+1}_not
- Handles downgrades when upper tier is full
- Extracts state variables (utilization, average temperature, number of files)

## Usage

```python
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

## State Variables

The default state variables are:
1. **Utilization**: used_capacity / total_capacity
2. **Average Temperature**: mean temperature of files in tier
3. **Number of Files**: normalized count of files in tier

These can be customized by modifying the `get_state_variables()` method.

## Migration Policy

The algorithm implements the upgrade policy from the paper:
- When a file is requested and not in the fastest tier, the policy evaluates whether to upgrade it
- The decision is based on comparing cost values before and after upgrade
- If the upper tier is full, files with lowest temperature are downgraded to make space

## Parameters

- `num_state_variables`: Number of state variables (default: 3)
- `learning_rate` (α): Learning rate for TD(λ) (default: 0.1)
- `discount_factor` (γ): Discount factor (default: 0.9)
- `lambda_trace` (λ): Trace decay parameter (default: 0.7)
- `a_params`: Hyperparameters a_j for FRB membership functions
- `b_params`: Hyperparameters b_j for FRB membership functions

## Integration with Simulator

The algorithm can be used with the existing Simulator class. To enable RL agent updates after requests, you may want to modify the simulator to call `algorithm.update_after_request()` after each read/write operation.

## References

Zhang et al., 2022. "Reinforcement learning based policy for hierarchical storage management"
