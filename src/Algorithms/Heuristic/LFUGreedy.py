"""
LFU (Least Frequently Used) Greedy Placement Algorithm

This algorithm uses access frequency within a time window to determine
optimal storage tier placement. Frequently accessed data is placed in
faster tiers, while less frequently accessed data is placed in slower tiers.
"""

from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size
from utils.logger import logger


class LFUGreedy(AlgorithmBase):
    """
    LFU-based placement algorithm that uses access frequency to determine
    storage tier placement.
    
    The algorithm:
    1. Calculates access frequency for the data object within a time window
    2. Uses frequency thresholds to determine appropriate storage tier
    3. Places high-frequency data in FAST tier, low-frequency in SLOW tier
    """
    
    def __init__(self, sys, high_frequency_threshold: int = 5, medium_frequency_threshold: int = 2):
        """
        Initialize the LFU Greedy algorithm.
        
        Args:
            sys: The hierarchical storage system
            high_frequency_threshold (int): Minimum frequency for FAST tier placement
            medium_frequency_threshold (int): Minimum frequency for MEDIUM tier placement
        """
        super().__init__(sys)
        self.high_frequency_threshold = high_frequency_threshold
        self.medium_frequency_threshold = medium_frequency_threshold
    
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
        Determine the optimal storage tier based on access frequency.
        
        The algorithm uses the access frequency within the LFU time window to determine
        placement. Files with high frequency are placed in FAST tier, medium frequency
        in MEDIUM tier, and low frequency in SLOW tier.
        
        For new files that haven't been accessed yet, the frequency will be 0,
        so they will be placed in SLOW tier initially. As they are accessed more
        frequently, they can be migrated to faster tiers.
        
        Args:
            currentData (DataObject): The data object to place
            
        Returns:
            StorageNodeType: The selected storage tier
        """
        self.currentObject = currentData
        required_capacity = currentData.size * self.replication_factor
        
        # Get access frequency for this data object
        # The system will use its current timestamp if not provided
        # For new files that haven't been accessed yet, this will be 0
        # For files that were read before being written, this will reflect their frequency
        access_frequency = self.sys.get_access_frequency(currentData.id)
        
        logger.info(
            f"LFUGreedy: Data {currentData.id} has access frequency {access_frequency} "
            f"(thresholds: high={self.high_frequency_threshold}, medium={self.medium_frequency_threshold})"
        )
        
        # Determine placement based on frequency
        # Priority order based on frequency: FAST -> MEDIUM -> SLOW
        if access_frequency >= self.high_frequency_threshold:
            # High frequency: prefer FAST tier
            preferred_tiers = [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]
        elif access_frequency >= self.medium_frequency_threshold:
            # Medium frequency: prefer MEDIUM tier
            preferred_tiers = [StorageNodeType.MEDIUM, StorageNodeType.FAST, StorageNodeType.SLOW]
        else:
            # Low frequency: prefer SLOW tier (cost-effective)
            preferred_tiers = [StorageNodeType.SLOW, StorageNodeType.MEDIUM, StorageNodeType.FAST]
        
        # Try each tier in order of preference
        for node_type in preferred_tiers:
            if self.sys.get_available_capacity(node_type) >= required_capacity:
                logger.info(
                    f"LFUGreedy: Placing data {currentData.id} (frequency={access_frequency}) "
                    f"in {node_type.name} tier"
                )
                return node_type
        
        # If no tier has capacity, raise exception
        raise NoStorageAvailableException(
            f"LFUGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )
    
    def name(self) -> str:
        return "LFUGreedy"
