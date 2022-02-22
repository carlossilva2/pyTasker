import sys

import chalk

from .cli import get_args, get_logger
from .parser import Parser
from .templater import ask_file_to_run, create_template

__version__ = "0.4.0"


def main() -> None:
    logger = get_logger()
    try:
        args = get_args(sys.argv, __version__)
    except IndexError:
        logger.error("No action provided")
        sys.exit(1)

    if args.action == "list":
        print("Available InstructionSets:")
        for task in Parser.list_all_tasks():
            print(f"   {chalk.green('➡')} {task}")
    elif args.action == "execute":
        ans = (
            ask_file_to_run([*Parser.list_all_tasks(), "nevermind..."])
            if args.Instruction_Set is None
            else args.Instruction_Set
        )
        if ans != None:
            P = Parser(ans, logger)
            P.execute()
    elif args.action == "edit":
        Parser.open_file_for_edit(args.file)
    elif args.action == "create":
        Parser.create_new_task(args.f, args.n, args.d)
    elif args.action == "templater":
        create_template(logger)
    else:
        logger.error("Check Help for command syntax")

    sys.exit(0)
