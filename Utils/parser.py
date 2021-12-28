import json
import os
import sys
import shutil
import os.path as Path
import Utils.operations as Operations
import platform
from .types import *
from logging import Logger
from zipfile import ZipFile, ZIP_DEFLATED

class Parser:

    def __init__(self, task: str, logger: Logger, default_location: str = Path.expanduser('~')) -> None:
        self.task: InstructionSet = json.load(open(f'./Tasks/{task}.json','r'))
        analysis = self.__analyse_keys()
        if not analysis[0]:
            logger.error(f'{analysis[3]} \"{analysis[1]}\" in {analysis[2]}')
            sys.exit(1)
        self.__optional_parameters()
        self.home = default_location
        self.logger = logger
        self.__change_relative_locations(default_location)
        self.__executed_tasks: 'List[Task]' = []
        self.__operation_stack = []
        self.__supported_os = ['Windows'] #List of Tasker supported OSes
    
    def execute(self) -> None:
        self.task['tasks'] = sorted(self.task['tasks'], key=lambda d: d['step'])
        for task in self.task['tasks']:
            if self.__execute(task):
                self.logger.debug(f"Task \"{task['name']}\" - OK")
            else:
                self.logger.error(f"Task \"{task['name']}\" - ERROR")
        #Reverse Operation Stack
        #Do this to use rollback feature on a reverse order
        self.__operation_stack.reverse()
        for operation in self.__operation_stack:
            if not operation.get_state():
                self.logger.debug("Failed operation")
    
    def warn_user(self) -> None:
        "Verifies if current OS is one of the allowed ones"
        if platform.system() not in self.__supported_os:
            ans = input(f"'{platform.system()}' is not part of the current supported OS list.\nAre you sure you want to continue? Y/n\n")
            if ans.lower() == 'y':
                pass
            elif ans.lower() == 'n':
                sys.exit(0)
            else:
                self.logger.error("Answer not allowed. Aborting...")
                sys.exit(1)

    def __execute(self, task: Task) -> bool:
        try:
            self.__check_destination_path(task)
            if task['operation'] == 'copy':
                c = Operations.Copy(self, task, self.logger)
                c.execute()
                self.__operation_stack.append(c)
                #_copy(self, task)
            elif task['operation'] == 'move':
                m = Operations.Move(self, task, self.logger)
                m.execute()
                self.__operation_stack.append(m)
                #_move(self, task)
            elif task['operation'] == 'delete':
                _delete(self, task)
            elif task['operation'] == 'zip':
                _zip(self, task)
            else:
                raise Exception(f"{task['operation']} is an Unknown Operation")
            self.__executed_tasks.append(task)
            return True
        except Exception as e:
            return False
    
    def __check_destination_path(self, task: Task) -> None:
        "Check destination path if requested end folder is present. If not, create it."
        if 'destination' not in task.keys():
            if task['target'].startswith('$'):
                ref = self._get_step_reference(task)
                task['destination'] = ref['destination']
            else:
                self.logger.debug("Destination parameter is not present")
                raise Exception()
        destination = task['destination'].split('/')[-1]
        destination_parent = '/'.join(_ for _ in task['destination'].split('/')[:-1])
        if destination not in os.listdir(f"{destination_parent}"):
            os.mkdir(f"{task['destination']}")
    
    def __analyse_keys(self) -> 'tuple[bool, str, str, str]':
        "Verify if the structure of the Instruction Set is defined correctly"
        for key in OP_INSTRUCTION:
            if key not in self.task.keys():
                return (False, key, 'Definition', 'Missing key')
        if len(self.task['tasks']) > 0:
            for _task in self.task['tasks']:
                for key in OP_TASK:
                    if key not in _task.keys():
                        return (False, key, 'Task', 'Missing key')
                op = _task['operation']
                if op not in OPERATIONS:
                    return (False, op, f"\"{_task['name']}\" Task", 'Unknown Operation')
                operation_keys: list[str] = eval(f'OP_{op.upper()}')
                for key in operation_keys:
                    if key not in _task.keys():
                        #Check for optional parameters
                        if not key.startswith("!"):
                            return (False, key, f"\"{_task['name']}\" Task", 'Missing key')
        return (True, None, None, None)
    
    def __optional_parameters(self) -> None:
        to_change = []
        for i in range(len(self.task['tasks'])):
            #Replace optional parameter identifier with a definitive one
            for key in self.task['tasks'][i].keys():
                if key.startswith("!"):
                    to_change.append([i,key])
        for obj in to_change:
            self.task['tasks'][obj[0]][obj[1].replace("!","")] = self.task['tasks'][obj[0]][obj[1]]
            del self.task['tasks'][obj[0]][obj[1]]

    def _get_all_file_paths(self, directory: str) -> 'List[str]':
        file_paths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                file_paths.append(Path.join(root, filename).replace('\\','/'))
        return file_paths
    
    def _get_file_name(self, p: str) -> str:
        if '/' in p:
            return p.split('/')[-1]
        return p
    
    def __change_relative_locations(self, home: str) -> None:
        for task in self.task['tasks']:
            if (home != None or home != ''):
                if 'destination' in task.keys():
                    task['destination'] = f"{home}/{task['destination']}".replace('\\','/')
                if 'origin' in task.keys() and ":" not in task['origin']:
                    task['origin'] = f"{home}/{task['origin']}".replace('\\','/')
    
    def _get_step_reference(self, task: Task) -> Task:
        #get step in reference
        step_index = next((index for (index, d) in enumerate(self.__executed_tasks) if d['step'] == int(task['target'].replace('$',''))), None)
        if step_index == None:
            self.logger.error(f"Reference in Task \"{task['name']}\" is either not been executed or doesn't exist.")
            raise Exception()
        return self.__executed_tasks[step_index]


