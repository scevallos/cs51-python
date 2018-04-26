import argparse
import configparser
import importlib
from typing import List, Dict, Any
from types import ModuleType
from json import load
from os import listdir, mkdir
from os.path import isdir, exists, join

def cli_args() -> argparse.Namespace:
    """
    Parses optional arguments for either verbose output or
    config file in a different directory than this file.

    Returns:
        parsed arguments object
    """
    argprsr = argparse.ArgumentParser()
    argprsr.add_argument('-v', '--verbose', help='increase verbosity of output', action="store_true")
    argprsr.add_argument('-c', '--config', help="specify the path to the config file (default is 'config.ini')", action='store', default='config.ini')
    return argprsr.parse_args()

def parse_config(path: str = 'config.ini') -> configparser.SectionProxy:
    """
    Sets up the config parser from the config file. Returns the DEFAULT
    object setup.

    Args:
        path - path to config file; defaults to local file called 'config.ini'
    Returns:
        DEFAULT config object that is a dict of the setup
    """
    config = configparser.ConfigParser()
    config.read(path)
    default = config['DEFAULT']
    return default

def import_assignments(asgts_dir: str, asgt_num: str, who: str) -> List[ModuleType]:
    """
    Use the importlib library to create a list of Module objects from
    the student assignments in the specified directory.

    Note: assignments must be in the form "<username>_assignment<asgt_num>.py"

    Args:
        asgts_dir - path to directory w/ student assignments
        asgt_num  - num referring to assignment number
        who       - string indicating whose asgts should be imported/tested
    Returns:
        list of student modules
    """

    assignment_modules = []
    for asgt in listdir(asgts_dir):
        # skip any non python files, any file that doesn't have the word 'assignment', or any
        # file that doesn't have the asgt num in its name
        if not asgt.endswith('.py') or not 'assignment' in asgt or not asgt_num in asgt:
            continue

        # get username of the person's asgt
        username = asgt.split('_')[0]

        # if we want specific people, this username is not who we want, skip it
        if who != '*':
            if who[0] == '-':
                # doing negative filtering => do everyone minus the people w/ a minus sign
                if username in who:
                    continue
            else:
                # positive filtering => only grab people whose names are on here
                if username not in who:
                    continue



        # try to import the assignment
        try:
            assignment_modules.append(importlib.import_module(join(asgts_dir, asgt[:-3]).replace('/', '.')))
        except Exception as err:
            print(f'Issues with importing the assignment "{asgt}" - {err}')
            continue


    # no asgts were actually imported
    if not assignment_modules:
        print('''No assignments were imported!! Please make sure that there the asgts are in the directory you specified ({})
                The assignments must be of the form "<username>_assignment<assignment_num>.py" inside the AssignmentsFolder specified in the config file.
                The <assignment_num> must match the AssignmentNumber in the config file'''.format(asgts_dir))

    return assignment_modules

def maybe_mkdir(dir_name: str) -> None:
    """
    Safely tries to make a directory with the given name, if it doesn't
    already exists. If it exists already, does nothing.

    Args:
        dir_name - name of directory to be made
    """
    if not(exists(dir_name) and isdir(dir_name)):
        mkdir(dir_name)

def load_tests(tests_dir: str, test_fname: str = 'tests.json', funcs: str = '*') -> Dict[str, Any]:
    """
    Tries to load in tests file from given tests_dir.

    Args:
        tests_dir - directory where the tests file is
        test_fname - name of the json file with the tests; defaults to 'tests.json'
    """
    # make sure it's a json file
    if not test_fname.endswith('.json'):
        print('File with tests must be a json file! Stopping autograder...')
        exit()

    # make sure dir exists and is a directory
    if exists(tests_dir) and isdir(tests_dir):
        try:
            with open(join(tests_dir, test_fname)) as tests_file:
                tests = load(tests_file)
        except Exception as err:
            print(f'Issue while trying to load in tests: {err}')
            exit()
    else:
        print(f"Given directory ({tests_dir}) either doesn't exist, or is not a directory")
        exit()

    # filter tests based on FuncsToTest config var
    if funcs != '*':
        tests_to_run = {}
        for func_name, test_params in tests.items():
            if func_name in funcs:
                tests_to_run[func_name] = test_params
        return tests_to_run
    else:
        return tests

