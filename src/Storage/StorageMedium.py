import numpy as np
import uuid
from typing import Dict

from utils.Utility import format_data_size, generate_file_size
from utils.logger import logger

from .exceptions import (
    StorageMediumUnavailableException,
    InsufficientCapacityException,
    DataAlreadyExistsException,
    DataNotFoundException,
    StorageMediumFailureException
)
from .storage_types import StorageMediumType
from .storage_config import STORAGE_MEDIUM_CONFIG
from .storage_types import DataObject

class StorageMedium:
    def __init__(self, *, name: str, type: StorageMediumType, baseline_response_time=5):
        config = STORAGE_MEDIUM_CONFIG[type]

        self.name = name
        self.storage_type = type
        self.read_latency = config["read_latency"]
        self.write_latency = config["write_latency"]
        self.delete_latency = config["delete_latency"]
        self.write_throughput = config["write_throughput"]
        self.read_throughput = config["read_throughput"]
        self.availability = config["availability"]
        self.durability = config["durability"]
        self.power_consumption = config["power_consumption"]
        self.error_rate = config["error_rate"]
        self.capacity = config["capacity"] # Capacity in KB
        self.baseline_response_time = baseline_response_time

        self.used_capacity = 0  # Track used capacity (in KB)
        self.num_unavailable = 0  # Number of times the medium has been unavailable
        self.num_reads = 0  # Number of read operations
        self.num_writes = 0  # Number of write operations
        self.num_deletes = 0  # Number of delete operations
        self.total_read_response_time = 0  # Total read response time in milliseconds
        self.total_write_response_time = 0  # Total write response time in milliseconds
        self.total_delete_response_time = 0  # Total delete response time in milliseconds

        self.data_objects: Dict[str, DataObject] = {}  # Store data objects as {data_id: DataObject}

    def check_availability(self):
        """Simulate medium availability."""
        is_available = np.random.choice([True, False], p=[self.availability, 1 - self.availability])
        logger.info(f"StorageMedium: {self.name} storage availability: {is_available}")
        if not is_available:
            self.num_unavailable += 1
            raise StorageMediumUnavailableException(f"{self.name} storage medium is currently unavailable.")

    def simulate_failure(self):
        """Simulate a random failure based on the error rate."""
        is_failure = np.random.choice([True, False], p=[self.error_rate, 1 - self.error_rate])
        if is_failure:
            raise StorageMediumFailureException(f"A failure occurred on {self.storage_type} storage medium during the operation.")

    def get_error_response_time(self):
        """Simulate response time of the storage medium."""
        return self.baseline_response_time
    
    def has_data(self, data_id: str):
        """Check if the storage medium has data with the given ID."""
        return data_id in self.data_objects
    
    def get_available_space(self):
        """
        Calculate the available space on the storage medium.

        Returns:
            float: Available space in KB.
        """
        return self.capacity - self.used_capacity

    def write_data(self, data: DataObject, overwrite=False) -> float:
        """
        Simulate writing data to the storage medium.

        Args:
            data (DataObject): Data object containing id and size.
            overwrite (bool): If True, allows overwriting existing data.

        Returns:
            float: Time taken to write the data.

        Raises:
            DataAlreadyExistsException: If data exists and overwrite is False.
            InsufficientCapacityException: If not enough space to write or overwrite.
        """
        self.check_availability()
        self.simulate_failure()

        old_data_size = 0
        if data.id in self.data_objects:
            if not overwrite:
                raise DataAlreadyExistsException(f"StorageMedium: data with ID {data.id} already exists on {self.storage_type}.")
            
            old_data_size = self.data_objects[data.id].size

        size_diff = data.size - old_data_size
        if size_diff > 0 and self.get_available_space() < size_diff:
            raise InsufficientCapacityException(
                f"StorageMedium: Insufficient capacity on {self.name} to overwrite data {data.id}. "
                f"Required additional: {format_data_size(size_diff)}, Available: {format_data_size(self.get_available_space())}."
            )

        self.num_writes += 1

        # Adjust used capacity
        self.used_capacity += size_diff

        # Store or overwrite the data
        self.data_objects[data.id] = data

        # Simulate response time
        latency = np.random.uniform(self.write_latency[0], self.write_latency[1])
        throughput = np.random.uniform(self.write_throughput[0], self.write_throughput[1])
        response_time = latency + data.size / throughput
        self.total_write_response_time += response_time

        logger.info(
            f"StorageMedium: {'Overwritten' if overwrite else 'Written'} {format_data_size(data.size)} with ID {data.id} "
            f"response time: {response_time:.2f} ms to {self.storage_type}. "
            f"Used capacity: {format_data_size(self.used_capacity)}/{format_data_size(self.capacity)}. "
            f"Available space: {format_data_size(self.get_available_space())}."
        )

        return response_time

    def read_data(self, data_id: str) -> float:
        """
        Simulate reading data from the storage medium.
        :param data_id: ID of the data to retrieve.

        :return: Time taken to read the data.
        """

        self.check_availability()
        self.simulate_failure()

        self.num_reads += 1

        if data_id not in self.data_objects:
            raise DataNotFoundException(f"Data with ID {data_id} not found on {self.storage_type}.")
        
        dataObject: DataObject = self.data_objects[data_id]

        logger.debug(f"StorageMedium: Reading data with ID {dataObject.id} from {self.storage_type}.")

        data_size: int = dataObject.size

        # Read time based on the size of the data
        # response_time = latency + data_size / throughput (milliseconds)
        latency = np.random.uniform(self.read_latency[0], self.read_latency[1])  # Simulate write time
        throughput = np.random.uniform(self.read_throughput[0], self.read_throughput[1])  # Simulate throughput
        response_time = latency + data_size / throughput
        self.total_read_response_time += response_time
        
        logger.info(f"StorageMedium: Read data with ID {data_id} ({format_data_size(data_size)}) from {self.storage_type} response time {response_time} milliseconds. Remaining capacity: {format_data_size(self.used_capacity)}/{format_data_size(self.capacity)}.")

        return response_time

    def get_data(self, data_id) -> DataObject:
        """Get the data object with the given ID."""
        if not self.has_data(data_id):
            raise DataNotFoundException(f"Data with ID {data_id} not found on {self.storage_type}.")
        
        return self.data_objects[data_id]

    def delete_data(self, data_id) -> float:
        """
        Simulate deleting data from the storage medium.
        :param data_id: ID of the data to delete.

        :return: Time taken to delete the data.
        """

        self.check_availability()
        self.simulate_failure()

        self.num_deletes += 1

        if data_id not in self.data_objects:
            raise DataNotFoundException(f"Data with ID {data_id} not found on {self.storage_type}.")

        dataObj: DataObject = self.data_objects.pop(data_id)
        self.used_capacity -= dataObj.size

        latency = np.random.uniform(self.delete_latency[0], self.delete_latency[1])  # Simulate deletion time
        response_time = latency
        self.total_delete_response_time += response_time

        logger.info(f"StorageMedium: Deleted data with ID {data_id} ({format_data_size(dataObj.size)}) from {self.storage_type} response time {response_time} milliseconds. Used capacity: {format_data_size(self.used_capacity)}/{format_data_size(self.capacity)}.")

        return response_time

    def calculate_power_usage(self, *, active=True):
        """Calculate power usage based on activity state."""
        return self.power_consumption[0] if active else self.power_consumption[1]

    def reset(self):
        """Reset the storage medium's used capacity and clear all stored data."""
        self.data_objects.clear()
        self.used_capacity = 0
        logger.info(f"StorageMedium: {self.storage_type} storage reset. Capacity is now {format_data_size(self.capacity)}.")

