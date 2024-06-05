import json
import random
from pathlib import Path
from typing import List, Set, Dict, Optional
from cloud_shield_ai.utils import get_aws_manager_instance
from cloud_shield_ai import logger
import names
from cloud_shield_ai import output_folder


aws = get_aws_manager_instance()

class Entity:
    def __init__(self, name: str):
        self.name: str = name
        self.next: Set['Entity'] = set()
        self.prec: Set['Entity'] = set()
        self.marked: bool = False
        self.allowed_actions: List[str] = []
        if aws is not None:
            aws.add_entity(self.name, type(self).__name__)

    def add_next(self, entity: 'Entity') -> None:
        """Add a next entity ensuring no self-reference."""
        if entity != self and entity not in self.next:
            self.next.add(entity)
            entity.prec.add(self)
            if aws is not None:
                aws.add_connection(from_entity=(self.name, type(self).__name__), 
                                   to_entity=(entity.name, type(entity).__name__))

    def add_prec(self, entity: 'Entity') -> None:
        """Add a preceding entity ensuring no self-reference."""
        if entity != self and entity not in self.prec:
            self.prec.add(entity)
            entity.next.add(self)

    def generate_trace(self, direction: str = "forward", last: bool = True, prefix: str = "", actions = True) -> str:
        """Return the entity tree in the specified direction as a string."""
        result = []
        connections = self.next if direction == "forward" else self.prec
        result.append(prefix)
        if last:
            result.append("└── ")
            new_prefix = prefix + "    "
        else:
            result.append("├── ")
            new_prefix = prefix + "│   "
        
        result.append(f"{self.name}\t({type(self).__name__})\n")
        
        if actions and self.allowed_actions:
            result.append(new_prefix + f"|-- actions: {', '.join(self.allowed_actions)}\n")
        
        connection_list = sorted(connections, key=lambda x: x.name)
        for i, next_entity in enumerate(connection_list):
            result.append(next_entity.generate_trace(direction, i == len(connection_list) - 1, new_prefix, actions))
        
        return ''.join(result)



class User(Entity):
    pass

class Group(Entity):
    pass

class Role(Entity):
    pass

class Resource(Entity):
    pass

class EntityGenerator:
    def __init__(self, num_users: int, num_groups: int, num_roles: int, num_resources: int, num_users_to_resource_paths: int):
        self.users: List[User] = [User(f"{names.get_first_name()}_{_}") for _ in range(num_users - num_users_to_resource_paths)]
        # self.user_to_resources: List[User] = [User(f"{names.get_first_name()}__{_}") for _ in range(num_users_to_resource_paths)]
        # TODO: changed for easy reproducibility
        self.user_to_resources: List[User] = [User(f"Alice__{_}") for _ in range(num_users_to_resource_paths)]
        self.groups: List[Group] = [Group(f"Group{names.get_last_name()}_{_}") for _ in range(num_groups)]
        self.roles: List[Role] = [Role(f"Role{str(i)}") for i in range(num_roles)]
        self.resources: List[Resource] = [Resource(f"s3-bucket-{str(i)}") for i in range(num_resources)]
        self.entities: Dict[str, List[Entity]] = {
            "user": self.users,
            "group": self.groups,
            "role": self.roles,
            "resource": self.resources
        }

class ConnectionManager:
    def __init__(self, entities: Dict[str, List[Entity]], empty_connection_probability: float = 0.1):
        self.entities: Dict[str, List[Entity]] = entities
        self.empty_connection_probability: float = empty_connection_probability
        self.valid_connections = {
            "user": {"forward": ["group", "role", "resource"], "backward": []},
            "group": {"forward": ["role", "resource", None], "backward": ["user"]},
            "role": {"forward": ["role", "resource", None], "backward": ["user", "group", "role"]},
            "resource": {"forward": [], "backward": ["user", "group", "role"]}
        }

    def is_cycle(self, node: Entity, to_add: Entity, direction: str, visited: Optional[Set[Entity]] = None) -> bool:
        """Check if adding an entity creates a cycle."""
        if visited is None:
            visited = set()
        if node is to_add or node in visited:
            return True
        connections = node.prec if direction == "forward" else node.next
        for neighbor in connections:
            if self.is_cycle(neighbor, to_add, direction, visited | {node}):
                return True
        return False

    def create_connections(self, entity: Entity, direction: str = "forward", exclude_types: List[str] = [], force_type: str = "") -> Optional[Entity]:
        """Create connections between entities ensuring no cycles."""
        attempt_count = 0
        while attempt_count < 100:  # Limit attempts to prevent infinite loops
            valid_entities = set()
            for entity_type in self.valid_connections[entity.__class__.__name__.lower()][direction]:
                if entity_type in exclude_types:
                    continue
                if force_type and entity_type != force_type:
                    continue
                if entity_type is None:
                    if random.random() < self.empty_connection_probability:
                        return None
                else:
                    valid_entities |= set(self.entities[entity_type])
            if not valid_entities:
                continue
            new_entity = random.choice(list(valid_entities))
            # Enforcing group
            if "group" in list(valid_entities):
                new_entity = "group"
            if not self.is_cycle(entity, new_entity, direction):
                if direction == "forward":
                    entity.add_next(new_entity)
                else:
                    entity.add_prec(new_entity)
                return new_entity
            attempt_count += 1
        logger.warning(f"Failed to create a valid connection for entity {entity.name} after {attempt_count} attempts.")
        return None

    def ensure_connections(self) -> None:
        """Ensure all entities have the required connections."""
        for user in self.entities["user"]:
            self.create_connections(user)
        for group in self.entities["group"]:
            self.create_connections(group)
            self.create_connections(group, direction="backward")
            while not any(isinstance(prec, User) for prec in group.prec):
                self.create_connections(group, direction="backward")
        for role in self.entities["role"]:
            self.create_connections(role)
            self.create_connections(role, direction="backward")
            while not any(isinstance(prec, User) for prec in role.prec):
                self.create_connections(role, direction="backward")
        for resource in self.entities["resource"]:
            self.create_connections(resource, direction="backward")

    def get_connected_resources(self, entity_name: str, entity_type: str) -> List[Entity]:
        """Get all connected resources for a given entity."""
        entity_list = self.entities.get(entity_type, [])
        for entity in entity_list:
            if entity.name == entity_name:
                return [next_entity for next_entity in entity.next if isinstance(next_entity, Resource)]
        return []

