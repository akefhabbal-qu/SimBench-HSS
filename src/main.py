import os
from pathlib import Path
from datetime import datetime


from Algorithms.RL.RLTrainer import RLTrainer
from Algorithms.RL.DQN import DQN
from Algorithms.RL.DDQN import DDQN
from Simulation import Simulator

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent  # Get the script's directory
    # Use smaller dataset for testing
    train_path = os.path.join(root_dir, "data", "train", "file_access_trace.jsonl")
    # train_path = os.path.join(root_dir, "data", "train", "file_access_trace.jsonl")  # Full dataset
    # train_path = os.path.join(root_dir, "data", "train", "combined.jsonl")
    # test_path = os.path.join(root_dir, "data/test/access_pattern.json")
    # train_path = "C:/Users/Akef/Documents/GitHub/optimizing_data_placement/data/train/trace_0.jsonl"
    # test_path = "C:/Users/Akef/Documents/GitHub/optimizing_data_placement/data/test/access_pattern.json"


    #  # Correct way to measure time:
    # start_time = datetime.now()
    # # OR: start_time = time.time()

    Simulator.run(train_path)

    # end_time = datetime.now()
    # # OR: end_time = time.time()

    # elapsed_time = (end_time - start_time).total_seconds()
    # # OR: elapsed_time = end_time - start_time

    # print(f"Simulation completed in {elapsed_time:.2f} seconds.")


    # trainer = RLTrainer(access_pattern_path=train_path, episodes=2)  # Reduced to 2 for testing

    # Use optimized parameters for faster training
    # dqn = DQN(trainer.storage_system, batch_size=16, memory_size=1000, learning_rate=0.01)
    # trainer.train(dqn)
    # dqn.save_model(os.path.join(os.getcwd(), "models"))

    # Comment out DDQN for now to focus on DQN testing
    # ddqn = DDQN(trainer.storage_system)
    # trainer.train(ddqn)
    # ddqn.save_model(os.path.join(os.getcwd(), "models"))
