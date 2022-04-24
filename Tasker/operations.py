import os
import shutil
from logging import WARNING, Logger, getLogger
from zipfile import ZIP_DEFLATED, ZipFile

import chalk
import requests

from Tasker.regutils import backup

from .common import alias, get_file_name, ref
from .inspector import implements
from .types import OperationType as Operation
from .types import ParserType as Parser
from .types import Registry as RegType
from .types import Task

try:
    from .regutils import (
        create_key,
        get_key_value,
        get_type,
        parse_input,
        set_key_value,
    )
except Exception:
    not_imported = True


@implements(Operation)
class Copy(Operation):
    "Copy Action"

    __annotations__ = {
        "name": "Copy Action",
        "intent": "Create a duplicate of a specific file on a different location",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "copy"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        files = (
            self.context._get_all_file_paths(self.task["origin"])
            if self.task["subfolders"] is True
            else os.listdir(self.task["origin"])
        )
        if self.task["target"] == "*":
            self.__execute(files)
        elif "*" in self.task["target"]:
            _files = [
                _
                for _ in files
                if get_file_name(_).endswith(self.task["target"].split(".")[1])
            ]
            self.__execute(_files)
        else:
            shutil.copyfile(
                f"{self.task['origin']}/{self.task['target']}",
                f"{self.task['destination']}/{self.task['target']}",
            )

    def rollback(self) -> None:
        for file in self.affected_files:
            file_name = get_file_name(file)
            shutil.copyfile(
                f"{self.task['destination']}/{file_name}",
                f"{self.task['origin']}/{file_name}",
            )
        self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def __execute(self, files: "list[str]") -> None:
        "Copy files execution action"
        for f in files:
            ori_path = (
                f if self.task["subfolders"] is True else f"{self.task['origin']}/{f}"
            )
            self.affected_files.append(ori_path)
            shutil.copyfile(
                f"{ori_path}", f"{self.task['destination']}/{get_file_name(f)}"
            )


@implements(Operation)
class Move(Operation):
    "Move Action"

    __annotations__ = {
        "name": "Move Action",
        "intent": "Move file/files from one location to another",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "move"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        files = self.context._get_all_file_paths(self.task["origin"])
        if self.task["target"] == "*":
            self.__execute(files)
        elif "*" in self.task["target"]:
            _files = [
                _
                for _ in files
                if get_file_name(_).endswith(self.task["target"].split(".")[1])
            ]
            self.__execute(_files)
        else:
            shutil.copyfile(
                f"{self.task['origin']}/{self.task['target']}",
                f"{self.task['destination']}/{self.task['target']}",
            )

    def rollback(self) -> None:
        for file in self.affected_files:
            file_name = get_file_name(file)
            shutil.move(
                f"{self.task['destination']}/{file_name}",
                f"{self.task['origin']}/{file_name}",
            )
        self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state

    def __execute(self, files: "list[str]") -> None:
        "Move files execution action"
        for f in files:
            ori_path = f
            self.affected_files.append(ori_path)
            shutil.move(f"{ori_path}", f"{self.task['destination']}/{get_file_name(f)}")


@implements(Operation)
class Delete(Operation):
    "Delete Action"

    __annotations__ = {
        "name": "Delete Action",
        "intent": "Delete file/files from the system",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "delete"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        fp = []
        if self.task["target"] == "*":
            fp = (
                self.context._get_all_file_paths(self.task["destination"])
                if self.task["subfolders"] is True
                else os.listdir(self.task["destination"])
            )
        elif "*" in self.task["target"]:
            all_files = self.context._get_all_file_paths(self.task["destination"])
            fp = [
                _
                for _ in all_files
                if get_file_name(_).lower().endswith(self.task["target"].split(".")[1])
            ]
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
class Zip(Operation):
    "Zip Action"

    __annotations__ = {
        "name": "Zip Action",
        "intent": "Group files into one zipped folder",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "zip"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        fp = []
        files = []
        if self.task["target"] == "*":
            fp = (
                self.context._get_all_file_paths(self.task["destination"])
                if self.task["subfolders"] is True
                else [
                    f"{self.task['destination']}/{_}"
                    for _ in os.listdir(self.task["destination"])
                ]
            )
            files = os.listdir(self.task["destination"])
        elif "*" in self.task["target"]:
            ending = self.task["target"].replace("*", "")
            fps = (
                self.context._get_all_file_paths(self.task["destination"])
                if self.task["subfolders"] is True
                else [
                    f"{self.task['destination']}/{_}"
                    for _ in os.listdir(self.task["destination"])
                ]
            )
            fp = [_ for _ in fps if get_file_name(_).endswith(ending)]
            files = [
                _
                for _ in os.listdir(self.task["destination"])
                if get_file_name(_).lower().endswith(ending)
            ]

        with ZipFile(
            f"{self.task['destination']}/{self.task['rename']}.zip", "w", ZIP_DEFLATED
        ) as zip:
            for i, _ in enumerate(fp):
                if "deflate" in self.task.keys():
                    if self.task["deflate"] is True:
                        zip.write(_, files[i])
                    else:
                        zip.write(_)
                else:
                    zip.write(_)
            zip.close()

    def rollback(self) -> None:
        # Step 1: Extract Zipfile
        # Step 2: Delete created Zip
        with ZipFile(
            f"{self.task['destination']}/{self.task['rename']}.zip", "r", ZIP_DEFLATED
        ) as zip:
            zip.extractall(self.task["destination"])
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

    __annotations__ = {"name": "Command Action", "intent": "Execute CLI commands"}

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag

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
class Registry(Operation):
    "Registry Action"

    __annotations__ = {
        "name": "Registry Action",
        "intent": "Change Windows Registry values/keys",
    }

    def __init__(self, ctx: Parser, task: RegType, logger: Logger) -> None:
        if ctx.system != "Windows":
            ctx.abort(f"Operation not available on {ctx.system} Systems!")
        self.regex = r"\w>"
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "registry"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        self.path = ">".join([self.task["start_key"], self.task["key"]])
        if self.task["function"] == "get":
            self.value = get_key_value(self.path, self.logger)
        elif self.task["function"] == "set":
            if self.task["value"] == "" or self.task["value"] == None:
                self.context.abort("No value was provided")
            self.safeguard = get_key_value(self.path, self.logger)
            parsed = parse_input(self.path)
            values = parsed[1]
            self.v = values[-1]
            values.pop()
            self.correct_path = ">".join([self.task["start_key"], *values])
            set_key_value(
                self.correct_path, self.v, get_type(self.task["type"]), self.task["value"]
            )
            self.value = get_key_value(self.path, self.logger)
        elif self.task["function"] == "create":
            create_key(self.path, self.task["value"])
        elif self.task["function"] == "backup":
            raise NotImplementedError(
                "Feature under development. Refer to future versions"
            )
            backup(self.task["start_key"], self.task["key"], self.task["rename"])

    def rollback(self) -> None:
        if self.task["function"] == "set":
            set_key_value(
                self.correct_path, self.v, get_type(self.task["type"]), self.safeguard
            )
            self.logger.warn(f"Rolled back \"{self.task['name']}\" task")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state


@implements(Operation)
class Input(Operation):
    "Input Action"

    __annotations__ = {
        "name": "Input Action",
        "intent": "Ask User for Input in the console",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.value = None  # where the value of the Input will be kept
        self.__internal_state = True  # Faulty execution flag
        self._type = "input"
        ref(self)
        alias(self, self.context.settings)

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


@implements(Operation)
class Echo(Operation):
    "Echo Action"

    __annotations__ = {"name": "Echo Action", "intent": "Print a value to the console"}

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "echo"
        ref(self)
        alias(self, self.context.settings)

    def execute(self) -> None:
        value = self.task["value"]
        self.logger.debug(
            f"Output of \"{self.task['name']}\" Task ➡ {chalk.yellow(value)}"
        )

    def rollback(self) -> None:
        self.logger.warn("No rollback support for Echo Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state


@implements(Operation)
class Request(Operation):
    "Request Action"

    __annotations__ = {
        "name": "Request Action",
        "intent": "Make API Calls and store JSON value",
    }

    def __init__(self, ctx: Parser, task: Task, logger: Logger) -> None:
        getLogger("requests").setLevel(WARNING)
        getLogger("urllib3").setLevel(WARNING)
        self.context = ctx  # Parser Context
        self.task = task  # Current assigned Task
        self.logger = logger
        self.affected_files: list[str] = []
        self.__internal_state = True  # Faulty execution flag
        self._type = "request"
        ref(self)
        alias(self, self.context.settings)
        self.response = None

    def execute(self) -> None:
        verb = self.task["method"]
        res = None
        if verb == "get":
            res = requests.get(
                self.task["endpoint"],
                json=self.task["body"] if "body" in self.task.keys() else None,
                headers=self.task["headers"] if "headers" in self.task.keys() else None,
            ).json()
        elif verb == "post":
            res = requests.post(
                self.task["endpoint"],
                json=self.task["body"] if "body" in self.task.keys() else None,
                headers=self.task["headers"] if "headers" in self.task.keys() else None,
            ).json()
        elif verb == "delete":
            res = requests.delete(
                self.task["endpoint"],
                json=self.task["body"] if "body" in self.task.keys() else None,
                headers=self.task["headers"] if "headers" in self.task.keys() else None,
            ).json()
        elif verb == "put":
            res = requests.put(
                self.task["endpoint"],
                json=self.task["body"] if "body" in self.task.keys() else None,
                headers=self.task["headers"] if "headers" in self.task.keys() else None,
            ).json()
        else:
            self.set_state(False)
        self.response = res if res is not None else {}

    def rollback(self) -> None:
        self.logger.warn("No rollback support for Echo Action")

    def set_state(self, state: bool) -> None:
        "Sets the state for the Internal Fault flag"
        self.__internal_state = state

    def get_state(self) -> bool:
        "Returns the of the Internal Fault flag"
        return self.__internal_state
