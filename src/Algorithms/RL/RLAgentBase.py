import random
import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import os

from Storage import (
    StorageNodeType, 
    DataObject,
    HierarchicalStorageSystem
)
from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import MetricsCalculator

class RLAgentBase(AlgorithmBase):
    def __init__(self, sys: HierarchicalStorageSystem, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, batch_size=32, memory_size=2000):
        super().__init__(sys)
    
    def _build_model(self):
        """Builds the DQN model."""
        raise NotImplementedError
    
    def get_all_actions(self) -> list[StorageNodeType]:
        """Get all possible actions (storage nodes)."""
        return list([StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW])
    
    def get_available_actions(self, data_size: int) -> list[StorageNodeType]:
        """Get the list of possible actions (storage nodes) for a given data size."""
        
        required_capacity = data_size * self.replication_factor
        actions = []
        if self.sys.get_available_capacity(StorageNodeType.FAST) >= required_capacity:
            actions.append(StorageNodeType.FAST)
        if self.sys.get_available_capacity(StorageNodeType.MEDIUM) >= required_capacity:
            actions.append(StorageNodeType.MEDIUM)
        if self.sys.get_available_capacity(StorageNodeType.SLOW) >= required_capacity:
            actions.append(StorageNodeType.SLOW)
        if len(actions) == 0:
            raise NoStorageAvailableException("No storage node has enough space for writing data.")
        return actions
    
    def construct_state(self, file_id: str, file_size: int):
        """Create a state representation for the RL agent."""
        # Calculate success rate
        total_operations = self.sys.get_num_successful_write() + self.sys.get_num_unsuccessful_write()
        success_rate = self.sys.get_num_successful_write() / max(1, total_operations)
        
        return np.array([
            # File characteristics
            file_size,
            
            # Capacity information (normalized)
            self.sys.get_available_capacity(StorageNodeType.FAST) / self.sys.get_nodes_capacity(StorageNodeType.FAST),
            self.sys.get_available_capacity(StorageNodeType.MEDIUM) / self.sys.get_nodes_capacity(StorageNodeType.MEDIUM),
            self.sys.get_available_capacity(StorageNodeType.SLOW) / self.sys.get_nodes_capacity(StorageNodeType.SLOW),
            
            # Utilization levels
            self.sys.get_utilization(StorageNodeType.FAST),
            self.sys.get_utilization(StorageNodeType.MEDIUM),
            self.sys.get_utilization(StorageNodeType.SLOW),
            
            # Average response times (if available)
            self.sys.get_total_write_response_time_by_type(StorageNodeType.FAST) / max(1, self.sys.get_num_successful_write()),
            self.sys.get_total_write_response_time_by_type(StorageNodeType.MEDIUM) / max(1, self.sys.get_num_successful_write()),
            self.sys.get_total_write_response_time_by_type(StorageNodeType.SLOW) / max(1, self.sys.get_num_successful_write()),
            
            # System load balance (variance in utilization)
            np.var([self.sys.get_utilization(StorageNodeType.FAST), 
                   self.sys.get_utilization(StorageNodeType.MEDIUM), 
                   self.sys.get_utilization(StorageNodeType.SLOW)]),
            
            # Success rate
            success_rate,
            
            # Estimated System Response (ESR) - system-wide performance prediction
            self.sys.metrics_calculator.calculate_estimated_system_response(),
        ]).reshape(1, -1)
    
    def select_action(self, state, data_size: int):
        """Selects an action using the epsilon-greedy policy from available actions."""

        if np.random.rand() < self.epsilon:
            return random.choice(self.get_available_actions(data_size))  # Explore
        
        q_values = self.model.predict(state, verbose=0)
        best_action_index = np.argmax(q_values[0])

        all_actions = self.get_all_actions()
        # if the node type doesn't have enough capacity for the data, select a random available node
        if not self.is_action_applicable(all_actions[best_action_index], data_size):
            return random.choice(self.get_available_actions(data_size)) # Explore
        
        return all_actions[best_action_index] # Exploit
    
    def is_action_applicable(self, action: StorageNodeType, data_size: int) -> bool:
        """Check if the selected action is applicable for the given data size."""
        return self.sys.get_available_capacity(action) >= data_size * self.replication_factor
    
    def remember(self, state, action: StorageNodeType, reward: float, next_state, done):
        """Stores experience in replay memory."""
        action_index = self.get_all_actions().index(action)
        self.memory.append((state, action_index, reward, next_state, done))
    
    def _train(self):
        """Trains the model using experience replay."""
        raise NotImplementedError
    
    def apply(self, dataObject: DataObject) -> StorageNodeType:
        """Processes the data object and selects a storage node."""
        state = self.construct_state(dataObject.id, dataObject.size)
        action = self.select_action(state, dataObject.size)
        return action
    
    def update(self, state, action: StorageNodeType, reward: float, next_state, done):
        """Update the model using the given experience."""
        self.remember(state, action, reward, next_state, done)
        self._train()
        return action
    
    def save_model(self, folder_path: str):
        # Ensure the directory exists before saving
        raise NotImplementedError

    def load_model(self, folder_path: str):
        """Load a pre-trained DQN model."""
        raise NotImplementedError
    
    def name(self):
        return "RLAgentBase"