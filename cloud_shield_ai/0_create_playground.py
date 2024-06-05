from cloud_shield_ai.utils import get_aws_manager_instance
from cloud_shield_ai.generator.playground import Playground
from cloud_shield_ai import output_folder

# File to create synthetic data to populate aws cloud


# aws_access_key_id = "test",
# aws_secret_access_key = "test",
# endpoint_url = "http://localhost:4566",
# region_name = "us-east-1",

aws = get_aws_manager_instance()

aws.reset_all()

import time

# Sleep for 3 seconds
time.sleep(3)




playground_small = Playground(
    total_num_users=3,
    total_num_roles=2,
    total_num_groups=1,
    total_num_resources=1,
    path_length=[2,3],
)


# playground = Playground(
#     total_num_users=10,
#     total_num_roles=10,
#     total_num_groups=5,
#     total_num_resources=2,
#     path_length=[3,5],
# )

playground_small.run()
print(playground_small.generate_report())
with open(output_folder / "playground.txt", "w") as f:
    f.write(playground_small.generate_report())
    
