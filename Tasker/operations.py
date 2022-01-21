import os
import shutil
from logging import Logger
from .inspector import implements
from .types import (
    Task, 
    ParserType as Parser, 
    OperationType as Operation
)
from zipfile import ZipFile, ZIP_DEFLATED

def get_file_name(p: str) -> str:
    if '/' in p:
        return p.split('/')[-1]
    return p

@implements(Operation)
class Copy:
    "Copy Action"
    
    __annotations__ = {
        "name": "Copy Action",
        "intent": "Create a duplicate of a specific file on a different location"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
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
            _files = [_ for _ in files if get_file_name(_).endswith(self.task['target'].split('.')[1])]
            self.__execute(_files)
        else:
            shutil.copyfile(f"{self.task['origin']}/{self.task['target']}", f"{self.task['destination']}/{self.task['target']}")
        #self.logger.debug("Test")

    def rollback(self) -> None:
        for file in self.affected_files:
            file_name = get_file_name(file)
            shutil.copyfile(f"{self.task['destination']}/{file_name}", f"{self.task['origin']}/{file_name}")
        self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def __execute(self, files: 'list[str]') -> None:
        "Copy files execution action"
        for f in files:
            ori_path = f if self.task['subfolders'] == True else f"{self.task['origin']}/{f}"
            self.affected_files.append(ori_path)
            shutil.copyfile(f"{ori_path}", f"{self.task['destination']}/{get_file_name(f)}")

@implements(Operation)
class Move:
    "Move Action"

    __annotations__ = {
        "name": "Move Action",
        "intent": "Move file/files from one location to another"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
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
            _files = [_ for _ in files if get_file_name(_).endswith(self.task['target'].split('.')[1])]
            self.__execute(_files)
        else:
            shutil.copyfile(f"{self.task['origin']}/{self.task['target']}", f"{self.task['destination']}/{self.task['target']}")

    def rollback(self) -> None:
        for file in self.affected_files:
            file_name = get_file_name(file)
            shutil.move(f"{self.task['destination']}/{file_name}", f"{self.task['origin']}/{file_name}")
        self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
    
    def __execute(self, files: 'list[str]') -> None:
        "Move files execution action"
        for f in files:
            ori_path = f if self.task['subfolders'] == True else f"{self.task['origin']}/{f}"
            self.affected_files.append(ori_path)
            shutil.move(f"{ori_path}", f"{self.task['destination']}/{get_file_name(f)}")

@implements(Operation)
class Delete:
    "Delete Action"

    __annotations__ = {
        "name": "Delete Action",
        "intent": "Delete file/files from the system"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
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
            fp = [_ for _ in all_files if get_file_name(_).endswith(self.task['target'].split('.')[1])]
        elif self.task['target'].startswith('$'):
            step = self.context._get_step_reference(self.task)
            all_files = self.context._get_all_file_paths(step['destination'])
            fp = [_ for _ in all_files if get_file_name(_).endswith(step['target'].split('.')[1])]
        for _ in fp:
            os.remove(_)

    def rollback(self) -> None:
        self.logger.warn("No rollback support for Delete Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

@implements(Operation)
class Zip:
    "Zip Action"

    __annotations__ = {
        "name": "Zip Action",
        "intent": "Group files into one zipped folder"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag

    def execute(self) -> None:
        fp = []
        files = []
        if self.task['target'].startswith('$'):
            step = self.context._get_step_reference(self.task)
            fp = self.context._get_all_file_paths(step['destination']) if self.task['subfolders'] == True else [f"{step['destination']}/{_}" for _ in os.listdir(step['destination'])]
            files = []#TODO: [_ for _ in os.listdir(step['destination']) if not os.path.isfile(_)  f"{step['destination']}/{_}"]
        else:
            if self.task['target'] == '*':
                fp = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else [f"{self.task['destination']}/{_}" for _ in os.listdir(self.task['destination'])]
                files = os.listdir(self.task['destination'])
        with ZipFile(f"{self.task['destination']}/{self.task['rename']}.zip", 'w', ZIP_DEFLATED) as zip:
            for i, _ in enumerate(fp):
                if "deflate" in self.task.keys():
                    if self.task['deflate'] == True:
                        zip.write(_, files[i])
                    else:
                        zip.write(_)
                else:
                    zip.write(_)
            zip.close()

    def rollback(self) -> None:
        #Step 1: Extract Zipfile
        #Step 2: Delete created Zip
        with ZipFile(f"{self.task['destination']}/{self.task['rename']}.zip", 'r', ZIP_DEFLATED) as zip:
            zip.extractall(self.task['destination'])
        os.remove(f"{self.task['destination']}/{self.task['rename']}.zip")
        self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

@implements(Operation)
class Command:
    "Command Action"

    __annotations__ = {
        "name": "Command Action",
        "intent": "Execute CLI commands"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag

    def execute(self) -> None:
        raise NotImplementedError("Command action has not been implemented yet")

    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

#Add Input Action
#Params-> Question

#Add Encrypt Action
#Params-> Algorithm, What