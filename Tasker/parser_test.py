import os
import sys

import pytest

from Tasker import __main__, parser

# ----------------------------------- __main__ -------------------------------------------


def test_check_for_system_exit():
    sys.argv = [""]
    with pytest.raises(SystemExit):
        __main__.main()


def test_create_flag_system():
    sys.argv = ["", "create"]
    with pytest.raises(SystemExit):
        __main__.main()


def test_edit_flag_system():
    sys.argv = ["", "edit"]
    with pytest.raises(SystemExit):
        __main__.main()


def test_create_partial_flag_system():
    sys.argv = ["", "create", "--File aws"]
    with pytest.raises(SystemExit):
        __main__.main()


def test_edit_partial_flag_system():
    sys.argv = ["", "edit", "-NO"]
    with pytest.raises(SystemExit):
        __main__.main()


# ----------------------------------- Parser ---------------------------------------------


def test_list_instructions():
    "Check if all files returned by the Task Lister is using the correct file termination"
    all_files = [
        _.replace(".tasker.json", "")
        for _ in os.listdir(f"{os.path.expanduser('~')}/.tasker/Tasks")
        if _.endswith(".tasker.json")
    ]
    check = parser.Parser.list_all_tasks()
    assert all_files == check
