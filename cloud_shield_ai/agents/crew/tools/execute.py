import json
import uuid
from crewai_tools import BaseTool
from cloud_shield_ai import logger
from cloud_shield_ai.utils import get_aws_manager_instance

aws_manager = get_aws_manager_instance()

# Action Tools

class CreateUserAction(BaseTool):
    name: str = "CreateUser"
    description: str = "Creates an IAM user in AWS."

    def _run(self, user_name: str) -> str:
        try:
            aws_manager.iam.create_user(UserName=user_name)
            logger.info(f"User '{user_name}' created successfully.")
            return f"User '{user_name}' created successfully."
        except Exception as e:
            logger.error(f"Failed to create user '{user_name}': {e}")
            raise

class AttachPolicyToUserAction(BaseTool):
    name: str = "AttachPolicyToUser"
    description: str = "Attaches a policy to an IAM user in AWS."

    def _run(self, user_name: str, policy_arn: str) -> str:
        try:
            aws_manager.iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
            logger.info(f"Policy '{policy_arn}' attached to user '{user_name}'.")
            return f"Policy '{policy_arn}' attached to user '{user_name}'."
        except Exception as e:
            logger.error(f"Failed to attach policy '{policy_arn}' to user '{user_name}': {e}")
            raise

class CreateRoleAction(BaseTool):
    name: str = "CreateRole"
    description: str = "Creates an IAM role in AWS."

    def _run(self, role_name: str, assume_role_policy_document: str) -> str:
        try:
            aws_manager.iam.create_role(RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_document)
            logger.info(f"Role '{role_name}' created successfully.")
            return f"Role '{role_name}' created successfully."
        except Exception as e:
            logger.error(f"Failed to create role '{role_name}': {e}")
            raise

class AssumeRoleAction(BaseTool):
    name: str = "AssumeRole"
    description: str = "Assumes an IAM role in AWS."

    def _run(self, role_arn: str, role_session_name: str) -> str:
        try:
            response = aws_manager.sts.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name)
            credentials = response['Credentials']
            logger.info(f"Assumed role '{role_arn}' with session '{role_session_name}'.")
            return f"Assumed role '{role_arn}' with session '{role_session_name}'. AccessKeyId: {credentials['AccessKeyId']}, SecretAccessKey: {credentials['SecretAccessKey']}, SessionToken: {credentials['SessionToken']}"
        except Exception as e:
            logger.error(f"Failed to assume role '{role_arn}': {e}")
            raise

class CreateS3BucketAction(BaseTool):
    name: str = "CreateS3Bucket"
    description: str = "Creates an S3 bucket in AWS."

    def _run(self, bucket_name: str) -> str:
        try:
            # Validate or generate a valid bucket name
            if not bucket_name:
                bucket_name = f"bucket-{uuid.uuid4()}"
            
            aws_manager.s3.create_bucket(Bucket=bucket_name)
            logger.info(f"S3 bucket '{bucket_name}' created successfully.")
            return f"S3 bucket '{bucket_name}' created successfully."
        except Exception as e:
            logger.error(f"Failed to create S3 bucket '{bucket_name}': {e}")
            raise

class PutS3ObjectAction(BaseTool):
    name: str = "PutS3Object"
    description: str = "Puts an object into an S3 bucket in AWS."

    def _run(self, bucket_name: str, key: str, body: bytes) -> str:
        try:
            aws_manager.s3.put_object(Bucket=bucket_name, Key=key, Body=body)
            logger.info(f"Put object '{key}' into bucket '{bucket_name}'.")
            return f"Put object '{key}' into bucket '{bucket_name}'."
        except Exception as e:
            logger.error(f"Failed to put object '{key}' into bucket '{bucket_name}': {e}")
            raise

class PutBucketPolicyAction(BaseTool):
    name: str = "PutBucketPolicy"
    description: str = "Attacks a policy that makes the bucket publicly accessible by putting a bucket policy on an S3 bucket in AWS."

    def _run(self, bucket_name: str) -> str:
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            aws_manager.s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
            logger.info(f"Bucket policy applied to '{bucket_name}'.")
            return f"Bucket policy applied to '{bucket_name}'."
        except Exception as e:
            logger.error(f"Failed to put bucket policy on '{bucket_name}': {e}")
            raise

class UploadToS3Action(BaseTool):
    name: str = "UploadToS3"
    description: str = "Uploads data to an S3 bucket."

    def _run(self, bucket_name: str, key: str, body: bytes) -> str:
        try:
            aws_manager.s3.put_object(Bucket=bucket_name, Key=key, Body=body)
            logger.info(f"Data uploaded to bucket '{bucket_name}' with key '{key}'.")
            return f"Data uploaded to bucket '{bucket_name}' with key '{key}'."
        except Exception as e:
            logger.error(f"Failed to upload data to bucket '{bucket_name}' with key '{key}': {e}")
            raise
