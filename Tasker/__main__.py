import sys
import logging

from Tasker.types import InstructionSet
from .parser import Parser
from .cli import get_parsed_flags, check_flag_validity

__version__ = '0.0.1'

HELP_TEXT = """
Usage:
  tasker <command>
Commands:
  list                      Lists all available Tasks in the system.
  execute <task>            Executes the specified Task. Options [-NO].
  create                    Creates a new Task. Options [-NO | -Description | -Name | -File].
  edit                      Opens the specified Task file on the default text editor. Options [-NO | -File]
  help                      Show help for commands.
General Options:
  -v, -version              Show version and exit.
  -h, -help                 Show help.
  -NO                       Makes the parser not output anything to the console.
  -Name                     Task Human Readable Name flag.
  -File                     Task File Name flag.
  -Description              Description for Task template.
"""
def main() -> None: 
    args = sys.argv[1:]
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][%(asctime)s] → %(message)s',datefmt='%H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    #print(get_parsed_flags(args))
    if len(args) > 0:
        if args[0] == 'list':
            for task in Parser.list_all_tasks():
                print(f"   ➡ {task}")
        elif args[0] == 'execute' and len(args) >= 2:
            P = Parser(args[1], logger)
            P.warn_user()
            P.execute()
        elif args[0] == 'edit' and len(args) >= 2:
            f = get_parsed_flags(args)
            if not check_flag_validity(f, 'create'):
                logger.error('Flags were not constructed properly')
                sys.exit(1)
            Parser.open_file_for_edit(f['-File'])
        elif args[0] == 'create':
            f = get_parsed_flags(args)
            if not check_flag_validity(f, 'create'):
                logger.error('Flags were not constructed properly')
                sys.exit(1)
            Parser.create_new_task(f['-File'], f['-Name'], f['-Description'])
        elif args[0] == '-version' or args[0] == '-v':
            print(f"Tasker V{__version__}")
        elif args[0] == '-help' or args[0] == '-h' or args[0] == 'help':
            print(HELP_TEXT)
        else:
            logger.error('Check Help for command syntax')
    else:
        #logger.error('No Instruction Set Provided')
        print(HELP_TEXT)
    sys.exit(1)

if __name__ == '__main__':
    main()