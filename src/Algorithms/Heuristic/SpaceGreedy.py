from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size

class SpaceGreedy(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
            It always tries to write to the storage node with the most available space.
        """
        # Start with the current optimization score
        self.currentObject = currentData

        # Get available capacities for each storage node type
        capacities = {
            StorageNodeType.FAST: self.sys.get_available_capacity(StorageNodeType.FAST),
            StorageNodeType.MEDIUM: self.sys.get_available_capacity(StorageNodeType.MEDIUM),
            StorageNodeType.SLOW: self.sys.get_available_capacity(StorageNodeType.SLOW),
        }

        # Sort storage nodes by available space in descending order
        sorted_nodes = sorted(capacities.items(), key=lambda x: x[1], reverse=True)

        required_capacity = currentData.size * self.replication_factor

        # Select the storage node with the most available space that can fit the data
        for node, capacity in sorted_nodes:
            if capacity >= required_capacity:
                return node

        # If no storage node can accommodate the data, raise an error
        raise NoStorageAvailableException(
            f"SpaceGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )

    def name(self):
        return "SpaceGreedy"
