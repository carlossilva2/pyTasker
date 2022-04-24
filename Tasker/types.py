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
OP_COMMAND = ["target", "origin", "destination"]
OP_DELETE = ["target", "destination"]
OP_ZIP = ["target", "rename", "!deflate", "!destination"]
OP_INPUT = ["question"]
OP_ECHO = ["value"]
OP_REQUEST = ["endpoint", "method", "!body", "!headers"]
OP_REGISTRY = ["start_key", "key", "function", "!value", "!rename"]
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
    "copy", "zip", "move", "delete", "input", "echo", "registry", "request", "custom"
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


class Registry(TypedDict, total=False):
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
    rename: Optional[str]


class Custom(TypedDict):
    name: str
    step: int
    operation: Literal["custom"]
    extension_name: str


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


# Structure Definition for instruction_set
class InstructionSet(TypedDict):
    name: str
    description: str
    tasks: List[
        Union[Task, Copy, Move, Zip, Delete, Input, Echo, Request, Registry, Custom]
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

    def execute(self, task: str, logger: Logger, default_location: str) -> None:
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

    def _get_step_reference(self, task: Task, ref: str) -> Task:
        pass

    def __first_execution_routine(self) -> None:
        pass

    def __get_configs(self) -> Settings:
        pass

    def __load_extensions(self) -> None:
        return []


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


class CustomOperation(TypedDict):
    summon: str
    executable: OperationType


DESTINATION_CHECK_MAP: Dict[str, bool] = {
    "copy": True,
    "custom": False,
    "delete": True,
    "echo": False,
    "input": False,
    "move": True,
    "registry": False,
    "request": False,
    "zip": True,
}
