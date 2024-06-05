from json import tool
from multiprocessing import context
from crewai import Task
from textwrap import dedent
from cloud_shield_ai.agents.crew.tools import *

from pydantic import BaseModel

class DocumentAnalysisOutput(BaseModel):
    sensitive_documents: dict[str, list[str]]  # {bucket_name: [object_key, object_key, ...]}
    

class CloudExplorationTasks:
    
    def lateral_exploration_task(self, agent, username):
        return Task(
            description=dedent(f"""\
                Explore the direct and indirect permissions of the user '{username}' to any S3 bucket. 
                This involves examining user groups, roles, and the policies attached to these entities 
                to identify all possible access paths.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A detailed summary of all direct and indirect permissions the user '{username}' has to any S3 bucket. 
                Include explanations for each indirect permission, detailing how access is granted (e.g., via role assumption or group membership). 
                The report should highlight potential avenues for data exfiltration and ransomware attacks.
                
                Provide a structured list for each bucket, defining the direct and indirect paths for user access.
                """),
            tools=[
                explore_user_path,
            ]
        )

    def document_analysis_task(self, agent, username):
        return Task(
            description=dedent(f"""\
                Analyze the content of each S3 bucket accessible to the user '{username}'
                For each object within the buckets, assess the content to determine if it is sensitive.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A list of objects in each bucket with an indication of whether they are sensitive or not.
                """),
            output_json=DocumentAnalysisOutput,
            tools=[
                # S3 Operations
                list_s3_buckets,
                list_s3_objects,
                get_s3_object,
            ]
        )
        
    def data_exfiltration_task(self, agent, username):
        return Task(
            description=dedent(f"""\
                Attempt to exfiltrate all identified sensitive data accessible by the user '{username}' to a public bucket.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A schematic report detailing the steps taken to exfiltrate sensitive data to a public bucket. 
                Include methods used, challenges faced, and the final outcome.
                """),
            tools=[
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
                list_s3_objects,
                get_s3_object,
                create_s3_bucket,
                put_s3_object,
                put_bucket_policy,
                upload_to_s3,
                
                # Utility Tools
                report_tool,
                bucket_name_generator
            ]
        )

    def ransomware_exploration_task(self, agent):
        return Task(
            description=dedent(f"""\
                Perform a ransomware attack using.
                This involves encrypting data in accessible S3 buckets and leaving a ransom note.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A detailed report on the ransomware attack, including the steps taken to encrypt data in the S3 buckets accessible to the user.
                The report should also describe any ransom note left and the effectiveness of the attack.
                """),
            tools=[
                list_s3_buckets,
                get_s3_object,
                put_s3_object,
                report_tool,
            ]
        )
