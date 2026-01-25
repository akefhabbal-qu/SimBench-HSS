"""
Fuzzy Rule Based (FRB) Value Function Approximation

This module implements the FRB function approximation for the state-value function
as described in the HSM-RL paper (Zhang et al., 2022).

The FRB function maps an input state s ∈ R^k to an output y ∈ R using a weighted
average of fuzzy rule outputs.
"""

import numpy as np
from typing import List, Dict, Tuple
import math


class FRBValueFunction:
    """
    Fuzzy Rule Based value function approximation.
    
    The function uses two fuzzy categories {Small, Large} for each state variable
    and computes the value as a weighted average of rule outputs.
    """
    
    def __init__(self, num_state_variables: int, num_rules: int = None, 
                 a_params: List[float] = None, b_params: List[float] = None):
        """
        Initialize the FRB value function.
        
        Args:
            num_state_variables (int): Number of state variables (k)
            num_rules (int): Number of fuzzy rules (N). Defaults to 2^k
            a_params (List[float]): Hyperparameters a_j for membership functions
            b_params (List[float]): Hyperparameters b_j for membership functions
        """
        self.k = num_state_variables
        
        # Number of rules: 2^k (each variable can be Small or Large)
        self.N = num_rules if num_rules is not None else 2 ** num_state_variables
        
        # Initialize output parameters p_i for each rule
        self.p = np.zeros(self.N)
        
        # Initialize hyperparameters for membership functions
        if a_params is None:
            # Default: a_j = 1.0 for all variables
            self.a = np.ones(num_state_variables)
        else:
            self.a = np.array(a_params)
            
        if b_params is None:
            # Default: b_j = 1.0 for all variables
            self.b = np.ones(num_state_variables)
        else:
            self.b = np.array(b_params)
    
    def membership_large(self, x_j: float, j: int) -> float:
        """
        Calculate membership function for 'Large' category.
        
        μLarge(xj) = 1 / (1 + a_j * e^(-b_j * xj))
        
        Args:
            x_j (float): Input value for variable j
            j (int): Index of the state variable
            
        Returns:
            float: Membership value in [0, 1]
        """
        exponent = -self.b[j] * x_j
        # Prevent overflow
        if exponent > 700:
            return 1.0
        return 1.0 / (1.0 + self.a[j] * math.exp(exponent))
    
    def membership_small(self, x_j: float, j: int) -> float:
        """
        Calculate membership function for 'Small' category.
        
        μSmall(xj) = 1 - μLarge(xj)
        
        Args:
            x_j (float): Input value for variable j
            j (int): Index of the state variable
            
        Returns:
            float: Membership value in [0, 1]
        """
        return 1.0 - self.membership_large(x_j, j)
    
    def get_rule_weights(self, state: np.ndarray) -> np.ndarray:
        """
        Calculate weights for all rules given a state.
        
        For rule i, weight w_i(s) = ∏(j=1 to k) μ_{A_i^j}(x_j)
        where A_i^j is the fuzzy category (Small or Large) for variable j in rule i.
        
        Args:
            state (np.ndarray): State vector of length k
            
        Returns:
            np.ndarray: Array of weights for each rule
        """
        weights = np.ones(self.N)
        
        # For each rule, compute the product of memberships
        for i in range(self.N):
            # Determine which category (Small=0, Large=1) each variable belongs to in this rule
            # Rule i corresponds to binary representation of i
            for j in range(self.k):
                # Get the j-th bit of i to determine if variable j is Small (0) or Large (1)
                category = (i >> j) & 1
                
                if category == 0:  # Small
                    weights[i] *= self.membership_small(state[j], j)
                else:  # Large
                    weights[i] *= self.membership_large(state[j], j)
        
        return weights
    
    def evaluate(self, state: np.ndarray) -> float:
        """
        Evaluate the value function at a given state.
        
        v̂(s) = Σ(p_i * w_i(s)) / Σ(w_i(s))
        
        Args:
            state (np.ndarray): State vector of length k
            
        Returns:
            float: Approximated value function
        """
        weights = self.get_rule_weights(state)
        weight_sum = np.sum(weights)
        
        if weight_sum == 0:
            return 0.0
        
        # Weighted average of rule outputs
        value = np.sum(self.p * weights) / weight_sum
        return float(value)
    
    def update_parameters(self, state: np.ndarray, target: float, learning_rate: float):
        """
        Update the output parameters p_i using gradient descent.
        
        This is a simplified update. In practice, the TD(λ) algorithm updates
        the value function through eligibility traces, which is handled separately.
        
        Args:
            state (np.ndarray): State vector
            target (float): Target value (from TD update)
            learning_rate (float): Learning rate for parameter update
        """
        weights = self.get_rule_weights(state)
        weight_sum = np.sum(weights)
        
        if weight_sum == 0:
            return
        
        # Normalize weights
        normalized_weights = weights / weight_sum
        
        # Update each parameter proportionally to its weight
        current_value = self.evaluate(state)
        error = target - current_value
        
        self.p += learning_rate * error * normalized_weights
    
    def get_parameters(self) -> np.ndarray:
        """Get the current output parameters."""
        return self.p.copy()
    
    def set_parameters(self, p: np.ndarray):
        """Set the output parameters."""
        if len(p) != self.N:
            raise ValueError(f"Parameter array length {len(p)} does not match number of rules {self.N}")
        self.p = np.array(p)
