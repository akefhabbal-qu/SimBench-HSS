from ..storage_types import StorageNodeType, DataObject
from ..storage_config import HIERARCHICAL_STORAGE_CONFIG
from .NodeManager import NodeManager
from .CapacityManager import CapacityManager
from .DataManager import DataManager
from utils.logger import logger
from utils.Utility import format_data_size
from ..MetricsCalculator import MetricsCalculator

class HierarchicalStorageSystem:
    def __init__(self):
        self.config = HIERARCHICAL_STORAGE_CONFIG
        self.node_manager = NodeManager(self.config)
        self.capacity_manager = CapacityManager(self.node_manager)
        self.data_manager = DataManager(self.node_manager, self.capacity_manager, HIERARCHICAL_STORAGE_CONFIG)
        
        self.metrics_calculator = None

    def initialize_metrics_calculator(self, metrics_calculator: MetricsCalculator):
        self.metrics_calculator = metrics_calculator

    # Node-related methods
    def get_nodes(self, node_type: StorageNodeType):
        return self.node_manager.get_nodes(node_type)

    def get_all_nodes(self):
        return self.node_manager.get_all_nodes()

    def add_node(self, node_type: StorageNodeType, node):
        self.node_manager.add_node(node_type, node)

    def delete_node(self, node_id: str):
        self.node_manager.delete_node(node_id)

    # Capacity-related methods
    def get_available_capacity(self, node_type: StorageNodeType):
        return self.capacity_manager.get_available_capacity(node_type)

    def has_sufficient_capacity(self, node_type: StorageNodeType, data_size: int):
        return self.capacity_manager.has_sufficient_capacity(node_type, data_size)

    def get_nodes_capacity(self, node_type: StorageNodeType):
        return self.capacity_manager.get_nodes_capacity(node_type)

    def get_used_storage_size(self, node_type: StorageNodeType):
        return self.capacity_manager.get_used_storage_size(node_type)

    def total_capacity(self):
        return self.capacity_manager.total_capacity()

    def get_sys_available_capacity(self):
        return self.capacity_manager.get_sys_available_capacity()

    # Data-related methods
    def has_data(self, data_id: str) -> bool:
        return self.data_manager.has_data(data_id)

    def write_to_node(self, node_type: StorageNodeType, data, timestamp: int):
        return self.data_manager.write_to_node(node_type, data, timestamp)

    def read_data(self, data_id: str, timestamp: int):
        return self.data_manager.read_data(data_id, timestamp)

    def delete_data(self, data_id: str, timestamp: int):
        return self.data_manager.delete_data(data_id, timestamp)

    def get_num_files(self):
        return self.data_manager.get_num_files()

    def get_num_successful_write(self):
        return self.data_manager.get_num_successful_write()
    
    def increment_num_unsuccessful_write(self):
        self.data_manager.increment_num_unsuccessful_write()

    def get_num_unsuccessful_write(self):
        return self.data_manager.get_num_unsuccessful_write()
    
    def get_num_successful_read(self):
        return self.data_manager.get_num_successful_read()
    
    def get_num_unsuccessful_read(self):
        return self.data_manager.get_num_unsuccessful_read()

    def get_num_replicas(self):
        return self.data_manager.get_num_replicas()

    def get_file_num_replicas(self, file_id: str):
        return self.data_manager.get_file_num_replicas(file_id)
    
    def print_system_architecture(self):
        logger.info("System Architecture:")
        for node_name, nodes in zip(["Fast", "Medium", "Slow"], [self.node_manager.fast_nodes, self.node_manager.medium_nodes, self.node_manager.slow_nodes]):
            logger.info(f"{node_name} Node:")
            for node in nodes:
                logger.info(f"  Node: {node.name}")
                logger.info(f"    Type: {node.type.name}")
                logger.info(f"    Process Time: {node.process_time}")
                logger.info(f"    Inter-node Latency: {node.inter_node_latency}")
                logger.info(f"    Availability: {node.availability}")
                logger.info("    Storage Mediums:")
                for medium in node.storage_media:
                    logger.info(f"      - {medium.name}: {format_data_size(medium.used_capacity)} used of {format_data_size(medium.capacity)}")

        logger.info("\n\n")

    def get_utilization(self, node_type: StorageNodeType) -> float:
        return self.capacity_manager.get_utilization(node_type)
    
    def cost(self, node_type: StorageNodeType) -> float:
        return self.node_manager.cost(node_type)
    
    def process_time(self, node_type: StorageNodeType) -> float:
        return self.node_manager.process_time(node_type)
    
    def availability(self, node_type: StorageNodeType) -> float:
        return self.node_manager.availability(node_type)
    
    def get_total_write_response_time_by_type(self, node_type: StorageNodeType) -> float:
        """Calculate the total write latency for a specific storage node type."""
        return sum(node.total_write_response_time for node in self.get_nodes(node_type))
    
    def get_total_read_response_time_by_type(self, node_type: StorageNodeType) -> float:
        """Calculate the total read latency for a specific storage node type."""
        return sum(node.total_read_response_time for node in self.get_nodes(node_type))
    
    def get_total_delete_response_time_by_type(self, node_type: StorageNodeType) -> float:
        """Calculate the total delete latency for a specific storage node type."""
        return sum(node.total_delete_response_time for node in self.get_nodes(node_type))

    def get_total_write_response_time(self) -> float:
        """Calculate the total write latency across all storage nodes."""
        return sum(node.total_write_response_time for node in self.node_manager.storage_nodes.values())
    
    def get_total_read_response_time(self) -> float:
        """Calculate the total read latency across all storage nodes."""
        return sum(node.total_read_response_time for node in self.node_manager.storage_nodes.values())
    
    def get_total_delete_response_time(self) -> float:
        """Calculate the total delete latency across all storage nodes."""
        return sum(node.total_delete_response_time for node in self.node_manager.storage_nodes.values())

    def calculate_current_total_read_time(self):
        return self.metrics_calculator.calculate_current_total_read_time()
    
    def calculate_total_num_unavailability(self):
        return self.metrics_calculator.calculate_total_num_unavailability()
    
    def calculate_total_num_replicas(self):
        return self.metrics_calculator.calculate_total_num_replicas()
    
    def calculate_total_num_files(self):
        return self.metrics_calculator.calculate_total_num_files()
    
    def calculate_total_num_read_requests(self):
        return self.metrics_calculator.calculate_total_num_read_requests()
    
    def calculate_total_num_write_requests(self):
        return self.metrics_calculator.calculate_total_num_write_requests()
    
    def calculate_total_num_delete_requests(self):
        return self.metrics_calculator.calculate_total_num_delete_requests()
    
    def optimization_function(self):
        return self.metrics_calculator.optimization_function()
    
    def calculate_total_cost_by_node(self, node_type: StorageNodeType) -> float:
        total_cost = 0

        for node in self.get_nodes(node_type):
            total_cost += node.total_cost

        return total_cost
    
    def get_node_types(self) -> list[StorageNodeType]:
        node_types = [StorageNodeType.FAST, StorageNodeType.MEDIUM, StorageNodeType.SLOW]

        return node_types
    
    def reset(self):
        self.data_manager.reset()
        self.node_manager.reset()

    def generate_data(self, data_id: str, size: int) -> DataObject:
        return self.data_manager.generate_data(data_id, size)


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