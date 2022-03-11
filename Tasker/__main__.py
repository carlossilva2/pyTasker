import sys

import chalk

from .cli import flag_present, get_args, get_logger
from .parser import Parser
from .templater import ask_file_to_run, create_template, check_duplicate_names

__version__ = "0.4.3"


def main() -> None:
    logger = get_logger()
    try:
        args = get_args(__version__, logger)
    except IndexError:
        logger.error("No action provided")
        sys.exit(1)

    if args.action == "list":
        print("Available InstructionSets:")
        for task in Parser.list_all_tasks():
            print(f"   {chalk.green('➡')} {task}")
    elif args.action == "execute":
        ans = (
            ask_file_to_run([*Parser.list_all_tasks(), "nevermind..."], "execute")
            if args.Instruction_Set is None
            else args.Instruction_Set
        )
        if ans != None:
            P = Parser(ans, logger)
            P.execute()
    elif args.action == "edit":
        ans = (
            ask_file_to_run([*Parser.list_all_tasks(), "nevermind..."], "edit")
            if args.Instruction_Set is None
            else args.Instruction_Set
        )
        if ans != None:
            Parser.open_file_for_edit(ans)
    elif args.action == "create":
        if flag_present(["File", "Description", "Name"], args):
            Parser.create_new_task(check_duplicate_names(args.File), args.Name, args.Description)
        else:
            create_template(logger)
    else:
        logger.error("Check Help for command syntax")

    sys.exit(0)
