from typing import Dict, List
from ..StorageNode import StorageNode
from ..storage_types import StorageNodeType, DataObject
from ..exceptions import (
    DataAlreadyExistsException,
    DataNotFoundException,
    InsufficientCapacityException,
    StorageNodeUnavailableException,
    StorageNodeFailureException,
)
import random
from utils.logger import logger
from utils.Utility import format_data_size
from .NodeManager import NodeManager
from .CapacityManager import CapacityManager

class DataManager:
    def __init__(self, node_manager: NodeManager, capacity_manager: CapacityManager, config: dict):
        self.config = config
        
        self.node_manager = node_manager
        self.capacity_manager = capacity_manager
        
        self.data_to_nodes: Dict[str, List[str]] = {}  # data_id -> list of node_ids
        self.data_objects: Dict[str, DataObject] = {}  # data_id -> DataObject
        self.data_access_count: Dict[str, int] = {}
        
        self.__num_successful_write = 0
        self.__num_unsuccessful_write = 0
        self.__num_successful_read = 0
        self.__num_unsuccessful_read = 0

    def has_data(self, data_id: str) -> bool:
        return data_id in self.data_objects and not self.data_objects.get(data_id).is_file_deleted()

    def write_to_node(self, node_type: StorageNodeType, data: DataObject, timestamp: int) -> float:
        if self.has_data(data.id):
            current_node_type = self.node_manager.get_node_by_id(self.data_to_nodes[data.id][0]).type
            if current_node_type != node_type:
                total_response_time = self.delete_data(data.id, timestamp)
                logger.info(f"Data {data.id} has been deleted from {current_node_type.name} node, to be written to {node_type.name} node")
                total_response_time += self._write_new_data(node_type, data, timestamp)
                return total_response_time
            else:
                return self._overwrite_existing_data(node_type, data, timestamp)
        else:
            return self._write_new_data(node_type, data, timestamp)

    def _overwrite_existing_data(self, node_type: StorageNodeType, data_object: DataObject, timestamp: int) -> float:
        old_data = self.data_objects[data_object.id]
        old_data.increment_write_access(timestamp)

        size_diff = data_object.size - old_data.size
        num_replica = self.config["num_data_replica"]

        required_capacity = max(0, size_diff * num_replica)

        # Should not happen due to the check we did before storing the data, but let's be safe
        if required_capacity > 0 and not self.capacity_manager.has_sufficient_capacity(node_type, required_capacity):
            self.__num_unsuccessful_write += 1
            raise InsufficientCapacityException(
                f"Cannot overwrite data {data_object.id} in {node_type.name} node. Additional required: {format_data_size(required_capacity)}, "
                f"Available: {format_data_size(self.capacity_manager.get_available_capacity(node_type))}"
            )

        data_node_ids = [node_id for node_id in self.data_to_nodes[data_object.id]]
        total_response_time = 0

        while data_node_ids:
            node_id = random.choice(data_node_ids)
            node: StorageNode = self.node_manager.get_node_by_id(node_id)
            try:
                total_response_time += node.write_data(data=data_object, overwrite=True)
                data_node_ids.remove(node_id)
                logger.info(f"Overwritten data {data_object.id} on node {node.name}")
            except (StorageNodeUnavailableException, StorageNodeFailureException) as e:
                logger.error(f"DataManager: node {node.name} failed to overwrite file {data_object.id}: {str(e)}")
                total_response_time += node.get_error_response_time()

        self.__num_successful_write += 1
        old_data.size = data_object.size
        
        logger.info(f"Data {data_object.id} has been overwritten with new size {format_data_size(data_object.size)}.")
        return total_response_time

    def _write_new_data(self, node_type: StorageNodeType, data_object: DataObject, timestamp: int) -> float:
        # if the data already exists, but was marked as deleted, 
        # we increment the write access and mark it as not deleted
        if data_object.id in self.data_objects:
            self.data_objects[data_object.id].increment_write_access(timestamp)
            self.data_objects[data_object.id].mark_written()
        else:
            data_object.increment_write_access(timestamp)

        num_replica = self.config["num_data_replica"]
        required_capacity = num_replica * data_object.size

        # Should not happen due to the check we did before storing the data, but let's be safe
        if not self.capacity_manager.has_sufficient_capacity(node_type, required_capacity):
            self.__num_unsuccessful_write += 1
            raise InsufficientCapacityException(
                f"Insufficient capacity in {node_type.name} node for file {data_object.id}. Required: {format_data_size(required_capacity)}, "
                f"Available: {format_data_size(self.capacity_manager.get_available_capacity(node_type))}"
            )

        logger.info(
            f"Writing data {data_object.id} to {node_type.name} node. Required capacity: {format_data_size(required_capacity)}, "
            f"Available capacity: {format_data_size(self.capacity_manager.get_available_capacity(node_type))}"
        )

        self.data_access_count[data_object.id] = 1
        suitable_nodes = [node for node in self.node_manager.get_nodes(node_type) if node.get_node_available_space() >= data_object.size]

        data_written_to_node_ids = []
        total_nodes_response_time = 0
        while suitable_nodes and num_replica > 0:
            suitable_node = random.choice(suitable_nodes)
            try:
                total_nodes_response_time += suitable_node.write_data(data=data_object)
                data_written_to_node_ids.append(suitable_node.id)
                num_replica -= 1
                suitable_nodes.remove(suitable_node)
                logger.info(f"Data {data_object.id} written to node {suitable_node.name}")
            except (StorageNodeUnavailableException, StorageNodeFailureException) as e:
                logger.error(f"DataManager: node {suitable_node.name} error writing new data: {str(e)}")
                total_nodes_response_time += suitable_node.get_error_response_time()

        self.__num_successful_write += 1

        # this is new data that has not been written before, so we add it to the data_objects
        if not data_object.id in self.data_objects:
            self.data_objects[data_object.id] = data_object
        else:
            # if it already exists, we just update the size
            self.data_objects[data_object.id].size = data_object.size
        self.data_to_nodes[data_object.id] = data_written_to_node_ids
        
        data_object.mark_written()
        logger.info(f"Data {data_object.id} has been written with {len(data_written_to_node_ids)} replicas.")

        return total_nodes_response_time

    def read_data(self, data_id: str, timestamp: int) -> float:
        if not self.has_data(data_id):
            self.__num_unsuccessful_read += 1
            raise DataNotFoundException(f"Data {data_id} is not found for reading")

        self.data_objects[data_id].increment_read_access(timestamp)

        node_ids = self.data_to_nodes.get(data_id)
        self.data_access_count[data_id] += 1

        total_nodes_response_time = 0
        while True:
            node_id = random.choice(node_ids)
            node: StorageNode = self.node_manager.storage_nodes.get(node_id)
            try:
                total_nodes_response_time += node.read_data(data_id)
                logger.info(f"Data {data_id} read from node {node.name}")
                self.__num_successful_read += 1
                return total_nodes_response_time
            except (StorageNodeUnavailableException, StorageNodeFailureException) as e:
                logger.error(f"Node {node.name} error reading data: {str(e)}")
                total_nodes_response_time += node.get_error_response_time()

    def delete_data(self, data_id: str, timestamp: int) -> float:
        if not self.has_data(data_id):
            raise DataNotFoundException(f"DataManager: data {data_id} is not found for deletion")

        node_ids = self.data_to_nodes.pop(data_id)
        if not node_ids:
            raise DataNotFoundException(f"Data {data_id} is not found in any node for deletion, unexpected state")
        
        total_nodes_response_time = 0
        while node_ids:
            node_id = random.choice(node_ids)
            node: StorageNode = self.node_manager.storage_nodes.get(node_id)
            try:
                total_nodes_response_time += node.delete_data(data_id)
                logger.info(f"Data {data_id} deleted from node {node.name}")
                node_ids.remove(node_id)
            except (StorageNodeUnavailableException, StorageNodeFailureException) as e:
                logger.error(f"Node {node.name} error deleting data: {str(e)}")
                total_nodes_response_time += node.get_error_response_time()

        data_object = self.data_objects[data_id]
        data_object.increment_delete_access(timestamp)
        # self.data_objects.pop(data_id)
        data_object.mark_deleted()
        # self.data_access_count.pop(data_id)

        return total_nodes_response_time

    def get_num_files(self) -> int:
        return len(self.data_objects)

    def get_num_successful_write(self) -> int:
        return self.__num_successful_write

    def get_num_unsuccessful_write(self) -> int:
        return self.__num_unsuccessful_write
    
    def get_num_successful_read(self) -> int:
        return self.__num_successful_read
    
    def get_num_unsuccessful_read(self) -> int:
        return self.__num_unsuccessful_read

    def get_num_replicas(self) -> int:
        return sum(len(nodes) for nodes in self.data_to_nodes.values())

    def get_file_num_replicas(self, file_id: str) -> int:
        if file_id not in self.data_to_nodes:
            raise ValueError(f"Data {file_id} not found for getting number of replicas")
        return len(self.data_to_nodes[file_id])
    
    def generate_data(self, data_id: str, size: int) -> DataObject:
        """
        Generate a data object with the given ID and size.

        Args:
            data_id (str): The ID of the data.
            size (int): The size of the data in KB.
        """
        dataObject = DataObject(id=data_id, size=size)
        logger.info(
            f"HierarchicalStorageSystem: Generated data object {dataObject.id} size {format_data_size(dataObject.size)}."
        )
        return dataObject
    
    def reset(self):
        """
        Reset the data manager by clearing all data objects and access counts.
        """
        self.data_to_nodes.clear()
        self.data_objects.clear()
        self.data_access_count.clear()
        self.__num_successful_write = 0
        self.__num_unsuccessful_write = 0
        
        logger.info("DataManager: Reset all data objects and access counts.")

    def increment_num_unsuccessful_write(self):
        self.__num_unsuccessful_write += 1

    def get_tier_data(self, node_type: StorageNodeType) -> List[DataObject]:
        """
        Get all data objects stored in the specified node type.
        
        Args:
            node_type (StorageNodeType): The type of storage node to get data from.

        Returns:
            List[DataObject]: A list of data objects stored in the specified node type.
        """

        data_objects = []
        for data_id, node_ids in self.data_to_nodes.items():
            if any(self.node_manager.get_node_by_id(node_id).type == node_type for node_id in node_ids):
                data_objects.append(self.data_objects[data_id])
        return data_objects
    
    def get_all_tiers_data_objects(self) -> Dict[StorageNodeType, DataObject]:
        """
        Get all data objects stored in the system across all tiers.

        Returns:
            Dict[StorageNodeType, List[DataObject]]: A dictionary mapping each storage node type to a list of data objects.
        """
        tier_data_objects = {}
        for node_type in StorageNodeType:
            tier_data_objects[node_type] = self.get_tier_data(node_type)
        return tier_data_objects
