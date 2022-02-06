import os
import shutil
import requests
import chalk
from logging import Logger, getLogger, WARNING
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
        self._type = 'copy'
        self.handle_references()

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
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

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
        self._type = 'move'
        self.handle_references()

    def execute(self) -> None:
        files = self.context._get_all_file_paths(self.task['origin'])
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
            ori_path = f
            self.affected_files.append(ori_path)
            shutil.move(f"{ori_path}", f"{self.task['destination']}/{get_file_name(f)}")
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

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
        self._type = 'delete'
        self.handle_references()

    def execute(self) -> None:
        fp = []
        if self.task['target'] == '*':
            fp = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else os.listdir(self.task['destination'])
        elif '*' in self.task['target']:
            all_files = self.context._get_all_file_paths(self.task['destination'])
            fp = [_ for _ in all_files if get_file_name(_).lower().endswith(self.task['target'].split('.')[1])]
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
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

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
        self._type = 'zip'
        self.handle_references()

    def execute(self) -> None:
        fp = []
        files = []
        if self.task['target'] == '*':
            fp = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else [f"{self.task['destination']}/{_}" for _ in os.listdir(self.task['destination'])]
            files = os.listdir(self.task['destination'])
        elif '*' in self.task['target']:
            ending = self.task['target'].replace('*', '')
            fps = self.context._get_all_file_paths(self.task['destination']) if self.task['subfolders'] == True else [f"{self.task['destination']}/{_}" for _ in os.listdir(self.task['destination'])]
            fp = [_ for _ in fps if get_file_name(_).endswith(ending)]
            files = [_ for _ in os.listdir(self.task['destination']) if get_file_name(_).lower().endswith(ending)]

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
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

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

@implements(Operation)
class Registry:
    "Registry Action"

    __annotations__ = {
        "name": "Registry Action",
        "intent": "Change Windows Registry values/keys"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        if ctx.system != "Windows":
            ctx.abort(f"Operation not available on {ctx.system} Systems!")
        import regutils
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag
        self._type = 'registry'
        #with sub operations
        #Params-> Key, SubKey, value
        #Must have Rollback
    
    def execute(self) -> None:
        raise NotImplementedError("Registry action has not been implemented yet")
    
    def rollback(self) -> None:
        pass

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

@implements(Operation)
class Input:
    "Input Action"

    __annotations__ = {
        "name": "Input Action",
        "intent": "Ask User for Input in the console"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.value = None #where the value of the Input will be kept
        self.__internal_state = True #Faulty execution flag
        self._type = 'input'
        self.handle_references()
    
    def execute(self) -> None:
        question = input(self.task["question"])
        self.value = question

    
    def rollback(self) -> None:
        self.logger.warn("No rollback support for Input Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

@implements(Operation)
class Echo:
    "Echo Action"

    __annotations__ = {
        "name": "Echo Action",
        "intent": "Print a value to the console"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag
        self._type = 'echo'
        self.handle_references()
    
    def execute(self) -> None:
        value = self.task['value']
        self.logger.debug(f"Output of \"{self.task['name']}\" Task ➡ {chalk.yellow(value)}")

    
    def rollback(self) -> None:
        self.logger.warn("No rollback support for Echo Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

@implements(Operation)
class Request:
    "Request Action"

    __annotations__ = {
        "name": "Request Action",
        "intent": "Make API Calls and store JSON value"
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        getLogger('requests').setLevel(WARNING)
        getLogger('urllib3').setLevel(WARNING)
        self.context = ctx #Parser Context
        self.task = task #Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True #Faulty execution flag
        self._type = 'request'
        self.handle_references()
        self.response = None
    
    def execute(self) -> None:
        verb = self.task['method']
        res = None
        if verb == 'get':
            res = requests.get(self.task['endpoint']).json()
        elif verb == 'post':
            res = requests.post(
                self.task['endpoint'], 
                json=self.task['body'] if 'body' in self.task.keys() else None,
                headers=self.task['headers'] if 'headers' in self.task.keys() else None
            ).json()
        elif verb == 'delete':
            res = requests.delete(
                self.task['endpoint'], 
                json=self.task['body'] if 'body' in self.task.keys() else None,
                headers=self.task['headers'] if 'headers' in self.task.keys() else None
            ).json()
        elif verb == 'put':
            res = requests.put(
                self.task['endpoint'], 
                json=self.task['body'] if 'body' in self.task.keys() else None,
                headers=self.task['headers'] if 'headers' in self.task.keys() else None
            ).json()
        else:
            self.set_state(False)
        self.response = res if res != None else {}
    
    def rollback(self) -> None:
        self.logger.warn("No rollback support for Echo Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state
    
    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
    
    def handle_references(self) -> None:
        for key in self.task.keys():
            if type(self.task[key]) == str and self.task[key].startswith('$'):
                if '.' in self.task[key]:
                    _ = self.task[key].split('.')
                    step = self.context._get_step_reference(self.task, _[0])
                    self.task[key] = step[_[1]]
                else:
                    step = self.context._get_step_reference(self.task, self.task[key])
                    self.task[key] = step[key]

#Add Encrypt Action
#Params-> Algorithm, What