import json
import os.path as Path
from logging import Logger
from typing import List, Union

import questionary as qt
from validators import ValidationFailure, url

from .types import Copy, InstructionSet, Request


def ask_file_to_run(options: List[str]) -> Union[str, None]:
    option = qt.select(
        "Which InstructionSet do you want to execute?", choices=options, qmark="📁"
    ).ask()
    return option if option != "Nevermind..." else None


def create_template(logger: Logger) -> None:
    copy_a = "Copy Action"
    zip_a = "Zip Action"
    delete_a = "Delete Action"
    move_a = "Move Action"
    input_a = "Input Action"
    echo_a = "Echo Action"
    request_a = "Request Action"
    instruction_set: InstructionSet = {"name": "", "description": "", "tasks": []}
    no_break = True
    available_actions = [
        copy_a,
        delete_a,
        echo_a,
        input_a,
        move_a,
        request_a,
        zip_a,
        "Nothing else",
    ]
    file_name: str = (
        qt.text("What name should the file have?", qmark="📘")
        .ask()
        .lower()
        .replace(" ", "_")
    )
    instruction_set["name"] = qt.text(
        "What's the name of the InstructionSet?", qmark="📘"
    ).ask()
    want_description = qt.confirm("Do you want to add a description?", qmark="📕").ask()
    if want_description:
        instruction_set["description"] = qt.text(
            "How can you describe what your InstructionSet does?",
            qmark="📘",
            multiline=True,
        ).ask()
    while no_break:
        option = qt.select(
            "What Task do you want do add?",
            choices=available_actions,
            qmark="📘",
        ).ask()
        if option == "Nothing else":
            no_break = False
        elif option == copy_a:
            instruction_set["tasks"].append(
                create_copy_task(len(instruction_set["tasks"]), logger)
            )
        elif option == request_a:
            instruction_set["tasks"].append(
                create_request_task(len(instruction_set["tasks"]), logger)
            )
    save = qt.confirm("Do you want save?", qmark="📕", default=False).ask()
    print(instruction_set)
    if save:
        json.dump(
            instruction_set,
            open(f"{Path.expanduser('~')}/.tasker/Tasks/{file_name}.tasker.json", "w"),
            indent=4,
        )


def create_copy_task(step: int, logger: Logger) -> Copy:
    ans: Copy = {
        "name": "",
        "step": step,
        "operation": "copy",
        "target": "",
        "origin": "",
        "destination": "",
        "subfolders": False,
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark="©").ask()
    ans["target"] = qt.text("What's the Target?", qmark="©").ask()
    ans["origin"] = qt.path("Where should it Copy from?", qmark="©").ask()
    ans["destination"] = qt.path("Where should it Copy to?", qmark="©").ask()
    ans["destination"] = qt.confirm(
        "Should it search inside subfolders?", qmark="©"
    ).ask()
    return ans


def create_request_task(step: int, logger: Logger) -> Request:
    ans: Request = {
        "name": "",
        "step": step,
        "operation": "request",
        "endpoint": "",
        "method": "get",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark="®").ask()
    ans["method"] = qt.select(
        "Select a type of request:",
        choices=["get", "post", "delete", "put"],
        qmark="®",
    ).ask()
    try:
        u = qt.text("What's the endpoint URL?", qmark="®").ask()
        if isinstance(url(u), ValidationFailure):
            raise ValidationFailure(url, {"value": u, "public": False})
        ans["endpoint"] = u
    except ValidationFailure:
        ans["endpoint"] = "https://jsonplaceholder.typicode.com/posts"
        logger.error(
            "Endpoint provided was not a valid URL. Using default URL, please modify file after completion."
        )
    body = qt.confirm("Do you want to send anything in the body?", qmark="®").ask()
    if body:
        try:
            ans["body"] = json.loads(
                qt.text(
                    "What do you want to send (only accepts JSON strings)?", qmark="®"
                ).ask()
            )
        except Exception:
            logger.error("Value sent is not a valid JSON string")
    headers = qt.confirm("Do you want to send anything in the headers?", qmark="®").ask()
    if headers:
        try:
            ans["headers"] = json.loads(
                qt.text(
                    "What do you want to send (only accepts JSON strings)?", qmark="®"
                ).ask()
            )
        except Exception:
            logger.error("Value sent is not a valid JSON string")
    return ans
