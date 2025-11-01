from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size

class CostGreedy(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
            It always tries to write to the cheapest storage node available.
        """
        # Start with the current optimization score
        self.currentObject = currentData

        required_capacity = currentData.size * self.replication_factor

        if self.sys.get_available_capacity(StorageNodeType.SLOW) >= required_capacity:
            return StorageNodeType.SLOW
        elif self.sys.get_available_capacity(StorageNodeType.MEDIUM) >= required_capacity:
            return StorageNodeType.MEDIUM
        elif self.sys.get_available_capacity(StorageNodeType.FAST) >= required_capacity:
            return StorageNodeType.FAST
        else:
             raise NoStorageAvailableException(
            f"CostGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )

    def name(self):
        return "CostGreedy"
        
        
