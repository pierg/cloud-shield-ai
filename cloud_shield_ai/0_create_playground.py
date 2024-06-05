from cloud_shield_ai.utils import get_aws_manager_instance
from cloud_shield_ai.generator.playground import Playground
from cloud_shield_ai import output_folder
import time

# File to create synthetic data to populate AWS cloud

# Configuration parameters for AWS manager instance
# aws_access_key_id = "test"
# aws_secret_access_key = "test"
# endpoint_url = "http://localhost:4566"
# region_name = "us-east-1"

# Get AWS manager instance
aws = get_aws_manager_instance()

# Reset all AWS resources
aws.reset_all()

# Sleep for 3 seconds to ensure reset is completed
time.sleep(3)

# Define different playground configurations
playground_configs = {
    "small": {
        "total_num_users": 10,
        "total_num_roles": 4,
        "total_num_groups": 5,
        "total_num_resources": 1,
        "path_length": [5, 6],
    },
    "large": {
        "total_num_users": 100,
        "total_num_roles": 40,
        "total_num_groups": 20,
        "total_num_resources": 1,
        "path_length": [7, 8],
    }
}

# Select the desired playground configuration
selected_config = "small"

# Create playground with selected configuration
playground = Playground(**playground_configs[selected_config])

# Run playground simulation
playground.run()

# Generate and print the playground report
report = playground.generate_report()
print(report)

# Save the playground report to a file
with open(output_folder / "playground.txt", "w") as f:
    f.write(report)
