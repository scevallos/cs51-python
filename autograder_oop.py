#!/usr/bin/env python3.6
"""
blah blah blah
"""
from types import ModuleType
from typing import List, Tuple, Dict, Any, Text
from configparser import SectionProxy
from argparse import Namespace
from multiprocessing import Queue
from time import time

from lib.testcase import Testcase
from lib.student import Student, make_student_objs
from utils import setup

def run_setup(args: Namespace) -> Tuple[List[ModuleType], Dict[Text, Any], SectionProxy]:

    if args.verbose:
        print('parsing config file...')

    # setup config parser
    default = setup.parse_config(args.config)

    if args.verbose:
        print('importing the assignments...')

    # import the assignments as modules
    assignment_modules = setup.import_assignments(default['AssignmentsFolder'], default['AssignmentNumber'], default['WhoToTest'])

    # set up results dir if doesn't exist
    setup.maybe_mkdir(default['GradesFolder'])

    if args.verbose:
        print('loading in tests...')

    # set up tests from tests json file
    tests = setup.load_tests(default['TestsFolder'], 'tests2.json')

    return assignment_modules, tests, default


def main():
    # parse cli arguments specified when running autograder
    args = setup.cli_args()

    # start timer if verbose output desired
    if args.verbose:
        start = time()

    # get assignments, load in tests, and get config default object
    assignment_modules, tests, default = run_setup(args)

    # used for safely handling multiple processes
    queue = Queue()

    students = make_student_objs(assignment_modules)

    all_testcases: Dict[Text, List[Testcase]] = {}
    for student in students:
        all_testcases[student.username] = student.run(tests, queue, args.verbose)

    all_results: Dict[Text, Tuple[Text, List[Text]]] = {}
    for student, testcases in all_testcases.items():
        for testcase in testcases:
            testcase.join()
            all_results[student] = queue.get()

    if args.verbose:
        print("Execution time: {0:.5f} secs".format(time() - start))


if __name__ == '__main__':
    main()