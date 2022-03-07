import argparse
import logging
from os import environ as env
from typing import List, Union

import chalk


def get_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.DEBUG,
        format=f'[{chalk.blue("%(levelname)s")}] → %(message)s',
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger


def get_args(version: str) -> argparse.Namespace:
    "Create Argument parser for CLI use and return all the parsed args"
    parser = argparse.ArgumentParser(
        prog="pyTasker",
        description="Run pipelines on your own computer for better automation",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s v{version}"
    )

    parser.add_argument(
        "action",
        help="What action should Tasker perform",
        choices=["list", "execute", "create", "edit", "templater"],
    )

    options = parser.add_argument_group("parameters")
    options.add_argument(
        "-i",
        "--Instruction-Set",
        type=str,
        metavar="",
        required=False,
        help=f"Instruction Set name flag. Use {chalk.green('`tasker list`')} for a list",
    )
    options.add_argument(
        "-f",
        "--File",
        type=str,
        metavar="",
        required=False,
        help="Task File Name flag.",
    )
    options.add_argument(
        "-n",
        "--Name",
        type=str,
        metavar="",
        required=False,
        help="Task Human Readable Name flag.",
    )
    options.add_argument(
        "-d",
        "--Description",
        type=str,
        metavar="",
        required=False,
        help="Description for Task template.",
    )
    options.add_argument(
        "-nw",
        "--No-Warning",
        action="store_true",
        help="Removes the verification of the Users OS.",
    )
    options.add_argument(
        "-nr",
        "--No-Rollback",
        action="store_true",
        help="Prevents Tasker to perform Rollback in case of Task failure.",
    )
    args = parser.parse_args()
    if args.No_Warning:
        env["-No-Warning"] = "1"
    if args.No_Rollback:
        env["-No-Rollback"] = "1"
    return args


def flag_present(flag: Union[str, List[str]], args: argparse.Namespace) -> bool:
    if isinstance(flag, list):
        return all([args.__dict__[_] is not None for _ in flag])
    return flag in args.__dict__
