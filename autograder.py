"""
CS51P Autograder (written in python3)

TODO: fix a lot of things

Author(s):
    scevallos (Sebastian)
"""
import subprocess as sub
import configparser
import importlib
from sys import exit, version_info
from os import listdir, mkdir
from os.path import isdir, exists, join
from json import load
from types import ModuleType
from typing import List, Dict

# Ensure python 3 is being used
if version_info[0] < 3:
    print("Please run this using a version of Python 3.")
    exit()


def test_functions(modules: List[ModuleType], tests: Dict[str, str], default: configparser.ConfigParser):
    """
    Used to test the functions the submissions are required to have,
    in isolation, on the test cases defined in the tests file.

    Args:
        modules - all the imported submissions
        tests   - tests to be run on submissions, specified in tests file
        default - config object used to refer to grading specifications
    """
    # setup results file if specified in config file
    writing_results_file = default.getboolean('ResultsFile')
    if writing_results_file:
        all_scores = open(join(default['GradesFolder'], 'results.txt'), 'w')

    # see whose submissions are supposed to be tested
    if default['WhoToTest'] != '*':
        # not everyone -> use set intersection of all and testing str in config
        modules_to_test = set(modules) & set(testing.split())
    else:
        # test everyone
        modules_to_test = modules

    for module in modules_to_test:
        # get the name of the module to make individual score file
        modname = module.__name__
        score_fname = join(default['GradesFolder'], modname.split('.')[-1]+'.out')
        with open(score_fname, 'w') as score_file:
            score_file.write("*TESTING FUNCTIONS*\n")
            
            if writing_results_file:
                all_scores.write(modname[(modname.find('.') + 1):(modname.find('_'))] + ':\t')
                total_correct = total_tests = 0

            # TODO: maybe make test cases an ordered dict to preserve order
            # accross runs?

            # filter tests by ones specified in config
            funcs_to_test = default['FuncsToTest']

            # start putting module thru tests
            for func_name, test_case_obj in tests.items():
                # skipping any funcs not in the FuncsToTest config var
                if funcs_to_test != '*' and func_name not in funcs_to_test:
                    continue
                # used for abstraction of optional schema for output testing
                if type(test_case_obj) == list:
                    schema, test_in_out = test_case_obj
                else:
                    test_in_out = test_case_obj
                    schema = None
                # used for numbering of testcases and keeping track of correct
                func_num_correct = func_num_test_case = 0

                # write down function currently being tested
                score_file.write(func_name + '\n')

                # get the function object
                try:
                    func = getattr(module, func_name)
                except AttributeError:
                    print('Unable to get function {} from {}'.format(func_name, modname))
                    score_file.write('\tno such function in this module\n')

                # go through all testcases for this function
                for test_in, test_out in test_in_out.items():
                    # Increment number of test case
                    func_num_test_case += 1

                    # Try eval'ing function input
                    try:
                        inp = eval(test_in)
                    except Exception as err:
                        print('Issue during literal eval of input ({}): {}'.format(test_in, err))
                        score_file.write("\t#{}: TESTCASE ERROR - input eval issue\n".format(func_num_test_case))
                        continue
                    # Try running student code
                    try:
                        if type(inp) == list:
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
                        # check if doing schema abstraction
                        if schema:
                            student_correct = eval(schema.format(test_out))
                        else:
                            student_correct = eval(test_out)
                        tp_std_correct = type(student_correct)
                        assert tp_std_correct == bool
                    except AssertionError:
                        print("Testcase #{} for {}: expr ({}) must evaluate to type 'bool' but was {}".format(func_num_test_case, func_name, test_out, tp_std_correct))
                        score_file.write("\t#{}: TESTCASE ERROR - output eval was not bool\n".format(func_num_test_case))
                        continue
                    except Exception as err:
                        print('Testcase #{} for {}: error during literal eval of output ({}): {}'.format(func_num_test_case, func_name, test_out, err))
                        score_file.write("\t#{}: TESTCASE ERROR - output eval issue\n".format(func_num_test_case))
                        continue

                    if student_correct:
                        func_num_correct += 1
                        score_file.write("\t#{}: PASSED\n".format(func_num_test_case))
                    else:
                        score_file.write("\t#{}: FAILED; got {}, but needed {}\n".format(func_num_test_case, student_ans, test_out))
                score_file.write("\tscore: {}/{}\n".format(func_num_correct, func_num_test_case))
                if writing_results_file:
                    total_correct += func_num_correct
                    total_tests += func_num_test_case
            if writing_results_file:
                all_scores.write('{}/{}\n'.format(total_correct, total_tests))

            score_file.write("\n\tTOTAL SCORE: {}/{} CORRECT\n".format(total_correct, total_tests))
    all_scores.close()


def main():
    """
    write doc string soon
    """
    # setup config parser
    config = configparser.ConfigParser()
    config.read('config.ini')
    default = config['DEFAULT']

    # import the assignments as modules
    try:
        assignment_modules = [importlib.import_module(default['AssignmentsFolder'] + '.' + m[:-3]) for m in listdir(default['AssignmentsFolder']) if ('sig' in m and default['AssignmentNumber'] in m)]
    except Exception as err:
        print('Issues with importing assignments as modules: {}'.format(err))
        print('The assignments must be of the form "<username>_assignment<assignment_num>.py"')
        exit()

    # set up results dir if doesn't exist
    if not(exists(default['GradesFolder']) and isdir(default['GradesFolder'])):
        mkdir(default['GradesFolder'])

    # set up tests from tests json file
    with open(default['TestsFile']) as tests_file:
        tests = load(tests_file)

    test_functions(assignment_modules, tests, default)


if __name__=='__main__':
    main()