# Example Usage
if __name__ == "__main__":
    # Create an NVMe storage medium
    nvme = StorageMedium(name="NVMe_1", type=StorageMediumType.NVMe)

    while True:
        # Simulate some operations
        try:
            logger.info(f"StorageMedium: Response time: {nvme.get_error_response_time()} ms")
            dataObject1 = DataObject(id=uuid.uuid4(), size=generate_file_size())
            dataObject2 = DataObject(id=uuid.uuid4(), size=generate_file_size())
            nvme.write_data(dataObject1)  # Write
            nvme.write_data(dataObject2)  # Write
            nvme.read_data("file_001")  # Read
            nvme.delete_data("file_001")  # Delete
            nvme.read_data("file_002")  # Read
            logger.info(f"StorageMedium: Power usage (active): {nvme.calculate_power_usage(active=True)} watts")
            logger.info(f"StorageMedium: Power usage (idle): {nvme.calculate_power_usage(active=False)} watts")
        except StorageMediumUnavailableException as e:
            logger.error(f"StorageMedium: Error: {e}")
        except InsufficientCapacityException as e:
            logger.error(f"StorageMedium: Error: {e}")
        except DataAlreadyExistsException as e:
            logger.error(f"StorageMedium: Error: {e}")
        except Exception as e:
            logger.error(f"StorageMedium: Error: {e}")

        # Reset storage
        # nvme.reset()
