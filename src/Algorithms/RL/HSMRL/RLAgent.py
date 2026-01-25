"""
RL Agent for Hierarchical Storage Management

This module implements an RL agent for each tier using TD(λ) algorithm
as described in the HSM-RL paper (Zhang et al., 2022).
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from .FRBValueFunction import FRBValueFunction
from utils.logger import logger


class RLAgent:
    """
    Reinforcement Learning agent for a storage tier.
    
    The agent uses:
    - FRB value function approximation
    - TD(λ) algorithm for updating the value function
    """
    
    def __init__(self, tier_name: str, num_state_variables: int, 
                 learning_rate: float = 0.1, discount_factor: float = 0.9,
                 lambda_trace: float = 0.7, a_params: List[float] = None,
                 b_params: List[float] = None):
        """
        Initialize the RL agent.
        
        Args:
            tier_name (str): Name of the tier this agent manages
            num_state_variables (int): Number of state variables
            learning_rate (float): Learning rate α for TD(λ)
            discount_factor (float): Discount factor γ
            lambda_trace (float): Trace decay parameter λ
            a_params (List[float]): Hyperparameters a_j for FRB
            b_params (List[float]): Hyperparameters b_j for FRB
        """
        self.tier_name = tier_name
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.lambda_trace = lambda_trace
        
        # Initialize value function approximation
        self.value_function = FRBValueFunction(
            num_state_variables=num_state_variables,
            a_params=a_params,
            b_params=b_params
        )
        
        # Eligibility traces: E_n(s) for each state
        self.eligibility_traces: Dict[Tuple, float] = defaultdict(float)
        
        # Track state history for TD(λ) updates
        self.state_history: List[Tuple] = []  # List of state tuples
        self.reward_history: List[float] = []  # List of rewards
        self.response_times: Dict[Tuple, List[Tuple[float, float]]] = defaultdict(list)
        # response_times[state] = [(r_i, t_i), ...] where r_i is response time, t_i is arrival time
        
        # Current state
        self.current_state: Optional[Tuple] = None
        self.current_state_time: int = 0  # Time when we entered current state
        
    def get_value(self, state: np.ndarray) -> float:
        """
        Get the value function estimate for a state.
        
        Args:
            state (np.ndarray): State vector
            
        Returns:
            float: Value function estimate
        """
        return self.value_function.evaluate(state)
    
    def record_request(self, state: np.ndarray, response_time: float, 
                      request_time: int):
        """
        Record a request in the current state.
        
        Args:
            state (np.ndarray): Current state vector
            response_time (float): Response time for this request
            request_time (int): Arrival time of the request
        """
        state_tuple = tuple(state)
        self.response_times[state_tuple].append((response_time, request_time))
    
    def calculate_reward(self, state_tuple: Tuple, state_time: int) -> float:
        """
        Calculate reward R_n for a state.
        
        R_n = (1/X_n) * Σ(r_i * e^(-(t_n,i - t_n)))
        
        where:
        - X_n is the total number of requests in state s_n
        - r_i is the response time of request i
        - t_n,i is the arrival time of request i
        - t_n is the time we arrived at state s_n
        
        Args:
            state_tuple (Tuple): State tuple
            state_time (int): Time when we entered this state
            
        Returns:
            float: Calculated reward
        """
        if state_tuple not in self.response_times:
            return 0.0
        
        requests = self.response_times[state_tuple]
        X_n = len(requests)
        
        if X_n == 0:
            return 0.0
        
        reward_sum = 0.0
        for r_i, t_n_i in requests:
            # Exponential decay based on time difference
            time_diff = t_n_i - state_time
            decay = math.exp(-max(0, time_diff))  # Ensure non-negative
            reward_sum += r_i * decay
        
        return reward_sum / X_n
    
    def update_eligibility_trace(self, state_tuple: Tuple):
        """
        Update eligibility traces.
        
        E_n(s) = λγ * E_{n-1}(s) + 1(s = s_n)
        
        Args:
            state_tuple (Tuple): Current state
        """
        # Decay all traces
        for state in self.eligibility_traces:
            self.eligibility_traces[state] *= self.lambda_trace * self.gamma
        
        # Add 1 to current state trace
        self.eligibility_traces[state_tuple] += 1.0
    
    def update_value_function(self, next_state: np.ndarray, next_state_time: int):
        """
        Update the value function using TD(λ) algorithm.
        
        v̂(s) = v̂(s) + α * (R_n + γ * v̂(s_{n+1}) - v̂(s_n)) * E_n(s)
        
        Args:
            next_state (np.ndarray): Next state s_{n+1}
            next_state_time (int): Time when we enter next state
        """
        if self.current_state is None:
            return
        
        current_state_array = np.array(self.current_state)
        current_value = self.value_function.evaluate(current_state_array)
        next_value = self.value_function.evaluate(next_state)
        
        # Calculate reward for current state
        R_n = self.calculate_reward(self.current_state, self.current_state_time)
        
        # TD error
        td_error = R_n + self.gamma * next_value - current_value
        
        # Update value function for all states with non-zero eligibility traces
        for state_tuple, eligibility in self.eligibility_traces.items():
            if eligibility > 1e-10:  # Only update if trace is significant
                state_array = np.array(state_tuple)
                target = self.value_function.evaluate(state_array) + td_error
                
                # Update parameters using the eligibility-weighted TD error
                weights = self.value_function.get_rule_weights(state_array)
                weight_sum = np.sum(weights)
                
                if weight_sum > 0:
                    normalized_weights = weights / weight_sum
                    update = self.alpha * td_error * eligibility
                    self.value_function.p += update * normalized_weights
        
        # Clear response times for current state (they've been incorporated into reward)
        if self.current_state in self.response_times:
            del self.response_times[self.current_state]
    
    def transition_to_state(self, new_state: np.ndarray, new_state_time: int):
        """
        Transition to a new state and update the value function.
        
        Args:
            new_state (np.ndarray): New state vector
            new_state_time (int): Time when entering new state
        """
        new_state_tuple = tuple(new_state)
        
        # If we have a current state, update value function
        if self.current_state is not None:
            self.update_eligibility_trace(self.current_state)
            self.update_value_function(new_state, new_state_time)
        
        # Transition to new state
        self.current_state = new_state_tuple
        self.current_state_time = new_state_time
        self.state_history.append(new_state_tuple)
    
    def reset(self):
        """Reset the agent for a new episode."""
        self.eligibility_traces.clear()
        self.state_history.clear()
        self.reward_history.clear()
        self.response_times.clear()
        self.current_state = None
        self.current_state_time = 0
