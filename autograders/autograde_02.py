"""
CS51P Autograder for assignment02 (written in python3)

Requires that there be a directory wherever this script is being run called 'assignments'.
Within that directory, this script expects a bunch .py files that are the assignment02
submissions. This script calls the 'get_last' and 'generate' functions of each submission
through some test cases and (doesn't yet but will soon) generate a directory of all the
results of the test cases.

Date:
    1.25.18
Author(s):
    scevallos (Sebastian)
"""
import argparse
from sys import exit, version_info
from types import ModuleType
import types

# Ensure python 3 is being used
if version_info[0] < 3:
    print("Please run this using a version of Python 3.")
    exit()

# Try to import the assignments
try:
    from assignments import *
except ImportError:
    print("Could not import modules from 'assignments'.")
    exit()


def imports():
    """
    Gets modules currently imported as generator object.
    """
    for name, val in globals().items():
        if isinstance(val, ModuleType):
            yield val.__name__

def get_submission_names():
    """
    Parse the imported modules to produce a list of student submission names
    """
    return [f.split('.')[-1] for f in imports() if 'assign' in f]

def run_testcases(module_name):
    """
    Given the module name, tests the get_last and generate functions
    """

    # test cases dict maps input to get_last to expected output of get_last
    test_cases = {
        123456789012 : 8,
        474747474747 : 6,
        # TODO: write more tests?
    }
    
    for test_input, expected_output in test_cases.items():
        # Call this person's get_last function w all the inputs from test cases
        student_out = globals()[module_name].get_last(test_input)

        if student_out == expected_output:
            pass # write to text file or something #TODO

def main():
    """
    write doc string soon
    """

    # gets list of module names (e.g. ['scevallos_assignment02', ..., ])
    assignments = get_submission_names()


if __name__=='__main__':
    main()