#OPERATIONS

def _copy(ctx: Parser, task: Task) -> None:
    if task['target'] == '*':
        files = ctx._get_all_file_paths(task['origin']) if task['subfolders'] == True else os.listdir(task['origin'])
        for f in files:
            ori_path = f if task['subfolders'] == True else f"{task['origin']}/{f}"
            shutil.copyfile(f"{ori_path}", f"{task['destination']}/{ctx._get_file_name(f)}")
    elif '*' in task['target']:
        all_files = ctx._get_all_file_paths(task['origin']) if task['subfolders'] == True else os.listdir(task['origin'])
        files = [_ for _ in all_files if ctx._get_file_name(_).endswith(task['target'].split('.')[1])]
        for f in files:
            ori_path = f if task['subfolders'] == True else f"{task['origin']}/{f}"
            shutil.copyfile(f"{ori_path}", f"{task['destination']}/{ctx._get_file_name(f)}")
    else:
        shutil.copyfile(f"{task['origin']}/{task['target']}", f"{task['destination']}/{task['target']}")

def _move(ctx: Parser, task: Task) -> None:
    pass

def _delete(ctx: Parser, task: Task) -> None:
    fp = []
    if task['target'] == '*':
        fp = ctx._get_all_file_paths(task['destination']) if task['subfolders'] == True else os.listdir(task['destination'])
    elif '*' in task['target']:
        all_files = ctx._get_all_file_paths(task['destination']) if task['subfolders'] == True else os.listdir(task['destination'])
        fp = [_ for _ in all_files if ctx._get_file_name(_).endswith(task['target'].split('.')[1])]
    elif task['target'].startswith('$'):
        step = ctx._get_step_reference(task)
        all_files = ctx._get_all_file_paths(step['destination'])
        fp = [_ for _ in all_files if ctx._get_file_name(_).endswith(step['target'].split('.')[1])]
    for _ in fp:
        os.remove(_)

def _zip(ctx: Parser, task: Task) -> None:
    fp = []
    files = []
    if task['target'].startswith('$'):
        step = ctx._get_step_reference(task)
        fp = ctx._get_all_file_paths(step['destination']) if task['subfolders'] == True else [f"{step['destination']}/{_}" for _ in os.listdir(step['destination'])]
        files = []#TODO: [_ for _ in os.listdir(step['destination']) if not os.path.isfile(_)  f"{step['destination']}/{_}"]
    else:
        if task['target'] == '*':
            fp = ctx._get_all_file_paths(task['destination']) if task['subfolders'] == True else [f"{task['destination']}/{_}" for _ in os.listdir(task['destination'])]
            files = os.listdir(task['destination'])
    with ZipFile(f"{task['destination']}/{task['rename']}.zip", 'w', ZIP_DEFLATED) as zip:
        for i, _ in enumerate(fp):
            if "deflate" in task.keys():
                if task['deflate'] == True:
                    zip.write(_, files[i])
                else:
                    zip.write(_)
            else:
                zip.write(_)
        zip.close()