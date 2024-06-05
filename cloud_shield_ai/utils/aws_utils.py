from cloud_shield_ai import logger
from botocore.exceptions import ClientError
from typing import Any

def delete_s3_buckets(s3: Any) -> None:
    """Delete all S3 buckets and their contents."""
    try:
        for bucket in s3.list_buckets()['Buckets']:
            bucket_name = bucket['Name']
            logger.info(f"Deleting contents and bucket: {bucket_name}")
            try:
                s3.delete_bucket_policy(Bucket=bucket_name)
            except ClientError as e:
                logger.warning(f"No policy found for bucket {bucket_name}: {e}")
            objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
            for obj in objects:
                try:
                    s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                except ClientError as e:
                    logger.warning(f"Error deleting object {obj['Key']} in bucket {bucket_name}: {e}")
            try:
                s3.delete_bucket(Bucket=bucket_name)
                logger.info(f"Deleted bucket: {bucket_name}")
            except ClientError as e:
                logger.error(f"Error deleting bucket {bucket_name}: {e}")
    except ClientError as e:
        logger.error(f"Error listing S3 buckets: {e}")

def delete_iam_roles(iam: Any) -> None:
    """Delete all IAM roles and their policies."""
    try:
        for role in iam.list_roles()['Roles']:
            role_name = role['RoleName']
            for policy in iam.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']:
                try:
                    iam.detach_role_policy(RoleName=role_name, PolicyArn=policy['PolicyArn'])
                except ClientError as e:
                    logger.warning(f"Error detaching policy {policy['PolicyArn']} from role {role_name}: {e}")
            for policy_name in iam.list_role_policies(RoleName=role_name)['PolicyNames']:
                try:
                    iam.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
                except ClientError as e:
                    logger.warning(f"Error deleting inline policy {policy_name} from role {role_name}: {e}")
            try:
                iam.delete_role(RoleName=role_name)
                logger.info(f"Deleted role: {role_name}")
            except ClientError as e:
                logger.error(f"Error deleting role {role_name}: {e}")
    except ClientError as e:
        logger.error(f"Error deleting IAM roles: {e}")

def delete_iam_users(iam: Any) -> None:
    """Delete all IAM users and their policies."""
    try:
        for user in iam.list_users()['Users']:
            user_name = user['UserName']
            attached_policies = iam.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
            for policy in attached_policies:
                try:
                    iam.detach_user_policy(UserName=user_name, PolicyArn=policy['PolicyArn'])
                except ClientError as e:
                    logger.warning(f"Error detaching policy {policy['PolicyArn']} from user {user_name}: {e}")
            inline_policies = iam.list_user_policies(UserName=user_name)['PolicyNames']
            for policy_name in inline_policies:
                try:
                    iam.delete_user_policy(UserName=user_name, PolicyName=policy_name)
                except ClientError as e:
                    logger.warning(f"Error deleting inline policy {policy_name} from user {user_name}: {e}")
            groups = iam.list_groups_for_user(UserName=user_name)['Groups']
            for group in groups:
                try:
                    iam.remove_user_from_group(UserName=user_name, GroupName=group['GroupName'])
                except ClientError as e:
                    logger.warning(f"Error removing user {user_name} from group {group['GroupName']}: {e}")
            try:
                iam.delete_user(UserName=user_name)
                logger.info(f"Deleted user: {user_name}")
            except ClientError as e:
                logger.error(f"Error deleting user {user_name}: {e}")
    except ClientError as e:
        logger.error(f"Error deleting IAM users: {e}")

def delete_iam_groups(iam: Any) -> None:
    """Delete all IAM groups and their policies."""
    try:
        for group in iam.list_groups()['Groups']:
            group_name = group['GroupName']
            for policy in iam.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']:
                try:
                    iam.detach_group_policy(GroupName=group_name, PolicyArn=policy['PolicyArn'])
                except ClientError as e:
                    logger.warning(f"Error detaching policy {policy['PolicyArn']} from group {group_name}: {e}")
            for policy_name in iam.list_group_policies(GroupName=group_name)['PolicyNames']:
                try:
                    iam.delete_group_policy(GroupName=group_name, PolicyName=policy_name)
                except ClientError as e:
                    logger.warning(f"Error deleting inline policy {policy_name} from group {group_name}: {e}")
            try:
                iam.delete_group(GroupName=group_name)
                logger.info(f"Deleted group: {group_name}")
            except ClientError as e:
                logger.error(f"Error deleting group {group_name}: {e}")
    except ClientError as e:
        logger.error(f"Error deleting IAM groups: {e}")

def delete_iam_policies(iam: Any) -> None:
    """Delete all IAM policies."""
    try:
        for policy in iam.list_policies(Scope='Local')['Policies']:
            try:
                iam.delete_policy(PolicyArn=policy['Arn'])
                logger.info(f"Deleted policy: {policy['Arn']}")
            except ClientError as e:
                logger.warning(f"Error deleting policy {policy['Arn']}: {e}")
    except ClientError as e:
        logger.error(f"Error deleting IAM policies: {e}")

def reset_all_resources(iam: Any, s3: Any) -> None:
    """Reset all AWS resources: S3 buckets and IAM entities."""
    delete_s3_buckets(s3)
    delete_iam_roles(iam)
    delete_iam_users(iam)
    delete_iam_groups(iam)
    delete_iam_policies(iam)
    logger.info("All AWS resources reset successfully.")
