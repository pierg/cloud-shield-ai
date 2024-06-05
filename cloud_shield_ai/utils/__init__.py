from cloud_shield_ai.utils.aws import AWSManager

def get_aws_manager_instance():
    """Returns the singleton instance of AWSManager."""
    return AWSManager()
