import random

from Algorithms import AlgorithmBase, NoStorageAvailableException
from Storage import (
    StorageNodeType, 
    DataObject
)
from utils.Utility import format_data_size

class RandomSelection(AlgorithmBase):
    def apply(self, currentData: DataObject) -> StorageNodeType:
      """
          It always tries to write to the fastest storage node available.
      """
      # Start with the current optimization score
      self.currentObject = currentData

      possible_nodes = []

      required_capacity = currentData.size * self.replication_factor

      # Get the list of storage nodes
      if self.sys.get_available_capacity(StorageNodeType.FAST) >= required_capacity:
          possible_nodes.append(StorageNodeType.FAST)

      if self.sys.get_available_capacity(StorageNodeType.MEDIUM) >= required_capacity:
          possible_nodes.append(StorageNodeType.MEDIUM)

      if self.sys.get_available_capacity(StorageNodeType.SLOW) >= required_capacity:
          possible_nodes.append(StorageNodeType.SLOW)

      if len(possible_nodes) == 0:
           raise NoStorageAvailableException(
            f"RandomSelection: No storage node available for data size: {format_data_size(required_capacity)} | "
            f"FAST: {format_data_size(self.sys.get_available_capacity(StorageNodeType.FAST))}, "
            f"MEDIUM: {format_data_size(self.sys.get_available_capacity(StorageNodeType.MEDIUM))}, "
            f"SLOW: {format_data_size(self.sys.get_available_capacity(StorageNodeType.SLOW))}"
        )
      else:
          return random.choice(possible_nodes)

    def name(self):
        return "RandomSelection"
        
        