class PathCreator:
    def __init__(self, connection_manager: ConnectionManager, path_length: List[int]):
        self.connection_manager: ConnectionManager = connection_manager
        self.path_length: List[int] = path_length

    def create_paths(self, user_to_resources: List[User]) -> List[List[Entity]]:
        """Create paths from users to resources."""
        paths_created: List[List[Entity]] = []
        for user in user_to_resources:
            path = [user]
            num_steps_to_resource = random.randint(self.path_length[0], self.path_length[1])
            current_entity = user
            current_entity.marked = True
            for step in range(num_steps_to_resource):
                if step == num_steps_to_resource - 1:
                    new_entity = self.connection_manager.create_connections(current_entity, direction="forward", force_type="resource")
                else:
                    new_entity = self.connection_manager.create_connections(current_entity, direction="forward", exclude_types=["resource", None])
                if new_entity is None:
                    break
                # Log the created path from user to the new entity
                logger.info(f"Created path from {user.name} to {new_entity.name}.")
                logger.info(f"Path so far: {' -> '.join([e.name for e in path])}")
                path.append(new_entity)
                current_entity = new_entity
                current_entity.marked = True
            if len(path) > 1:
                paths_created.append(path)
        return paths_created

class Playground:
    def __init__(self, 
                 total_num_users: int, 
                 total_num_roles: int, 
                 total_num_groups: int, 
                 total_num_resources: int, 
                 path_length: List[int]):
        self.entity_generator = EntityGenerator(total_num_users, total_num_groups, total_num_roles, total_num_resources, num_users_to_resource_paths=1)
        self.connection_manager = ConnectionManager(self.entity_generator.entities, empty_connection_probability=0.1)
        self.path_creator = PathCreator(self.connection_manager, path_length)
        
        actions_file = Path(__file__).parent / "actions.json"
        with open(actions_file, 'r') as f:
            self.actions = json.load(f)

        self.aws_manager = aws

    def instantiate_entities(self) -> None:
        """Instantiate entities."""
        self.entities = self.entity_generator.entities

    def connect_entities(self) -> None:
        """Ensure all entities are connected."""
        self.connection_manager.ensure_connections()
        
    def populate_permissions(self) -> None:
        """Populate permissions with random actions, according to the type of entity and its connections"""
        for entity_type, entities in self.entities.items():
            if entity_type == 'user':
                print("CISO")
            for entity in entities:
                # Determine applicable actions for the entity
                applicable_actions = []
                for action, details in self.actions['resource-specific'].items():
                    if entity_type in details['source']:
                        applicable_actions.append(action)
                        
                for action, details in self.actions['non-resource-specific'].items():
                    if entity_type in details['source']:
                        applicable_actions.append(action)

                # Randomly select some actions
                if applicable_actions:
                    # selected_actions = random.sample(applicable_actions, random.randint(1, 3))
                    selected_actions = applicable_actions
                    entity.allowed_actions = selected_actions
                    
                    self.aws_manager.update_identity_policy(entity.name, selected_actions)

                    # Get the connected resources for the entity
                    # TODO: not implemented
                    connected_resources = self.connection_manager.get_connected_resources(entity.name, entity_type)
                    connected_resource_names = [res.name for res in connected_resources]


    def inject_fault(self, user_name: str) -> None:
        # TODO: Implement a path from user_name to a resource such that one can 
        # perform a data exfiltration attack
        pass
    

    def create_paths(self) -> None:
        """Create paths from users to resources."""
        self.paths_created = self.path_creator.create_paths(self.entity_generator.user_to_resources)

    def generate_report(self) -> str:
        """Generate a comprehensive report of the entity trees."""
        report = []
        report.append("Users:\n")
        for user in self.entity_generator.users:
            report.append(user.generate_trace())
        report.append("\nResources:\n")
        for resource in self.entity_generator.resources:
            report.append(resource.generate_trace())
        report.append("\nUser to Resource Paths:\n")
        for user in self.entity_generator.user_to_resources:
            report.append(user.generate_trace())
        report.append("\nGroups:\n")
        for group in self.entity_generator.groups:
            report.append(group.generate_trace())
        report.append("\nRoles:\n")
        for role in self.entity_generator.roles:
            report.append(role.generate_trace())
        return ''.join(report)

    
    def user_to_resource_path(self) -> str:
        """Generate a comprehensive report of the entity trees."""
        report = []
        for user in self.entity_generator.user_to_resources:
            report.append(user.generate_trace(actions=False))
        return ''.join(report)

    def run(self) -> str:
        """Run the simulation to generate the report."""
        self.instantiate_entities()
        self.connect_entities()
        self.create_paths()
        self.populate_permissions()
        info = self.user_to_resource_path()
        with open(output_folder / "info.txt", "w") as f:
            f.write(info)
            print("Info saved to", output_folder / "info.txt")