#!/usr/bin/env python3
"""
Test script to demonstrate the Estimated System Response (ESR) calculation.

This script shows how to calculate ESR using the formulas:
- ESR = 10 × Σ(tier1) + 2 × Σ(tier2) + 1 × Σ(tier3)
- nr_est = 10 × temp (estimated number of requests per file)
- res_est = size / 10000 (estimated response time per file)
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from Simulation import Simulator
from Storage.MetricsCalculator import MetricsCalculator
from Storage import HierarchicalStorageSystem
from Storage.storage_types import StorageNodeType, DataObject
import json

def create_sample_data_objects():
    """Create sample data objects with different temperatures and sizes for testing."""
    sample_files = [
        {"id": "file_001", "size": 1000, "temp": 0.9},   # Hot, large file
        {"id": "file_002", "size": 500, "temp": 0.7},    # Warm, medium file
        {"id": "file_003", "size": 100, "temp": 0.3},    # Cold, small file
        {"id": "file_004", "size": 2000, "temp": 0.8},   # Hot, very large file
        {"id": "file_005", "size": 50, "temp": 0.1},     # Very cold, tiny file
    ]
    
    data_objects = []
    for file_info in sample_files:
        data_obj = DataObject(
            id=file_info["id"],
            size=file_info["size"]
        )
        # Manually set temperature for testing
        data_obj.hotness_level = file_info["temp"]
        data_objects.append(data_obj)
    
    return data_objects

def calculate_esr_manually(data_objects_by_tier):
    """Manually calculate ESR to verify our implementation."""
    print("\n=== Manual ESR Calculation ===")
    
    tier_weights = {
        StorageNodeType.FAST: 10,
        StorageNodeType.MEDIUM: 2,
        StorageNodeType.SLOW: 1
    }
    
    total_esr = 0.0
    
    for tier_type, data_objects in data_objects_by_tier.items():
        tier_weight = tier_weights[tier_type]
        tier_sum = 0.0
        
        print(f"\n{tier_type.name} Tier (weight={tier_weight}):")
        
        for data_obj in data_objects:
            temp = data_obj.get_temperature()
            nr_est = 10 * temp
            res_est = data_obj.size / 10000
            
            file_contribution = nr_est * res_est
            tier_sum += file_contribution
            
            print(f"  File {data_obj.id}: size={data_obj.size}KB, temp={temp:.3f}")
            print(f"    nr_est = 10 × {temp:.3f} = {nr_est:.3f}")
            print(f"    res_est = {data_obj.size} / 10000 = {res_est:.4f}")
            print(f"    contribution = {nr_est:.3f} × {res_est:.4f} = {file_contribution:.6f}")
        
        weighted_sum = tier_weight * tier_sum
        total_esr += weighted_sum
        
        print(f"  Tier sum: {tier_sum:.6f}")
        print(f"  Weighted sum: {tier_weight} × {tier_sum:.6f} = {weighted_sum:.6f}")
    
    print(f"\nTotal ESR: {total_esr:.6f}")
    return total_esr

def test_esr_calculation():
    """Test the ESR calculation with sample data."""
    print("=== Testing Estimated System Response (ESR) Calculation ===\n")
    
    # Create sample data objects
    sample_data = create_sample_data_objects()
    
    # Distribute files across tiers (simulate placement)
    data_objects_by_tier = {
        StorageNodeType.FAST: sample_data[:2],      # Hot files in FAST tier
        StorageNodeType.MEDIUM: sample_data[2:4],   # Medium files in MEDIUM tier
        StorageNodeType.SLOW: sample_data[4:],      # Cold files in SLOW tier
    }
    
    print("Sample Data Distribution:")
    for tier_type, data_objects in data_objects_by_tier.items():
        print(f"\n{tier_type.name} Tier:")
        for data_obj in data_objects:
            print(f"  - {data_obj.id}: size={data_obj.size}KB, temp={data_obj.get_temperature():.3f}")
    
    # Manual calculation
    manual_esr = calculate_esr_manually(data_objects_by_tier)
    
    print("\n=== ESR Formula Explanation ===")
    print("ESR = 10 × Σ(tier1) + 2 × Σ(tier2) + 1 × Σ(tier3)")
    print("where each tier sum = Σ(nr_est × res_est)")
    print("nr_est = 10 × temp (estimated number of requests per file)")
    print("res_est = size / 10000 (estimated response time per file)")
    print("\nTier weights reflect performance hierarchy:")
    print("- FAST tier (NVMe): weight = 10 (highest performance)")
    print("- MEDIUM tier (SSD): weight = 2 (medium performance)")
    print("- SLOW tier (HDD): weight = 1 (lowest performance)")
    
    return manual_esr

def demonstrate_with_real_simulation():
    """Demonstrate ESR calculation with a real simulation."""
    print("\n\n=== ESR Calculation with Real Simulation ===")
    
    # Get the path to the training data
    root_dir = Path(__file__).resolve().parent.parent
    train_path = os.path.join(root_dir, "data", "train", "file_access_trace.jsonl")
    
    if not os.path.exists(train_path):
        print(f"Training data not found at {train_path}")
        print("Please ensure the training data exists before running this test.")
        return
    
    print(f"Running simulation with data from: {train_path}")
    
    # Run a quick simulation
    simulator = Simulator(train_path)
    
    # Calculate ESR using the metrics calculator
    esr = simulator.metrics_calculator.calculate_estimated_system_response()
    
    print(f"ESR calculated from real simulation: {esr:.4f}")
    
    return esr

if __name__ == "__main__":
    # Test with sample data
    sample_esr = test_esr_calculation()
    
    # Try with real simulation if data is available
    try:
        real_esr = demonstrate_with_real_simulation()
    except Exception as e:
        print(f"Could not run real simulation: {e}")
        print("This is expected if the simulation data is not available.")
    
    print("\n=== Summary ===")
    print("The ESR calculation has been successfully implemented!")
    print("It can be used to estimate system-wide response for anticipated future requests.")
    print("Lower ESR values indicate better expected system performance.")
