from cloud_shield_ai.utils import get_aws_manager_instance
from cloud_shield_ai.generator.playground import Playground
from cloud_shield_ai import output_folder

# File to create synthetic data to populate aws cloud

aws = get_aws_manager_instance()
aws.reset_all()

playground = Playground(
    total_num_users=10,
    total_num_roles=10,
    total_num_groups=5,
    total_num_resources=2,
    path_length=[3, 3],
)

playground.run()
print(playground.generate_report())
with open(output_folder / "playground.txt", "w") as f:
    f.write(playground.generate_report())
    
