from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size

class LoadBalancingGreedy(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
            It always tries to write to the least loaded storage node.
        """
        self.currentObject = currentData

        required_capacity = currentData.size * self.replication_factor

        # Get current usage per storage node type
        usage = {
            StorageNodeType.FAST: self.sys.get_used_storage_size(StorageNodeType.FAST),
            StorageNodeType.MEDIUM: self.sys.get_used_storage_size(StorageNodeType.MEDIUM),
            StorageNodeType.SLOW: self.sys.get_used_storage_size(StorageNodeType.SLOW),
        }

        # Sort storage nodes by current usage (ascending order)
        sorted_nodes = sorted(usage.items(), key=lambda x: x[1])

        # Select the least loaded storage node that has enough capacity
        for node_type, load in sorted_nodes:
            if self.sys.get_available_capacity(node_type) >= required_capacity:
                return node_type

        raise NoStorageAvailableException(
            f"LoadBalancingGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )

    def name(self):
        return "LoadBalancingGreedy"
