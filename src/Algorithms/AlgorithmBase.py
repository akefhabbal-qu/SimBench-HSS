from Storage import (
    HierarchicalStorageSystem, 
    MetricsCalculator, 
    DataObject,
)

class AlgorithmBase:
    def __init__(self, sys: HierarchicalStorageSystem):
        self.sys = sys
        self.metrics_calculator = MetricsCalculator(sys)
        self.replication_factor = sys.config["num_data_replica"]

    def apply(self, data: DataObject):
        """Method to be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden in subclasses.")
    
    def name(self):
        """Method to be overridden by subclasses."""
        raise NotImplementedError("This method should be overridden in subclasses.")
