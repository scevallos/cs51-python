"""
blah blah
"""
from typing import Any, Dict, Text, List, Callable
import threading
import time

class Testcase(threading.Thread):
    """
    A testcase object for a certain assignment function to be tested.
    Consists of:
        * the dict mapping test inputs to (expected) test output
        * the student function to be tested
        * (optional) schema to be used for formatting test output
        * (optional) setup code to run prior to test
        * (optional) whether or not to have verbose output
        * (optional) name of asgt function being tested
    """
    def __init__(self, tests: Dict[str, str], # TODO: probably change/fix callback type annot.
                schema: str = None, setup: str = None, callback: Callable[[Any], Any] = None,
                verbose: bool = False, name: str = 'NoName') -> None:
        # constructor from super class
        threading.Thread.__init__(self)

        # 3 things that make up a test case obj
        self.tests = tests
        self.schema = schema
        self.setup = setup
        self.callback = callback
        
        # verbosity and name of the test case (used for verbosity)
        self.verbose = verbose
        self.name = name

        # used to count num correct/total questions
        self.correct = 0
        self.total = 0

        # vars in scope of this testcase
        self.vars : Dict[Text, Any] = {}

    def run(self):
        """
        Override the threading.Thread run method to invoke running on a new thread
        """
        if self.verbose:
            print(f'Running tests for {self.name}...')
            start = time.time()

        # try running setup
        if self.setup:
            try:
                exec(self.setup, self.vars)
            except Exception as err:
                print(f'Issue during execution of setup: {err}')
                print(f'Setup was: {self.setup}')
                return

        for test_in, test_out in self.tests.items():
            # increment total num of tests
            self.total += 1

            if self.verbose:
                print(f'Running test #{self.total}')

            # evaluate test input w/ setup vars, if any
            try:
                inp = eval(test_in, self.vars)
            except Exception as err:
                print(f'Issue during evaluation of test input: {err}')
                if self.verbose:
                    print(f'Test input was: {test_in}')
                    print('Vars from execution: {}'.format({k : v for k, v in self.vars.items() if k != '__builtins__'}))
                continue

            # try running student code with test input
            try:
                # checking if function input has more than one arg
                if type(inp) == list:
                    student_out = self.student_function(*inp)
                else:
                    student_out = self.student_function(inp)

                # ans alias for ease of answer checking
                ans = student_out
            except Exception as err:
                # exception raised during student code execution
                # TODO: figure out what to do about score file - pass as another param, student object?
                pass
    def __str__(self):
        maybe_param_name = lambda arg: arg + ',' if getattr(self, arg) else ''
        str_to_print = ''.join(map(maybe_param_name, ('schema', 'setup', 'tests', 'verbose', 'callback')))
        return f'Testcase<{self.name}> - has ' + ('only tests' if not str_to_print else '(' + str_to_print[:-1] + ')')

    def __repr__(self):
        return f'Testcase<{self.name}>'


def make_test_objs(tests: Dict[Text, Dict[Text, Any]], verbose: bool) -> List[Testcase]:
    """
    Makes Testcase objects from the tests dictionary made from loading the
    tests json.
    """
    testcases = []
    for func_name, test_params in tests.items():
        try:
            test_params['name'] = func_name
            test_params['verbose'] = verbose
            testcases.append(Testcase(**test_params))
        except Exception as err:
            print(f'Issue during making of Testcase object for {func_name}: {err}')
            continue
    return testcases



