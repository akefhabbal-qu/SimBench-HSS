from ..storage_types import StorageNodeType
from .NodeManager import NodeManager

class CapacityManager:
    def __init__(self, node_manager: NodeManager):
        self.node_manager = node_manager

    def get_available_capacity(self, node_type: StorageNodeType) -> int:
        return sum(node.get_node_available_space() for node in self.node_manager.get_nodes(node_type))

    def has_sufficient_capacity(self, node_type: StorageNodeType, data_size: int) -> bool:
        return self.get_available_capacity(node_type) >= data_size

    def get_nodes_capacity(self, node_type: StorageNodeType) -> int:
        return sum(node.get_total_capacity() for node in self.node_manager.get_nodes(node_type))

    def get_used_storage_size(self, node_type: StorageNodeType) -> int:
        return sum(node.get_used_capacity() for node in self.node_manager.get_nodes(node_type))

    def total_capacity(self) -> int:
        return sum(node.get_total_capacity() for node in self.node_manager.get_all_nodes())

    def get_sys_available_capacity(self) -> int:
        return sum(node.get_node_available_space() for node in self.node_manager.get_all_nodes())

    def get_utilization(self, node_type: StorageNodeType) -> float:
        """
        Calculate the utilization of the specified node type.

        RETURN: The utilization percentage of the specified node type.
        """
        return self.get_used_storage_size(node_type) / self.get_nodes_capacity(node_type)
    
    