# from typing import Dict, List
# import random

# from .MetricsCalculator import MetricsCalculator
# from .StorageNode import StorageNode
# from .StorageMedium import StorageMedium
# from .storage_types import StorageNodeType, DataObject, StorageMediumType
# from .storage_config import HIERARCHICAL_STORAGE_CONFIG
# from .exceptions import (
#     StorageNodeUnavailableException, 
#     DataNotFoundException, 
#     DataAlreadyExistsException, 
#     InsufficientCapacityException,
#     StorageNodeFailureException
# )

# from utils.logger import logger
# from utils.Utility import format_data_size

# class HierarchicalStorageSystem:
#     def __init__(self):
#         """
#         A hierarchical storage system that manages storage nodes and data objects.

#         Attributes:
#             data_objects (Dict[str, List[str]]): Store data objects as map [data_id] = List[node_id].
#         """
#         self.config = HIERARCHICAL_STORAGE_CONFIG
#         self.fast_nodes = self._init_nodes(StorageNodeType.FAST, StorageMediumType.NVMe, self.config["num_fast_nodes"])
#         self.medium_nodes = self._init_nodes(StorageNodeType.MEDIUM, StorageMediumType.SSD, self.config["num_medium_nodes"])
#         self.slow_nodes = self._init_nodes(StorageNodeType.SLOW, StorageMediumType.HDD, self.config["num_slow_nodes"])


#         # Combine all nodes into a unified list for easy management
#         all_nodes = self.fast_nodes + self.medium_nodes + self.slow_nodes
#         self.storage_nodes: Dict[str, StorageNode] = {node.id: node for node in all_nodes}
        
#         # Store the data nodes that store a specific data object
#         self.data_to_nodes: Dict[str, List[str]] = {}  # Store data objects as map [data_id] = List[node_id]

#         # Store the data objects
#         self.data_objects: Dict[str, DataObject] = {}  # Store data objects as map [data_id] = DataObject
#         # self.data_access_count: Dict[str, int] = {}  # Store data access count as map [data_id] = int(number of access)
#         self.num_served_files = 0
#         self.num_not_served_files = 0
#         self.metrics_calculator: MetricsCalculator = None
        
#     def _init_nodes(self, node_type: StorageNodeType, medium_type: StorageMediumType, count: int) -> List[StorageNode]:
#         """Helper method to initialize nodes of a given type."""
#         return [
#             StorageNode(
#                 name=f"{node_type.name.lower()}_node_{i}",
#                 node_type=node_type,
#                 storage_mediums=[StorageMedium(name=f"{node_type.name.lower()}_medium_{i}", type=medium_type)]
#             )
#             for i in range(count)
#         ]


#     def initialize_metrics_calculator(self, metrics_calculator: MetricsCalculator):
#         self.metrics_calculator = metrics_calculator

#     def get_num_files(self) -> int:
#         return len(self.data_objects)
    
#     def get_num_served_files(self) -> int:
#         return self.num_served_files
    
#     def get_num_not_served_files(self) -> int:
#         return self.num_not_served_files

#     def get_num_replicas(self) -> int:
#         """Return the total number of replicas in the system."""
#         return sum([len(nodes) for nodes in self.data_to_nodes.values()])

#     def get_file_num_replicas(self, file_id: str) -> int:
#         """Return the number of replicas for the specified file."""
#         if file_id not in self.data_to_nodes:
#             raise ValueError(f"Data {file_id} is not found")
        
#         return len(self.data_to_nodes.get(file_id, []))

#     def print_system_architecture(self):
#         logger.info("System Architecture:")
#         for node_name, nodes in zip(["Fast", "Medium", "Slow"], [self.fast_nodes, self.medium_nodes, self.slow_nodes]):
#             logger.info(f"{node_name} Node:")
#             for node in nodes:
#                 logger.info(f"  Node: {node.name}")
#                 logger.info(f"    Type: {node.type.name}")
#                 logger.info(f"    Process Time: {node.process_time}")
#                 logger.info(f"    Inter-node Latency: {node.inter_node_latency}")
#                 logger.info(f"    Availability: {node.availability}")
#                 logger.info(f"    Storage Mediums:")
#                 for medium in node.storage_mediums:
#                     logger.info(f"      - {medium.name}: {format_data_size(medium.used_capacity)} used of {format_data_size(medium.capacity)}")

#         logger.info("\n\n")

