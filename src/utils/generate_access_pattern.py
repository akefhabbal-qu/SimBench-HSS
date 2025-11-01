import json
import random

# Configuration for the access pattern generation
num_files = 100
operations = ["read", "write", "delete"]

# Generate access pattern
access_pattern = []
file_write_status = set()  # Track files that have been written

for i in range(num_files):
    file_id = f"{i+1}"

    # Ensure that each file has a write before any read or delete
    write_entry = {"file_id": file_id, "operation_type": "write"}
    access_pattern.append(write_entry)
    file_write_status.add(file_id)

# Randomly add read and delete operations, ensuring rules are followed
for file_id in file_write_status:
    num_additional_ops = random.randint(1, 3)  # Add 1 to 3 additional operations per file

    for _ in range(num_additional_ops):
        operation = random.choice(["read", "delete"])
        access_pattern.append({"file_id": file_id, "operation_type": operation})

# Shuffle the access pattern while maintaining logical constraints
random.shuffle(access_pattern)

# Write to a JSON file
file_name = "access_pattern.json"
with open(file_name, "w") as file:
    json.dump(access_pattern, file, indent=2)