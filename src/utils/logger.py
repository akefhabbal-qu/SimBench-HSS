import logging
import os
import datetime
import csv

# Toggle to control whether logs are printed to the console
SHOW_CONSOLE_LOG = False  # Set to False to disable console output
LOG_TO_FILE = False
LOG_LEVEL = logging.CRITICAL

date = datetime.datetime.now().strftime('%Y-%m-%d')
time = datetime.datetime.now().strftime('%H-%M-%S')

# Create logs directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_DIR = os.path.join(BASE_DIR, "logs", date)
LOG_DIR = f"../logs/{date}"
os.makedirs(LOG_DIR, exist_ok=True)

# Define log file paths
MAIN_LOG_FILE = os.path.join(LOG_DIR, f"{time} - project.log")
RESULT_LOG_FILE = os.path.join(LOG_DIR, f"{time} - results.log")
RESULT_CSV_FILE = os.path.join(LOG_DIR, f"{time} - results.csv")

def setup_logger(
    name="ProjectLogger", 
    log_file=MAIN_LOG_FILE, 
    level=LOG_LEVEL, 
    show_console=SHOW_CONSOLE_LOG,
    log_to_file=LOG_TO_FILE
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Add file handler only if log_to_file is True
        if log_to_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(file_handler)

        # Add console handler only if show_console is True
        if show_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(
                '%(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(console_handler)

    return logger
class CustomLogger(logging.Logger):
    def log_to_csv(self, data):
        file_exists = os.path.exists(RESULT_CSV_FILE)

        formatted_data = {
            "Algorithm": data["algorithm"],
            "Optimization Function": f"{float(data['optimization_function']):.3f}",
            "Estimated System Response (ESR)": f"{float(data['estimated_system_response']):.4f}",
            "Total Cost ($)": f"{float(data['total_cost'])}",
            "Total Response (ms)": f"{float(data['total_response_time']):.3f}",
            "Total Unavailable Accesses": data["total_num_unavailable"],
            "Total Successful Write": data["total_num_successful_write"],
            "Total Unsuccessful Write": data["total_num_unsuccessful_write"],
            "Total Successful Read": data["total_num_successful_read"],
            "Total Unsuccessful Read": data["total_num_unsuccessful_read"],
        }

        existing_data = []
        if file_exists:
            with open(RESULT_CSV_FILE, mode='r', newline='') as file:
                reader = csv.reader(file)
                existing_data = list(reader)

        transposed_data = [[key] + ([formatted_data[key]]) for key in formatted_data]

        if existing_data:
            for i, row in enumerate(existing_data):
                if i < len(transposed_data):
                    transposed_data[i].extend(row[1:])

        with open(RESULT_CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(transposed_data)

        self.info(f"Results logged successfully in {RESULT_CSV_FILE}")

def result_logger(name="ResultLogger", 
                  log_file=RESULT_LOG_FILE, 
                  level=logging.DEBUG, 
                  show_console=SHOW_CONSOLE_LOG) -> CustomLogger:
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger(name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter('%(message)s'))

    if not logger.handlers:
        logger.addHandler(file_handler)

        if show_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter('%(message)s'))
            logger.addHandler(console_handler)

    return logger

# Initialize the loggers
logger = setup_logger()
resultLogger = result_logger()