#     def add_node(self, node_type: StorageNodeType, node: StorageNode):
#         self.get_nodes(node_type).append(node)
#         self.storage_nodes[node.id] = node
        
#     def delete_node(self, node_id: str):
#         node = self.storage_nodes.pop(node_id, None)
#         if not node:
#             raise ValueError(f"Invalid node id: {node_id}")
#         nodes = self.get_nodes(node.type)
#         nodes[:] = [n for n in nodes if n.id != node_id]

#     def has_data(self, data_id: str) -> bool:
#         return data_id in self.data_objects

#     def write_to_node(self, node_type: StorageNodeType, data: DataObject) -> float:
#         """Write a file to the specified node."""

#         if self.has_data(data.id):
#             raise DataAlreadyExistsException(f"Data {data.id} already exists in the system")

#         num_replica = self.config["num_data_replica"]
#         required_capacity = num_replica * data.size
     
#         if not self.has_sufficient_capacity(node_type, required_capacity):
#             self.num_not_served_files += 1
#             raise InsufficientCapacityException(f"Insufficient capacity in {node_type.name} node for file {data.id}. Required: {format_data_size(required_capacity)}, Available: {format_data_size(self.get_available_capacity(node_type))}")
        
#         logger.info(f"HierarchicalStorageSystem: Writing data {data.id} to {node_type.name} node. Required capacity: {format_data_size(required_capacity)}, Available capacity: {format_data_size(self.get_available_capacity(node_type))}")
    
#         self.data_access_count[data.id] = 1

#         # Get the list of nodes of the specified type with enough space
#         nodes: List[StorageNode] = [node for node in self.get_nodes(node_type) if node.get_node_available_space() >= data.size]
        
#         data_written_to_node_ids = []

#         total_nodes_response_time = 0
#         while len(nodes) > 0:
#             # Select a random node to write the data
#             node = random.choice(nodes)
#             logger.debug(
#                 f"HierarchicalStorageSystem: Writing data {data.id} to node {node.name}. "
#                 f"Available capacity: {format_data_size(node.get_node_available_space())}"
#             )
#             try:
#                 total_nodes_response_time += node.write_data(data=data)
#                 data_written_to_node_ids.append(node.id)
#                 num_replica -= 1
#                 nodes.remove(node)

#                 logger.info(f"HierarchicalStorageSystem: Data {data.id} written to node {node.name}")
#             except StorageNodeUnavailableException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} is unavailable. Need to try again.")
#                 total_nodes_response_time += node.get_error_response_time()
#             except StorageNodeFailureException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} has failed. Need to try again.")
#                 total_nodes_response_time += node.get_error_response_time()

#             if num_replica == 0:
#                 break
        
#         self.num_served_files += 1
#         logger.info(f"HierarchicalStorageSystem: Data {data.id} has {self.config['num_data_replica'] - num_replica} replicas.")

#         logger.info(f"HierarchicalStorageSystem: Data {data.id} has been written to {node_type.name} node. Nodes capacity: {format_data_size(self.get_available_capacity(node_type))}")

#         self.data_objects[data.id] = data
#         self.data_to_nodes[data.id] = data_written_to_node_ids

#         return total_nodes_response_time

#     def read_data(self, data_id: str) -> float:
#         """Read a data from the specified node."""

#         if not self.has_data(data_id):
#             raise DataNotFoundException(f"Data {data_id} is not found")
        
#         # Get the list of nodes that store the data
#         node_ids: List[str] = self.data_to_nodes.get(data_id)
#         self.data_access_count[data_id] += 1
        
#         total_nodes_response_time = 0
#         while True:
#             # Select a random node to read the data
#             node: StorageNode = self.storage_nodes.get(random.choice(node_ids))

#             try:
#                 total_nodes_response_time += node.read_data(data_id)
#                 logger.info(f"HierarchicalStorageSystem: Data {data_id} read from node {node.name}")

#                 return total_nodes_response_time # Exit the loop if data is read successfully
#             except StorageNodeUnavailableException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} is unavailable.")
#                 total_nodes_response_time += node.get_error_response_time()
#             except StorageNodeFailureException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} has failed.")
#                 total_nodes_response_time += node.get_error_response_time()

#     def increment_num_not_served_files(self):
#         self.num_not_served_files += 1

#     def delete_data(self, data_id: str) -> float:
#         """Delete a file from the specified node."""

#         if not self.has_data(data_id):
#             raise DataNotFoundException(f"Data {data_id} is not found")
        
