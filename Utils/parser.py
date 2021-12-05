import json
import os
import sys
import shutil
import os.path as Path
from .types import *
from logging import Logger
from zipfile import ZipFile, ZIP_DEFLATED

class Parser:

    def __init__(self, task: str, logger: Logger, default_location: str = Path.expanduser('~')) -> None:
        self.task: InstructionSet = json.load(open(f'./Tasks/{task}.json','r'))
        analysis = self.__analyse_keys(self.task)
        if not analysis[0]:
            logger.error(f'{analysis[3]} \"{analysis[1]}\" in {analysis[2]}')
            sys.exit(1)
        self.home = default_location
        self.logger = logger
        self.__change_relative_locations(default_location)
        self.__executed_tasks: 'List[Task]' = []
    
    def execute(self) -> None:
        self.task['tasks'] = sorted(self.task['tasks'], key=lambda d: d['step'])
        for task in self.task['tasks']:
            if self.__execute(task):
                self.logger.debug(f"Task \"{task['name']}\" - OK")
            else:
                self.logger.error(f"Task \"{task['name']}\" - ERROR")

    def __execute(self, task: Task) -> bool:
        try:
            self.__check_destination_path(task)
            if task['operation'] == 'copy':
                if '*' in task['target']:
                    all_files = self.__get_all_file_paths(task['origin']) if task['subfolders'] == True else os.listdir(task['origin'])
                    files = [_ for _ in all_files if self.__get_file_name(_).endswith(task['target'].split('.')[1])]
                    for f in files:
                        ori_path = f if task['subfolders'] == True else f"{task['origin']}/{f}"
                        shutil.copyfile(f"{ori_path}", f"{task['destination']}/{self.__get_file_name(f)}")
                else:
                    shutil.copyfile(f"{task['origin']}/{task['target']}", f"{task['destination']}/{task['target']}")
            elif task['operation'] == 'move':
                pass
            elif task['operation'] == 'delete':
                pass
            elif task['operation'] == 'zip':
                fp = []
                files = []
                if task['target'].startswith('$'):
                    #get step in reference
                    step_index = next((index for (index, d) in enumerate(self.__executed_tasks) if d['step'] == int(task['target'].replace('$',''))), None)
                    if step_index == None:
                        self.logger.error(f"Reference in Task \"{task['name']}\" is either not been executed or doesn't exist.")
                        raise Exception()
                    step = self.__executed_tasks[step_index]
                    fp = [f"{step['destination']}/{_}" for _ in os.listdir(step['destination'])]
                    files = os.listdir(step['destination'])
                else:
                    pass

                with ZipFile(f"{task['destination']}/{task['rename']}.zip", 'w', ZIP_DEFLATED) as zip:
                    for i, _ in enumerate(fp):
                        zip.write(_, files[i])
                    zip.close()

            else:
                raise Exception(f"{task['operation']} is an Unknown Operation")
            self.__executed_tasks.append(task)
            return True
        except Exception as e:
            return False
    
    def __check_destination_path(self, task: Task) -> None:
        "Check destination path if requested end folder is present. If not, create it."
        destination = task['destination'].split('/')[-1]
        destination_parent = '/'.join(_ for _ in task['destination'].split('/')[:-1])
        if destination not in os.listdir(f"{destination_parent}"):
            os.mkdir(f"{task['destination']}")
    
    def __analyse_keys(self, task: InstructionSet) -> 'tuple[bool, str, str, str]':
        "Verify if the structure of the Instruction Set is defined correctly"
        for key in OP_INSTRUCTION:
            if key not in task.keys():
                return (False, key, 'Definition', 'Missing key')
        if len(task['tasks']) > 0:
            for _task in task['tasks']:
                for key in OP_TASK:
                    if key not in _task.keys():
                        return (False, key, 'Task', 'Missing key')
                op = _task['operation']
                if op not in OPERATIONS:
                    return (False, op, f"\"{_task['name']}\" Task", 'Unknown Operation')
                operation_keys = eval(f'OP_{op.upper()}')
                for key in operation_keys:
                    if key not in _task.keys():
                        return (False, key, f"\"{_task['name']}\" Task", 'Missing key')
        return (True, None, None)
    
    def __get_all_file_paths(self, directory: str) -> 'List[str]':
        file_paths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                file_paths.append(Path.join(root, filename).replace('\\','/'))
        return file_paths
    
    def __get_file_name(self, p: str) -> str:
        return p.split('/')[-1]
    
    def __change_relative_locations(self, home: str) -> None:
        for task in self.task['tasks']:
            if (home != None or home != ''):
                task['destination'] = f"{home}/{task['destination']}".replace('\\','/')
                if 'origin' in task.keys() and ":" not in task['origin']:
                    task['origin'] = f"{home}/{task['origin']}".replace('\\','/')
