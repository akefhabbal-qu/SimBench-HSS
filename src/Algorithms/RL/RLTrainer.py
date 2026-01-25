import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tqdm import tqdm

from Algorithms.RL.RLAgentBase import RLAgentBase
from .DQN import DQN
from Storage import HierarchicalStorageSystem, StorageNodeType
from utils.logger import logger
from Algorithms import NoStorageAvailableException
from Storage.MetricsCalculator import MetricsCalculator
from Storage.storage_types import DataObject

class RLTrainer:
    def __init__(self, access_pattern_path: str, episodes: int = 1000):
        """
        DQNTrainer class to train DQNDataPlacementAgent.

        Args:
            access_pattern_path (str): Path to access pattern JSON file.
            episodes (int): Number of training episodes.
        """
        self.access_pattern = self.load_access_pattern(access_pattern_path)
        self.episodes = episodes
        self.storage_system = HierarchicalStorageSystem()
        self.metrics_calculator = MetricsCalculator(self.storage_system)
        self.storage_system.initialize_metrics_calculator(self.metrics_calculator)
    
    def load_access_pattern(self, access_pattern_path: str):
        """Load access pattern from JSON or JSONL file."""
        access_pattern = []
        
        with open(access_pattern_path, "r") as file:
            if access_pattern_path.endswith('.jsonl'):
                # Handle JSONL format (one JSON object per line)
                for line in file:
                    line = line.strip()
                    if line:  # Skip empty lines
                        access_pattern.append(json.loads(line))
            else:
                # Handle JSON format (single JSON array)
                access_pattern = json.load(file)
        
        return access_pattern

    def train(self, agent: RLAgentBase):
        """Train the DQN agent over multiple episodes."""
        print(f"Starting DQN training for {self.episodes} episodes.")
        total_operations = len(self.access_pattern)
        print(f"Total operations per episode: {total_operations}")
        
        # Create progress bar for episodes
        episode_pbar = tqdm(range(self.episodes), desc="Episodes", position=0, leave=True)
        
        for episode in episode_pbar:
            episode_pbar.set_description(f"Episode {episode + 1}/{self.episodes}")
            self.storage_system.reset()  # Reset the storage system for each episode
            
            last_reward = 0
            last_state = None
            last_action = None
            
            # Create progress bar for operations within each episode
            operations_pbar = tqdm(enumerate(self.access_pattern), 
                                 total=total_operations, 
                                 desc=f"Episode {episode + 1} Operations", 
                                 position=1, 
                                 leave=False)
            
            for op_idx, op in operations_pbar:
                operations_pbar.set_postfix({
                    'op_num': op.get('operation_num', 0),
                    'type': op.get('operation_type', 'unknown')
                })
                file_id = op.get("file_id")
                file_size = op.get("size", 100)
                op_type = op.get("operation_type")
                timestamp = op.get("time", 0)

                if file_id is None or op_type is None:
                    continue

                if op_type == "write":
                    # Generate a new data object
                    file = self.storage_system.generate_data(file_id, file_size)

                    # Select an action
                    try:
                        state = agent.construct_state(file_id, file_size)

                        if last_state is not None:
                            agent.update(last_state, last_action, last_reward, state, False)
                        
                        action = agent.apply(file)
                    except NoStorageAvailableException as e:
                        self.storage_system.increment_num_unsuccessful_write()
                        print(f"Trainer: {e}")
                        continue
                    
                    # Execute action
                    self.storage_system.write_to_node(action, file, timestamp)
                    reward = self.storage_system.metrics_calculator.optimization_function()

                    last_reward = reward
                    last_state = state
                    last_action = action
                elif op_type == "read":
                    try:
                        self.storage_system.read_data(file_id, timestamp)
                    except Exception as e:
                        print(f"Trainer: Error during read: {e}")
                
                elif op_type == "delete":
                    try:
                        self.storage_system.delete_data(file_id, timestamp)
                    except Exception as e:
                        print(f"Trainer: Error during delete: {e}")
            
            # Close the operations progress bar for this episode
            operations_pbar.close()
            
            # Call end_episode on the agent to properly increment episode count
            agent.end_episode()
            episode_pbar.set_postfix({'Status': 'Completed'})
        
        # Close the episode progress bar
        episode_pbar.close()
        print("Training completed.")
    
    def execute_action(self, action: StorageNodeType, file: DataObject, timestamp: int = 0):
        """Simulate writing a file to the selected storage node and return a reward."""
        try:
            self.storage_system.write_to_node(action, file, timestamp)
            return self.storage_system.metrics_calculator.optimization_function()
        except Exception as e:
            print(f"Trainer: Error during write: {e}")
    
# Example Usage
if __name__ == "__main__":
    trainer = RLTrainer(access_pattern_path="access_pattern.json", episodes=100)
    trainer.train()
    trainer.save_model(os.path.join(os.getcwd(), "dqn_model.h5"))