#         # Get the list of nodes that store the data
#         node_ids = [node_id for node_id in self.data_to_nodes.get(data_id)]
        
#         self.data_access_count.pop(data_id)
#         self.data_objects.pop(data_id)
#         self.data_to_nodes.pop(data_id)

#         total_nodes_response_time = 0
#         while len(node_ids) > 0:
#             # Select a random node to delete the data
#             node_id: str = random.choice(node_ids)
#             node: StorageNode = self.storage_nodes.get(node_id)
            
#             try:
#                 total_nodes_response_time += node.delete_data(data_id)
#                 logger.info(f"HierarchicalStorageSystem: Data {data_id} deleted from node {node.name}")
#                 node_ids.pop(node_ids.index(node_id))
#             except StorageNodeUnavailableException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} is unavailable.")
#                 total_nodes_response_time += node.get_error_response_time()
#             except StorageNodeFailureException as e:
#                 logger.error(f"HierarchicalStorageSystem: Node {node.name} has failed.")
#                 total_nodes_response_time += node.get_error_response_time()

#         return total_nodes_response_time
        
#     def get_nodes(self, node_type: StorageNodeType) -> List[StorageNode]:
#         """Return the list of nodes of the specified type."""

#         if node_type == StorageNodeType.FAST:
#             return self.fast_nodes
#         elif node_type == StorageNodeType.MEDIUM:
#             return self.medium_nodes
#         elif node_type == StorageNodeType.SLOW:
#             return self.slow_nodes
#         else:
#             raise ValueError(f"Invalid node type: {node_type}")
        
#     def get_available_capacity(self, node_type: StorageNodeType) -> int:
#         """Return the total available capacity of the specified node type."""
#         return sum([node.get_node_available_space() for node in self.get_nodes(node_type)])
    
#     def get_utilization(self, node_type: StorageNodeType) -> float:
#         """
#         Calculate the utilization of the specified node type.

#         RETURN: The utilization percentage of the specified node type.
#         """
#         return self.get_used_storage_size(node_type) / self.get_nodes_capacity(node_type)
    
#     def has_sufficient_capacity(self, node_type: StorageNodeType, data_size: int) -> bool:
#         """Check if the specified node type has enough capacity to store the data."""
#         return self.get_available_capacity(node_type) >= data_size
    
#     def get_nodes_capacity(self, node_type: StorageNodeType) -> int:
#         """Return the total capacity of the specified node type."""
#         return sum([node.get_total_capacity() for node in self.get_nodes(node_type)])
    
#     def total_capacity(self) -> int:
#         return sum([node.get_total_capacity() for node in self.storage_nodes.values()])
    
#     def get_sys_available_capacity(self) -> int:
#         return sum([node.get_node_available_space() for node in self.storage_nodes.values()])
    
#     def get_used_storage_size(self, node_type: StorageNodeType) -> int:
#         """
#         Calculate the total used storage of the specified node type.

#         :param node_type: The type of storage node to calculate the used capacity for.
#         :return: The total used storage of the specified node type.
#         """
#         return sum([node.get_used_capacity() for node in self.get_nodes(node_type)])
    
#     def cost(self, node_type: StorageNodeType) -> float:
#         """
#         Calculate the cost of storing data on the specified node type.

#         :param node_type: The type of storage node to calculate the cost for.
#         :return: The cost of storing in the specified node type.
#         """
#         node = self.get_nodes(node_type)[0]

#         if not node:
#             raise ValueError(f"Invalid node type: {node_type}")
        
#         return node._read_cost
    
#     def process_time(self, node_type: StorageNodeType) -> float:
#         """
#         Calculate the speed of the specified node type.

#         :param node_type: The type of storage node to calculate the speed for.
#         :return: The speed of the specified node type.
#         """
#         node = self.get_nodes(node_type)[0]

#         if not node:
#             raise ValueError(f"Invalid node type: {node_type}")
        
#         return node.process_time
    
#     def availability(self, node_type: StorageNodeType) -> float:
#         """
#         Get the availability percentage of the specified node type.

#         :param node_type: The type of storage node to calculate the availability for.
#         :return: The availability percentage of the specified node type.
#         """
#         node: StorageNode = self.get_nodes(node_type)[0]

#         if not node:
#             raise ValueError(f"Invalid node type: {node_type}")
        
#         return node.availability
    
