from uuid import uuid4
import math
import random

from utils.Utility import generate_file_importance

class File:
    def __init__(self, id=None, size=10, num_replicas=3):
        """
        Initialize a file with the given ID and size.

        Args:
            id (str): The ID of the file.
            size (int): The size of the file in KB.
            num_replicas (int): The number of replicas to create for the file.
        """
        self.id = id if id else uuid4()
        self.size = size  # Size in KB
        self.importance = generate_file_importance()  # hot, medium, cold

        self._num_write_access: int = 0
        self._num_read_access: int = 0
        self._num_delete_access: int = 0
        self._is_deleted: bool = True

        self.hotness_level = 0.0  # initialize as coldest
        self.last_access_time = 0  # last time it was accessed

    def is_file_deleted(self) -> bool:
        """Check if the file is marked as deleted."""
        return self._is_deleted
    
    def is_file_deleted(self) -> bool:
        """Check if the file is marked as deleted."""
        return self._is_deleted
    
    def increment_write_access(self, timestamp: int):
        """Increment the write access count."""
        self._num_write_access += 1
        self.update_on_request(timestamp)

    def increment_read_access(self, timestamp: int):
        """Increment the read access count."""
        self._num_read_access += 1
        self.update_on_request(timestamp)

    def increment_delete_access(self, timestamp: int):
        """Increment the delete access count and mark the file as deleted."""
        self._num_delete_access += 1
        self.update_on_request(timestamp)

    def mark_deleted(self):
        """Mark the file as deleted."""
        self._is_deleted = True

    def mark_written(self):
        """Mark the file as not deleted."""
        self._is_deleted = False
        
    def get_total_accesses(self):
        """Get the total number of accesses (reads + writes + deletes)."""
        return self._num_read_access + self._num_write_access + self._num_delete_access

    def update_on_request(self, timestamp: int):
        """
        Call this method whenever the file is accessed.
        It updates the hotness based on access behavior.
        """
        self.last_access_time = timestamp

        if self.hotness_level < 1.0:
            # If currently cold or warm, give a chance to become hot
            if random.random() < 0.01:
                self.hotness_level = 1.0  # become hot

    def decay_temperature(self, timestamp: int):
        """
        Call this periodically to decay temperature if idle.
        """
        if timestamp - self.last_access_time >= 5:
            self.hotness_level = max(0.0, self.hotness_level - 0.1)

    def get_temperature(self) -> float:
        """
        Compute the dynamic temperature based on access patterns and hotness level.
        """
        req_time = self.get_total_accesses()

        # Safe temperature computation
        exponent_temp = 0.01 * req_time
        if exponent_temp > 700:
            temperature = 1.0
        else:
            temperature = 1 - (0.5 / math.exp(exponent_temp))

        # Safe ratio computation
        exponent_ratio = 5 * ((self.size / 1000) * req_time)
        if exponent_ratio > 700:
            ratio = 1.0
        else:
            exp_val = math.exp(exponent_ratio)
            ratio = exp_val / (1 + exp_val)

        # Pick based on ratio condition
        dynamic_temp = temperature if ratio > 0.8 else ratio

        # Combine with explicit hotness_level:
        # Priority to manual hotness level if higher
        return max(dynamic_temp, self.hotness_level)