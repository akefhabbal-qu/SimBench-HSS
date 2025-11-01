import matplotlib.pyplot as plt

from utils.Utility import format_data_size

class StorageVisualizer:
    def __init__(self, nodes, total_capacity: int, used_capacity: int, figure_name="Storage Utilization"):
        """
        Initialize the StorageVisualizer class.
        :param nodes: List of storage node names.
        :param total_capacity: List of total capacities for each node.
        :param used_capacity: List of used capacities for each node.
        :param figure_name: Name of the figure.
        """
        self.nodes = nodes
        self.total_capacity = total_capacity
        self.used_capacity = used_capacity
        self.free_capacity = [t - u for t, u in zip(total_capacity, used_capacity)]
        self.figure_name = figure_name
    
    def plot_storage_utilization(self):
        """Generates and displays the storage utilization bar chart."""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        bars_used = ax.bar(self.nodes, self.used_capacity, color='red', label='Used Capacity')
        # bars_capacity = ax.bar(self.nodes, self.total_capacity, color='blue', label='Total Capacity')
        bars_free = ax.bar(self.nodes, self.free_capacity, bottom=self.used_capacity, color='green', label='Free Capacity')
        
        # Labels and title
        ax.set_ylabel("Storage Capacity")
        ax.set_title(self.figure_name)
        ax.legend()
        
        # Display values on bars
        for i, bar in enumerate(bars_used):
            height = bar.get_height()
            if height > 0:
                percentage_utilization = (self.used_capacity[i] / self.total_capacity[i]) * 100
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2, f'{format_data_size(int(height))}\n({percentage_utilization:.1f}%)',
                        ha='center', va='center', fontsize=10, color='white')
        
        plt.show()

# Example Usage:
# nodes = ['Node A', 'Node B', 'Node C']
# total_capacity = [100, 200, 150]
# used_capacity = [60, 120, 90]

# visualizer = StorageVisualizer(nodes, total_capacity, used_capacity, "Custom Storage Utilization")
# visualizer.plot_storage_utilization()