"Windows Registry Utils file"
import winreg
#import os.path as Path
from os import listdir, remove

ROOTS: dict[str,int] = {
    "classes-root": winreg.HKEY_CLASSES_ROOT,
    "current-user": winreg.HKEY_CURRENT_USER,
    "current-config": winreg.HKEY_CURRENT_CONFIG,
    "local-machine": winreg.HKEY_LOCAL_MACHINE,
    "users": winreg.HKEY_USERS,
}

def parse_input(k: str):
    if k == '':
        raise Exception("Cannot provide empty Registry Path")
    str_list = k.split('>')
    root: int = ROOTS[str_list[0]]
    str_list.pop(0)
    return [root, [_ for _ in str_list if _ != '']]

""" def get_all_keys(root: str) -> List[str]:
    keys = []
    i = 0
    try:
        _ = eval(f"winreg.HKEY_{root.upper()}")
        while True:
            k = winreg.EnumKey(_, i)
            keys.append(k)
            i += 1
    except Exception as e:
        pass
    return keys """

def create_key(path: str, key_name: str) -> None:
    k = parse_input(path)
    with winreg.OpenKey(k[0], r'\\'.join(k[1]), reserved=0, access=winreg.KEY_CREATE_SUB_KEY) as key:
        winreg.CreateKeyEx(key, key_name)

def set_key_value(path: str, name: str, _type: int, value: str) -> None:
    k = parse_input(path)
    with winreg.OpenKey(k[0], r'\\'.join(k[1]), reserved=0, access=winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, name, 0, _type, value)

def get_key_value(path: str) -> str:
    k = parse_input(path)
    v = k[1][-1]
    k[1].pop(-1)
    with winreg.OpenKey(k[0], r'\\'.join(k[1]), access=winreg.KEY_READ) as key:
        return winreg.QueryValueEx(key, rf'{v}')[0]

def backup(root: str, path: str, fname: str):
    files = listdir(path)
    if f"{fname}.reg" in files:
        remove(f"{path}/{fname}.reg")
    r = winreg.ConnectRegistry(None, ROOTS[root])
    with winreg.OpenKey(r, '', reserved=0, access=winreg.KEY_ALL_ACCESS) as key:
        winreg.SaveKey(key, f"{path}/{fname}.reg")


if __name__ == '__main__':
    #print(get_all_keys('LOCAL_MACHINE'))
    #print(get_key_value("local-machine>SOFTWARE>Autodesk>3dsMax>Current Version>Executable"))
    print(get_key_value("local-machine>SOFTWARE>BlueStacksInstaller>MachineID"))
    #set_key_value("local-machine>SOFTWARE>BlueStacksInstaller", "MachineIDs", winreg.REG_SZ, 'a')
    #print(get_key_value("local-machine>SOFTWARE>BlueStacksInstaller>MachineID"))
    #get_key_value("classes-root>.iso")
    #backup("current-config", f"{Path.expanduser('~')}/Desktop/", 'current_config')
    #create_key("local-machine>SOFTWARE>BlueStacksInstaller", "MachineIDs")
    #print(get_key_value("local-machine>SOFTWARE>ATI Technologies>Install>Packages>W-06-3U01-000-001-044-001-00-25>breboot_req"))