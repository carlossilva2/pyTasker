from typing import TypedDict, List, Literal

#Structure definitions
OP_INSTRUCTION = ['name', 'description', 'tasks']
OP_TASK = ['name', 'step', 'operation']

#Operation Key values
OP_COPY = ['target', 'origin', 'destination', 'subfolders']
OP_MOVE = ['target', 'origin', 'destination']
OP_DELETE = ['target', 'destination']
OP_ZIP = ['target', 'destination', 'rename']

#Available Operations
OPERATIONS = ['copy', 'zip', 'move', 'delete']
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

#Structure Definition for instruction_set
class InstructionSet(TypedDict):
    name: str
    description: str
    tasks: List[Task]