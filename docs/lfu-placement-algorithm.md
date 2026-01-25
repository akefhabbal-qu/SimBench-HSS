# LFU (Least Frequently Used) Placement Algorithm

## Overview

The LFU (Least Frequently Used) placement algorithm is a frequency-based data placement strategy that uses access frequency within a time window to determine optimal storage tier placement. Unlike eviction policies that decide **what** to remove, placement algorithms decide **where** to place data initially or during migration.

## Conceptual Foundation

### Core Principle

The LFU placement algorithm operates on the principle that data objects with higher access frequency should be placed in faster storage tiers to minimize access latency, while less frequently accessed data can be placed in slower, more cost-effective tiers.

### Time-Windowed Frequency

The algorithm uses a **time-windowed frequency metric** that:
- Tracks read and write accesses within a configurable time window
- Calculates frequency as the count of accesses within that window
- Adapts to changing access patterns by only considering recent accesses

## Algorithm Description

### Placement Decision Logic

The LFU placement algorithm uses frequency thresholds to determine storage tier:

1. **High Frequency** (≥ `high_frequency_threshold`): 
   - Preferred tier: **FAST**
   - Fallback: MEDIUM → SLOW
   - Rationale: Frequently accessed data benefits from low latency

2. **Medium Frequency** (≥ `medium_frequency_threshold` but < `high_frequency_threshold`):
   - Preferred tier: **MEDIUM**
   - Fallback: FAST → SLOW
   - Rationale: Moderate access frequency justifies medium-tier performance

3. **Low Frequency** (< `medium_frequency_threshold`):
   - Preferred tier: **SLOW**
   - Fallback: MEDIUM → FAST
   - Rationale: Infrequently accessed data can use cost-effective storage

### Default Thresholds

- `high_frequency_threshold`: 5 accesses within time window
- `medium_frequency_threshold`: 2 accesses within time window

These thresholds are configurable when instantiating the algorithm.

## Implementation Details

### Access Frequency Calculation

The algorithm retrieves access frequency from the system's LFU eviction policy:

```python
access_frequency = self.sys.get_access_frequency(data_id)
```

This frequency is calculated as:
```
frequency(data_id, t) = count(accesses where timestamp >= t - time_window)
```

### Placement Process

1. **Calculate frequency**: Get access frequency for the data object
2. **Determine tier preference**: Based on frequency thresholds
3. **Check capacity**: Verify selected tier has sufficient capacity
4. **Fallback**: If preferred tier lacks capacity, try next tier in preference order

### Integration with System

The algorithm integrates seamlessly with:
- **Heuristic algorithms**: Can be used alongside other placement strategies
- **RL agents**: Provides frequency-based placement for comparison
- **Eviction policy**: Shares the same LFU frequency tracking mechanism

## Advantages

### 1. Frequency-Aware Placement

Unlike time-based algorithms (e.g., TimeGreedy) that only consider recency, LFU considers cumulative access patterns, making it more effective for:
- Repeated access patterns
- Files accessed multiple times over a period
- Workloads with frequency-based locality

### 2. Cost-Performance Optimization

By placing frequently accessed data in faster tiers and infrequent data in slower tiers, the algorithm:
- Minimizes access latency for hot data
- Reduces storage costs for cold data
- Balances performance and cost objectives

### 3. Adaptive Behavior

The time-windowed approach ensures:
- Recent access patterns influence placement decisions
- Stale frequency counts don't affect current decisions
- Algorithm adapts to changing workload characteristics

## Usage Example

```python
from Algorithms.Heuristic import LFUGreedy
from Storage import HierarchicalStorageSystem

# Initialize system with LFU eviction enabled (for frequency tracking)
sys = HierarchicalStorageSystem(enable_lfu_eviction=True, lfu_time_window=1000)

# Create LFU placement algorithm with custom thresholds
algorithm = LFUGreedy(
    sys, 
    high_frequency_threshold=5,  # 5+ accesses → FAST tier
    medium_frequency_threshold=2  # 2-4 accesses → MEDIUM tier
)

# Use algorithm for placement
node_type = algorithm.apply(data_object)
```

## Comparison with Other Placement Algorithms

| Algorithm | Decision Metric | Advantages | Use Case |
|-----------|----------------|------------|----------|
| **LFUGreedy** | Time-windowed frequency | Frequency-aware, adaptive | Repeated access patterns |
| **TimeGreedy** | Recency | Simple, fast | Time-sensitive workloads |
| **SpaceGreedy** | Available capacity | Maximizes space utilization | Capacity-constrained systems |
| **CostGreedy** | Storage cost | Cost minimization | Budget-constrained deployments |
| **HybridGreedy** | Weighted combination | Multi-objective optimization | Complex requirements |

## Experimental Considerations

### Threshold Tuning

The frequency thresholds significantly impact placement behavior:
- **High thresholds**: More data placed in slower tiers (cost-effective)
- **Low thresholds**: More data placed in faster tiers (performance-oriented)
- **Optimal values**: Depend on workload characteristics and system objectives

### Time Window Selection

The time window (shared with LFU eviction policy) affects:
- **Sensitivity**: Smaller windows = more responsive to recent changes
- **Stability**: Larger windows = more stable placement decisions
- **Default**: 1000 time units provides balanced behavior

### Performance Metrics

When evaluating LFU placement, consider:
- **Access latency**: Average response time for read operations
- **Storage costs**: Total cost across all tiers
- **Tier utilization**: Distribution of data across tiers
- **Migration overhead**: Cost of moving data between tiers

## Mathematical Formulation

For data object $d$ at time $t$:

**Frequency Calculation:**
$$F(d, t) = \sum_{i=1}^{n} \mathbf{1}[t_i \geq t - W]$$

**Placement Decision:**
$$Tier(d) = \begin{cases}
\text{FAST} & \text{if } F(d, t) \geq \theta_h \\
\text{MEDIUM} & \text{if } \theta_m \leq F(d, t) < \theta_h \\
\text{SLOW} & \text{if } F(d, t) < \theta_m
\end{cases}$$

where:
- $F(d, t)$ is access frequency
- $W$ is the time window
- $\theta_h$ is high frequency threshold
- $\theta_m$ is medium frequency threshold

## Conclusion

The LFU placement algorithm provides an effective frequency-based approach to data placement in hierarchical storage systems. By considering access frequency within a time window, it balances performance and cost objectives while adapting to changing workload patterns. This makes it particularly suitable for testing and comparing with heuristic algorithms and reinforcement learning agents in storage optimization research.
