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
from os.path import join

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
    tests = setup.load_tests(default['TestsFolder'], default['TestsFile'], default['FuncsToTest'])

    return assignment_modules, tests, default


def write_results_files(all_results: Dict[Text, Dict[Text, Tuple[Text, List[Text]]]], grades_dir: Text, all_results_file: bool) -> None:
    # results file for everyone if specified
    if all_results_file:
        results_file = open(join(grades_dir, 'results.txt'), 'w')

    # write individual result files
    for name, func_results in sorted(all_results.items()):
        total_score = 0
        total_total = 0
        student_result = open(join(grades_dir, name + '.out'), 'w')
        for func_name, (score, details) in func_results.items():
            if all_results_file:
                correct_str, total_str = score.split('/')
                total_score += int(correct_str)
                total_total += int(total_str)
            student_result.write(f'{func_name}: {score}\n')
            for i in range(len(details)):
                student_result.write(f'\t#{i+1} - {details[i]}\n')
        student_result.close()
        if all_results_file:
            results_file.write(f'{name}:\t{total_score}/{total_total}\n')

    if all_results_file:
        results_file.close()


def main():
    # parse cli arguments specified when running autograder
    args = setup.cli_args()

    # start timer if verbose output desired
    if args.verbose:
        start = time()

    # get assignments, load in tests, and get config default object
    assignment_modules, tests, default = run_setup(args)

    # used for safely handling data across multiple processes
    queue = Queue()

    students = make_student_objs(assignment_modules)

    all_testcases: List[List[Testcase]] = []
    for student in students:
        all_testcases.append(student.run(tests, queue, args.verbose))

    all_results: Dict[Text, Dict[Text, Tuple[Text, List[Text]]]] = {}
    for testcases in all_testcases:
        for testcase in testcases:
            testcase.join()
            queue_output = queue.get()
            if queue_output[0] not in all_results:
                all_results[queue_output[0]] = {}
            all_results[queue_output[0]][queue_output[1]] = queue_output[2:]
    
    if args.verbose:
        print("Writing results to score files...")
    write_results_files(all_results, default['GradesFolder'], default.getboolean('ResultsFile'))

    if args.verbose:
        print("Execution time: {0:.5f} secs".format(time() - start))

if __name__ == '__main__':
    main()
