from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size

class HybridGreedy(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
        """
            It selects the best storage node based on a weighted combination of cost, speed, space, and reliability.
        """
        self.currentObject = currentData

        required_capacity = currentData.size * self.replication_factor

        # Define weights for each criterion (adjust as needed)
        weights = {
            "cost": 0.3,
            "process_time": 0.3,
            "space": 0.2,
            "availability": 0.2
        }

        # Get data for each storage node type
        scores = {}
        for node_type in [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]:
            cost = self.sys.cost(node_type)
            process_time = self.sys.process_time(node_type)
            space = self.sys.get_available_capacity(node_type)
            availability = self.sys.availability(node_type)

            # Calculate weighted score
            scores[node_type] = (
                weights["cost"] * (1 / cost) +  # Lower cost is better
                weights["process_time"] * process_time +  # Higher speed is better
                weights["space"] * space +  # More space is better
                weights["availability"] * availability  # Higher availability is better
            )

        # Sort nodes by score in descending order
        sorted_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Select the best storage node that has enough capacity
        for node_type, score in sorted_nodes:
            if self.sys.get_available_capacity(node_type) >= required_capacity:
                return node_type

        raise NoStorageAvailableException(
            f"HybridGreedy: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )

    def name(self):
        return "HybridGreedy"
