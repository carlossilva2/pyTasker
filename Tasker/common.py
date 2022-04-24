import os.path as Path
from hashlib import md5
from os import listdir
from time import time

from .types import Alias, OperationType, Settings


def ref(self: OperationType) -> None:
    for key in self.task.keys():
        if type(self.task[key]) == str and self.task[key].startswith("$"):
            if "." in self.task[key]:
                _ = self.task[key].split(".")
                step = self.context._get_step_reference(self.task, _[0])
                self.task[key] = step[_[1]]
            else:
                step = self.context._get_step_reference(self.task, self.task[key])
                self.task[key] = step[key]


def alias(self: OperationType, settings: Settings) -> None:
    for key in self.task.keys():
        if type(self.task[key]) == str and self.task[key].startswith("&"):
            p = self.task[key].split("/")
            trigger = p[0].replace("&", "")
            p = p[1:] if len(p) > 1 else []
            alias: Alias = next(
                (p for p in settings["alias"] if p["name"] == trigger),
                Alias(name="home", path=Path.expanduser("~")),
            )
            self.task[key] = "/".join(
                [
                    alias["path"],
                    *p,
                ]
            )


def get_file_name(p: str) -> str:
    if "/" in p:
        return p.split("/")[-1]
    return p


def md5_hash(string: str) -> str:
    return f"{string}_{md5(f'{time()}'.encode('UTF-8')).hexdigest()[:6]}"


def check_duplicate_names(file: str) -> str:
    if f"{file}.tasker.json" in listdir(f"{Path.expanduser('~')}/.tasker/Tasks"):
        return md5_hash(file)
    return file


class Timer:
    def __init__(self) -> None:
        self.start_time = 0.0
        self.end_time = 0.0
        self.ellapsed_time = ""

    def start(self) -> None:
        if self.start_time == 0.0:
            self.start_time = time()

    def stop(self) -> None:
        if self.end_time == 0.0:
            self.end_time = time()
            self.ellapsed_time = f"{round(self.end_time-self.start_time, 4)}s"

    def reset(self) -> None:
        self.start_time = 0.0
        self.end_time = 0.0
        self.ellapsed_time = ""
