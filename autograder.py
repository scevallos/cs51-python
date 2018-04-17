#!/usr/bin/env python3.6
"""
CS51P Autograder

TODO: fix a lot of things

Author(s):
    scevallos (Sebastian)
"""
import time

import subprocess as sub
import configparser
import argparse
import importlib
from sys import exit, version_info
from os import listdir, mkdir
from os.path import isdir, exists, join
from json import load
from types import ModuleType
from typing import List, Dict, Tuple

from utils import setup

# Ensure python 3.6+ is being used
if version_info[:2] < (3,6):
    print("Please run this using a version of Python 3.6+")
    exit()

def get_username_from_module(module: ModuleType) -> str:
    """
    Returns the username of the person who submitted, given
    their imported module. Note: this relies on the naming
    convention where the assignments submitted are in the
    format <username>_assignment<asgt_num>.py.

    Args:
        module - single imported submission
    Returns:
        username of student that was submitted
    """
    modname = module.__name__
    return modname[modname.find('.')+1:modname.find('_')]


def get_modules_to_test(whoToTest: str, modules: List[ModuleType]) -> List[ModuleType]:
    """
    Uses config 'WhoToTest' option and does set intersection of that
    and all modules to return the modules that we want to test
    
    Args:
        whoToTest - config var; either * or <usernames>
        modules   - all the imported submissions
    Returns:
        {modules} & {whoToTest}
    """
    if whoToTest == '*':
        # test everyone
        return modules
    else:
        # list of modules where the username is one of the whoToTest
        return [module for name in whoToTest.split() for module in modules if get_username_from_module(module) == name]
        



