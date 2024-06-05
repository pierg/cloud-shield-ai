from cloud_shield_ai.agents.crew.tools.monitor import *
from cloud_shield_ai.agents.crew.tools.execute import *
from cloud_shield_ai.agents.crew.tools.authentication import *
from cloud_shield_ai.agents.crew.tools.monitor import *
from cloud_shield_ai.agents.crew.tools.utility import *



# User Management
get_user_roles = GetUserRolesAction(description="Given a user name, return all role names the user can assume.")
get_user_groups = GetUserGroupsAction(description="Given a user name, return all the groups the user is part of.")
list_iam_users = ListIAMUsersAction(description="Lists all IAM users in AWS.")
create_user = CreateUserAction(description="Creates an IAM user in AWS.")
authenticate_iam_user = AtheticateIAMUser(description="Authenticates as an IAM user in AWS.")
attach_policy_to_user = AttachPolicyToUserAction(description="Attaches a policy to an IAM user in AWS.")
list_attached_user_policies = ListAttachedUserPoliciesAction(description="Lists all policies attached to a specific IAM user.")
explore_user_path = ExploreUserPathAction(description="Explores all the paths (via role assumptions, groups, and policies) that a user has to every S3 bucket.")

# Role Management
get_role_s3_access = GetRoleS3AccessAction(description="Given a role name, return all S3 bucket names it can access.")
get_role_assumable_roles = GetRoleAssumableRolesAction(description="Given a role name, return all role names the role can assume.")
list_iam_roles = ListIAMRolesAction(description="Lists all IAM roles in AWS.")
create_role = CreateRoleAction(description="Creates an IAM role in AWS.")
assume_role = AssumeRoleAction(description="Assumes an IAM role in AWS.")
list_attached_role_policies = ListAttachedRolePoliciesAction(description="Lists all policies attached to a specific IAM role.")

# Group Management
get_group_s3_access = GetGroupS3AccessAction(description="Given a group name, return all S3 bucket names the group has access to.")
list_iam_groups = ListIAMGroupsAction(description="Lists all IAM groups in AWS.")
list_attached_group_policies = ListAttachedGroupPoliciesAction(description="Lists all policies attached to a specific IAM group.")

# S3 Operations
list_s3_buckets = ListS3BucketsAction(description="Lists all S3 buckets in AWS.")
list_s3_objects = ListS3ObjectsAction(description="Lists all objects in an S3 bucket in AWS.")
get_s3_object = GetS3ObjectAction(description="Gets an object from an S3 bucket in AWS.")
create_s3_bucket = CreateS3BucketAction(description="Creates an S3 bucket in AWS.")
put_s3_object = PutS3ObjectAction(description="Puts an object into an S3 bucket in AWS.")
put_bucket_policy = PutBucketPolicyAction(description="Puts a bucket policy on an S3 bucket in AWS.")
upload_to_s3 = UploadToS3Action(description="Uploads data to an S3 bucket.")

# Utility Tools
random_name_generator = RandomNameGeneratorTool(description="Generates a random first name.")
bucket_name_generator = BucketNameGeneratorTool(description="Generates a unique valid S3 bucket name.")
report_tool = CompileReportTool(description="Compiles the exploration results into a report.")
encryption_tool = EncryptionUtility(description="Utility for generating key, encrypting, and decrypting data.")



all_tools = [
    # User Management
    get_user_roles,
    get_user_groups,
    list_iam_users,
    list_attached_user_policies,
    explore_user_path,
    
    # Role Management
    get_role_s3_access,
    get_role_assumable_roles,
    list_iam_roles,
    list_attached_role_policies,
    assume_role,
    
    # Group Management
    get_group_s3_access,
    list_iam_groups,
    list_attached_group_policies,
    
    # S3 Operations
    list_s3_buckets,
    get_s3_object,
    create_s3_bucket,
    put_s3_object,
    put_bucket_policy,
    upload_to_s3,
    
    # Utility Tools
    report_tool,
    encryption_tool
]
