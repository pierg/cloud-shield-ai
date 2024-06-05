from crewai import Crew
from langchain_openai import ChatOpenAI

from cloud_shield_ai.agents.crew.agents import CloudExplorationAgents
from cloud_shield_ai.agents.crew.tasks import CloudExplorationTasks

class Manager:

    def __init__(self, agents_instance, tasks_instance):
        self.agents_instance = agents_instance
        self.tasks_instance = tasks_instance
        self.agents = {}
        self.tasks = {}

    def create_all_agents(self):
        self.agents['lateral_exploration_agent'] = self.agents_instance.lateral_exploration_agent()
        self.agents['document_analysis_agent'] = self.agents_instance.document_analysis_agent()
        self.agents['data_exfiltration_agent'] = self.agents_instance.data_exfiltration_agent()
        self.agents['ransomware_exploration_agent'] = self.agents_instance.ransomware_exploration_agent()
        self.agents['summary_and_briefing_agent'] = self.agents_instance.summary_and_briefing_agent()

    def create_all_tasks(self, username):
        # Create the lateral exploration task
        self.tasks['lateral_exploration_task'] = self.tasks_instance.lateral_exploration_task(
            self.agents['lateral_exploration_agent'], username
        )
        
        # Create the document analysis task, which depends on the lateral exploration task
        self.tasks['document_analysis_task'] = self.tasks_instance.document_analysis_task(
            self.agents['document_analysis_agent'], username, 
            context=[self.tasks['lateral_exploration_task']]
        )
        
        # Create the data exfiltration task, which depends on the both previous tasks
        self.tasks['data_exfiltration_task'] = self.tasks_instance.data_exfiltration_task(
            self.agents['data_exfiltration_agent'], username,
            context=[self.tasks['lateral_exploration_task'], self.tasks['document_analysis_task']]
        )
        
        # Create the ransomware exploration task
        self.tasks['ransomware_exploration_task'] = self.tasks_instance.ransomware_exploration_task(
            self.agents['ransomware_exploration_agent'],
            context=[self.tasks['lateral_exploration_task'], self.tasks['document_analysis_task']]
        )

        # Create the summary and briefing task, which depends on all previous tasks
        self.tasks['summary_and_briefing_task'] = self.tasks_instance.summary_and_briefing_task(
            self.agents['summary_and_briefing_agent'], 
            context=[
                self.tasks['lateral_exploration_task'], 
                self.tasks['document_analysis_task'], 
                self.tasks['data_exfiltration_task'],
                self.tasks['ransomware_exploration_task']
            ]
        )


class CloudExplorationCrew:
    def __init__(self):
        # Initialize TaskManager with CloudExplorationAgents and CloudExplorationTasks instances
        self.manager = Manager(CloudExplorationAgents(), CloudExplorationTasks())
        
        # Create all agents
        self.manager.create_all_agents()

    def kickoff(self, username: str):
        # Create all tasks for the specified user
        self.manager.create_all_tasks(username)
        
        # Gather agents and tasks from the task manager
        agents = [
            self.manager.agents['lateral_exploration_agent'],
            self.manager.agents['document_analysis_agent'],
            self.manager.agents['data_exfiltration_agent'],
            self.manager.agents['ransomware_exploration_agent'],
            self.manager.agents['summary_and_briefing_agent']
        ]
        
        tasks = [
            self.manager.tasks['lateral_exploration_task'],
            self.manager.tasks['document_analysis_task'],
            self.manager.tasks['data_exfiltration_task'],
            self.manager.tasks['ransomware_exploration_task'],
            self.manager.tasks['summary_and_briefing_task']
        ]
        
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
