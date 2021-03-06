import json
import os.path as Path
from hashlib import md5
from logging import Logger
from time import time
from typing import List, Literal, Union

import questionary as qt
from validators import ValidationFailure, url

from .common import check_duplicate_names
from .types import *

REFERENCES = []


def ask_file_to_run(
    options: List[str], operation: Literal["execute", "edit"]
) -> Union[str, None]:
    option = qt.select(
        f"Which InstructionSet do you want to {operation}?", choices=options, qmark="📁"
    ).ask()
    return option if option != "nevermind..." else None


def _create_text_or_autocomplete(
    message: str, mark: str, choices: List[str]
) -> qt.Question:
    "Create a Text Question with/without Autocomplete based on the `choices`"
    if len(choices) == 0:
        return qt.text(message, qmark=mark)
    return qt.autocomplete(message, choices=choices, qmark=mark)


def _create_path_or_autocomplete(
    message: str, mark: str, choices: List[str]
) -> qt.Question:
    "Create a Path Question with/without Autocomplete based on the `choices`"
    if len(choices) == 0:
        return qt.text(message, qmark=mark)
    return qt.path(message, qmark=mark, only_directories=True)


def create_template(logger: Logger) -> InstructionSet:
    settings: Settings = json.load(
        open(f"{Path.expanduser('~')}/.tasker/config.json", "r")
    )
    command_a = "Command Action"
    copy_a = "Copy Action"
    custom_a = "Custom Action"
    zip_a = "Zip Action"
    delete_a = "Delete Action"
    move_a = "Move Action"
    input_a = "Input Action"
    echo_a = "Echo Action"
    request_a = "Request Action"
    registry_a = "Registry Action"
    hold_a = "Hold Action"
    sleep_a = "Sleep Action"
    instruction_set: InstructionSet = InstructionSet(name="", description="", tasks=[])
    no_break = True
    available_actions = [
        copy_a,
        command_a,
        delete_a,
        echo_a,
        input_a,
        move_a,
        request_a,
        zip_a,
        custom_a,
        "Nothing else",
    ]
    installed = [_["name"] for _ in settings["extensions"]]
    if "Registry" in installed:
        available_actions.insert(0, registry_a)
    if "Sleep" in installed:
        available_actions.insert(0, sleep_a)
    if "Hold" in installed:
        available_actions.insert(0, hold_a)
    file_name: str = check_duplicate_names(
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
        elif option == command_a:
            instruction_set["tasks"].append(
                create_command_task(len(instruction_set["tasks"]), logger)
            )
        elif option == zip_a:
            instruction_set["tasks"].append(
                create_zip_task(len(instruction_set["tasks"]), logger)
            )
        elif option == delete_a:
            instruction_set["tasks"].append(
                create_delete_task(len(instruction_set["tasks"]), logger)
            )
        elif option == move_a:
            instruction_set["tasks"].append(
                create_move_task(len(instruction_set["tasks"]), logger)
            )
        elif option == input_a:
            instruction_set["tasks"].append(
                create_input_task(len(instruction_set["tasks"]), logger)
            )
        elif option == echo_a:
            instruction_set["tasks"].append(
                create_echo_task(len(instruction_set["tasks"]), logger)
            )
        elif option == request_a:
            instruction_set["tasks"].append(
                create_request_task(len(instruction_set["tasks"]), logger)
            )
        elif option == registry_a:
            instruction_set["tasks"].append(
                create_registry_task(len(instruction_set["tasks"]), logger)
            )
        elif option == hold_a:
            instruction_set["tasks"].append(
                create_hold_task(len(instruction_set["tasks"]), logger)
            )
        elif option == sleep_a:
            instruction_set["tasks"].append(
                create_sleep_task(len(instruction_set["tasks"]), logger)
            )
        elif option == custom_a:
            instruction_set["tasks"].append(
                create_custom_task(len(instruction_set["tasks"]), logger)
            )
    save = qt.confirm("Do you want save?", qmark="📕", default=False).ask()
    if save:
        json.dump(
            instruction_set,
            open(f"{Path.expanduser('~')}/.tasker/Tasks/{file_name}.tasker.json", "w"),
            indent=4,
        )
    return instruction_set


def create_copy_task(step: int, logger: Logger) -> Copy:
    mark = "©️"
    ans: Copy = {
        "name": "",
        "step": step,
        "operation": "copy",
        "target": "",
        "origin": "",
        "destination": "",
        "subfolders": False,
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["target"] = _create_text_or_autocomplete(
        "What's the Target?", mark, REFERENCES
    ).ask()
    ans["origin"] = _create_path_or_autocomplete(
        "Where should it Copy from?", mark, REFERENCES
    ).ask()
    ans["destination"] = _create_path_or_autocomplete(
        "Where should it Copy to?", mark, REFERENCES
    ).ask()
    ans["subfolders"] = qt.confirm(
        "Should it search inside subfolders?", qmark=mark
    ).ask()
    REFERENCES.append(f"${step}.target")
    REFERENCES.append(f"${step}.origin")
    REFERENCES.append(f"${step}.destination")
    return ans


def create_move_task(step: int, logger: Logger) -> Move:
    mark = "🔀"
    ans: Move = {
        "name": "",
        "step": step,
        "operation": "move",
        "target": "",
        "origin": "",
        "destination": "",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["target"] = _create_text_or_autocomplete(
        "What's the Target?", mark, REFERENCES
    ).ask()
    ans["origin"] = _create_path_or_autocomplete(
        "Where should it Move from?", mark, REFERENCES
    ).ask()
    ans["destination"] = _create_path_or_autocomplete(
        "Where should it Move to?", mark, REFERENCES
    ).ask()
    REFERENCES.append(f"${step}.target")
    REFERENCES.append(f"${step}.origin")
    REFERENCES.append(f"${step}.destination")
    return ans


def create_zip_task(step: int, logger: Logger) -> Zip:
    mark = "📁"
    ans: Zip = {
        "name": "",
        "step": step,
        "operation": "zip",
        "target": "",
        "rename": "",
        "subfolders": False,
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["target"] = _create_text_or_autocomplete(
        "What's the Target?", mark, REFERENCES
    ).ask()
    q = _create_text_or_autocomplete(
        "What name should the Zip have?",
        mark,
        REFERENCES,
    )
    q.default = md5(f"{time()}{ans['step']}{ans['name']}".encode("UTF-8")).hexdigest()
    ans["rename"] = q.ask()
    destination = qt.confirm("Do you want to add a destination?", qmark=mark).ask()
    if destination:
        ans["destination"] = _create_path_or_autocomplete(
            "Where should it Copy to?", mark, REFERENCES
        ).ask()
    ans["deflate"] = qt.confirm(
        "Do you want the Zip deflated?", qmark=mark, default=False
    ).ask()
    ans["subfolders"] = qt.confirm(
        "Should it search inside subfolders?", qmark=mark
    ).ask()
    REFERENCES.append(f"${step}.target")
    REFERENCES.append(f"${step}.rename")
    return ans


def create_delete_task(step: int, logger: Logger) -> Delete:
    mark = "❌"
    ans: Delete = {
        "name": "",
        "step": step,
        "operation": "delete",
        "destination": "",
        "target": "",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["target"] = _create_text_or_autocomplete(
        "What's the Target?", mark, REFERENCES
    ).ask()
    ans["destination"] = _create_path_or_autocomplete(
        "Where should it Delete?", mark, REFERENCES
    ).ask()
    REFERENCES.append(f"${step}.target")
    REFERENCES.append(f"${step}.destination")
    return ans


def create_input_task(step: int, logger: Logger) -> Input:
    mark = "🔠"
    ans: Input = {"name": "", "step": step, "operation": "input", "question": ""}
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["question"] = _create_text_or_autocomplete(
        "What's the question you want to ask?", mark, REFERENCES
    ).ask()
    REFERENCES.append(f"${step}.question")
    REFERENCES.append(f"${step}.value")
    return ans


def create_echo_task(step: int, logger: Logger) -> Echo:
    mark = "📢"
    ans: Echo = {"name": "", "step": step, "operation": "echo", "value": ""}
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["value"] = _create_text_or_autocomplete(
        "What do you want to output?", mark, REFERENCES
    ).ask()
    REFERENCES.append(f"${step}.value")
    return ans


def create_request_task(step: int, logger: Logger) -> Request:
    mark = "®️"
    ans: Request = {
        "name": "",
        "step": step,
        "operation": "request",
        "endpoint": "",
        "method": "get",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["method"] = qt.select(
        "Select a type of request:",
        choices=["get", "post", "delete", "put"],
        qmark=mark,
    ).ask()
    try:
        u = _create_text_or_autocomplete(
            "What's the endpoint URL?", mark, REFERENCES
        ).ask()
        if isinstance(url(u), ValidationFailure):
            raise ValidationFailure(url, {"value": u, "public": False})
        ans["endpoint"] = u
    except ValidationFailure:
        ans["endpoint"] = "https://jsonplaceholder.typicode.com/posts"
        logger.error(
            "Endpoint provided was not a valid URL. Using default URL, please modify file after completion."
        )
    body = qt.confirm("Do you want to send anything in the body?", qmark=mark).ask()
    if body:
        try:
            ans["body"] = json.loads(
                _create_text_or_autocomplete(
                    "What do you want to send (only accepts JSON strings)?",
                    mark,
                    REFERENCES,
                ).ask()
            )
        except Exception:
            logger.error("Value sent is not a valid JSON string")
    headers = qt.confirm("Do you want to send anything in the headers?", qmark=mark).ask()
    if headers:
        try:
            ans["headers"] = json.loads(
                _create_text_or_autocomplete(
                    "What do you want to send (only accepts JSON strings)?",
                    mark,
                    REFERENCES,
                ).ask()
            )
        except Exception:
            logger.error("Value sent is not a valid JSON string")
    REFERENCES.append(f"${step}.endpoint")
    REFERENCES.append(f"${step}.method")
    REFERENCES.append(f"${step}.body")
    REFERENCES.append(f"${step}.headers")
    return ans


def create_registry_task(step: int, logger: Logger):
    mark = "🗄️"
    ans = {
        "name": "",
        "step": step,
        "operation": "custom",
        "extension_name": "Registry",
        "function": "get",
        "key": "",
        "start_key": "local-machine",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["function"] = qt.select(
        "Select a type of operation:",
        choices=["get", "set", "create", "backup"],
        qmark=mark,
    ).ask()
    ans["start_key"] = qt.select(
        "Select the root of the Registry:",
        choices=[
            "classes-root",
            "current-user",
            "current-config",
            "local-machine",
            "users",
        ],
        qmark=mark,
    ).ask()
    ans["key"] = qt.text(
        "What's the Key you're trying to access/edit/create?", qmark=mark
    ).ask()
    if ans["function"] in ["set", "create"]:
        change = qt.confirm("Are you changing any value in a Key?", qmark=mark).ask()
        if change:
            ans["type"] = qt.select(
                "Select a Key type:",
                choices=["sz", "multisz", "none", "binary", "dword", "qword"],
                qmark=mark,
            ).ask()
            ans["value"] = _create_text_or_autocomplete(
                "What's the Key value you want to change to?",
                mark,
                REFERENCES,
            ).ask()
        elif qt.confirm("Are you creating a Key?", qmark=mark).ask():
            ans["value"] = _create_text_or_autocomplete(
                "What's the Key value you want to create?",
                mark,
                REFERENCES,
            ).ask()
    elif ans["function"] == "backup":
        ans["key"] = _create_path_or_autocomplete(
            "Where to you want to store the backup file?", mark, REFERENCES
        ).ask()
        ans["rename"] = _create_text_or_autocomplete(
            "What's the name you want to give the file?",
            mark,
            REFERENCES,
        ).ask()
        REFERENCES.append(f"${step}.rename")
    REFERENCES.append(f"${step}.function")
    REFERENCES.append(f"${step}.start_key")
    REFERENCES.append(f"${step}.key")
    REFERENCES.append(f"${step}.type")
    REFERENCES.append(f"${step}.value")
    return ans


def create_hold_task(step: int, logger: Logger):
    mark = "🛑"
    ans = {
        "name": "",
        "step": step,
        "operation": "custom",
        "extension_name": "Hold",
        "type": "",
        "condition": "",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["type"] = qt.select(
        "Select a type of operation:",
        choices=["time", "date", "datetime"],
        qmark=mark,
    ).ask()
    ans["condition"] = qt.text("What's the Hold Condition?", qmark=mark).ask()
    REFERENCES.append(f"${step}.type")
    REFERENCES.append(f"${step}.condition")
    return ans


def create_sleep_task(step: int, logger: Logger):
    mark = "💤"
    ans = {
        "name": "",
        "step": step,
        "operation": "custom",
        "extension_name": "Sleep",
        "amount": "",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["condition"] = int(qt.text("How long should it sleep?", qmark=mark).ask())
    REFERENCES.append(f"${step}.amount")
    return ans


def create_custom_task(step: int, logger: Logger) -> Custom:
    mark = "🛠️"
    ans: Custom = {"name": "", "step": step, "operation": "custom", "extension_name": ""}
    settings: Settings = json.load(
        open(f"{Path.expanduser('~')}/.tasker/config.json", "r")
    )
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["extension_name"] = qt.select(
        "Select an extension:",
        choices=[e["name"] for e in settings["extensions"]],
        qmark=mark,
    ).ask()
    exec_additional = True
    t = 0
    while exec_additional:
        sec = qt.confirm(
            f"Do you want to add {'a' if t == 0 else 'another'} parameter?",
            qmark=mark,
            default=False,
        ).ask()
        if not sec:
            exec_additional = False
        else:
            name = _create_text_or_autocomplete(
                "What's the name of the parameter?", mark, REFERENCES
            ).ask()
            ans[name] = _create_text_or_autocomplete(
                f"What's the value of {name}?", mark, REFERENCES
            ).ask()
            t += 1
    return ans


def create_command_task(step: int, logger: Logger) -> Custom:
    mark = "🖥️"
    ans: Command = {
        "name": "",
        "step": step,
        "operation": "command",
        "output": False,
        "command": "",
    }
    ans["name"] = qt.text("What's the name of the Task?", qmark=mark).ask()
    ans["output"] = qt.confirm(
        "Do you want to save the output of command?",
        qmark=mark,
        default=False,
    ).ask()
    ans["command"] = _create_text_or_autocomplete(
        "What command do you want to execute?", mark, REFERENCES
    ).ask()

    REFERENCES.append(f"${step}.output")
    REFERENCES.append(f"${step}.command")
    return ans
