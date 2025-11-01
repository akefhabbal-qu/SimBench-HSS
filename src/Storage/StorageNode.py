import numpy as np
from typing import List
from uuid import uuid4
from typing import Dict
import random

from .storage_config import STORAGE_NODE_CONFIG
from .exceptions import (
  StorageNodeUnavailableException, 
  StorageMediumUnavailableException,
  DataNotFoundException,
  StorageMediumFailureException,
  DataAlreadyExistsException,
  StorageNodeFailureException,
  InsufficientCapacityException
)
from .storage_types import StorageNodeType, DataObject, StorageMediumType
from .StorageMedium import StorageMedium
from utils.logger import logger
from utils.Utility import format_data_size

class StorageNode:
    def __init__(self, *, id= None, name, 
                 node_type: StorageNodeType, 
                 storage_mediums: List[StorageMedium],
                 baseline_response_time=5, # baseline response time in milliseconds
            ):
        """
        Initialize a storage node for a distributed storage system.

        Args:
            name (str): Name of the storage node.
            node_type (StorageNodeType): Type of the storage node (FAST, MEDIUM, SLOW).
            storage_mediums (list[StorageMedium]): List of storage mediums attached to the node.
        """
        config = STORAGE_NODE_CONFIG[node_type]

        self.id = id if id else uuid4()
        self.name = name
        self.type = node_type
        self._read_cost = config["read_cost"]
        self._write_cost = config["write_cost"]
        self._delete_cost = config["delete_cost"]
        self.process_time = config["process_time"]
        self.inter_node_latency = config["inter_node_latency"]
        self.network_speed = config["network_speed"]  # Network speed in Gbps
        self.availability = config["availability"]
        self.failure_rate = config["failure_rate"]
        self.network_write_latency = config["network_write_latency"]
        self.network_read_latency = config["network_read_latency"]
        self.network_delete_latency = config["network_delete_latency"]
        self.base_response_time = baseline_response_time
        
        self.is_available = True
        self.num_unavailable = 0  # Number of times the node has been unavailable
        self.num_reads = 0  # Number of read operations
        self.num_writes = 0  # Number of write operations
        self.num_deletes = 0  # Number of delete operations
        self.total_read_response_time = 0  # Total read latency
        self.total_write_response_time = 0  # Total write latency
        self.total_delete_response_time = 0  # Total delete latency

        self.storage_media = storage_mediums

        self.total_cost = 0

    def get_used_capacity(self):
        """Return the used storage capacity of the node."""
        return sum(medium.used_capacity for medium in self.storage_media)
    
    def get_total_capacity(self):
        """Return the total storage capacity of the node."""
        return sum(medium.capacity for medium in self.storage_media)

    def get_node_available_space(self):
        """
        Return the available storage capacity in the node in KB.
        """
        return sum(medium.get_available_space() for medium in self.storage_media)
    
    def get_error_response_time(self):
        """Simulate response time of the storage node."""
        return self.base_response_time
    
    def check_availability(self):
        """Simulate node availability."""
        is_available = np.random.choice([True, False], p=[self.availability, 1 - self.availability])
        logger.info(f"StorageNode: Node {self.name} availability: {is_available}")
        if not is_available:
            self.num_unavailable += 1
            raise StorageNodeUnavailableException(f"{self.type} storage node is currently unavailable.")
        
    def simulate_failure(self):
        """Simulate a random failure based on the failure rate."""
        is_failure = np.random.choice([True, False], p=[self.failure_rate, 1 - self.failure_rate])
        if is_failure:
            raise StorageNodeFailureException(f"A failure occurred on {self.type} storage node during the operation.")
        
    def write_data(self, data: DataObject, overwrite=False) -> float:
        """
        Simulate writing data to the storage node.
        Write or overwrite the data to one of the storage mediums with enough space.

        Args:
            data (Data): Data object containing the data attributes (id, size).
            overwrite (bool): If True, allows overwriting existing data.

        Raises:
            StorageTierUnavailableException: If the node is unavailable.
            ValueError: If the write request exceeds available capacity.
            DataAlreadyExistsException: If data exists and overwrite is False.
            InsufficientCapacityException: If there is not enough space.
        """
        self.check_availability()
        self.simulate_failure()

        old_data_size = 0
        if self.has_data(data.id):
            if not overwrite:
                raise DataAlreadyExistsException(f"StorageNode: data with ID {data.id} already exists on {self.name}.")
            
            # If overwriting, get the size of the existing data
            old_data_size = self.get_data(data.id).size

        size_diff = data.size - old_data_size
        if size_diff > 0 and size_diff > self.get_node_available_space():
            raise InsufficientCapacityException(
                f"StorageNode: Insufficient capacity on {self.name} to overwrite data {data.id}. "
                f"Additional required: {format_data_size(size_diff)}, Available: {format_data_size(self.get_node_available_space())}."
            )

        self.num_writes += 1
        logger.info(f"StorageNode: Writing{' (overwriting)' if overwrite else ''} data {data.id} to {self.name}.")

        suitable_storage_mediums: list[StorageMedium] = [
            medium for medium in self.storage_media if medium.get_available_space() + (old_data_size if medium.has_data(data.id) else 0) >= data.size
        ]

        medium_response_time = 0
        while suitable_storage_mediums:
            medium = random.choice(suitable_storage_mediums)
            try:
                medium_response_time += medium.write_data(data, overwrite=overwrite)
                logger.debug(
                    f"StorageNode: Data {data.id} written to {medium.name} on {self.name}. "
                    f"Used capacity: {format_data_size(self.get_used_capacity())}/{format_data_size(self.get_total_capacity())}. "
                    f"Available space: {format_data_size(self.get_node_available_space())}."
                )
                break
            except StorageMediumUnavailableException:
                logger.error(f"StorageNode: Medium {medium.name} unavailable for writing data {data.id}.")
                medium_response_time += medium.get_error_response_time()
            except StorageMediumFailureException:
                logger.error(f"StorageNode: Medium {medium.name} failed while writing data {data.id}.")
                medium_response_time += medium.get_error_response_time()

        # Simulate network transfer time based on network speed
        data_transfer_time = data.size / self.network_speed
        network_time = self.network_write_latency + data_transfer_time
        response_time = self.process_time + network_time + medium_response_time

        self.total_write_response_time += response_time
        self.total_cost += self._write_cost

        return response_time

    def has_data(self, data_id: str) -> bool:
        """Check if the data with the given ID is stored in this node."""
        for medium in self.storage_media:
            if medium.has_data(data_id):
                return True
        return False
    
    def read_data(self, data_id: str) -> float:
        """
        Simulate reading a data from the storage node.

        Args:
            simEnv: Simulation environment.
            data (Data): Data object containing the data attributes (id, data_size).

        Raises:
            StorageTierUnavailableException: If the node is unavailable.
            ValueError: If the read request exceeds stored capacity.

        Returns:
            float: Total time taken for the read operation.
        """
        
        self.check_availability()
        self.simulate_failure()

        if not self.has_data(data_id):
            raise DataNotFoundException(f"Data with ID {data_id} not found on node {self.name}.")

        self.num_reads += 1
        
        medium_response_time = 0

        media_has_data = [medium for medium in self.storage_media if medium.has_data(data_id)]
        while True:
            # Select a random storage medium with the data, it should always be one
            # as it is not allowed to store the same data's replicas on the same node
            medium: StorageMedium = random.choice(media_has_data)
            if medium.has_data(data_id):
                try: 
                    medium_response_time += medium.read_data(data_id)
                    break
                except StorageMediumUnavailableException as e:
                    logger.error(f"StorageNode: Error reading data {data_id} from medium: {medium.name} as it is not available.")
                    medium_response_time += medium.get_error_response_time()
                except StorageMediumFailureException as e:
                    logger.error(f"StorageNode: Error reading data {data_id} from medium: {medium.name} due to failure.")
                    medium_response_time += medium.get_error_response_time()

        dataObject: DataObject = self.get_data(data_id)
        logger.debug(f"StorageNode: Reading data {dataObject.id} from {self.name}.")
        # Simulate network transfer time based on network speed
        data_transfer_time = dataObject.size / self.network_speed  # Time in milliseconds
        network_time = self.network_read_latency + data_transfer_time
        # Node response time = process time + network time + medium response time
        response_time = self.process_time + network_time + medium_response_time
        self.total_read_response_time += response_time

        # the size of the data read is negligible
        self.total_cost += self._read_cost

        return response_time
    
    def get_data(self, data_id: str) -> DataObject:
        """Get the data object with the given ID."""
            
        for medium in self.storage_media:
            if medium.has_data(data_id):
                return medium.get_data(data_id)

        raise DataNotFoundException(f"Data with ID {data_id} not found on node {self.name}.")

    def delete_data(self, data_id: str) -> float:
        """
        Simulate deleting a data from the storage node.

        Args:
            simEnv: Simulation environment.
            data (Data): Data object containing the data attributes (id, data_size).

        Raises:
            StorageTierUnavailableException: If the node is unavailable.
            ValueError: If the data is not found on any medium.

        Returns:
            float: Total time taken for the delete operation.
        """

        self.check_availability()
        self.simulate_failure()

        if not self.has_data(data_id):
            raise DataNotFoundException(f"StorageNode: data with ID {data_id} not found on node {self.name}.")

        self.num_deletes += 1

        medium_response_time = 0

        media_contain_data = [medium for medium in self.storage_media if medium.has_data(data_id)]
        # Find and delete the data from all storage mediums
        while len(media_contain_data) > 0:
            # Select a random storage medium
            medium_contains_data: StorageMedium = np.random.choice(media_contain_data)
            try:
                medium_response_time += medium_contains_data.delete_data(data_id)
                media_contain_data.remove(medium_contains_data)
            except StorageMediumUnavailableException as e:
                logger.error(f"StorageNode: Error deleting data {data_id} from medium: {medium_contains_data.name} as it is not available.")
            except StorageMediumFailureException as e:
                logger.error(f"StorageNode: Error deleting data {data_id} from medium: {medium_contains_data.name} due to failure.")

        # Simulate network transfer time based on network speed
        # in delete there is no data transfer
        data_transfer_time = 0  # Time in milliseconds
        network_time = self.network_delete_latency + data_transfer_time
        # Node response time = process time + network time + medium response time
        response_time = self.process_time + network_time + medium_response_time
        self.total_delete_response_time += response_time

        self.total_cost += self._delete_cost

        return response_time

    def clear_storage(self):
        """
        Clear all data in the storage mediums of the node if it is available.

        Raises:
            StorageTierUnavailableException: If the node is unavailable.
        """
        self.check_availability()

        for medium in self.storage_media:
            medium.used_capacity = 0

    def reset(self):
        """Reset the node statistics."""
        self.num_reads = 0
        self.num_writes = 0
        self.num_deletes = 0
        self.total_read_response_time = 0
        self.total_write_response_time = 0
        self.total_delete_response_time = 0
        self.total_cost = 0
        
        for medium in self.storage_media:
            medium.reset()

if __name__ == "__main__":
    # Example usage
    storage_mediums = [
        StorageMedium(name="ssd_1", type=StorageMediumType.SSD),
        StorageMedium(name="ssd_2", type=StorageMediumType.SSD),
    ]
    node = StorageNode(name="Node1", node_type=StorageNodeType.FAST, storage_mediums=storage_mediums)
    logger.info(node.name)
    logger.info(node.type)
    logger.info(node.capacity)
    logger.info(node.used_capacity)
    logger.info(node.availability)
    logger.info(node.get_node_available_space())
    logger.info(node.check_availability())
    # logger.info(node.simulate_failures(simpy.Environment()))
    data_object = DataObject(id=1, size=10)
    # logger.info(node.write_data(simpy.Environment(), data_object))
    logger.info(node.has_data(10))
    logger.info(node.read_data(data_object.id))
    logger.info(node.delete_data(data_object))
    logger.info(node.clear_storage())