class StorageMediumUnavailableException(Exception):
    """Custom exception to indicate the storage medium is unavailable."""
    pass

class InsufficientCapacityException(Exception):
    """Custom exception for insufficient capacity errors."""
    pass

class DataAlreadyExistsException(Exception):
    """Custom exception for trying to write data with an already existing ID."""
    pass

class DataNotFoundException(Exception):
    """Custom exception for data ID not found in storage medium."""
    pass

class StorageMediumFailureException(Exception):
    """Custom exception for storage medium failure."""
    pass

class StorageNodeFailureException(Exception):
    """Custom exception for storage node failure."""
    pass
class StorageNodeUnavailableException(Exception):
    """Exception raised when the storage node is unavailable."""
    pass