from crewai_tools import BaseTool
from cloud_shield_ai.utils import get_aws_manager_instance

aws_manager = get_aws_manager_instance()

# Authentication Tools

class AtheticateIAMUser(BaseTool):
    name: str = "AtheticateIAMUser"
    description: str = "Authenticates as an IAM user in AWS."

    def _run(sel, user_name: str) -> str:
        """Retrieve or create a session based on the ARN."""
        user_arn = aws_manager.iam.get_user(UserName=user_name)['User']['Arn']

        aws_manager.switch_identity(user_arn)
        return "Authentication successful."



