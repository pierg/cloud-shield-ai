import random
from typing import List
from aiohttp import ClientError
from crewai_tools import BaseTool
from cloud_shield_ai import logger, output_folder
from cloud_shield_ai.utils import get_aws_manager_instance


aws_manager = get_aws_manager_instance()

# Information Gathering Tools

class ListS3BucketsAction(BaseTool):
    name: str = "ListS3Buckets"
    description: str = "Lists the S3 bucket names accessible from the user via identity-based policy or resource-based policy."

    def _run(self) -> List[str]:
        try:
            response = aws_manager.s3.list_buckets()
            bucket_names = [bucket['Name'] for bucket in response['Buckets']]
            logger.info(f"Successfully listed {len(bucket_names)} S3 buckets.")
            return bucket_names
        except Exception as e:
            logger.error(f"Failed to list S3 buckets: {e}")
            raise

class GetUserRolesAction(BaseTool):
    name: str = "GetUserRoles"
    description: str = "Given a user name, return all role names the user can assume."

    def _run(self, user_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_user_policies(UserName=user_name)
            roles = []
            for policy in response['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_document = aws_manager.iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy['DefaultVersionId'])['PolicyVersion']['Document']
                roles += [statement['Resource'] for statement in policy_document['Statement'] if statement['Effect'] == 'Allow' and 'sts:AssumeRole' in statement['Action']]
            logger.info(f"Successfully retrieved roles for user {user_name}.")
            return list(set(roles))
        except Exception as e:
            logger.error(f"Failed to get roles for user {user_name}: {e}")
            raise

class GetUserGroupsAction(BaseTool):
    name: str = "GetUserGroups"
    description: str = "Given a user name, return all the groups the user is part of."

    def _run(self, user_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_groups_for_user(UserName=user_name)
            group_names = [group['GroupName'] for group in response['Groups']]
            logger.info(f"Successfully retrieved groups for user {user_name}.")
            return group_names
        except Exception as e:
            logger.error(f"Failed to get groups for user {user_name}: {e}")
            raise

class GetRoleS3AccessAction(BaseTool):
    name: str = "GetRoleS3Access"
    description: str = "Given a role name, return all S3 bucket names it can access."

    def _run(self, role_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_role_policies(RoleName=role_name)
            bucket_names = []
            for policy in response['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_document = aws_manager.iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy['DefaultVersionId'])['PolicyVersion']['Document']
                for statement in policy_document['Statement']:
                    if statement['Effect'] == 'Allow' and 's3' in statement['Action']:
                        bucket_names += [res.split(':')[-1] for res in statement['Resource']]
            logger.info(f"Successfully retrieved S3 bucket access for role {role_name}.")
            return list(set(bucket_names))
        except Exception as e:
            logger.error(f"Failed to get S3 bucket access for role {role_name}: {e}")
            raise

class GetRoleAssumableRolesAction(BaseTool):
    name: str = "GetRoleAssumableRoles"
    description: str = "Given a role name, return all role names the role can assume."

    def _run(self, role_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_role_policies(RoleName=role_name)
            assumable_roles = []
            for policy in response['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_document = aws_manager.iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy['DefaultVersionId'])['PolicyVersion']['Document']
                assumable_roles += [statement['Resource'] for statement in policy_document['Statement'] if statement['Effect'] == 'Allow' and 'sts:AssumeRole' in statement['Action']]
            logger.info(f"Successfully retrieved assumable roles for role {role_name}.")
            return assumable_roles
        except Exception as e:
            logger.error(f"Failed to get assumable roles for role {role_name}: {e}")
            raise

class GetGroupS3AccessAction(BaseTool):
    name: str = "GetGroupS3Access"
    description: str = "Given a group name, return all S3 bucket names the group has access to."

    def _run(self, group_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_group_policies(GroupName=group_name)
            bucket_names = []
            for policy in response['AttachedPolicies']:
                policy_arn = policy['PolicyArn']
                policy_document = aws_manager.iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy['DefaultVersionId'])['PolicyVersion']['Document']
                for statement in policy_document['Statement']:
                    if statement['Effect'] == 'Allow' and 's3' in statement['Action']:
                        bucket_names += [res.split(':')[-1] for res in statement['Resource']]
            logger.info(f"Successfully retrieved S3 bucket access for group {group_name}.")
            return list(set(bucket_names))
        except Exception as e:
            logger.error(f"Failed to get S3 bucket access for group {group_name}: {e}")
            raise

class ListS3ObjectsAction(BaseTool):
    name: str = "ListS3Objects"
    description: str = "Lists all objects in a specified S3 bucket."

    def _run(self, bucket_name: str) -> List[str]:
        try:
            response = aws_manager.s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                object_keys = [obj['Key'] for obj in response['Contents']]
                logger.info(f"Listed all objects in bucket '{bucket_name}' successfully.")
                return object_keys
            else:
                logger.info(f"No objects found in bucket '{bucket_name}'.")
                return []
        except Exception as e:
            logger.error(f"Failed to list objects in bucket '{bucket_name}': {e}")
            raise

class GetS3ObjectAction(BaseTool):
    name: str = "GetS3Object"
    description: str = "Gets an object from an S3 bucket in AWS."

    def _run(self, bucket_name: str, key: str) -> str:
        try:
            response = aws_manager.s3.get_object(Bucket=bucket_name, Key=key)
            logger.info(f"Retrieved object '{key}' from bucket '{bucket_name}'.")
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to get object '{key}' from bucket '{bucket_name}': {e}")
            raise

class ListIAMUsersAction(BaseTool):
    name: str = "ListIAMUsers"
    description: str = "Lists all IAM users in AWS."

    def _run(self) -> List[str]:
        try:
            response = aws_manager.iam.list_users()
            user_names = [user['UserName'] for user in response['Users']]
            logger.info("Listed all IAM users successfully.")
            return user_names
        except Exception as e:
            logger.error(f"Failed to list IAM users: {e}")
            raise

class ListIAMRolesAction(BaseTool):
    name: str = "ListIAMRoles"
    description: str = "Lists all IAM roles in AWS."

    def _run(self) -> List[str]:
        try:
            response = aws_manager.iam.list_roles()
            role_names = [role['RoleName'] for role in response['Roles']]
            logger.info("Listed all IAM roles successfully.")
            return role_names
        except Exception as e:
            logger.error(f"Failed to list IAM roles: {e}")
            raise

class ListIAMGroupsAction(BaseTool):
    name: str = "ListIAMGroups"
    description: str = "Lists all IAM groups in AWS."

    def _run(self) -> List[str]:
        try:
            response = aws_manager.iam.list_groups()
            group_names = [group['GroupName'] for group in response['Groups']]
            logger.info("Listed all IAM groups successfully.")
            return group_names
        except Exception as e:
            logger.error(f"Failed to list IAM groups: {e}")
            raise

class ListAttachedUserPoliciesAction(BaseTool):
    name: str = "ListAttachedUserPolicies"
    description: str = "Lists all policies attached to a specific IAM user."

    def _run(self, user_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_user_policies(UserName=user_name)
            policy_arns = [policy['PolicyArn'] for policy in response['AttachedPolicies']]
            logger.info(f"Listed attached policies for user '{user_name}' successfully.")
            return policy_arns
        except Exception as e:
            logger.error(f"Failed to list attached policies for user '{user_name}': {e}")
            raise

class ListAttachedRolePoliciesAction(BaseTool):
    name: str = "ListAttachedRolePolicies"
    description: str = "Lists all policies attached to a specific IAM role."

    def _run(self, role_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_role_policies(RoleName=role_name)
            policy_arns = [policy['PolicyArn'] for policy in response['AttachedPolicies']]
            logger.info(f"Listed attached policies for role '{role_name}' successfully.")
            return policy_arns
        except Exception as e:
            logger.error(f"Failed to list attached policies for role '{role_name}': {e}")
            raise

class ListAttachedGroupPoliciesAction(BaseTool):
    name: str = "ListAttachedGroupPolicies"
    description: str = "Lists all policies attached to a specific IAM group."

    def _run(self, group_name: str) -> List[str]:
        try:
            response = aws_manager.iam.list_attached_group_policies(GroupName=group_name)
            policy_arns = [policy['PolicyArn'] for policy in response['AttachedPolicies']]
            logger.info(f"Listed attached policies for group '{group_name}' successfully.")
            return policy_arns
        except Exception as e:
            logger.error(f"Failed to list attached policies for group '{group_name}': {e}")
            raise

class ExploreUserPathAction(BaseTool):
    name: str = "ExploreUserPath"
    description: str = "Explores all the paths (via role assumptions, groups, and policies) that a user has to every S3 bucket."

    def _run(self, user_name: str) -> str:
        try:
            with open(output_folder / "info.txt", "r") as f:
                response = f.read()
            logger.info(f"Explored all paths for user '{user_name}'.")
            return response
        except Exception as e:
            logger.error(f"Failed to list paths for user '{user_name}': {e}")
            raise
