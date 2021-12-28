from typing import TypedDict, List, Literal
from logging import Logger

#Structure definitions
OP_INSTRUCTION = ['name', 'description', 'tasks']
OP_TASK = ['name', 'step', 'operation']

#Operation Key values
OP_COPY = ['target', 'origin', 'destination', 'subfolders']
OP_MOVE = ['target', 'origin', 'destination']
OP_COMMAND = ['target', 'origin', 'destination']
OP_DELETE = ['target', '!destination']
OP_ZIP = ['target', 'rename', '!deflate', '!destination']

#Available Operations
OPERATIONS = ['copy', 'zip', 'move', 'delete', 'command']
LIST_OPERATIONS = Literal['copy', 'zip', 'move', 'delete']

#Structure Definition for task
class Task(TypedDict):
    name: str
    step: int
    operation: str
    target: str
    origin: str
    destination: str
    rename: str
    subfolders: bool
    deflate: bool

#Structure Definition for instruction_set
class InstructionSet(TypedDict):
    name: str
    description: str
    tasks: List[Task]

class ParserType:

    def execute(self, task: str, logger: Logger, default_location: str) -> None:
        pass
    
    def warn_user(self) -> None:
        pass

    def __execute(self, task: Task) -> bool:
        pass

    def __check_destination_path(self, task: Task) -> None:
        pass

    def __analyse_keys(self) -> 'tuple[bool, str, str, str]':
        pass

    def __optional_parameters(self) -> None:
        pass

    def _get_all_file_paths(self, directory: str) -> 'List[str]':
        pass

    def _get_file_name(self, p: str) -> str:
        pass

    def __change_relative_locations(self, home: str) -> None:
        pass

    def _get_step_reference(self, task: Task) -> Task:
        pass

class OperationType:
    "Skeleton class for creating other, more complex Operations"

    __internal_state: bool
    task: Task
    context: ParserType
    logger: Logger

    def execute(self) -> None:
        pass
    
    def rollback(self) -> None:
        pass
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        pass