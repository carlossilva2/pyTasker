from logging import Logger
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

try:
    from typing import TypedDict
except Exception:
    from typing_extensions import TypedDict

# Structure definitions
OP_INSTRUCTION = ["name", "description", "tasks"]
OP_TASK = ["name", "step", "operation"]

# Operation Key values
OP_COPY = ["target", "origin", "destination", "subfolders"]
OP_MOVE = ["target", "origin", "destination"]
OP_COMMAND = ["output", "command"]
OP_DELETE = ["target", "destination"]
OP_ZIP = ["target", "rename", "!deflate", "!destination"]
OP_INPUT = ["question"]
OP_ECHO = ["value"]
OP_REQUEST = ["endpoint", "method", "!body", "!headers"]
# OP_REGISTRY = ["start_key", "key", "function", "!value", "!rename"]
OP_CUSTOM = ["extension_name"]

# Available Operations
OPERATIONS = [
    "copy",
    "zip",
    "move",
    "delete",
    "command",
    "input",
    "echo",
    "registry",
    "request",
    "custom",
]
LIST_OPERATIONS = Literal[
    "copy",
    "zip",
    "move",
    "delete",
    "input",
    "echo",
    "registry",
    "request",
    "custom",
    "command",
]


class Copy(TypedDict):
    name: str
    step: int
    operation: Literal["copy"]
    target: str
    origin: str
    destination: str
    subfolders: bool


class Move(TypedDict):
    name: str
    step: int
    operation: Literal["move"]
    target: str
    origin: str
    destination: str


class Zip(TypedDict, total=False):
    name: str
    step: int
    operation: Literal["zip"]
    rename: str
    target: str
    subfolders: bool
    destination: Optional[str]
    deflate: Optional[bool]


class Delete(TypedDict):
    name: str
    step: int
    operation: Literal["delete"]
    target: str
    destination: str


class Input(TypedDict):
    name: str
    step: int
    operation: Literal["input"]
    question: str


class Echo(TypedDict):
    name: str
    step: int
    operation: Literal["echo"]
    value: str


class Request(TypedDict, total=False):
    name: str
    step: int
    operation: Literal["request"]
    endpoint: str
    method: Literal["get", "post", "delete", "put"]
    body: Optional[Union[str, Dict[str, Any], None]]
    headers: Optional[Union[str, Dict[str, Any], None]]


""" class Registry(TypedDict, total=False):
    name: str
    step: int
    operation: Literal["registry"]
    start_key: Literal[
        "classes-root", "current-user", "current-config", "local-machine", "users"
    ]
    key: str
    function: Literal["get", "set", "create", "backup"]
    type: Literal["sz", "multisz", "none", "binary", "dword", "qword"]
    value: Optional[Union[str, int]]
    rename: Optional[str] """


class Custom(TypedDict):
    name: str
    step: int
    operation: Literal["custom"]
    extension_name: str


class Command(TypedDict):
    name: str
    step: int
    operation: Literal["command"]
    output: bool
    command: str


# Structure Definition for task
class Task(TypedDict):
    name: str
    step: int
    operation: LIST_OPERATIONS
    target: str
    origin: str
    destination: str
    rename: str
    subfolders: bool
    deflate: Optional[bool]
    question: str
    value: str
    endpoint: str
    method: Literal["get", "post", "delete", "put"]
    body: Optional[Union[str, Dict[str, Any], None]]
    headers: Optional[Union[str, Dict[str, Any], None]]
    start_key: Literal[
        "classes-root", "current-user", "current-config", "local-machine", "users"
    ]
    function: Literal["get", "set", "create", "backup"]
    extension_name: str
    output: bool
    command: str


# Structure Definition for instruction_set
class InstructionSet(TypedDict):
    name: str
    description: str
    tasks: List[
        Union[Task, Copy, Move, Zip, Delete, Input, Echo, Request, Custom, Command]
    ]


class Extension(TypedDict):
    name: str
    file: str
    path: str


class Alias(TypedDict):
    name: str
    path: str


class Settings(TypedDict):
    current_location: str
    default_location: str
    extensions: List[Extension]
    alias: List[Alias]


class ParserType:

    system: str
    task: InstructionSet
    logger: Logger
    settings: Settings
    execution: Dict[str, Union[float, str]]
    supported_os: List[str]
    extensions: list
    default_location: str
    __executed_tasks: List[Task]
    __operation_stack: list

    def execute(self) -> None:
        pass

    def warn_user(self) -> None:
        pass

    def abort(self, reason: str) -> None:
        pass

    def __execute(self, task: Task) -> bool:
        return True

    def __check_destination_path(self, task: Task) -> None:
        pass

    def __analyse_keys(self) -> Tuple[bool, str, str, str]:
        return (True, "", "", "")

    def __optional_parameters(self) -> None:
        pass

    def _get_all_file_paths(self, directory: str) -> List[str]:
        return []

    def _get_file_name(self, p: str) -> str:
        return ""

    def __change_relative_locations(self, home: str) -> None:
        pass

    def _get_step_reference(self, task: Task, ref: str) -> Union[Task, dict]:
        return Task()

    def __first_execution_routine(self) -> None:
        pass

    def __get_configs(self) -> Settings:
        return Settings()

    def __load_extensions(self) -> None:
        pass

    @staticmethod
    def do_config() -> None:
        pass

    @staticmethod
    def list_all_tasks() -> List[str]:
        return []

    @staticmethod
    def create_new_task(file_name: str, name: str, description: str) -> InstructionSet:
        return InstructionSet()

    @staticmethod
    def open_file_for_edit(file: str) -> None:
        pass

    @staticmethod
    def create_extension(name: str) -> None:
        pass

    @staticmethod
    def add_alias(alias: Alias, logger: Logger) -> None:
        pass


class OperationType:
    "Skeleton class for creating other, more complex Operations"

    task: Task
    context: ParserType
    logger: Logger
    affected_files: List[str]
    _type: str
    __internal_state: bool

    def execute(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        pass


class CustomOperation(TypedDict):
    summon: str
    executable: OperationType


DESTINATION_CHECK_MAP: Dict[str, bool] = {
    "copy": True,
    "command": False,
    "custom": False,
    "delete": True,
    "echo": False,
    "input": False,
    "move": True,
    "request": False,
    "zip": True,
}
