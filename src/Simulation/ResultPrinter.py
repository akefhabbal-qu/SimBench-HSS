from Storage import HierarchicalStorageSystem
import Storage
import json

from Storage.MetricsCalculator import MetricsCalculator
from utils.logger import (
    resultLogger
)

from utils.Utility import format_data_size

class PrintResulter:
    def __init__(self, metrics_calculator: MetricsCalculator):
        self.metrics_calculator = metrics_calculator

    def log_results(self, algorithm_name: str):
        resultLogger.info(f"Simulation: Algorithm ({algorithm_name}).")

        self.log_system_metrics(algorithm_name)
        self.log_tiers_info()

    def log_system_metrics(self, algorithm_name: str):
        r = resultLogger

        # Compute all metrics
        total_cost = self.metrics_calculator.calculate_total_cost()
        total_read_response_time = self.metrics_calculator.calculate_total_read_response_time()
        total_write_response_time = self.metrics_calculator.calculate_total_write_response_time()
        total_delete_response_time = self.metrics_calculator.calculate_total_delete_response_time()
        total_response_time = total_read_response_time + total_write_response_time + total_delete_response_time

        total_num_unavailable = self.metrics_calculator.calculate_total_num_unavailability()
        total_num_successful_write = self.metrics_calculator.calculate_total_successful_write()
        total_num_unsuccessful_write = self.metrics_calculator.calculate_total_unsuccessful_write()
        total_num_successful_read = self.metrics_calculator.calculate_total_successful_read()
        total_num_unsuccessful_read = self.metrics_calculator.calculate_total_unsuccessful_read()
        total_num_reads = self.metrics_calculator.calculate_total_num_read_requests()
        total_num_writes = self.metrics_calculator.calculate_total_num_write_requests()
        total_num_deletes = self.metrics_calculator.calculate_total_num_delete_requests()

        optimization_function = self.metrics_calculator.optimization_function()
        
        # Calculate Estimated System Response (ESR)
        estimated_system_response = self.metrics_calculator.calculate_estimated_system_response()

        # CSV log
        r.log_to_csv({
            "algorithm": algorithm_name,
            "optimization_function": optimization_function,
            "estimated_system_response": estimated_system_response,
            "total_cost": total_cost,
            "total_response_time": total_response_time,
            "total_num_unavailable": total_num_unavailable,
            "total_num_successful_write": total_num_successful_write,
            "total_num_unsuccessful_write": total_num_unsuccessful_write,
            "total_num_successful_read": total_num_successful_read,
            "total_num_unsuccessful_read": total_num_unsuccessful_read,
        })

        # General summary
        r.info("\n\nSimulation Results:")
        r.info(f"Optimization Function: {optimization_function:.3f}")
        r.info(f"Estimated System Response (ESR): {estimated_system_response:.4f}")
        r.info(f"Total Cost: {total_cost} $")
        r.info(f"Total Response: {total_response_time:.3f} ms")
        r.info(f"Total Number of Unavailable Accesses: {total_num_unavailable}")
        r.info(f"Total Number of Successful Write: {total_num_successful_write}")
        r.info(f"Total Number of Unsuccessful Write: {total_num_unsuccessful_write}")
        r.info(f"Total Number of Successful Reads: {total_num_successful_read}")
        r.info(f"Total Number of Unsuccessful Reads: {total_num_unsuccessful_read}")

        storage_system: HierarchicalStorageSystem = self.metrics_calculator.sys  # assume it's attached

        r.info(f"Total Capacity: {format_data_size(storage_system.total_capacity())}")
        r.info(f"Total Available Capacity: {format_data_size(storage_system.get_sys_available_capacity())}")

        r.info(f"Total Read Latency: {total_read_response_time:.3f} ms")
        r.info(f"Total Write Latency: {total_write_response_time:.3f} ms")
        r.info(f"Total Delete Latency: {total_delete_response_time:.3f} ms")

        r.info(f"Total Number of Reads: {total_num_reads}")
        r.info(f"Total Number of Writes: {total_num_writes}")
        r.info(f"Total Number of Deletes: {total_num_deletes}")

        # Node-level stats
        for node in storage_system.node_manager.storage_nodes.values():
            r.info("\n\n")
            r.info(f"Node {node.name}:")
            r.info(f"Total Number of Reads: {node.num_reads}")
            r.info(f"Total Number of Writes: {node.num_writes}")
            r.info(f"Total Number of Deletes: {node.num_deletes}")
            r.info(f"Total Number of Unavailable Accesses: {node.num_unavailable}")
            r.info(f"Total Read Latency: {node.total_read_response_time:.3f} ms")
            r.info(f"Total Write Latency: {node.total_write_response_time:.3f} ms")
            r.info(f"Total Delete Latency: {node.total_delete_response_time:.3f} ms")
            r.info(f"Total Capacity: {format_data_size(node.get_total_capacity())}")
            r.info(f"Total Available Capacity: {format_data_size(node.get_node_available_space())}")

        r.info("\nSimulation complete.")

    def log_tiers_info(self):
        self.log_tiers_info_jsonl()
        r = resultLogger
        r.info("\n\nStorage Tiers Information:")

        tiers_info: dict[Storage.StorageNodeType, dict[str, any]] = self.metrics_calculator.get_tiers_capacities_info_with_data_objects()

        for tier_name, tier_info in tiers_info.items():
            r.info(f"\nTier: {tier_name}")
            r.info(f"Available Capacity: {format_data_size(tier_info['available_capacity'])}")
            r.info(f"Used Capacity: {format_data_size(tier_info['used_capacity'])}")
            r.info(f"Total Capacity: {format_data_size(tier_info['total_capacity'])}")
            r.info(f"Total Data Size: {format_data_size(tier_info['total_data_size'])}")
            r.info(f"Data Objects: {len(tier_info['data_objects'])}")
            
            for data_object in tier_info['data_objects']:
                data_object: Storage.DataObject = data_object
                r.info(f"  - id: {data_object.id} size: ({format_data_size(data_object.size)}) replicas size: ({format_data_size(data_object.size * 3)}) total_access: {data_object.get_total_accesses()} temp: {data_object.get_temperature()})")

        r.info("\nAll tiers information logged successfully.")

    def log_tiers_info_jsonl(self):
        tiers_info: dict[Storage.StorageNodeType, dict[str, any]] = self.metrics_calculator.get_tiers_capacities_info_with_data_objects()

        # Specify your output .jsonl file path
        jsonl_file = "tiers_info.jsonl"

        with open(jsonl_file, "w") as f:
            for tier_name, tier_info in tiers_info.items():
                # Build a dict for the tier
                tier_data = {
                    "tier_name": str(tier_name),
                    "available_capacity": tier_info['available_capacity'],
                    "used_capacity": tier_info['used_capacity'],
                    "total_capacity": tier_info['total_capacity'],
                    "total_data_size": tier_info['total_data_size'],
                    "data_objects_count": len(tier_info['data_objects']),
                    "data_objects": []
                }

                for data_object in tier_info['data_objects']:
                    data_object: Storage.DataObject = data_object
                    obj_data = {
                        "id": data_object.id,
                        "size": data_object.size,
                        "replicas_size": data_object.size * 3,
                        "total_access": data_object.get_total_accesses(),
                        "temperature": round(data_object.get_temperature(), 3)
                    }
                    tier_data["data_objects"].append(obj_data)

                # Write this tier as a JSON line
                f.write(json.dumps(tier_data) + "\n")

        print("All tiers information written to tiers_info.jsonl successfully.")


