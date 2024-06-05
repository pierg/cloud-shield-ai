from crewai import Crew
from langchain_openai import ChatOpenAI

from cloud_shield_ai.agents.crew.agents import CloudExplorationAgents
from cloud_shield_ai.agents.crew.tasks import CloudExplorationTasks


class CloudExplorationCrew:
    def __init__(self):
        
        agents = CloudExplorationAgents()
        self.lateral_exploration_agent = agents.lateral_exploration_agent()
        self.document_analysis_agent = agents.document_analysis_agent()
        self.data_exfiltration_agent = agents.data_exfiltration_agent()
        self.ransomware_exploration_agent = agents.ransomware_exploration_agent()

    def kickoff(self, username: str):
                
        tasks = CloudExplorationTasks()
                
        crew = Crew(
            agents=[self.lateral_exploration_agent, 
                    self.document_analysis_agent,
                    self.data_exfiltration_agent,
                    # self.ransomware_exploration_agent
                    ],
            tasks=[
                tasks.lateral_exploration_task(self.lateral_exploration_agent, username),
                tasks.document_analysis_task(self.document_analysis_agent, username),
                tasks.data_exfiltration_task(self.data_exfiltration_agent, username),
				# tasks.ransomware_exploration_task(self.ransomware_exploration_agent),
            ],
            manager_llm=ChatOpenAI(model="gpt-4"),
            verbose=True
        )
        
        result = crew.kickoff()
        return result
        