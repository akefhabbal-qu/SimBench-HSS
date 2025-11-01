import json

from .types import DataOperation
from DataObject import File
from Storage import (
    HierarchicalStorageSystem, 
    StorageNodeType,
    MetricsCalculator
)
from utils.logger import (
    logger,
)

from utils.StorageVisualizer import StorageVisualizer
from Algorithms.Heuristic import (
    TimeGreedy, 
    RandomSelection, 
    SpaceGreedy,
    CostGreedy,
    HybridGreedy,
    LoadBalancingGreedy
)
from Algorithms.RL import DQN, DDQN
from utils.Utility import format_data_size
from Algorithms import AlgorithmBase, NoStorageAvailableException
from .ResultPrinter import PrintResulter

class Simulator:
    def __init__(self, access_pattern_path: str):
        self.access_pattern = self.load_access_pattern(access_pattern_path)
        self.storage_system = HierarchicalStorageSystem()
        self.metrics_calculator = MetricsCalculator(self.storage_system)
        self.storage_system.initialize_metrics_calculator(self.metrics_calculator)

        self.storage_system.print_system_architecture()

        self.print_resulter = PrintResulter(self.metrics_calculator)

    def load_config(self, config_path: str):
        """Load simulation configuration from a JSON file."""
        with open(config_path, "r") as file:
            return json.load(file)

    def load_access_pattern(self, access_pattern_path: str):
        """Load file access pattern from a JSON Lines file."""
        try:
            access_pattern = []
            with open(access_pattern_path, "r") as file:
                for line in file:
                    try:
                        access_pattern.append(json.loads(line))  # Parse each line as a separate JSON object
                    except json.JSONDecodeError:
                        logger.error(f"Simulation: Error decoding JSON from line in access pattern file: {access_pattern_path}")
                        continue  # Skip any invalid lines
            return access_pattern
        except FileNotFoundError:
            logger.error(f"Simulation: Access pattern file not found: {access_pattern_path}")
            return []
        except Exception as e:
            logger.error(f"Simulation: Unexpected error loading access pattern: {e}")
            return []

    def generate_file(self, file_id: str, size: int) -> File:
        """
        Generate a file with the given ID and size.

        Args:
            file_id (str): The ID of the file.
            size (int): The size of the file in KB.
        """
        file = File(id=file_id, size=size)
        logger.info(
            f"Simulation: Generated file {file.id} size {format_data_size(file.size)}."
        )
        return file

    @staticmethod
    def run(access_pattern_path: str):
        """Run the simulation."""
        logger.info("Simulation: Running simulation.")
        
        algorithms = {
            # "TimeGreedy": TimeGreedy,
            # "Random": RandomSelection,
            # "SpaceGreedy": SpaceGreedy,
            # "CostGreedy": CostGreedy,
            # "HybridGreedy": HybridGreedy,
            # "LoadBalancingGreedy": LoadBalancingGreedy,
            "DQN": DQN,
            # "DDQN": DDQN
        }
        
        for name, algorithm in algorithms.items():
            Simulator.run_algorithm(access_pattern_path, algorithm)

    @staticmethod
    def run_algorithm(access_pattern_path: str, algorithm: AlgorithmBase):
        """Helper method to execute a given algorithm."""
        sim = Simulator(access_pattern_path)
        strategy: AlgorithmBase = algorithm(sim.storage_system)
        sim.execute_access_pattern(strategy)
        sim.print_resulter.log_results(strategy.name())

        types = [node_type.name for node_type in StorageNodeType]
        capacities = [sim.storage_system.get_nodes_capacity(node_type) for node_type in StorageNodeType]
        used_capacities = [sim.storage_system.get_used_storage_size(node_type) for node_type in StorageNodeType]
        # visualizer = StorageVisualizer(types, capacities, used_capacities, strategy.name())
        # visualizer.plot_storage_utilization()
        
    def execute_access_pattern(self, algorithm: AlgorithmBase):
        """Execute the file operations defined in the access pattern."""
        logger.info(f"\n\nSimulation: Executing access pattern using algorithm: {algorithm.name()}")
        for op in self.access_pattern:
            logger.info(f"\nSimulation: Executing operation: {op}")
            file_id: str = op.get("file_id", None)
            file_size: int = op.get("size", 100)  # Default size: 100 KB
            op_type = op.get("operation_type", None)
            op_time = op.get("time", 0) # Default time: 0 ms
            timestamp = op.get("operation_num", 0)  # Default timestamp: 0

            if file_id is None or op_type is None:
                logger.error("Simulation: Invalid operation format.")
                continue

            if op_type == DataOperation.READ.value:
                self._handle_read(file_id, timestamp)
            elif op_type == DataOperation.WRITE.value:
                file: File = self.generate_file(file_id, file_size)
                self._handle_write(file, algorithm, timestamp)
            elif op_type == DataOperation.DELETE.value:
                self._handle_delete(file_id, timestamp)

    def _handle_read(self, file_id: str, timestamp: int):
        """Handle a read operation on a file."""
        logger.info(f"Simulation: Reading file: {file_id}")
        try:
            self.storage_system.read_data(file_id, timestamp)
        except Exception as e:
            logger.info(f"Simulation: Error during read: {e}")

    def _handle_write(self, file: File, algorithm: AlgorithmBase, timestamp: int):
        """Handle a write operation on a file."""
        try: 
            node_type = algorithm.apply(file)
            logger.info(f"Simulation: Writing file: {file.id} to nodes type {node_type.name}")
        except NoStorageAvailableException as e:
            self.storage_system.increment_num_unsuccessful_write()
            logger.info(f"Simulation: No storage available for writing file: {e}")
            return
        except Exception as e:
            logger.info(f"Simulation: Error applying the algorithm: {e}")
            return
        
        try:
            self.storage_system.write_to_node(node_type, file, timestamp)
        except Exception as e:
            logger.info(f"Simulation: Error during write: {e}")

    def _handle_delete(self, file_id: str, timestamp: int):
        """Handle a delete operation on a file."""
        logger.info(f"Simulation: Deleting file: {file_id}")
        try:
            self.storage_system.delete_data(file_id, timestamp)
        except Exception as e:
            logger.error(f"Simulation: Error during delete: {e}")

# Example Usage
if __name__ == "__main__":
    sim = Simulator(
        access_pattern_path="access_pattern.json",
    )
    sim.run()
