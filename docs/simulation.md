# Simulation System

This document details the simulation environment and its configuration options.

## Simulation Environment

The simulation environment provides a controlled setting for testing and evaluating data placement strategies. It simulates a cloud storage system with multiple tiers and network considerations.

### Key Components

1. **Storage Tiers**

   - Hot storage (fast access, high cost)
   - Warm storage (medium access speed, moderate cost)
   - Cold storage (slow access, low cost)

2. **Network Model**

   - Latency simulation
   - Bandwidth constraints
   - Cost per transfer

3. **Access Patterns**
   - File access frequency
   - Temporal patterns
   - Size-based patterns

## Configuration Options

### Storage Configuration

```python
# Example configuration in sim_config.py
STORAGE_CONFIG = {
    'hot_tier': {
        'capacity': 1000,  # GB
        'latency': 1,      # ms
        'cost_per_gb': 0.1
    },
    'warm_tier': {
        'capacity': 5000,  # GB
        'latency': 10,     # ms
        'cost_per_gb': 0.05
    },
    'cold_tier': {
        'capacity': 10000, # GB
        'latency': 100,    # ms
        'cost_per_gb': 0.01
    }
}
```

### Network Configuration

```python
NETWORK_CONFIG = {
    'bandwidth': 1000,     # Mbps
    'latency': 5,          # ms
    'cost_per_gb': 0.02
}
```

### Simulation Parameters

```python
SIMULATION_CONFIG = {
    'duration': 3600,      # seconds
    'metrics_interval': 60, # seconds
    'log_level': 'INFO'
}
```

## Performance Metrics

The simulation tracks several key metrics:

1. **Response Time**

   - Mean response time
   - Median response time
   - 95th percentile
   - 99th percentile

2. **Cost Metrics**

   - Storage costs
   - Network transfer costs
   - Total operational costs

3. **Utilization**
   - Storage tier utilization
   - Network bandwidth utilization
   - Cache hit rates

## Running Simulations

### Basic Usage

```python
from Simulation import Simulator

# Run simulation with default configuration
Simulator.run(train_path)
```

### Custom Configuration

```python
from Simulation import Simulator
from Simulation.sim_config import update_config

# Update configuration
update_config({
    'STORAGE_CONFIG': {
        'hot_tier': {'capacity': 2000}
    }
})

# Run simulation with custom configuration
Simulator.run(train_path)
```

## Output and Logging

### Log Files

- Simulation logs: `logs/simulation.log`
- Performance metrics: `logs/metrics.json`
- Error logs: `logs/errors.log`

### Visualization

- Response time distribution
- Cost analysis
- Utilization graphs
- Access pattern analysis

## Best Practices

1. **Configuration**

   - Start with default settings
   - Adjust parameters incrementally
   - Document configuration changes

2. **Data Preparation**

   - Validate input data format
   - Check data consistency
   - Preprocess if necessary

3. **Performance Tuning**
   - Monitor memory usage
   - Optimize simulation parameters
   - Use appropriate logging levels

## Troubleshooting

Common issues and solutions:

1. **Memory Issues**

   - Reduce simulation duration
   - Decrease metrics collection frequency
   - Optimize data structures

2. **Performance Issues**

   - Check network configuration
   - Verify storage tier settings
   - Monitor system resources

3. **Data Issues**
   - Validate input format
   - Check data integrity
   - Verify access patterns
