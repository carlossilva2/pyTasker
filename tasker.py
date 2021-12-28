import sys
import logging
from Utils.parser import Parser

__version__ = '0.0.1'
args = sys.argv[1:]

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][%(asctime)s] → %(message)s',datefmt='%H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    print(f"Tasker V{__version__}")
    if len(args) > 0:
        P = Parser(args[0], logger)
        #P.warn_user()
        P.execute()
    else:
        logger.error('No Instruction Set Provided')