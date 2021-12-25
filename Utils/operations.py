import os
import sys
import shutil
from Utils.types import Task
from logging import Logger
from tqdm import tqdm

class Copy:

    def __init__(self, ctx, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag

    def execute(self) -> None:
        files = self.context._get_all_file_paths(self.task['origin']) if self.task['subfolders'] == True else os.listdir(self.task['origin'])
        if self.task['target'] == '*':
            self.__execute(files)
        elif '*' in self.task['target']:
            _files = [_ for _ in files if self.context._get_file_name(_).endswith(self.task['target'].split('.')[1])]
            self.__execute(_files)
        else:
            shutil.copyfile(f"{self.task['origin']}/{self.task['target']}", f"{self.task['destination']}/{self.task['target']}")
        self.logger.debug("Test")

    def rollback(self) -> None:
        for file in self.affected_files:
            file_name = self.context._get_file_name(file)
            shutil.copyfile(f"{self.task['destination']}/{file_name}", f"{self.task['origin']}/{file_name}")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def __execute(self, files: 'list[str]') -> None:
        "Copy files execution action"
        for f in tqdm(files):
            ori_path = f if self.task['subfolders'] == True else f"{self.task['origin']}/{f}"
            self.affected_files.append(ori_path)
            shutil.copyfile(f"{ori_path}", f"{self.task['destination']}/{self.context._get_file_name(f)}")

class Move:

    def __init__(self) -> None:
        self.affected_files = []

    def execute(self) -> None:
        pass

    def rollback(self) -> None:
        pass

class Delete:

    def __init__(self, ctx, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag

    def execute(self) -> None:
        fp = []
        if self.task['target'] == '*':
            fp = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else os.listdir(self.task['destination'])
        elif '*' in self.task['target']:
            all_files = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else os.listdir(self.task['destination'])
            fp = [_ for _ in all_files if self.context._get_file_name(_).endswith(self.task['target'].split('.')[1])]
        elif self.task['target'].startswith('$'):
            step = self.context._get_step_reference(self.task)
            all_files = self.context._get_all_file_paths(step['destination'])
            fp = [_ for _ in all_files if self.context._get_file_name(_).endswith(step['target'].split('.')[1])]
        for _ in fp:
            os.remove(_)

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

class Zip:

    def __init__(self) -> None:
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag

    def execute(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

class Command:

    def __init__(self) -> None:
        self.affected_files = []

    def execute(self) -> None:
        pass

    def rollback(self) -> None:
        pass