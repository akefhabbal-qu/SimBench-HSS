"""
HSM-RL: Hierarchical Storage Management using Reinforcement Learning

This module implements the HSM-RL framework as described in:
Zhang et al., 2022. "Reinforcement learning based policy for hierarchical storage management"

The framework uses:
- RL agents for each tier
- Fuzzy Rule Based (FRB) value function approximation
- TD(λ) algorithm for value function updates
- Migration policy based on cost value functions and average temperature
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import math

from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType,
    DataObject,
    HierarchicalStorageSystem
)
from .RLAgent import RLAgent
from utils.logger import logger
from utils.Utility import format_data_size


class HSMRL(AlgorithmBase):
    """
    HSM-RL algorithm for hierarchical storage management.
    
    The algorithm uses RL agents for each tier to make migration decisions
    based on cost value functions and file temperatures.
    """
    
    def __init__(self, sys: HierarchicalStorageSystem, 
                 num_state_variables: int = 3,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.9,
                 lambda_trace: float = 0.7,
                 a_params: List[float] = None,
                 b_params: List[float] = None):
        """
        Initialize the HSM-RL algorithm.
        
        Args:
            sys: The hierarchical storage system
            num_state_variables (int): Number of state variables for RL agents
            learning_rate (float): Learning rate α for TD(λ)
            discount_factor (float): Discount factor γ
            lambda_trace (float): Trace decay parameter λ
            a_params (List[float]): Hyperparameters a_j for FRB
            b_params (List[float]): Hyperparameters b_j for FRB
        """
        super().__init__(sys)
        
        self.num_state_variables = num_state_variables
        
        # Create RL agent for each tier
        self.agents: Dict[StorageNodeType, RLAgent] = {}
        tier_names = {
            StorageNodeType.FAST: "FAST",
            StorageNodeType.MEDIUM: "MEDIUM",
            StorageNodeType.SLOW: "SLOW"
        }
        
        for tier in StorageNodeType:
            self.agents[tier] = RLAgent(
                tier_name=tier_names[tier],
                num_state_variables=num_state_variables,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                lambda_trace=lambda_trace,
                a_params=a_params,
                b_params=b_params
            )
        
        # Track current timestamp for state transitions
        self.current_timestamp = 0
        
        # Track file locations
        self.file_locations: Dict[str, StorageNodeType] = {}
    
    def get_state_variables(self, tier: StorageNodeType) -> np.ndarray:
        """
        Extract state variables for a tier.
        
        State variables should represent properties of the dataset and access patterns.
        For this implementation, we use:
        - Utilization (used capacity / total capacity)
        - Average temperature of files in tier
        - Number of files in tier
        
        Args:
            tier (StorageNodeType): The tier to get state for
            
        Returns:
            np.ndarray: State vector
        """
        # Get tier data
        tier_data = self.sys.data_manager.get_tier_data(tier)
        
        # State variable 1: Utilization
        total_capacity = self.sys.get_nodes_capacity(tier)
        used_capacity = self.sys.get_used_storage_size(tier)
        utilization = used_capacity / total_capacity if total_capacity > 0 else 0.0
        
        # State variable 2: Average temperature
        if len(tier_data) > 0:
            avg_temperature = np.mean([data.get_temperature() for data in tier_data])
        else:
            avg_temperature = 0.0
        
        # State variable 3: Number of files (normalized)
        num_files = len(tier_data)
        # Normalize by assuming max 1000 files (adjust based on your system)
        normalized_num_files = min(num_files / 1000.0, 1.0)
        
        # Return state vector
        state = np.array([utilization, avg_temperature, normalized_num_files])
        
        # Pad or truncate to match num_state_variables
        if len(state) < self.num_state_variables:
            # Pad with zeros
            state = np.pad(state, (0, self.num_state_variables - len(state)), 'constant')
        elif len(state) > self.num_state_variables:
            # Truncate
            state = state[:self.num_state_variables]
        
        return state
    
    def get_average_temperature(self, tier: StorageNodeType, 
                               exclude_file: Optional[DataObject] = None,
                               include_file: Optional[DataObject] = None) -> float:
        """
        Calculate average temperature of files in a tier.
        
        Args:
            tier (StorageNodeType): The tier
            exclude_file (DataObject, optional): File to exclude from calculation
            include_file (DataObject, optional): File to include in calculation
            
        Returns:
            float: Average temperature
        """
        tier_data = self.sys.data_manager.get_tier_data(tier)
        
        # Filter files
        files = [f for f in tier_data if exclude_file is None or f.id != exclude_file.id]
        
        # Add file if specified
        if include_file is not None:
            files.append(include_file)
        
        if len(files) == 0:
            return 0.0
        
        return np.mean([f.get_temperature() for f in files])
    
    def should_upgrade(self, file: DataObject, current_tier: StorageNodeType) -> bool:
        """
        Determine if a file should be upgraded using the RL-based policy.
        
        File F in tier i will be upgraded to tier i+1 if:
        v_i_up * t̄_i_up + v_{i+1}_up * t̄_{i+1}_up < v_i_not * t̄_i_not + v_{i+1}_not * t̄_{i+1}_not
        
        Args:
            file (DataObject): The file to consider
            current_tier (StorageNodeType): Current tier of the file
            
        Returns:
            bool: True if file should be upgraded
        """
        # Get tier hierarchy
        tier_order = [StorageNodeType.SLOW, StorageNodeType.MEDIUM, StorageNodeType.FAST]
        
        try:
            current_index = tier_order.index(current_tier)
        except ValueError:
            return False
        
        # Check if there's a higher tier
        if current_index >= len(tier_order) - 1:
            return False  # Already at highest tier
        
        next_tier = tier_order[current_index + 1]
        
        # Check if next tier has capacity
        required_capacity = file.size * self.replication_factor
        if not self.sys.has_sufficient_capacity(next_tier, required_capacity):
            return False  # No capacity in next tier
        
        # Get state variables for current and next tier
        state_i = self.get_state_variables(current_tier)
        state_i1 = self.get_state_variables(next_tier)
        
        # Calculate average temperatures before upgrade
        t_i_not = self.get_average_temperature(current_tier)
        t_i1_not = self.get_average_temperature(next_tier)
        
        # Calculate average temperatures after upgrade (hypothetically)
        t_i_up = self.get_average_temperature(current_tier, exclude_file=file)
        t_i1_up = self.get_average_temperature(next_tier, include_file=file)
        
        # Get value functions
        v_i_not = self.agents[current_tier].get_value(state_i)
        v_i1_not = self.agents[next_tier].get_value(state_i1)
        
        # Calculate value functions after upgrade (approximate by using updated state)
        # For simplicity, we approximate by adjusting the state
        state_i_up = state_i.copy()
        state_i1_up = state_i1.copy()
        
        # Update utilization in states (simplified)
        # This is an approximation - in practice, you'd recalculate the full state
        tier_data_i = self.sys.data_manager.get_tier_data(current_tier)
        tier_data_i1 = self.sys.data_manager.get_tier_data(next_tier)
        
        # Recalculate states with file moved
        # Simplified: just update temperature component
        state_i_up[1] = t_i_up  # Update average temperature
        state_i1_up[1] = t_i1_up  # Update average temperature
        
        v_i_up = self.agents[current_tier].get_value(state_i_up)
        v_i1_up = self.agents[next_tier].get_value(state_i1_up)
        
        # Apply upgrade policy
        cost_not = v_i_not * t_i_not + v_i1_not * t_i1_not
        cost_up = v_i_up * t_i_up + v_i1_up * t_i1_up
        
        should_upgrade = cost_up < cost_not
        
        logger.debug(
            f"HSM-RL: Upgrade decision for file {file.id}: "
            f"cost_not={cost_not:.4f}, cost_up={cost_up:.4f}, "
            f"should_upgrade={should_upgrade}"
        )
        
        return should_upgrade
    
    def downgrade_lowest_temperature_file(self, tier: StorageNodeType, 
                                          required_capacity: int) -> bool:
        """
        Downgrade files with lowest temperature to make space.
        
        Args:
            tier (StorageNodeType): Tier to free space in
            required_capacity (int): Required capacity to free
            
        Returns:
            bool: True if enough space was freed
        """
        tier_data = self.sys.data_manager.get_tier_data(tier)
        
        if len(tier_data) == 0:
            return False
        
        # Sort files by temperature (ascending - lowest first)
        sorted_files = sorted(tier_data, key=lambda f: f.get_temperature())
        
        # Get tier hierarchy
        tier_order = [StorageNodeType.SLOW, StorageNodeType.MEDIUM, StorageNodeType.FAST]
        try:
            current_index = tier_order.index(tier)
        except ValueError:
            return False
        
        if current_index == 0:
            return False  # Already at lowest tier, can't downgrade
        
        lower_tier = tier_order[current_index - 1]
        freed_capacity = 0
        
        # Downgrade files until we have enough space
        for file in sorted_files:
            file_capacity = file.size * self.replication_factor
            
            # Check if lower tier has capacity
            if self.sys.has_sufficient_capacity(lower_tier, file_capacity):
                try:
                    # Move file to lower tier
                    self.sys.write_to_node(lower_tier, file, self.current_timestamp)
                    self.file_locations[file.id] = lower_tier
                    freed_capacity += file_capacity
                    
                    logger.info(
                        f"HSM-RL: Downgraded file {file.id} from {tier.name} to {lower_tier.name} "
                        f"to free {format_data_size(file_capacity)}"
                    )
                    
                    if freed_capacity >= required_capacity:
                        return True
                except Exception as e:
                    logger.error(f"HSM-RL: Error downgrading file {file.id}: {e}")
                    continue
        
        return freed_capacity >= required_capacity
    
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
        Determine the optimal storage tier for a data object.
        
        The algorithm:
        1. Checks if file already exists and should be upgraded
        2. Places new files initially in SLOW tier
        3. Uses RL-based policy to decide on upgrades
        
        Args:
            currentData (DataObject): The data object to place
            
        Returns:
            StorageNodeType: The selected storage tier
        """
        self.currentObject = currentData
        required_capacity = currentData.size * self.replication_factor
        
        # Check if file already exists
        if self.sys.has_data(currentData.id):
            # Get current location
            tier_data = self.sys.data_manager.get_tier_data(StorageNodeType.FAST)
            current_tier = None
            
            # Find which tier the file is in
            for tier in StorageNodeType:
                tier_files = self.sys.data_manager.get_tier_data(tier)
                if any(f.id == currentData.id for f in tier_files):
                    current_tier = tier
                    break
            
            if current_tier is None:
                # File exists but not found in any tier (shouldn't happen)
                current_tier = StorageNodeType.SLOW
            
            # Check if should upgrade
            if self.should_upgrade(currentData, current_tier):
                next_tier_order = [StorageNodeType.SLOW, StorageNodeType.MEDIUM, StorageNodeType.FAST]
                current_index = next_tier_order.index(current_tier)
                
                if current_index < len(next_tier_order) - 1:
                    next_tier = next_tier_order[current_index + 1]
                    
                    # Check capacity
                    if not self.sys.has_sufficient_capacity(next_tier, required_capacity):
                        # Try to free space by downgrading
                        if not self.downgrade_lowest_temperature_file(next_tier, required_capacity):
                            # Can't free space, stay in current tier
                            logger.info(
                                f"HSM-RL: Cannot upgrade file {currentData.id} to {next_tier.name}, "
                                f"staying in {current_tier.name}"
                            )
                            return current_tier
                    
                    logger.info(
                        f"HSM-RL: Upgrading file {currentData.id} from {current_tier.name} to {next_tier.name}"
                    )
                    self.file_locations[currentData.id] = next_tier
                    return next_tier
            
            # No upgrade, stay in current tier
            return current_tier
        
        # New file: start in SLOW tier
        if self.sys.has_sufficient_capacity(StorageNodeType.SLOW, required_capacity):
            logger.info(f"HSM-RL: Placing new file {currentData.id} in SLOW tier")
            self.file_locations[currentData.id] = StorageNodeType.SLOW
            return StorageNodeType.SLOW
        
        # If SLOW tier is full, try MEDIUM, then FAST
        for tier in [StorageNodeType.MEDIUM, StorageNodeType.FAST]:
            if self.sys.has_sufficient_capacity(tier, required_capacity):
                logger.info(f"HSM-RL: Placing new file {currentData.id} in {tier.name} tier (SLOW full)")
                self.file_locations[currentData.id] = tier
                return tier
        
        # No storage available
        raise NoStorageAvailableException(
            f"HSM-RL: No storage available for data size: {format_data_size(required_capacity)}"
        )
    
    def update_after_request(self, file_id: str, response_time: float, 
                            timestamp: int, operation_type: str):
        """
        Update RL agents after a request is processed.
        
        This should be called after each read/write operation to update
        the RL agents based on the new state.
        
        Args:
            file_id (str): ID of the file that was accessed
            response_time (float): Response time for the operation
            timestamp (int): Timestamp of the operation
            operation_type (str): Type of operation ('read' or 'write')
        """
        self.current_timestamp = timestamp
        
        # Find which tier the file is in
        file_tier = None
        for tier in StorageNodeType:
            tier_files = self.sys.data_manager.get_tier_data(tier)
            if any(f.id == file_id for f in tier_files):
                file_tier = tier
                break
        
        if file_tier is None:
            return  # File not found
        
        # Get current state for the tier
        current_state = self.get_state_variables(file_tier)
        
        # Record request in the agent
        agent = self.agents[file_tier]
        agent.record_request(current_state, response_time, timestamp)
        
        # Check if state has changed significantly (simplified: always transition)
        # In practice, you might want to check if state changed enough
        agent.transition_to_state(current_state, timestamp)
        
        # Update other tiers' agents as well (they might be affected)
        for tier, agent in self.agents.items():
            if tier != file_tier:
                state = self.get_state_variables(tier)
                agent.transition_to_state(state, timestamp)
    
    def name(self) -> str:
        return "HSM-RL"
