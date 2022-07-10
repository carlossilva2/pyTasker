import os.path as Path
import subprocess
import sys
from hashlib import md5
from os import listdir
from time import time

from .types import Alias, OperationType

FORBIDDEN_REF_ALIAS = ["name", "step", "operation"]


def ref(self: OperationType) -> None:
    for key in [_ for _ in self.task.keys() if _ not in FORBIDDEN_REF_ALIAS]:
        if type(self.task[key]) == str and self.task[key].startswith("$"):
            if "." in self.task[key]:
                _ = self.task[key].split(".")
                step = self.context._get_step_reference(self.task, _[0])
                self.task[key] = step[_[1]]
            else:
                step = self.context._get_step_reference(self.task, self.task[key])
                self.task[key] = step[key]


def alias(self: OperationType) -> None:
    for key in [_ for _ in self.task.keys() if _ not in FORBIDDEN_REF_ALIAS]:
        if type(self.task[key]) == str and self.task[key].startswith("&"):
            p = self.task[key].split("/")
            trigger = p[0].replace("&", "")
            p = p[1:] if len(p) > 1 else []
            alias: Alias = next(
                (p for p in self.context.settings["alias"] if p["name"] == trigger),
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


def pip(package: str):
    return subprocess.check_call([sys.executable, "-m", "pip", "install", package])


def pip_freeze() -> list[str]:
    return [
        _.decode().split("==")[0]
        for _ in subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).split()
    ]
