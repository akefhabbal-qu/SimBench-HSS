from typing import List, Dict
from ..StorageNode import StorageNode
from ..storage_types import StorageNodeType, StorageMediumType
from ..storage_config import HIERARCHICAL_STORAGE_CONFIG
from ..StorageMedium import StorageMedium

class NodeManager:
    def __init__(self, config):
        self.config = config
        self.fast_nodes = self._init_nodes(StorageNodeType.FAST, StorageMediumType.NVMe, self.config["num_fast_nodes"])
        self.medium_nodes = self._init_nodes(StorageNodeType.MEDIUM, StorageMediumType.SSD, self.config["num_medium_nodes"])
        self.slow_nodes = self._init_nodes(StorageNodeType.SLOW, StorageMediumType.HDD, self.config["num_slow_nodes"])

        self.tier_types = [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]
        all_nodes = self.fast_nodes + self.medium_nodes + self.slow_nodes
        self.storage_nodes: Dict[str, StorageNode] = {node.id: node for node in all_nodes}

    def _init_nodes(self, node_type: StorageNodeType, medium_type: StorageMediumType, count: int) -> List[StorageNode]:
        return [
            StorageNode(
                name=f"{node_type.name.lower()}_node_{i}",
                node_type=node_type,
                storage_mediums=[StorageMedium(name=f"{node_type.name.lower()}_medium_{i}", type=medium_type)]
            )
            for i in range(count)
        ]
        
    def get_node_by_id(self, node_id: str) -> StorageNode:
        node = self.storage_nodes.get(node_id)
        if not node:
            raise ValueError(f"Invalid node id: {node_id}")
        return node

    def get_nodes(self, node_type: StorageNodeType) -> List[StorageNode]:
        if node_type == StorageNodeType.FAST:
            return self.fast_nodes
        elif node_type == StorageNodeType.MEDIUM:
            return self.medium_nodes
        elif node_type == StorageNodeType.SLOW:
            return self.slow_nodes
        else:
            raise ValueError(f"Invalid node type: {node_type}")

    def get_all_nodes(self) -> List[StorageNode]:
        return list(self.storage_nodes.values())

    def add_node(self, node_type: StorageNodeType, node: StorageNode):
        self.get_nodes(node_type).append(node)
        self.storage_nodes[node.id] = node

    def delete_node(self, node_id: str):
        node = self.storage_nodes.pop(node_id, None)
        if not node:
            raise ValueError(f"Invalid node id: {node_id}")
        nodes = self.get_nodes(node.type)
        nodes[:] = [n for n in nodes if n.id != node_id]

    def cost(self, node_type: StorageNodeType) -> float:
        """
        Calculate the cost of storing data on the specified node type.

        :param node_type: The type of storage node to calculate the cost for.
        :return: The cost of storing in the specified node type.
        """
        node = self.get_nodes(node_type)[0]

        if not node:
            raise ValueError(f"Invalid node type: {node_type}")
        
        return node._read_cost
    
    def process_time(self, node_type: StorageNodeType) -> float:
        """
        Calculate the speed of the specified node type.

        :param node_type: The type of storage node to calculate the speed for.
        :return: The speed of the specified node type.
        """
        node = self.get_nodes(node_type)[0]

        if not node:
            raise ValueError(f"Invalid node type: {node_type}")
        
        return node.process_time
    
    def availability(self, node_type: StorageNodeType) -> float:
        """
        Get the availability percentage of the highest node of the specified type.

        :param node_type: The type of storage node to calculate the availability for.
        :return: The availability percentage for the highest node of the specified type.
        """
        nodes = self.get_nodes(node_type)
        if not nodes:
            raise ValueError(f"No nodes found for node type: {node_type}")

        node: StorageNode = max(nodes, key=lambda n: n.get_node_available_space())

        return node.availability
    
    def get_tier_total_capacity(self, node_type: StorageNodeType) -> float:
        """
        Get the total capacity of the specified storage node type.
        :param node_type: The type of storage node to get the total capacity for.
        :return: The total capacity of the specified storage node type.
        """
        nodes = self.get_nodes(node_type)
        if not nodes:
            raise ValueError(f"No nodes found for node type: {node_type}")
        
        return sum(node.get_total_capacity() for node in nodes)
    
    def get_tier_available_capacity(self, node_type: StorageNodeType) -> float:
        """
        Get the available capacity of the specified storage node type.
        :param node_type: The type of storage node to get the available capacity for.
        :return: The available capacity of the specified storage node type.
        """
        nodes = self.get_nodes(node_type)
        if not nodes:
            raise ValueError(f"No nodes found for node type: {node_type}")
        
        return sum(node.get_node_available_space() for node in nodes)
    
    def get_tier_used_capacity(self, node_type: StorageNodeType) -> float:
        """
        Get the used capacity of the specified storage node type.
        :param node_type: The type of storage node to get the used capacity for.
        :return: The used capacity of the specified storage node type.
        """
        nodes = self.get_nodes(node_type)
        if not nodes:
            raise ValueError(f"No nodes found for node type: {node_type}")
        
        return sum(node.get_used_capacity() for node in nodes)
    
    def get_tiers_capacity_info(self) -> Dict[StorageNodeType, Dict[str, float]]:
        """
        Get the available capacity and used capacity for all storage node types.
        :return: A dictionary mapping each storage node type to its available capacity.
        """

        return {
            tier_type: {
                "available_capacity": self.get_tier_available_capacity(tier_type),
                "used_capacity": self.get_tier_used_capacity(tier_type),
                "total_capacity": self.get_tier_total_capacity(tier_type)
            }
            for tier_type in self.tier_types
        }
    
    def reset(self):
        """
        Reset the state of all storage nodes.
        """
        for node in self.storage_nodes.values():
            node.reset()