def test_functions(modules: List[ModuleType], tests: Dict[str, str], default: configparser.ConfigParser, verbose: bool):
    """
    Used to test the functions the submissions are required to have,
    in isolation, on the test cases defined in the tests file.

    Args:
        modules - all the imported submissions
        tests   - tests to be run on submissions, specified in tests file
        default - config object used to refer to grading specifications
        verbose - whether or not to display verbose output
    """
    # setup results file if specified in config file
    try:
        writing_results_file = default.getboolean('ResultsFile')
    except ValueError:
        print("config file 'ResultsFile' var was {}; should be <yes|no>.".format(default['ResultsFile']))
        print("not writing results file!")
        writing_results_file = False

    if writing_results_file:
        if verbose:
            print('opening results file...')
        all_scores = open(join(default['GradesFolder'], 'results.txt'), 'w')

    if verbose:
        print('getting who to test...')
    # see whose submissions are supposed to be tested
    modules_to_test = get_modules_to_test(default['WhoToTest'], modules)

    for module in modules_to_test:
        # get the name of the student from the module to make individual score file
        student_username = get_username_from_module(module)

        if verbose:
            print('testing {}'.format(student_username))

        score_fname = join(default['GradesFolder'], student_username + '.out')
        with open(score_fname, 'w') as score_file:
            score_file.write("*TESTING FUNCTIONS*\n")
            
            if writing_results_file:
                all_scores.write(get_username_from_module(module) + ':\t')
            
            # keeping track of total number of test cases for this asgt
            total_correct = total_tests = 0

            # filter tests by ones specified in config
            funcs_to_test = default['FuncsToTest']

            # start putting module thru tests
            for func_name, test_case_obj in tests.items():
                # skipping any funcs not in the FuncsToTest config var
                if funcs_to_test != '*' and func_name not in funcs_to_test:
                    continue
                # used for abstraction of optional schema for output testing
                if type(test_case_obj) == list:
                    if len(test_case_obj) == 2:
                        schema, test_in_out = test_case_obj
                    elif len(test_case_obj) == 3:
                        schema, setup, test_in_out = test_case_obj
                    else:
                        # do not know what to do with test_case_obj that's not len 2 or 3
                        print("""The test case for a function must be in one of the below forms:
                            {<literal_input> : <literal_output>}
                            [<schema>, {<literal_input> : <format_values>}
                            [<schema>, setup, {<literal_input> : <format_values>}]
                            """)
                        continue
                else:
                    test_in_out = test_case_obj
                    schema = None
                    setup = None
                # used for numbering of testcases and keeping track of correct
                func_num_correct = func_num_test_case = 0

                # write down function currently being tested
                score_file.write(func_name + '\n')

                # get the function object
                try:
                    func = getattr(module, func_name)
                except AttributeError:
                    print('Unable to get function {} from {}'.format(func_name, student_username))
                    score_file.write('\tno such function in this module\n')
                    continue

                # go through all testcases for this function
                for test_in, test_out in test_in_out.items():
                    # Increment number of test case
                    func_num_test_case += 1

                    # If using setup, run that first
                    try:
                        if setup:
                            exec(setup) # TODO: probably use dicts for globals, locals instead of clogging
                                        #       global namespace here
                    except Exception as err:
                        print(f'Issue during execution of testcase setup: {err}')
                        continue
                    # Try eval'ing function input
                    try:
                        inp = eval(test_in)
                    except Exception as err:
                        print('Issue during literal eval of input ({}): {}'.format(test_in, err))
                        score_file.write("\t#{}: TESTCASE ERROR - input eval issue\n".format(func_num_test_case))
                        continue
                    # Try running student code
                    try:
                        if type(inp) == list or type(inp) == tuple:
                            # unpack test_in if func has multiple input args
                            student_ans = func(*inp)
                        else:
                            student_ans = func(inp)
                        # doing this for easiness of writing 'ans' in testcases
                        ans = student_ans
                    except Exception as err:
                        # error thrown when calling student func
                        score_file.write("\t#{}: STUDENT ERROR - {}\n".format(func_num_test_case, err))
                        continue

                    # Try eval'ing function output
                    try:
                        # print('ABOUT TO CHECK THING')
                        # print(f'test_out is {test_out}')
                        # print('evaling')
                        # xxx = eval(test_out)
                        # print(f'output was {xxx}')
                        # print('*DONE*')
                        # check if doing schema abstraction
                        if schema:
                            format_vals = eval(test_out)
                            if type(format_vals) == tuple:
                                # print('tuple case')
                                # print(f'about to eval: {schema.format(*format_vals)}')
                                student_correct = eval(schema.format(*format_vals))
                                # print('evaled w/ schema')
                            else:
                                # assuming if not tuple, then single val, e.g. int or something
                                student_correct = eval(schema.format(format_vals))
                        else:
                            student_correct = eval(test_out) == ans
                        tp_std_correct = type(student_correct)
                        assert tp_std_correct == bool
                    except AssertionError:
                        print("Testcase #{} for {}: expr ({}) must evaluate to type 'bool' but was {}".format(func_num_test_case, func_name, test_out, tp_std_correct))
                        score_file.write("\t#{}: TESTCASE ERROR - output eval was not bool\n".format(func_num_test_case))
                        continue
                    except Exception as err:
                        print('Testcase #{} for {}: error during literal eval of output {!r}: {}'.format(func_num_test_case, func_name, test_out, err))
                        score_file.write("\t#{}: TESTCASE ERROR - output eval issue\n".format(func_num_test_case))
                        continue

                    if student_correct:
                        func_num_correct += 1
                        score_file.write("\t#{}: PASSED\n".format(func_num_test_case))
                    else:
                        # TODO: Make the failed message a little better for schema usage
                        if schema:
                            try:
                                expected = schema.format(*format_vals)
                                gotten_exprs = [eval(left, {'ans': ans}) for left, right in [binop.split('==') for binop in schema.split('and')]]
                                got_str = schema.format(*gotten_exprs).replace('==', 'was')
                                score_file.write(f"\t#{func_num_test_case}: FAILED; expected:\n\t{expected}\ngot:\n\t{got_str}\n")
                            except Exception as err:
                                score_file.write(f"\t#{func_num_test_case}: FAILED; and bad error!\n")
                        else:
                            score_file.write("\t#{}: FAILED; got {}, but needed {}\n".format(func_num_test_case, student_ans, test_out))
                score_file.write("\tscore: {}/{}\n".format(func_num_correct, func_num_test_case))

                # keep count for total score calculation
                total_correct += func_num_correct
                total_tests += func_num_test_case
            if writing_results_file:
                all_scores.write('{}/{}\n'.format(total_correct, total_tests))

            score_file.write("\n\tTOTAL SCORE: {}/{} CORRECT\n".format(total_correct, total_tests))
    if writing_results_file:
        all_scores.close()


