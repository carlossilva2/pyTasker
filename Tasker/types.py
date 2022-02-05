from typing import TypedDict, List, Literal, Dict
from logging import Logger

#Structure definitions
OP_INSTRUCTION = ['name', 'description', 'tasks']
OP_TASK = ['name', 'step', 'operation']

#Operation Key values
OP_COPY = ['target', 'origin', 'destination', 'subfolders']
OP_MOVE = ['target', 'origin', 'destination']
OP_COMMAND = ['target', 'origin', 'destination']
OP_DELETE = ['target', 'destination']
OP_ZIP = ['target', 'rename', '!deflate', '!destination']
OP_INPUT = ['question']
OP_ECHO = ['value']
OP_REQUEST = ['endpoint', 'method', '!body', '!headers']

#Available Operations
OPERATIONS = ['copy', 'zip', 'move', 'delete', 'command', 'input', 'echo', 'request']
LIST_OPERATIONS = Literal['copy', 'zip', 'move', 'delete', 'input', 'echo', 'request']

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
    question: str
    value: str
    endpoint: str
    method: Literal['get', 'post', 'delete', 'put']

#Structure Definition for instruction_set
class InstructionSet(TypedDict):
    name: str
    description: str
    tasks: List[Task]

class ParserType:

    system: str
    task: InstructionSet
    logger: Logger

    def execute(self, task: str, logger: Logger, default_location: str) -> None:
        pass
    
    def warn_user(self) -> None:
        pass

    def abort(self, reason: str) -> None:
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

    def _get_step_reference(self, task: Task, ref: str, get_from_operation: bool = False) -> Task:
        pass

class OperationType:
    "Skeleton class for creating other, more complex Operations"

    __internal_state: bool
    task: Task
    context: ParserType
    logger: Logger
    _type: str

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

DESTINATION_CHECK_MAP: Dict[str, bool] = {
    "copy": True,
    "delete": True,
    "echo": False,
    "input": False,
    "move": True,
    "registry": False,
    "request": False,
    "zip": True
}