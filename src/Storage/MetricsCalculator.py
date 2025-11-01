import Storage.HierarchicalStorage as HierarchicalStorageSystem
from utils.logger import logger

class MetricsCalculator:

    def __init__(self, sys: HierarchicalStorageSystem):
        self.sys = sys
        self.alpha = 1
        self.beta = 1
        self.gamma = 1
        self.delta = 1
    
    def calculate_total_available_capacity(self):
        total_available_capacity = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_available_capacity += node.get_node_available_space()
        
        return total_available_capacity

    def calculate_total_read_response_time(self):
        total_read_response_time = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_read_response_time += node.total_read_response_time
        
        return total_read_response_time
    
    def calculate_total_write_response_time(self):
        total_write_response_time = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_write_response_time += node.total_write_response_time
        
        return total_write_response_time
    
    def calculate_total_delete_response_time(self):
        total_delete_response_time = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_delete_response_time += node.total_delete_response_time
        
        return total_delete_response_time
    
    def calculate_total_read(self):
        total_read = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_read += node.num_reads
        
        return total_read
    
    def calculate_total_write(self):
        total_write = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_write += node.num_writes
        
        return total_write
    
    def calculate_total_delete(self):
        total_delete = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_delete += node.num_deletes
        
        return total_delete
    
    def calculate_current_total_read_time(self):
        """
        Calculate the total response time of the system by trying to read all the files 
        from all the nodes then summing up the time taken to read each file.
        """
        total_read_response_time = 0

        # Get all the data objects and their corresponding nodes
        for data_id, nodes_ids in self.sys.data_manager.data_to_nodes.items():
            # Read the data from all the nodes
            for node_id in nodes_ids:
                node = self.sys.node_manager.storage_nodes.get(node_id)
                try:
                    total_read_response_time += node.read_data(data_id)
                except Exception as e:
                    logger.error(f"MetricsCalculator: Error during read: {e}")
        
        return total_read_response_time
    
    def calculate_total_num_replicas(self):
        total_replicas = 0

        for file_id, nodes in self.sys.data_manager.data_to_nodes.items():
            total_replicas += len(nodes)
        
        return total_replicas
    
    def calculate_total_num_unavailability(self):
        total_unavailability = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_unavailability += node.num_unavailable
        
        return total_unavailability
    
    def calculate_total_num_read_requests(self):
        total_read_requests = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_read_requests += node.num_reads
        
        return total_read_requests
    
    def calculate_total_num_write_requests(self) -> int:
        total_write_requests = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_write_requests += node.num_writes
        
        return total_write_requests
    
    def calculate_total_num_delete_requests(self) -> int:
        total_delete_requests = 0

        for node in self.sys.node_manager.storage_nodes.values():
            total_delete_requests += node.num_deletes
        
        return total_delete_requests
    
    def calculate_total_num_files(self) -> int:
        return len(self.sys.data_manager.data_objects)
    
    def calculate_metrics(self):
        total_cost = self.calculate_total_cost()

        total_read_response_time = self.calculate_total_read_response_time()
        total_write_response_time = self.calculate_total_write_response_time()
        total_delete_response_time = self.calculate_total_delete_response_time()
        total_response_time = total_read_response_time + total_write_response_time + total_delete_response_time
        
        total_read = self.calculate_total_read()
        total_write = self.calculate_total_write()
        total_delete = self.calculate_total_delete()
        total_access = total_read + total_write + total_delete

        total_unavailability = self.calculate_total_num_unavailability()

        total_served_files = self.calculate_total_successful_write()
        total_not_served_files = self.calculate_total_unsuccessful_write()

        return total_cost, total_response_time, total_unavailability, total_served_files, total_not_served_files

    def optimization_function(self) -> float:
        total_cost, total_response_time, total_unavailability, total_served_files, total_not_served_files = self.calculate_metrics()

        cost_normalizer = 1
        response_time_normalizer = 1

        normalized_cost = total_cost / cost_normalizer
        normalized_response_time = total_response_time / response_time_normalizer

        O = (self.alpha * normalized_cost) + \
            (self.beta * normalized_response_time) + \
            (self.delta * total_unavailability) - \
            (self.gamma * total_served_files) + \
            (self.gamma * total_not_served_files)

        return O
    
    def calculate_total_successful_write(self) -> int:
        return self.sys.get_num_successful_write()
    
    def calculate_total_unsuccessful_write(self) -> int:
        return self.sys.get_num_unsuccessful_write()
    
    def calculate_total_successful_read(self) -> int:
        return self.sys.get_num_successful_read()
    
    def calculate_total_unsuccessful_read(self) -> int:
        return self.sys.get_num_unsuccessful_read()
    
    def calculate_total_cost(self) -> float:

        total_cost = 0

        node_types = self.sys.get_node_types()

        for node_type in node_types:
            total_cost += self.sys.calculate_total_cost_by_node(node_type)

        return total_cost
    
    def get_tiers_capacities_info_with_data_objects(self) -> dict:
        """
        Get the available capacity for each storage node type along with the data objects stored in them.

        :return: A dictionary with storage node types as keys and a tuple of available capacity and data objects as values.
        """

        tiers_capacities_info = self.sys.node_manager.get_tiers_capacity_info()
        data_objects = self.sys.data_manager.get_all_tiers_data_objects()

        for node_type, capacities in tiers_capacities_info.items():
            available_capacity = capacities["available_capacity"]
            used_capacity = capacities["used_capacity"]
            total_capacity = capacities["total_capacity"]

            tiers_capacities_info[node_type] = {
                "available_capacity": available_capacity,
                "used_capacity": used_capacity,
                "total_capacity": total_capacity,
                "total_data_size": sum(x.size for x in data_objects.get(node_type, [])),
                "data_objects": data_objects.get(node_type, [])
            }

        return tiers_capacities_info
    
    def calculate_estimated_system_response(self) -> float:
        """
        Calculate the Estimated System Response (ESR) based on the provided formulas:
        
        ESR = 10 × Σ(tier1) + 2 × Σ(tier2) + 1 × Σ(tier3)
        where each tier sum = Σ(nr_est × res_est)
        
        nr_est = 10 × temp (estimated number of requests per file)
        res_est = size / 10000 (estimated response time per file)
        
        Args:
            None
            
        Returns:
            float: The estimated system response value
        """
        from .storage_types import StorageNodeType
        
        # Get all data objects organized by tier
        tiers_data = self.sys.data_manager.get_all_tiers_data_objects()
        
        # Tier weights as per the formula
        tier_weights = {
            StorageNodeType.FAST: 10,    # tier_1 (highest performance)
            StorageNodeType.MEDIUM: 2,   # tier_2 (medium performance) 
            StorageNodeType.SLOW: 1      # tier_3 (lowest performance)
        }
        
        total_esr = 0.0
        
        for node_type, data_objects in tiers_data.items():
            tier_weight = tier_weights.get(node_type, 1)
            tier_sum = 0.0
            
            for data_obj in data_objects:
                # Calculate estimated number of requests per file
                # Using the temperature from the data object
                temp = data_obj.get_temperature()
                nr_est = 10 * temp
                
                # Calculate estimated response time per file
                # Size is in KB, so we divide by 10000 as per formula
                res_est = data_obj.size / 10000
                
                # Add to tier sum: nr_est × res_est
                tier_sum += nr_est * res_est
            
            # Add weighted tier sum to total ESR
            total_esr += tier_weight * tier_sum
            
            logger.info(f"ESR calculation - {node_type.name} tier: "
                       f"weight={tier_weight}, files={len(data_objects)}, "
                       f"tier_sum={tier_sum:.4f}, weighted_sum={tier_weight * tier_sum:.4f}")
        
        logger.info(f"Total Estimated System Response (ESR): {total_esr:.4f}")
        return total_esr