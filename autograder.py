"""
CS51P Autograder (written in python3)

TODO: fix a lot of things

Author(s):
    scevallos (Sebastian)
"""
import configparser
import importlib
from sys import exit, version_info
from os import listdir
from types import ModuleType
import types

# Ensure python 3 is being used
if version_info[0] < 3:
    print("Please run this using a version of Python 3.")
    exit()


def imports():
    """
    Gets modules currently imported as generator object.
    """
    for name, val in globals().items():
        if isinstance(val, ModuleType):
            yield val.__name__


def run_testcases(student_module, tests_file, functions_dict):
    """
    Given the module, tests the functions as specified in the config file
    """
    # funs = []
    # # Get the functions we are gonna test
    # for func in functions_dict:
    #     if functions_dict.getboolean(func):
    #         funs.append(func)

    # TODO: un-hardcode this later
    get_last_tests = {
        981342885440 : 7,
        981342403958 : 1,
        444444444444 : 8,
        123456789012 : 8,
        474747474747 : 6
    }

    generate_tests = [
        123456,
        100000,
        444444,
        915276,
        999999,
        461926
    ]

    results = {
        "get_last" : {}, # mapping funcs to results, where results maps test_in to (student_out, outcome)
        "generate" : {}
    }

    for test in generate_tests:
        try:
            student_out = student_module.generate(test)
        except e:
            results['generate'][test] = ('oops', 'Raised error: ' + str(e))
            continue

        if len(str(student_out)) == 13:
            outcome = "PASSED"
        else:
            outcome = "FAILED: Not len 13, was " + str(len(str(student_out)))

        results['generate'][test] = (student_out, outcome)

    for test in get_last_tests:
        student_out = student_module.get_last(test)

        if student_out == get_last_tests[test]:
            outcome = "PASSED"
        else:
            outcome = "FAILED: Incorrect check digit"

        results['get_last'][test] = (student_out, outcome)

    # Getting name of module for grades file
    module_name = str(student_module)
    left = module_name.index('.') + 1
    fname = module_name[left: module_name.index("'", left)]

    # Write out results to file
    with open(fname + '.txt', 'w') as score:
        for func in results:
            score.write(func + "\n")
            for test, (ans, outcome) in results[func].items():
                score.write("\t" + outcome + "\t" + func + "(" + str(test) + ") returned " + str(ans) + "\n")
            score.write("\n")


def main():
    """
    write doc string soon
    """
    # setup config parser
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    default = config['DEFAULT']

    # see if grading individual students

    # import the assignments as modules
    assignment_names = [f[:-3] for f in listdir(default['SubmissionsFolder']) if 'ass' in f]
    assignment_modules = [importlib.import_module(default['SubmissionsFolder'] + '.' + m) for m in assignment_names]

    # test each of the student's code
    for module in assignment_modules:
        results = run_testcases(module, default['TestCases'], config['FunctionsToTest'])

if __name__=='__main__':
    main()
