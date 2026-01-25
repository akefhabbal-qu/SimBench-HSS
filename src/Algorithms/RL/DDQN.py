import random
import numpy as np
from tensorflow import keras
from collections import deque
import os
import re

from Storage import (
    HierarchicalStorageSystem
)
from .RLAgentBase import RLAgentBase

class DDQN(RLAgentBase):
    def __init__(self, sys: HierarchicalStorageSystem, gamma=0.9, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995, learning_rate=0.001, batch_size=32, memory_size=2000, target_update_freq=10):
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
        self.model = self._build_model()  # Primary Q-network
        self.target_model = self._build_model()  # Target Q-network
        self.update_target_model()  # Sync target model initially
        self.target_update_freq = target_update_freq  # Target update frequency counter
        self.train_step_counter = 0
        self.episode_count = 0  # Track episodes
        
        self.folder_path = os.path.join(os.getcwd(), "models")
        self.load_model(self.folder_path)
    
    def _build_model(self):
        """Builds the DDQN model."""
        model = keras.Sequential([
            keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(self.action_size, activation='linear')  # Output Q-values
        ])
        model.compile(loss='mse', optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate))
        return model
    
    def update_target_model(self):
        """Updates the target model weights to match the primary model."""
        self.target_model.set_weights(self.model.get_weights())
    
    def save_model(self, folder_path: str):
        """Saves both the model and target model."""
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        model_file = os.path.join(folder_path, f"ddqn_model_episode_{self.episode_count}.keras")
        target_model_file = os.path.join(folder_path, f"ddqn_target_model_episode_{self.episode_count}.keras")

        self.model.save(model_file)
        self.target_model.save(target_model_file)
        print(f"Models saved successfully at {folder_path} as ddqn_model_episode_{self.episode_count}.keras")
    
    def load_model(self, folder_path: str):
        """Load the latest pre-trained DDQN model."""
        if not os.path.exists(folder_path):
            print("No saved models found.")
            return
        
        model_files = [f for f in os.listdir(folder_path) if re.match(r'ddqn_model_episode_\d+\.keras', f)]
        if not model_files:
            print("No valid model files found.")
            return
        
        latest_model = max(model_files, key=lambda f: int(re.search(r'\d+', f).group()))
        latest_target_model = latest_model.replace("ddqn_model_", "ddqn_target_model_")
        
        self.model = keras.models.load_model(os.path.join(folder_path, latest_model))
        print(f"DDQN primary model loaded successfully from {latest_model}.")
        
        target_model_path = os.path.join(folder_path, latest_target_model)
        if os.path.exists(target_model_path):
            self.target_model = keras.models.load_model(target_model_path)
            print(f"DDQN target model loaded successfully from {latest_target_model}.")
    
    def _train(self):
        """Trains the model using experience replay with DDQN."""
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        for state, action_index, reward, next_state, done in minibatch:
            target_q_values = self.model.predict(state, verbose=0)
            target = reward
            
            if not done:
                best_action_index = np.argmax(self.model.predict(next_state, verbose=0)[0])
                target += self.gamma * self.target_model.predict(next_state, verbose=0)[0][best_action_index]
            
            target_q_values[0][action_index] = target
            self.model.fit(state, target_q_values, epochs=1, verbose=0)

        # Update the target model periodically
        self.train_step_counter += 1
        if self.train_step_counter % self.target_update_freq == 0:
            self.update_target_model()

        # Reduce exploration probability over time
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def end_episode(self):
        """Called at the end of each episode to increment episode count and save model if needed."""
        self.episode_count += 1
        
        # Save model every 25 episodes
        if self.episode_count % 25 == 0:
            self.save_model(self.folder_path)
    
    def name(self):
        return "DDQNDataPlacementAgent"
