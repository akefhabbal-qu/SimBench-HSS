import numpy as np

def generate_file_size(start: float = 1.0, end: float = 1000.0):
    """Generate a file size in GB using a log-normal distribution, clamped to a specified range.

    Args:
        start (float): The minimum value for the file size range. Default is 1.0 GB.
        end (float): The maximum value for the file size range. Default is 1000.0 GB.

    Returns:
        float: A file size within the specified range.
    """
    if start <= 0 or end <= 0 or start >= end:
        raise ValueError("Start and end must be positive, with start < end.")

    FILE_SIZE_MEAN = 4  # Logarithmic mean (adjust for typical file size)
    FILE_SIZE_SIGMA = 1.5  # Logarithmic standard deviation (adjust for spread of file sizes)

    # Generate a log-normal value
    file_size = np.random.lognormal(FILE_SIZE_MEAN, FILE_SIZE_SIGMA)

    # Clamp the value to the specified range
    return max(start, min(file_size, end))

def generate_file_importance():
    """Generate a file importance based on a power-law (Zipf-like) distribution."""
    ZIPF_A = 2
    zipf_value = np.random.zipf(ZIPF_A)
    if zipf_value == 1:
        return 'hot'
    elif zipf_value == 2:
        return 'medium'
    else:
        return 'cold'

def generate_next_operation(num_files):
    """Generate the next read/write operation."""
    operation_type = np.random.choice(['read', 'write'], p=[0.7, 0.3])  # 70% reads, 30% writes
    file_id = np.random.randint(0, num_files)  # Choose a random file to operate on
    return operation_type, file_id

def calculate_optimization_value(cost, response_time, replicas, unavailability, alpha=1, beta=1, gamma=1, delta=1):
    """Calculate the normalized optimization value."""
    availability = 1 - unavailability

    C_max = 15000  # Maximum expected cost
    RT_max = 10    # Maximum expected response time
    R_max = 100    # Maximum number of replicas

    optimization_value = (alpha * (cost / C_max)) + \
                            (beta * (response_time / RT_max)) + \
                            (gamma * (replicas / R_max)) - \
                            (delta * availability)

    return optimization_value

def format_data_size(file_size: int) -> str:
    """
    Formats the file size into KB, MB, or GB.

    Parameters:
        file_size (int): The size of the file in KB.

    Returns:
        str: A string representing the formatted file size.
    """
    KB = 1
    MB = KB * 1024
    GB = MB * 1024

    if file_size < MB:
        size_in_kb = file_size / KB
        return f"{size_in_kb:.2f} KB"
    elif file_size < GB:
        size_in_mb = file_size / MB
        return f"{size_in_mb:.2f} MB"
    else:
        size_in_gb = file_size / GB
        return f"{size_in_gb:.2f} GB"