def test_mains(modules: List[ModuleType], default: configparser.ConfigParser):
    """
    Used to test the execution of the main function in the specified
    submissions. Does this by starting subprocess and using stdin/out
    """
    # get the list of modules that we want to test
    modules_to_test = get_modules_to_test(default['WhoToTest'], modules)

    # run each of the tests (in#.txt) through each submission
    for module in modules_to_test:
        fname = module.__name__.split('.')[-1] + '.py'
        for input_test_fname in [t for t in listdir(default['TestsFolder']) if 'in' in t and 'txt' in t]:
            # get the path of the test file
            input_test_fpath = join(default['TestsFolder'], input_test_fname)
            # make the name for the output file
            out_fname = fname[:-3] + '_out' + input_test_fname[input_test_fname.find('.')-1] + '.txt'

            # read the lines of the input test file
            with open(input_test_fpath, 'r') as in_test_file:
                in_lines = in_test_file.readlines()

            # (maybe) modifying input based on the asgt being run
            with open(input_test_fpath, 'w') as in_test_file:
                for line in in_lines:
                    if 'out' in line:
                        in_test_file.write(join('.',default['GradesFolder'], out_fname[:-4] + '.ppm') + '\n')
                    else:
                        in_test_file.write(line)

            # open out file for writing stdout
            out_test_file = open(join(default['GradesFolder'], out_fname), 'w')
            in_test_file = open(input_test_fpath, 'r')

            # run their code as a new subprocess
            p = sub.Popen(['python3.6', join(default['AssignmentsFolder'], fname)], stdin=in_test_file, stdout=out_test_file)
            p.wait()

            out_test_file.close()
            in_test_file.close()

def setup_grader(args: argparse.Namespace) -> Tuple[List[ModuleType], Dict[str, str], configparser.ConfigParser]:
    """
    Runs setup for the autograder to work which includes:
    * reading in the 'config.ini'
    * importing all the appropriate assignment modules
    * loading in the tests

    Args:
        command line args
    Returns:
        imported assignment modules list, tests json as dict, config object
    """
    if args.verbose:
        print('parsing config file...')

    # setup config parser
    default = setup.parse_config()

    if args.verbose:
        print('importing the assignments...')

    # import the assignments as modules
    assignment_modules = setup.import_assignments(default['AssignmentsFolder'], default['AssignmentNumber'], default['WhoToTest'])

    # set up results dir if doesn't exist
    setup.maybe_mkdir(default['GradesFolder'])

    if args.verbose:
        print('loading in tests...')
    # set up tests from tests json file
    tests = setup.load_tests(default['TestsFolder'])

    return assignment_modules, tests, default



def main():
    """
    write doc string soon
    """
    # parse cli arguments specified when running autograder
    args = setup.cli_args()
    
    # setup the asgts, tests, and config object
    assignment_modules, tests, default = setup_grader(args)

    # time testing the functions
    start = time.time()

    # running tests on specified modules & functions
    if assignment_modules and tests:
        test_functions(assignment_modules, tests, default, args.verbose)

    print("Execution time = {0:.5f}".format(time.time() - start))

    # running main tests
    if default.getboolean('TestMain'):
        test_mains(assignment_modules, default)



if __name__=='__main__':
    main()
