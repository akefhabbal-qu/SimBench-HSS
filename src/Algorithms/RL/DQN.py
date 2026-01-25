import random
import numpy as np
from tensorflow import keras
from collections import deque
import os
import re

from Storage import (
    HierarchicalStorageSystem
)
from Algorithms.RL.RLAgentBase import RLAgentBase

class DQN(RLAgentBase):
    def __init__(self, sys: HierarchicalStorageSystem, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, batch_size=32, memory_size=2000):
        super().__init__(sys)
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration probability
        self.epsilon_min = epsilon_min  # Minimum epsilon value
        self.epsilon_decay = epsilon_decay  # Decay rate for epsilon
        self.learning_rate = learning_rate  # Learning rate
        self.batch_size = batch_size  # Mini-batch size for training
        self.memory = deque(maxlen=memory_size)  # Replay memory
        self.state_size = 13  # Number of state features
        self.action_size = 3  # Number of possible storage actions
        self.model = self._build_model()  # Initialize neural network
        self.episode_count = 0  # Track episodes
        
        self.folder_path = os.path.join(os.getcwd(), "models")
        self.load_model(self.folder_path)
    
    def _build_model(self):
        """Builds the DQN model."""
        model = keras.Sequential([
            keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(self.action_size, activation='linear')  # Output Q-values
        ])
        model.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model
    
    def _train(self):
        """Trains the model using experience replay."""
        if len(self.memory) < self.batch_size:
            return
        
        # Only train every 20 steps to reduce computational load
        if len(self.memory) % 20 != 0:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action_index, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target += self.gamma * np.max(self.model.predict(next_state, verbose=0)[0])
            target_q_values = self.model.predict(state, verbose=0)
            target_q_values[0][action_index] = target
            self.model.fit(state, target_q_values, epochs=1, verbose=0)
            
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def end_episode(self):
        """Called at the end of each episode to increment episode count and save model if needed."""
        self.episode_count += 1
        
        # Save model every 25 episodes
        if self.episode_count % 25 == 0:
            self.save_model(self.folder_path)
    
    def save_model(self, folder_path: str):
        # Ensure the directory exists before saving
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        model_file = os.path.join(folder_path, f"dqn_model_episode_{self.episode_count}.keras")
        # Save the model in .keras format
        self.model.save(model_file)
        print(f"Model saved successfully at {folder_path} as dqn_model_episode_{self.episode_count}.keras after {self.episode_count} episodes.")

    def load_model(self, folder_path: str):
        """Load the latest pre-trained DQN model."""
        if not os.path.exists(folder_path):
            print("No saved models found.")
            return
        
        model_files = [f for f in os.listdir(folder_path) if re.match(r'dqn_model_episode_\d+\.keras', f)]
        if not model_files:
            print("No valid model files found.")
            return
        
        latest_model = max(model_files, key=lambda f: int(re.search(r'\d+', f).group()))
        file_path = os.path.join(folder_path, latest_model)
        
        self.model = keras.models.load_model(file_path)
        print(f"DQN model loaded successfully from {file_path}.")
    
    def name(self):
        return "DQNDataPlacementAgent"
