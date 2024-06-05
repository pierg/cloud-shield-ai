import os
from pathlib import Path
import random
import boto3
import json
from typing import Any, Optional, Dict, Tuple, List

from cloud_shield_ai import logger
from cloud_shield_ai.utils.aws_utils import reset_all_resources

class SingletonMeta(type):
    """A Singleton metaclass to ensure only one instance of the class is created."""
    _instances: Dict[type, 'SingletonMeta'] = {}

    def __call__(cls, *args, **kwargs) -> 'SingletonMeta':
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class AWSManager:
    """Manages AWS sessions and resources."""

    CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
    print("CREDENTIALS_FILE", CREDENTIALS_FILE)

    def __init__(
        self,
        aws_access_key_id: str = "test",
        aws_secret_access_key: str = "test",
        endpoint_url: str = "http://localhost:4566",
        region_name: str = "us-east-1",
    ):
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self.sessions: Dict[str, boto3.Session] = {}
        self.credentials: Dict[str, Tuple[str, str, Optional[str]]] = self.load_credentials()

        default_arn = "admin"
        if default_arn not in self.credentials:
            self.store_credentials(default_arn, aws_access_key_id, aws_secret_access_key)
        self.current_session = self._get_session(default_arn)
        self.current_identity = default_arn

    def store_credentials(
        self, identity_arn: str, aws_access_key_id: str, aws_secret_access_key: str, session_token: Optional[str] = None
    ) -> None:
        """Store credentials for a given ARN."""
        self.credentials[identity_arn] = (aws_access_key_id, aws_secret_access_key, session_token)
        self.save_credentials()
        logger.info(f"Credentials stored for {identity_arn}.")

    def save_credentials(self) -> None:
        """Save credentials to a file."""
        with open(self.CREDENTIALS_FILE, 'w') as f:
            json.dump(self.credentials, f)
        logger.info("Credentials saved to file.")

    def load_credentials(self) -> Dict[str, Tuple[str, str, Optional[str]]]:
        """Load credentials from a file."""
        if os.path.exists(self.CREDENTIALS_FILE):
            with open(self.CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
            logger.info("Credentials loaded from file.")
            return {arn: tuple(creds) for arn, creds in credentials.items()}
        else:
            logger.info("No credentials file found. Starting with empty credentials.")
            return {}

    def _get_session(self, identity_arn: str) -> boto3.Session:
        """Retrieve or create a session based on the ARN."""
        if identity_arn not in self.credentials:
            logger.error(f"No credentials stored for ARN: {identity_arn}")
            raise ValueError("No credentials stored for this ARN")

        if identity_arn not in self.sessions:
            creds = self.credentials[identity_arn]
            aws_session_token = creds[2] if len(creds) > 2 else None
            self.sessions[identity_arn] = boto3.Session(
                aws_access_key_id=creds[0],
                aws_secret_access_key=creds[1],
                aws_session_token=aws_session_token,
                region_name=self.region_name,
            )
            logger.info(f"New session created for {identity_arn}")
        return self.sessions[identity_arn]
    
    def switch_identity(self, identity_arn: str) -> None:
        """Switch the current session by ARN or username."""
        if self.current_identity != identity_arn:
            self.current_session = self._get_session(identity_arn)
            self.current_identity = identity_arn
            logger.info(f"Switched to session for {identity_arn}")

    def add_entity(self, name: str, type_name: str) -> None:
        """Add a new IAM entity and store credentials if applicable."""
        try:
            if type_name == 'User':
                user_response = self.iam.create_user(UserName=name)
                user_arn = user_response["User"]["Arn"]

                keys_response = self.iam.create_access_key(UserName=name)
                access_key_id = keys_response["AccessKey"]["AccessKeyId"]
                secret_access_key = keys_response["AccessKey"]["SecretAccessKey"]

                self.store_credentials(user_arn, access_key_id, secret_access_key)
                logger.info(f"User {name} created and credentials stored.")
            elif type_name == 'Group':
                self.iam.create_group(GroupName=name)
                logger.info(f"Group {name} created.")
                # No credentials to store for groups
            elif type_name == 'Role':
                empty_trust_policy = {"Version": "2012-10-17", "Statement": []}
                role_response = self.iam.create_role(
                    RoleName=name,
                    AssumeRolePolicyDocument=json.dumps(empty_trust_policy)
                )
                logger.info(f"Role {name} created.")
                # No credentials to store for roles
            elif type_name == 'Resource':
                self.s3.create_bucket(Bucket=name)
                logger.info(f"S3 Bucket {name} created.")

                data_files = [
                    "financial_reports.txt",
                    "office_contact_info.txt",
                    "password_credentials.txt",
                    "project_details.txt",
                ]

                # Select between 2 and 3 random files
                selected_files = random.sample(data_files, random.randint(2, 3))
                
                # Upload selected files to the created bucket
                for file_name in selected_files:
                    file_path = Path(__file__).parent / "sample_data" / file_name
                    self.s3.upload_file(str(file_path), name, file_name)
                    logger.info(f"File {file_name} uploaded to S3 bucket {name}.")


            else:
                logger.error(f"Invalid entity type: {type_name}")
                raise ValueError("Invalid entity type")
        except Exception as e:
            logger.error(f"Failed to create {type_name} named {name}: {str(e)}")
            raise

    def get_current_identity(self) -> str:
        """Retrieve the current identity ARN."""
        sts_client = self.current_session.client('sts', endpoint_url=self.endpoint_url)
        identity = sts_client.get_caller_identity()
        return identity['Arn']

    def fetch_policies(self, identity_arn: str) -> List[Dict[str, Any]]:
        """Fetch all policies (inline and managed) for a given identity."""
        iam_client = self.current_session.client('iam', endpoint_url=self.endpoint_url)
        policies = []

        if ":role/" in identity_arn:
            policies.extend(self._fetch_role_policies(iam_client, identity_arn))
        elif ":user/" in identity_arn:
            policies.extend(self._fetch_user_policies(iam_client, identity_arn))

        return policies

    def _fetch_role_policies(self, iam_client: boto3.client, identity_arn: str) -> List[Dict[str, Any]]:
        """Fetch policies for a role."""
        role_name = identity_arn.split("/")[-1]
        policies = []
        
        inline_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
        managed_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']

        for policy_name in inline_policies:
            policy = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
            policies.append(policy['PolicyDocument'])

        for policy in managed_policies:
            policy_version = iam_client.get_policy_version(
                PolicyArn=policy['PolicyArn'],
                VersionId=iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
            )
            policies.append(policy_version['PolicyVersion']['Document'])

        return policies

    def _fetch_user_policies(self, iam_client: boto3.client, identity_arn: str) -> List[Dict[str, Any]]:
        """Fetch policies for a user."""
        user_name = identity_arn.split("/")[-1]
        policies = []
        
        inline_policies = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
        managed_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']

        for policy_name in inline_policies:
            policy = iam_client.get_user_policy(UserName=user_name, PolicyName=policy_name)
            policies.append(policy['PolicyDocument'])

        for policy in managed_policies:
            policy_version = iam_client.get_policy_version(
                PolicyArn=policy['PolicyArn'],
                VersionId=iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
            )
            policies.append(policy_version['PolicyVersion']['Document'])

        return policies

    def analyze_policies(self, policies: List[Dict[str, Any]]) -> List[str]:
        """Analyze policies to extract allowed actions."""
        allowed_actions = []
        for policy in policies:
            for statement in policy.get('Statement', []):
                if statement['Effect'] == 'Allow':
                    actions = statement['Action']
                    if isinstance(actions, str):
                        actions = [actions]
                    allowed_actions.extend(actions)
        return allowed_actions

    def get_allowed_actions(self) -> List[str]:
        """Get the list of allowed actions for the current identity."""
        identity_arn = self.get_current_identity()
        policies = self.fetch_policies(identity_arn)
        allowed_actions = self.analyze_policies(policies)
        return allowed_actions
    
    def _get_type(self, name: str) -> str:
        """Retrieve the type of the entity (User, Group, Role) by its name."""
        try:
            self.iam.get_user(UserName=name)
            return 'User'
        except self.iam.exceptions.NoSuchEntityException:
            try:
                self.iam.get_group(GroupName=name)
                return 'Group'
            except self.iam.exceptions.NoSuchEntityException:
                try:
                    self.iam.get_role(RoleName=name)
                    return 'Role'
                except self.iam.exceptions.NoSuchEntityException:
                    raise ValueError(f"Invalid entity name: {name}")

    def get_arn(self, name: str, type_name: str) -> str:
        """Retrieve the ARN for a given name and type."""
        if type_name == 'Role':
            return self.iam.get_role(RoleName=name)['Role']['Arn']
        elif type_name == 'User':
            return self.iam.get_user(UserName=name)['User']['Arn']
        elif type_name == 'Group':
            return self.iam.get_group(GroupName=name)['Group']['Arn']
        elif type_name == 'Resource':
            return f"arn:aws:s3:::{name}"
        else:
            raise ValueError(f"Invalid type: {type_name}")
        
    def get_arn_from_name(self, name: str) -> str:
        """Retrieve the ARN based on the entity name."""
        return self.get_arn(name, self._get_type(name))
        
    def _create_policy_document(self, actions: List[str], resources: List[str], principals: Optional[List[str]] = None) -> Dict:
        """Create a policy document."""
        statement = {
            "Effect": "Allow",
            "Action": actions,
            "Resource": resources
        }
        if principals:
            statement["Principal"] = {"AWS": principals}

        return {
            "Version": "2012-10-17",
            "Statement": [statement]
        }

    @property
    def iam(self) -> boto3.client:
        """Return the IAM client."""
        return self.current_session.client("iam", endpoint_url=self.endpoint_url)

    @property
    def s3(self) -> boto3.client:
        """Return the S3 client."""
        return self.current_session.client("s3", endpoint_url=self.endpoint_url)

    @property
    def sts(self) -> boto3.client:
        """Return the STS client."""
        return self.current_session.client("sts", endpoint_url=self.endpoint_url)

    def reset_all(self) -> None:
        """Reset all resources to their initial state."""
        reset_all_resources(self.iam, self.s3)

    def _get_policies(self, entity_name: str, entity_type: str) -> List[Tuple[Optional[str], Dict]]:
        """Return all policies attached to User, Group, Role or Resource."""
        policies = []
        try:
            if entity_type == 'User':
                policy_names = self.iam.list_user_policies(UserName=entity_name)['PolicyNames']
                for policy_name in policy_names:
                    policy_document = self.iam.get_user_policy(UserName=entity_name, PolicyName=policy_name)['PolicyDocument']
                    policies.append((policy_name, policy_document))
            elif entity_type == 'Group':
                policy_names = self.iam.list_group_policies(GroupName=entity_name)['PolicyNames']
                for policy_name in policy_names:
                    policy_document = self.iam.get_group_policy(GroupName=entity_name, PolicyName=policy_name)['PolicyDocument']
                    policies.append((policy_name, policy_document))
            elif entity_type == 'Role':
                policy_names = self.iam.list_role_policies(RoleName=entity_name)['PolicyNames']
                for policy_name in policy_names:
                    policy_document = self.iam.get_role_policy(RoleName=entity_name, PolicyName=policy_name)['PolicyDocument']
                    policies.append((policy_name, policy_document))
            elif entity_type == 'Resource':
                policy = self.s3.get_bucket_policy(Bucket=entity_name)['Policy']
                policies.append((None, json.loads(policy)))
        except self.iam.exceptions.NoSuchEntityException:
            pass
        return policies

    def _update_policy(self, entity_name: str, entity_type: str, policy_document: Dict, policy_name: Optional[str] = None) -> None:
        """Update the policy for the given entity, including a Resource (resource-based policy)."""
        if not policy_name:
            policy_name = f"{entity_name}_Policy_{len(policy_document['Statement'])}"
        if entity_type == 'User':
            self.iam.put_user_policy(
                UserName=entity_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
        elif entity_type == 'Group':
            self.iam.put_group_policy(
                GroupName=entity_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
        elif entity_type == 'Role':
            self.iam.put_role_policy(
                RoleName=entity_name,
                PolicyName=policy_name,
                PolicyDocument=json.dumps(policy_document)
            )
        elif entity_type == 'Resource':
            self.s3.put_bucket_policy(
                Bucket=entity_name,
                Policy=json.dumps(policy_document)
            )

    def update_resource_policy(self, resource_name: str, principals_names: List[str], actions: List[str]) -> None:
        """Update or create a resource-based policy for the specified resource."""
        resource_arn = self.get_arn(resource_name, 'Resource')
        principals_arns = [self.get_arn(name, self._get_type(name)) for name in principals_names]

        new_statement = self._create_policy_document(actions, [resource_arn], principals_arns)['Statement'][0]

        policies = self._get_policies(resource_name, 'Resource')
        if policies:
            policy_name, policy_document = policies[0]
            policy_document['Statement'].append(new_statement)
        else:
            policy_document = {"Version": "2012-10-17", "Statement": [new_statement]}
            policy_name = None

        self._update_policy(resource_name, 'Resource', policy_document, policy_name)

        logger.info(f"Updated resource policy for {resource_name} to allow actions {actions} for principals {principals_names}.")

    def update_identity_policy(self, identity_name: str, actions: List[str], resources_names: List[str] = None) -> None:
        """Update or create an identity-based policy for the specified identity."""
        resource_arns = [self.get_arn(name, 'Resource') for name in resources_names] if resources_names else ["*"]

        new_statement = self._create_policy_document(actions, resource_arns)['Statement'][0]

        policies = self._get_policies(identity_name, self._get_type(identity_name))
        if policies:
            policy_name, policy_document = policies[0]
            policy_document['Statement'].append(new_statement)
        else:
            policy_document = {"Version": "2012-10-17", "Statement": [new_statement]}
            policy_name = None

        self._update_policy(identity_name, self._get_type(identity_name), policy_document, policy_name)

        logger.info(f"Updated identity policy for {identity_name} to allow actions {actions} on resources {resources_names}.")


    def _create_policy_document(self, actions: List[str], resources: List[str], principals: Optional[List[str]] = None) -> Dict:
        """Create a policy document."""
        statement = {
            "Effect": "Allow",
            "Action": actions,
            "Resource": resources
        }
        if principals:
            statement["Principal"] = {"AWS": principals}

        return {
            "Version": "2012-10-17",
            "Statement": [statement]
        }

    def add_connection(self, from_entity: Tuple[str, str], to_entity: Tuple[str, str], actions: Optional[List[str]] = None) -> None:
        """Add a connection between IAM entities."""
        if actions is None:
            actions = []
        
        from_name, from_type = from_entity
        to_name, to_type = to_entity

        if from_type == 'User' and to_type == 'Group':
            self.iam.add_user_to_group(GroupName=to_name, UserName=from_name)
            logger.info(f"Added User {from_name} to Group {to_name}.")
            return

        if from_type == 'Group' and to_type == 'Group':
            self.add_group_to_group(from_name, to_name)
            logger.info(f"Added Group {from_name} to Group {to_name}.")
            return

        if not actions:
            if to_type == 'Role':
                actions.append("sts:AssumeRole")
            elif to_type == 'Resource':
                actions.extend(["s3:ListBucket", "s3:GetObject"])

        target_arn = self.get_arn(to_name, to_type)

        new_statement = self._create_policy_document(actions, [target_arn])['Statement'][0]
        policies = self._get_policies(from_name, from_type)

        if policies:
            policy_name, policy_document = policies[0]
            policy_document['Statement'].append(new_statement)
            self._update_policy(from_name, from_type, policy_document, policy_name)
        else:
            policy_document = self._create_policy_document(actions, [target_arn])
            self._update_policy(from_name, from_type, policy_document)
        
        logger.info(f"Updated {from_type} {from_name}'s policy to allow access to {to_type} {to_name}.")

    def add_group_to_group(self, from_group_name: str, to_group_name: str) -> None:
        """Add a group to another group. This is a conceptual function as AWS IAM does not directly support group-to-group relationships."""
        # Implement the logic for adding group-to-group relationships if applicable.
        # Note: AWS IAM does not support direct group-to-group relationships.
        # This can be a placeholder for any future implementation or a custom logic workaround.
        logger.warning(f"AWS IAM does not support direct group-to-group relationships between {from_group_name} and {to_group_name}.")
