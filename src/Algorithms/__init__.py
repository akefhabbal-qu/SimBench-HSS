from .AlgorithmBase import AlgorithmBase
from .exceptions import NoStorageAvailableException

# Try to import RL algorithms if they exist
try:
    from .RL.HSMRL import HSMRL
except ImportError:
    HSMRL = None

try:
    from .RL.DQN import DQN
except ImportError:
    DQN = None

try:
    from .RL.RLTrainer import RLTrainer
except ImportError:
    RLTrainer = None