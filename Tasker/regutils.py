"Windows Registry Utils file"
import winreg
from logging import Logger

# import os.path as Path
from os import listdir, remove
from typing import Dict, List, Literal, Tuple, Union

import win32api
import win32con
import win32security

ROOTS: Dict[str, int] = {
    "classes-root": winreg.HKEY_CLASSES_ROOT,
    "current-user": winreg.HKEY_CURRENT_USER,
    "current-config": winreg.HKEY_CURRENT_CONFIG,
    "local-machine": winreg.HKEY_LOCAL_MACHINE,
    "users": winreg.HKEY_USERS,
}

TYPES: Dict[str, int] = {
    "sz": winreg.REG_SZ,
    "multisz": winreg.REG_MULTI_SZ,
    "none": winreg.REG_NONE,
    "binary": winreg.REG_BINARY,
    "dword": winreg.REG_DWORD,
    "qword": winreg.REG_QWORD,
}

RootKeys = Literal[
    "classes-root", "current-user", "current-config", "local-machine", "users"
]
TypeList = Literal["sz", "multisz", "none", "binary", "dword", "qword"]


def parse_input(k: str) -> Tuple[int, List[str]]:
    if k == "":
        raise Exception("Cannot provide empty Registry Path")
    str_list = k.split(">")
    root: int = ROOTS[str_list[0]]
    str_list.pop(0)
    return (root, [_ for _ in str_list if _ != ""])


def get_type(key: TypeList) -> int:
    ans = TYPES.get(key)
    return ans if ans != None else TYPES["sz"]


def get_all_keys(root: RootKeys) -> List[str]:
    keys = []
    i = 0
    try:
        _ = ROOTS[root]
        while True:
            k = winreg.EnumKey(_, i)
            keys.append(k)
            i += 1
    except Exception:
        pass
    return keys


def create_key(path: str, key_name: str) -> None:
    k = parse_input(path)
    with winreg.OpenKey(
        k[0], r"\\".join(k[1]), reserved=0, access=winreg.KEY_CREATE_SUB_KEY
    ) as key:
        winreg.CreateKeyEx(key, key_name)


def set_key_value(path: str, name: str, _type: int, value: Union[str, int]) -> None:
    k = parse_input(path)
    with winreg.OpenKey(
        k[0], r"\\".join(k[1]), reserved=0, access=winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, name, 0, _type, value)


def get_key_value(path: str, logger: Logger) -> Union[str, None]:
    k = parse_input(path)
    v = k[1][-1]
    k[1].pop(-1)
    with winreg.OpenKey(k[0], r"\\".join(k[1]), access=winreg.KEY_READ) as key:
        try:
            return winreg.QueryValueEx(key, rf"{v}")[0]
        except Exception:
            logger.warning(f"No match for requested '{v}' Key Value")
            return ""


def backup(root: RootKeys, path: str, fname: str) -> None:
    files = listdir(path)
    if f"{fname}.reg" in files:
        remove(f"{path}/{fname}.reg")
    # r = winreg.ConnectRegistry(None, ROOTS[root])
    # with winreg.OpenKey(r, "", reserved=0, access=winreg.KEY_ALL_ACCESS) as key:
    with winreg.OpenKey(ROOTS[root], "") as key:
        pid = win32api.GetCurrentProcessId()
        ph = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)
        th = win32security.OpenProcessToken(
            ph, win32security.TOKEN_ALL_ACCESS | win32con.TOKEN_ADJUST_PRIVILEGES
        )
        win32security.AdjustTokenPrivileges(
            th,
            0,
            (
                (
                    win32security.LookupPrivilegeValue("", win32security.SE_BACKUP_NAME),
                    win32con.SE_PRIVILEGE_ENABLED,
                ),
                (
                    win32security.LookupPrivilegeValue(
                        "", win32security.SE_SECURITY_NAME
                    ),
                    win32con.SE_PRIVILEGE_ENABLED,
                ),
            ),
        )
        winreg.SaveKey(key, f"{path}/{fname}.reg")


# if __name__ == "__main__":
# print(get_all_keys("local-machine"))
# print(get_key_value("local-machine>SOFTWARE>Autodesk>3dsMax>Current Version>Executable"))
# print(get_key_value("local-machine>SOFTWARE>BlueStacksInstaller>MachineID"))
# set_key_value("local-machine>SOFTWARE>BlueStacksInstaller", "MachineIDs", winreg.REG_SZ, 'a')
# print(get_key_value("local-machine>SOFTWARE>BlueStacksInstaller>MachineID"))
# get_key_value("classes-root>.iso")
# backup("current-config", f"{Path.expanduser('~')}/Desktop/", 'current_config')
# create_key("local-machine>SOFTWARE>BlueStacksInstaller", "MachineIDs")
# print(get_key_value("local-machine>SOFTWARE>ATI Technologies>Install>Packages>W-06-3U01-000-001-044-001-00-25>breboot_req"))
