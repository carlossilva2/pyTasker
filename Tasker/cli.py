from typing import List, Union
from os import environ as env

CREATE_NO_DATA_FLAGS = ['-NO']
CREATE_WITH_DATA_FLAGS = ['-Name', '-Description', '-File']
EDIT_NO_DATA_FLAGS = ['-NO']
EDIT_WITH_DATA_FLAGS = ['-File']
EXECUTE_NO_DATA_FLAGS = ['-NO']
EXECUTE_WITH_DATA_FLAGS = []
GENERAL_FLAG = ['-No-Warning', '-No-Rollback']

def get_flags(args: List[str]) -> List[str]:
    return [_ for _ in args if _.startswith('-')]

def get_parsed_flags(args: List[str]) -> dict[str, Union[str, None]]:
    flags = {}
    argFlags = [_ for _ in args if _.startswith('-')]
    for _ in argFlags:
        if '=' in _:
            f = _.split('=')
            flags[f[0]] = f[1]
        else:
            flags[_] = None
        #Check Flags for global settings
        if _ in GENERAL_FLAG:
            if _ == '-No-Warning':
                env['-No-Warning'] = '1'
            if _ == '-No-Rollback':
                env['-No-Rollback'] = '1'
    return flags

def check_flag_validity(f: dict[str, Union[str, None]], op: str) -> bool:
    """
    Analyses the flag list sent for errors or missing parameters.
    Params:
        `f`: Parsed Flag List;
        `op`: Current Operation being executed;
    """
    operation_wd: List[str] = eval(f"{op.upper()}_WITH_DATA_FLAGS")
    operation_nd: List[str] = eval(f"{op.upper()}_NO_DATA_FLAGS")
    for _ in f.keys():
        if _ in operation_wd and f[_] == None:
            return False
        if _ in operation_nd and f[_] != None:
            f[_] = None
    return True