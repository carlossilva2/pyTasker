import json
import os
import sys
import os.path as Path
from .operations import *
import platform
from .types import *
from logging import Logger
from typing import Union, List
from webbrowser import open as FileOpener

class Parser:

    def __init__(self, task: str, logger: Logger) -> None:
        self.__first_execution_routine()
        self.task: InstructionSet = json.load(open(f'{self.default_location}/{task}.tasker.json','r'))
        analysis = self.__analyse_keys()
        if not analysis[0]:
            logger.error(f'{analysis[3]} \"{analysis[1]}\" in {analysis[2]}')
            sys.exit(1)
        self.__optional_parameters()
        self.logger = logger
        self.__change_relative_locations(Path.expanduser('~'))
        self.__executed_tasks: List[Task] = []
        self.__operation_stack: list[OperationType] = []
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
        tick = True
        for operation in self.__operation_stack:
            if not operation.get_state() and '-No-Rollback' not in os.environ:
                if tick:
                    print()
                    print("--------------  Rollbacks  --------------")
                    print()
                    tick = False
                operation.rollback()
    
    def warn_user(self) -> None:
        "Verifies if current OS is one of the allowed ones"
        self.system = platform.system()
        if platform.system() not in self.__supported_os and ('-No-Warning' not in os.environ):
            ans = input(f"'{platform.system()}' is not part of the current supported OS list.\nAre you sure you want to continue? Y/n\n")
            if ans.lower() == 'y':
                pass
            elif ans.lower() == 'n':
                sys.exit(0)
            else:
                self.logger.error("Answer not allowed. Aborting...")
                sys.exit(1)
    
    def abort(self, reason: str) -> None:
        self.logger.error(reason)
        sys.exit(1)

    def __execute(self, task: Task) -> bool:
        try:
            self.__check_destination_path(task, DESTINATION_CHECK_MAP[task['operation']])
            if task['operation'] == 'copy':
                c = Copy(self, task, self.logger)
                self.__operation_stack.append(c)
                c.execute()
            elif task['operation'] == 'move':
                m = Move(self, task, self.logger)
                self.__operation_stack.append(m)
                m.execute()
            elif task['operation'] == 'delete':
                d = Delete(self, task, self.logger)
                self.__operation_stack.append(d)
                d.execute()
            elif task['operation'] == 'zip':
                z = Zip(self, task, self.logger)
                self.__operation_stack.append(z)
                z.execute()
            elif task['operation'] == 'command':
                command = Command(self, task, self.logger)
                self.__operation_stack.append(command)
                command.execute()
            elif task['operation'] == 'input':
                i = Input(self, task, self.logger)
                self.__operation_stack.append(i)
                i.execute()
            elif task['operation'] == 'echo':
                e = Echo(self, task, self.logger)
                self.__operation_stack.append(e)
                e.execute()
            elif task['operation'] == 'request':
                r = Request(self, task, self.logger)
                self.__operation_stack.append(r)
                r.execute()
            else:
                raise Exception(f"{task['operation']} is an Unknown Operation")
            self.__executed_tasks.append(task)
            return True
        except Exception as e:
            #print(e.with_traceback())
            self.__operation_stack[-1].set_state(False)
            return False
    
    def __check_destination_path(self, task: Task, needs_path_check: bool = True) -> None:
        "Check destination path if requested end folder is present. If not, create it."
        if needs_path_check:
            if 'destination' in task.keys():
                if '$' in task['destination']:
                    splitted_path = task['destination'].split("/")[-1]
                    if '.' in splitted_path:
                        _ = splitted_path.split(".")
                        ref = self._get_step_reference(task, _[0])
                        task['destination'] = ref[_[1]]
                    else:
                        ref = self._get_step_reference(task, task['destination'])
                        task['destination'] = ref['destination']
            if 'origin' in task.keys():
                if '$' in task['origin']:
                    splitted_path = task['origin'].split("/")[-1]
                    if '.' in splitted_path:
                        _ = splitted_path.split(".")
                        ref = self._get_step_reference(task, _[0])
                        task['origin'] = ref[_[1]]
                    else:
                        ref = self._get_step_reference(task, task['destination'])
                        task['destination'] = ref['destination']
            if 'destination' not in task.keys():
                if task['target'].startswith('$'):
                    if '.' in task['target']:
                        _ = task['target'].split(".")
                        ref = self._get_step_reference(task, _[0])
                        task['destination'] = ref[_[1]]
                    else:
                        ref = self._get_step_reference(task, task['target'])
                        task['destination'] = ref['destination']
                else:
                    self.logger.debug("Destination parameter is not present")
                    raise Exception()
            destination = task['destination'].split('/')[-1]
            destination_parent = '/'.join(_ for _ in task['destination'].split('/')[:-1])
            if destination not in os.listdir(f"{destination_parent}"):
                os.mkdir(f"{task['destination']}")
    
    def __analyse_keys(self) -> 'tuple[bool, Union[str,None], Union[str,None], Union[str,None]]':
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
        for root, _, files in os.walk(directory):
            for filename in files:
                file_paths.append(Path.join(root, filename).replace('\\','/'))
        return file_paths
    
    def __change_relative_locations(self, home: str) -> None:
        for task in self.task['tasks']:
            if (home != None or home != ''):
                if 'destination' in task.keys():
                    task['destination'] = f"{home}/{task['destination']}".replace('\\','/')
                if 'origin' in task.keys() and ":" not in task['origin']:
                    task['origin'] = f"{home}/{task['origin']}".replace('\\','/')
    
    def _get_step_reference(self, task: Task, ref: str, get_from_operation: bool = False) -> Union[Task, dict]:
        #get step in reference
        step_index = next((index for (index, d) in enumerate(self.__executed_tasks) if d['step'] == int(ref.replace('$',''))), None)
        if step_index == None:
            self.logger.error(f"Reference in Task \"{task['name']}\" is either not been executed or doesn't exist.")
            raise Exception()
        vars = {}
        if get_from_operation:
            pass
        for _ in self.__operation_stack:
            if _.task["step"] == step_index:
                vars = _.__dict__
                break
        return dict(self.__executed_tasks[step_index], **vars)
    
    def __first_execution_routine(self) -> None:
        "Create the initial configuration and setup necessary directories"
        def create_initial_config(p: str) -> None:
            with open(f"{p}/.tasker/config.json",'w') as config:
                json.dump({
                    "current_location": p,
                    "default_location": p
                }, config, indent=4)
                config.close()
        root_path = Path.expanduser('~')
        root_folders = os.listdir(root_path)
        if '.tasker' not in root_folders:
            os.mkdir(f"{root_path}/.tasker")
            os.mkdir(f"{root_path}/.tasker/Tasks")
            create_initial_config(root_path)
        else:
            tasker_folder = os.listdir(f"{Path.expanduser('~')}/.tasker")
            if 'config.json' not in tasker_folder:
                create_initial_config(root_path)
        self.default_location = f"{root_path}/.tasker/Tasks"

    # Static Methods

    @staticmethod
    def do_config() -> None:
        "Create the initial configuration and setup necessary directories"
        def create_initial_config(p: str) -> None:
            with open(f"{p}/.tasker/config.json",'w') as config:
                json.dump({
                    "current_location": p,
                    "default_location": p
                }, config, indent=4)
                config.close()
        root_path = Path.expanduser('~')
        root_folders = os.listdir(root_path)
        if '.tasker' not in root_folders:
            os.mkdir(f"{root_path}/.tasker")
            os.mkdir(f"{root_path}/.tasker/Tasks")
            create_initial_config(root_path)
        else:
            tasker_folder = os.listdir(f"{Path.expanduser('~')}/.tasker")
            if 'config.json' not in tasker_folder:
                create_initial_config(root_path)
    
    @staticmethod
    def list_all_tasks() -> List[str]:
        "Lists all Task templates created"
        Parser.do_config()
        return [_.replace('.tasker.json', '') for _ in os.listdir(f"{Path.expanduser('~')}/.tasker/Tasks")]
    
    @staticmethod
    def create_new_task(file_name:str, name: str, description: str) -> InstructionSet:
        Parser.do_config()
        i: InstructionSet = {
            'name': name,
            'description': description,
            'tasks': [
                
            ]
        }
        with open(f"{Path.expanduser('~')}/.tasker/Tasks/{file_name}.tasker.json", 'w') as instruction_set:
            json.dump(i, instruction_set, indent=4)
            instruction_set.close()
        return i
    
    @staticmethod
    def open_file_for_edit(file: str) -> None:
        Parser.do_config()
        FileOpener(f"{Path.expanduser('~')}/.tasker/Tasks/{file}.tasker.json")