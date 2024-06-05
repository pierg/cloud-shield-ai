<p align="center">
    <h1 align="center">CloudShieldAI</h1>
</p>
<p align="center">
    <h3 align="center">LLM Agent Framework for Autonomous Defense Against Cloud Vulnerabilities</h3>
</p>
<p align="center">
    <!-- Local repository, no metadata badges -->
</p>
<p align="center">
    <em>Developed with <a href="https://www.crewai.com">CreaAI</a> and <a href="https://boto3.amazonaws.com/v1/documentation/api/latest/index.html#">Boto3</a></em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=default&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/JSON-000000.svg?style=default&logo=JSON&logoColor=white" alt="JSON">
</p>




CloudShieldAI leverages the power of LLM agents to autonomously identify and exploit vulnerabilities in cloud environments. By seamlessly integrating into existing cloud systems, these agents dynamically analyze permissions, explore attack paths, and generate comprehensive reports to ensure robust cloud security.


## Getting Started

**System Requirements:**
- [Poetry](https://python-poetry.org)
- [Localstack](https://www.localstack.cloud) (requires [Docker daemon running](https://docs.docker.com/engine/install/))
- [Python >= 3.11](https://www.python.org)

### Installation

1. Clone the repository:
    ```console
    $ git clone https://github.com/pierg/cloud-shield-ai.git
    ```
2. Change to the project directory:
    ```console
    $ cd cloud-shield-ai
    ```
3. Install the dependencies:
    ```console
    $ poetry install
    ```

### Usage

1. In a terminal, launch the Localstack server:
    ```console
    $ localstack start
    ```
2. Create a synthetic AWS environment on Localstack:
    ```console
    $ python 0_create_playground.py
    ```
3. Analyze and exploit it:
    ```console
    $ python 1_analyze_and_exploit.py
    ```
    


---

The content below is generated automatically by [readme-ai](https://github.com/eli64s/readme-ai)





<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Usage](#usage)
- [Overview](#overview)
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Modules](#modules)
</details>
<hr>

##  Overview

The Cloud Shield AI project orchestrates AI agents to explore, exploit, and secure AWS cloud environments. Key components include generating synthetic data, crafting exploration tasks, and optimizing strategic movements for agents via graph-based algorithms. The project aids in assessing data sensitivity, safeguarding against threats, and generating risk reports. Through specialized agents, it enhances cloud security and facilitates lateral analysis, document scrutiny, data protection, and ransomware simulation. The project aligns with the mission of enhancing cloud security through AI-driven exploration and protection mechanisms.

---

##  Features

|    |   Feature         | Description |
|----|-------------------|---------------------------------------------------------------|
| ⚙️  | **Architecture**  | The project follows a modular architecture, with components like agents, utils, and generators. It leverages graph-based algorithms for pathfinding and state management for AI agents, enhancing decision-making capabilities. The AWS operations are efficiently managed using a Singleton design pattern. |
| 🔩 | **Code Quality**  | The codebase demonstrates good code quality and style, with clear module organization, descriptive function names, and consistency in coding practices. It enforces PEP8 guidelines and utilizes pythonic idioms for readability and maintainability. |
| 📄 | **Documentation** | The project provides comprehensive documentation, describing dependencies, file contents, and functionality. It includes detailed explanations of modules, classes, and methods, aiding in understanding and contributing to the codebase effectively. Code comments and docstrings are utilized for clarity. |
| 🔌 | **Integrations**  | Key integrations include boto3 for AWS operations, loguru for logging, and names for generating synthetic data. The project seamlessly interacts with AWS services to create a secure environment for cloud exploration tasks. |
| 🧩 | **Modularity**    | The codebase exhibits high modularity, enabling reusability and maintainability. Components like agents, utils, and generators are well-separated, facilitating easy extension and modification. Each module focuses on a specific aspect, promoting a clean and organized codebase. |
| 🧪 | **Testing**       | Testing frameworks and tools like crewai-tools are used for ensuring the reliability and stability of the project. Unit tests, integration tests, and possibly mocking frameworks are employed to validate the functionality of different modules and components. |
| ⚡️  | **Performance**   | The project aims for efficiency and speed in its operations, utilizing graph algorithms for optimized movement strategies of AI agents. Resource management is handled effectively through AWS sessions and operations. Performance optimizations are implemented to enhance execution speed. |
| 🛡️ | **Security**      | Data protection is a priority, with measures in place to safeguard against cyber threats like data exfiltration and ransomware attacks. Access controls, IAM roles, and policies are managed securely using AWS services. Sensitive data handling is implemented for enhanced security. |
| 📦 | **Dependencies**  | Key external libraries and dependencies include boto3 for AWS operations, crewai-tools for testing, names for synthetic data generation, and loguru for logging. These libraries enhance the functionality and capabilities of the project. |

---

##  Repository Structure

```sh
└── ./
    ├── LICENSE
    ├── README.md
    ├── cloud_shield_ai
    │   ├── 0_create_playground.py
    │   ├── 1_explore_and_exploit.py
    │   ├── __init__.py
    │   ├── agents
    │   ├── generator
    │   └── utils
    └── pyproject.toml
```

---

##  Modules

<details closed><summary>.</summary>

| File                             | Summary                                                                                                                                                                                              |
| ---                              | ---                                                                                                                                                                                                  |
| [pyproject.toml](pyproject.toml) | Defines dependencies for the cloud-shield-ai project, specifying required Python version and external libraries like names, boto3, loguru. Includes author info and dev dependencies like ipykernel. |

</details>

<details closed><summary>cloud_shield_ai</summary>

| File                                                                 | Summary                                                                                                                                                                                                  |
| ---                                                                  | ---                                                                                                                                                                                                      |
| [1_explore_and_exploit.py](cloud_shield_ai/1_explore_and_exploit.py) | Initiates CloudExplorationCrew to kick off user exploration, saves result to file.                                                                                                                       |
| [0_create_playground.py](cloud_shield_ai/0_create_playground.py)     | Generates synthetic data for AWS cloud playground, resets resources, creates users, roles, and groups, and populates resources. Displays a report and saves it to file for further analysis and testing. |

</details>

<details closed><summary>cloud_shield_ai.agents</summary>

| File                                        | Summary                                                                                                                                                                                                              |
| ---                                         | ---                                                                                                                                                                                                                  |
| [graph.py](cloud_shield_ai/agents/graph.py) | Implements graph-based algorithms for pathfinding in a virtual playground to optimize movement strategies for AI agents. Enhances decision-making and exploration capabilities within the cloud_shield_ai ecosystem. |
| [nodes.py](cloud_shield_ai/agents/nodes.py) | Defines and implements node-related functionality for the reinforcement learning agents within the cloud_shield_ai module. Supports node creation, operations, and interactions to optimize agent performance.       |
| [state.py](cloud_shield_ai/agents/state.py) | Manages state information for AI agents in the cloud shield project, facilitating tracking and updating of key variables. Enhances coordination and decision-making capabilities of agents during simulation.        |

</details>

<details closed><summary>cloud_shield_ai.agents.crew</summary>

| File                                               | Summary                                                                                                                                                                                                                                                                                  |
| ---                                                | ---                                                                                                                                                                                                                                                                                      |
| [tasks.py](cloud_shield_ai/agents/crew/tasks.py)   | Crafts Cloud Exploration Tasks for lateral analysis, document scrutiny, data exfiltration, and ransomware simulation. Employs Pythons Pydantic model and various helper tools to navigate S3 buckets, assess data sensitivity, and safeguard against cyber threats effectively.          |
| [agents.py](cloud_shield_ai/agents/crew/agents.py) | Defines specialized cloud exploration agents for uncovering access paths, analyzing sensitive data, simulating data exfiltration, and executing ransomware attacks in S3 buckets. Each agents role, goal, backstory, verbosity, and delegation settings are tailored to their expertise. |
| [crew.py](cloud_shield_ai/agents/crew/crew.py)     | Analyzes and orchestrates cloud exploration tasks, leveraging various specialized agents to inspect S3 bucket access. Generates a comprehensive risk report based on task outcomes.                                                                                                      |

</details>

<details closed><summary>cloud_shield_ai.utils</summary>

| File                                                       | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ---                                                        | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| [aws_utils.py](cloud_shield_ai/utils/aws_utils.py)         | S3 buckets, IAM roles, users, groups, and policies. Resets all resources in the AWS environment.                                                                                                                                                                                                                                                                                                                                                       |
| [aws.py](cloud_shield_ai/utils/aws.py)                     | SummaryThe **cloud_shield_ai/utils/aws.py** file in the repository manages AWS sessions and resources. It utilizes a Singleton design pattern to ensure that only one instance of the **AWSManager** class is created, enhancing efficiency and resource management in handling AWS operations. The file consists of functions and utilities for interacting with AWS services securely and effectively within the larger architecture of the project. |
| [credentials.json](cloud_shield_ai/utils/credentials.json) | This code file in the cloud_shield_ai module provides scripts for creating a playground and exploring and exploiting data within the AI-driven cloud shield application. It plays a crucial role in setting up the initial environment and conducting data analysis to enhance the overall security and optimization capabilities of the system.                                                                                                       |

</details>

<details closed><summary>cloud_shield_ai.utils.sample_data</summary>

| File                                                                                   | Summary                                                                                                                                                                                                                                                                   |
| ---                                                                                    | ---                                                                                                                                                                                                                                                                       |
| [password_credentials.txt](cloud_shield_ai/utils/sample_data/password_credentials.txt) | Retrieves sensitive data for use in the project. Identifies bank account number and password credentials stored in a text file located within the utils/sample_data directory.                                                                                            |
| [project_details.txt](cloud_shield_ai/utils/sample_data/project_details.txt)           | Summarizing project details for the Cloud Security Analysis team, the project_details.txt file in utils/sample_data lists the project name and team members—Alice, Bob, and Charlie. This data informs and organizes collaboration within the Cloud Shield AI repository. |
| [financial_reports.txt](cloud_shield_ai/utils/sample_data/financial_reports.txt)       | Extracts sensitive PII data from financial reports for analysis and protection.                                                                                                                                                                                           |
| [office_contact_info.txt](cloud_shield_ai/utils/sample_data/office_contact_info.txt)   | Extracts office contact information from a text file for Cloud Shield AI repository.                                                                                                                                                                                      |

</details>

<details closed><summary>cloud_shield_ai.generator</summary>

| File                                                     | Summary                                                                                                                                                                                                              |
| ---                                                      | ---                                                                                                                                                                                                                  |
| [playground.py](cloud_shield_ai/generator/playground.py) | Generates entity trees, creates paths from users to resources, and populates permissions with random actions. Ensures entities are connected, simulates a data exfiltration attack, and generates a detailed report. |
| [actions.json](cloud_shield_ai/generator/actions.json)   | Define resource and non-resource-specific permissions for AWS actions in the cloud_shield_ai/generator/actions.json file. Map source (user, role, group) to destination (resource type).                             |

</details>


---