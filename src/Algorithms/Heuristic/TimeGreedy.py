from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import StorageNodeType, DataObject
from utils.Utility import format_data_size

class TimeGreedy(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
        self.currentObject = currentData
        required_capacity = currentData.size * self.replication_factor

        # Priority order: FAST -> MEDIUM -> SLOW
        for node_type in [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]:
            if self.sys.get_available_capacity(node_type) >= required_capacity:
                return node_type

        # No suitable storage found
        raise NoStorageAvailableException(
            f"TimeGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )

    def name(self) -> str:
        return "TimeGreedy"
