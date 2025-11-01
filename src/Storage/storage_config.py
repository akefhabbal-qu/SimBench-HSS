# storage_config.py

from .storage_types import StorageNodeType, StorageMediumType

KB = 1  # 1 KB
MB = 1024 * KB  # 1 MB = 1024 KB
GB = 1024 * MB  # 1 GB = 1024 MB
TB = 1024 * GB  # 1 TB = 1024 GB

# TODO: we need to use reasonable values for the storage medium configuration, we can measure if we don't find
STORAGE_MEDIUM_CONFIG = {
    StorageMediumType.NVMe: {
       "write_throughput": (1024, 3072),  # KB/ms
        "read_throughput": (1536, 3584),  # KB/ms
        "availability": 0.99, # 99%
        "durability": 3000,  # TBW
        "power_consumption": (5.5, 0.1),  # Active, Idle in watts
        "error_rate": 1e-15, # 1 error in 1 PB
        "capacity": 25 * GB,  # KB
        "read_latency": (0.1, 0.3),  # milliseconds
        "write_latency": (0.4, 0.6),  # milliseconds
        "delete_latency": (0.05, 0.1),  # milliseconds
    },
    StorageMediumType.SSD: {
        "write_throughput": (410, 512),  # KB/ms
        "read_throughput": (512, 614),  # KB/ms
        "availability": 0.95, # percent
        "durability": 1000,  # TBW
        "power_consumption": (3, 0.05),  # Active, Idle in watts
        "error_rate": 1e-14,
        "capacity": 50 * GB,  # KB
        "read_latency": (0.2, 0.4),  # milliseconds
        "write_latency": (0.5, 0.7),  # milliseconds
        "delete_latency": (0.1, 0.2),  # milliseconds
    },
    StorageMediumType.HDD: {
        "write_throughput": (102, 154),  # KB/ms
        "read_throughput": (123, 164),  # KB/ms
        "availability": 0.90, # percent
        "durability": 5,  # Years
        "power_consumption": (7, 1),  # Active, Idle in watts
        "error_rate": 1e-12,
        "capacity": 75 * GB,  # KB
        "read_latency": (1, 3),  # milliseconds
        "write_latency": (4, 6),  # milliseconds
        "delete_latency": (0.5, 1),  # milliseconds
    },
}

STORAGE_NODE_CONFIG = {
    StorageNodeType.FAST: {
        "read_cost": 0.0000004, # dollars per KB
        "write_cost": 0.0000005, # dollars per KB
        "delete_cost": 0.0000003, # dollars per KB
        "process_time": 500,  # milliseconds
        "inter_node_latency": 1000,  # milliseconds
        "network_speed": 1220703,  # KB/ms
        "availability": 0.99, # percent
        "failure_rate": 1e-15,  # 1 error in 1 PB
        "network_write_latency": 0.1,  # milliseconds
        "network_read_latency": 0.05,  # milliseconds
        "network_delete_latency": 0.02,  # milliseconds
    },
    StorageNodeType.MEDIUM: {
        "read_cost": 0.0000001, # dollars per KB
        "write_cost": 0.0000002, # dollars per KB
        "delete_cost": 0.0000001, # dollars per KB
        "process_time": 1000,  # milliseconds
        "inter_node_latency": 5000,  # milliseconds
        "network_speed": 610351,  # KB/ms
        "availability": 0.95, # percent
        "failure_rate": 1e-14, # 1 error in 1 EB
        "network_write_latency": 0.2,  # milliseconds
        "network_read_latency": 0.1,  # milliseconds
        "network_delete_latency": 0.05,  # milliseconds
    },
    StorageNodeType.SLOW: {
        "read_cost": 0.00000002, # dollars per KB
        "write_cost": 0.00000003, # dollars per KB
        "delete_cost": 0.00000001, # dollars per KB
        "process_time": 2000,  # milliseconds
        "inter_node_latency": 10000,  # milliseconds
        "network_speed": 122070,  # KB/ms
        "availability": 0.90, # percent
        "failure_rate": 1e-12, # 1 error in 1 TB
        "network_write_latency": 0.3,  # milliseconds
        "network_read_latency": 0.2,  # milliseconds
        "network_delete_latency": 0.1,  # milliseconds
    }
}

HIERARCHICAL_STORAGE_CONFIG = {
    "num_fast_nodes":3,
    "num_medium_nodes": 3,
    "num_slow_nodes": 3,
    "num_data_replica": 3,
}