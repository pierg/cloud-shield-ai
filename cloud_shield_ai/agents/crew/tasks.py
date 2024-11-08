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

    def document_analysis_task(self, agent, username, context):
        return Task(
            description=dedent(f"""\
                Analyze the content of each S3 bucket accessible to the user '{username}'
                For each object within the buckets, assess the content to determine if it is sensitive.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A list of objects in each bucket with an indication of whether they are sensitive or not.
                """),
            context=context,
            tools=[
                # S3 Operations
                list_s3_buckets,
                list_s3_objects,
                get_s3_object,
            ]
        )
        
    def data_exfiltration_task(self, agent, username, context):
        return Task(
            description=dedent(f"""\
                Attempt to exfiltrate all identified sensitive data accessible by the user '{username}' to a public bucket.
                """),
            agent=agent,
            context=context,
            async_execution=True,
            expected_output=dedent(f"""\
                A schematic report detailing the steps taken to exfiltrate sensitive data to a public bucket. 
                Include methods used, challenges faced, and the final outcome.
                """),
            tools=[
                # User Management
                # get_user_roles,
                # get_user_groups,
                # list_iam_users,
                # list_attached_user_policies,
                explore_user_path,
                
                # Role Management
                get_role_s3_access,
                get_role_assumable_roles,
                # list_iam_roles,
                # list_attached_role_policies,
                assume_role,
                
                # Group Management
                get_group_s3_access,
                # list_iam_groups,
                # list_attached_group_policies,
                
                # S3 Operations
                list_s3_buckets,
                list_s3_objects,
                get_s3_object,
                create_s3_bucket,
                put_s3_object,
                put_bucket_policy,
                upload_to_s3,
                
                # Utility Tools
                bucket_name_generator
            ]
        )

    def ransomware_exploration_task(self, agent, context):
        return Task(
            description=dedent(f"""\
                Perform a ransomware attack using.
                This involves encrypting data in accessible S3 buckets and leaving a ransom note.
                """),
            agent=agent,
            expected_output=dedent(f"""\
                A detailed report on the ransomware attack, including the steps taken to encrypt data in the S3 buckets accessible to the user.
                """),
            context=context,
            async_execution=True,
            tools=[
                # list_s3_buckets,
                get_s3_object,
                put_s3_object,
                encryption_tool,
            ]
        )
        
    def summary_and_briefing_task(self, agent, context):
        return Task(
            description=dedent(f"""\
                Compile all the findings, industry analysis, and strategic
                talking points into a concise, comprehensive briefing document for
                the meeting.
                Ensure the briefing is easy to digest and equips the meeting
                participants with all necessary information and strategies.
                """),
            expected_output=dedent("""\
                A well-structured security briefing document that includes. .... """),
            context=context,
            agent=agent
        )

    def summary_and_briefing_task(self, agent, context):
        return Task(
            description=dedent(f"""\
                Compile all gathered information from previous tasks into a comprehensive security report. 
                The report should detail all identified vulnerabilities, provide an assessment of the potential risks, 
                and propose strategic recommendations for mitigating these vulnerabilities.
                """),
            expected_output=dedent(f"""\
                A well-structured security report that includes:
                - Summary of all findings from the exploration tasks
                - Detailed assessment of identified vulnerabilities
                - Potential risks associated with each vulnerability
                - Strategic recommendations for mitigating the identified vulnerabilities
                - Actionable steps for improving the overall security posture
                """),
            context=context,
            agent=agent
        )