from textwrap import dedent
from crewai import Agent
from cloud_shield_ai.agents.crew.tools import *

class CloudExplorationAgents:
        
    def lateral_exploration_agent(self):
        return Agent(
            role='User Exploration Specialist',
            goal='Identify all direct and indirect access paths to S3 resources for a specified user.',
            backstory="Experienced in analyzing user, role, and group permissions to uncover all access paths to S3 resources.",
            verbose=True,
            allow_delegation=False
        )

    def document_analysis_agent(self):
        return Agent(
            role='Document Analysis Specialist',
            goal='Analyze the content of S3 buckets to identify sensitive data that can be accessed by a specified user (directly or indirectly).',
            backstory="Skilled in examining and classifying data in cloud environments to identify and report on sensitive information.",
            verbose=True,
            allow_delegation=False
        )

    def data_exfiltration_agent(self):
        return Agent(
            role='Data Exfiltration Specialist',
            goal='Perform and document the exfiltration of sensitive data accessible by a specified user to a public S3 bucket based on prior analysis.',
            backstory="Expert in identifying and exploiting S3 bucket vulnerabilities to simulate and document data exfiltration attempts.",
            verbose=True,
            allow_delegation=False
        )


    def ransomware_exploration_agent(self):
        return Agent(
            role='Ransomware Attack Specialist',
            goal='Simulate and document a ransomware attack on S3 buckets based on a prior exploration report',
            backstory=dedent("""\
                As a Ransomware Attack Specialist, you specialize in understanding and executing ransomware attacks in cloud environments.
                You have the skills to encrypt data and leave ransom notes in S3 buckets, exploiting any discovered permissions.
                Your task is to use the permissions identified in the lateral exploration report to simulate a ransomware attack, encrypting data in accessible S3 buckets, and documenting the attack strategy and its effectiveness in a comprehensive report.
            """),
            verbose=True,
            allow_delegation=False
        )
        
    def summary_and_briefing_agent(self):
        return Agent(
            role='Security Report Specialist',
            goal='Compile all gathered information into a comprehensive security report, including strategies to fix identified vulnerabilities.',
            backstory=dedent("""\
                As the Security Report Specialist, you excel at synthesizing complex information into clear and actionable reports.
                Your expertise lies in analyzing gathered data from various tasks, identifying key vulnerabilities, and proposing strategic remediation plans.
                You are adept at making technical information accessible and useful for stakeholders at all levels.
            """),
            verbose=True,
            allow_delegation=False
        )
