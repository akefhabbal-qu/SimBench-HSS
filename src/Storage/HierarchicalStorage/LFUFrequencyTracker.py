"""
LFU (Least Frequently Used) Frequency Tracker

This module tracks access frequency for data objects within a time window.
Used by the LFU placement algorithm to make frequency-based placement decisions.
"""

from typing import Dict, List
from collections import defaultdict
from utils.logger import logger


class LFUFrequencyTracker:
    """
    Tracks access frequency for data objects within a time window.
    Used for frequency-based placement decisions.
    """
    
    def __init__(self, time_window: int = 1000):
        """
        Initialize the LFU frequency tracker.
        
        Args:
            time_window (int): The time duration (in simulation time units) to consider
                              when calculating access frequency. Only accesses within
                              this window are counted.
        """
        self.time_window = time_window
        # Track access history: data_id -> list of (timestamp, access_type) tuples
        self.access_history: Dict[str, List[tuple[int, str]]] = defaultdict(list)
    
    def record_access(self, data_id: str, timestamp: int, access_type: str = "read"):
        """
        Record an access to a data object.
        
        Args:
            data_id (str): The ID of the data object being accessed
            timestamp (int): The current simulation timestamp
            access_type (str): Type of access - "read" or "write"
        """
        self.access_history[data_id].append((timestamp, access_type))
        # Clean up old access records outside the time window
        self._cleanup_old_accesses(data_id, timestamp)
    
    def _cleanup_old_accesses(self, data_id: str, current_timestamp: int):
        """
        Remove access records that are outside the time window.
        
        Args:
            data_id (str): The ID of the data object
            current_timestamp (int): The current simulation timestamp
        """
        cutoff_time = current_timestamp - self.time_window
        self.access_history[data_id] = [
            (ts, acc_type) for ts, acc_type in self.access_history[data_id]
            if ts >= cutoff_time
        ]
    
    def get_access_frequency(self, data_id: str, current_timestamp: int) -> int:
        """
        Calculate the access frequency for a data object within the time window.
        
        Args:
            data_id (str): The ID of the data object
            current_timestamp (int): The current simulation timestamp
            
        Returns:
            int: The number of read/write accesses within the time window
        """
        if data_id not in self.access_history:
            return 0
        
        # Clean up old accesses first
        self._cleanup_old_accesses(data_id, current_timestamp)
        
        # Count read and write accesses within the time window
        return len(self.access_history[data_id])
    
    def reset(self):
        """Reset the access history."""
        self.access_history.clear()
        logger.info("LFU Frequency Tracker: Reset access history.")
    
    def set_time_window(self, time_window: int):
        """
        Update the time window for frequency calculation.
        
        Args:
            time_window (int): New time window duration
        """
        self.time_window = time_window
        logger.info(f"LFU Frequency Tracker: Time window updated to {time_window}")
