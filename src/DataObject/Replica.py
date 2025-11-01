from Storage import StorageNodeUnavailableException
from utils.Utility import generate_file_size

class Replica:
    def __init__(self, id=None):
        self.id = id if id else generate_file_size()
        self.unavailable_accesses = 0  # Tracks how often this replica is unavailable

    def access(self, env):
        """Simulate accessing this replica."""
        try:
            # Attempt to get response time from the storage tier
            response_time = self.storage_tier.get_response_time()
            yield env.timeout(response_time)
        except StorageNodeUnavailableException as e:
            # Increment unavailability count if the storage tier is unavailable
            self.unavailable_accesses += 1
            raise e
        