#     def get_total_write_response_time_by_type(self, node_type: StorageNodeType) -> float:
#         """Calculate the total write latency for a specific storage node type."""
#         return sum(node.total_write_response_time for node in self.get_nodes(node_type))

#     def get_total_read_response_time_by_type(self, node_type: StorageNodeType) -> float:
#         """Calculate the total read latency for a specific storage node type."""
#         return sum(node.total_read_response_time for node in self.get_nodes(node_type))

#     def get_total_delete_response_time_by_type(self, node_type: StorageNodeType) -> float:
#         """Calculate the total delete latency for a specific storage node type."""
#         return sum(node.total_delete_response_time for node in self.get_nodes(node_type))

#     def get_total_write_response_time(self) -> float:
#         """Calculate the total write latency across all storage nodes."""
#         return sum(node.total_write_response_time for node in self.storage_nodes.values())

#     def get_total_read_response_time(self) -> float:
#         """Calculate the total read latency across all storage nodes."""
#         return sum(node.total_read_response_time for node in self.storage_nodes.values())

#     def get_total_delete_response_time(self) -> float:
#         """Calculate the total delete latency across all storage nodes."""
#         return sum(node.total_delete_response_time for node in self.storage_nodes.values())

#     def calculate_current_total_read_time(self):
#         return self.metrics_calculator.calculate_current_total_read_time()
    
#     def calculate_total_num_unavailability(self):
#         return self.metrics_calculator.calculate_total_num_unavailability()
    
#     def calculate_total_num_replicas(self):
#         return self.metrics_calculator.calculate_total_num_replicas()
    
#     def calculate_total_num_files(self):
#         return self.metrics_calculator.calculate_total_num_files()
    
#     def calculate_total_num_read_requests(self):
#         return self.metrics_calculator.calculate_total_num_read_requests()
    
#     def calculate_total_num_write_requests(self):
#         return self.metrics_calculator.calculate_total_num_write_requests()
    
#     def calculate_total_num_delete_requests(self):
#         return self.metrics_calculator.calculate_total_num_delete_requests()
    
#     def optimization_function(self):
#         return self.metrics_calculator.optimization_function()
    
#     def calculate_total_cost_by_node(self, node_type: StorageNodeType) -> float:
#         total_cost = 0

#         for node in self.get_nodes(node_type):
#             total_cost += node.total_cost

#         return total_cost
    
#     def get_node_types(self) -> list[StorageNodeType]:
#         node_types = [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]

#         return node_types
    
#     def reset(self):
#         self.data_objects = {}
#         self.data_to_nodes = {}
#         self.data_access_count = {}
#         self.num_served_files = 0
#         self.num_not_served_files = 0

#         for node in self.storage_nodes.values():
#             node.reset()

#     def generate_data(self, data_id: str, size: int) -> DataObject:
#         """
#         Generate a data object with the given ID and size.

#         Args:
#             data_id (str): The ID of the data.
#             size (int): The size of the data in KB.
#         """
#         dataObject = DataObject(id=data_id, size=size)
#         logger.info(
#             f"HierarchicalStorageSystem: Generated data object {dataObject.id} size {format_data_size(dataObject.size)}."
#         )
#         return dataObject
    
# if __name__ == "__main__":
#     sys = HierarchicalStorageSystem()
#     metrics_calculator = MetricsCalculator(sys)
#     sys.print_system_architecture()

#     # Add a new node
#     new_node = StorageNode(
#         name="new_node",
#         node_type=StorageNodeType.FAST,
#         storage_mediums=[
#             StorageMedium(name="new_medium", type=StorageMediumType.NVMe)
#         ]
#     )
#     sys.add_node(type=StorageNodeType.FAST, node=new_node)
#     sys.print_system_architecture()

#     # Write a file to the system
#     dataObject = DataObject(id="file_001", size=500)
#     try:
#         sys.write_to_node(node_type=StorageNodeType.SLOW, data=dataObject)
#     except Exception as e:
#         logger.error(f"HierarchicalStorageSystem: Error during write: {e}")

#     try:
#         # Read the file from the system
#         sys.read_data(dataObject.id)
#     except Exception as e:
#         logger.error(f"HierarchicalStorageSystem: Error during read: {e}")

#     # Calculate total cost and response time
#     total_cost = metrics_calculator.calculate_total_cost()
#     total_response_time = metrics_calculator.calculate_current_total_read_time()
#     logger.info(f"Total Cost: {total_cost}")
#     logger.info(f"Total Response Time: {total_response_time}")