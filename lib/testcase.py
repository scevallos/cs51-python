"""
blah blah
"""
from typing import Any, Dict, Text, List, Callable
from multiprocessing import Process, Queue

class Testcase(Process):
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
    def __init__(self, tests: Dict[str, str], queue: Queue,
        student_function: Callable[[Any], Any], # TODO: probably change/fix callback type
        schema: Text = None, setup: Text = None, callback: Callable[[Any], Any] = None,
        verbose: bool = False, name: Text = 'NoName') -> None:
        # constructor from super class
        super(Process, self).__init__()

        # 3 things that make up a test case obj
        self.tests = tests
        self.schema = schema
        self.setup = setup
        self.callback = callback
        self.queue = queue
        self.student_function = student_function
        
        # verbosity and name of the test case (used for verbosity)
        self.verbose = verbose
        self.name = name

        # used to count num correct/total questions
        self.correct = 0
        self.total = 0

        # vars in scope of this testcase
        self.vars : Dict[Text, Any] = {}

    def __try_exec_line(self, line: Text) -> None:
        """
        Safely attempts to execute line literally, storing side-vars in self.vars
        """
        try:
            exec(line, self.vars)
        except Exception as err:
            print(f'Issue during execution of setup: {err}')
            print(f'Line was: {line}')
            return # TODO: does this stop the process??

    def __process_setup(self):
        """
        Executes the the setup code intended to be run prior to running the
        test. Stores vars that might have been assigned here in self.vars
        """
        setup_type = type(self.setup)

        # setup should be str (single line to exec) or [str] - multiple lines to exec
        if setup_type == str:
            self.__try_exec_line(self.setup)
        elif setup_type == list:
            for line in self.setup:
                self.__try_exec_line(line)
        else:
            print(f'Expected setup to be str or list but was {setup_type}')
            return #TODO: does this stop the process??

    def __process_schema(self, format_vals: Any) -> (List[bool], List[Text]):
        """
        blah
        """
        schema_type = type(self.schema)
        check_results = []
        maybe_failed_schema = []

        if schema_type == str:
            check_results = [eval(self.schema.format(format_vals), self.vars)]
            if not check_results[0]:
                maybe_failed_schema = [self.schema]
        elif schema_type == list:
            schema_len = len(self.schema)
            fvals_len = len(format_vals)
            if schema_len != fvals_len:
                # something wrong
                print(f'Num of exprs in schema ({schema_len}) != num of exprs in format values ({fvals_len})!')
                if self.verbose:
                    print(f'Schema was: {self.schema}\nFormat vals were: {format_vals}')
                return None
            else:
                i = 0
                while i < schema_len:
                    single_result = eval(self.schema[i].format(format_vals[i]), self.vars)
                    check_results.append(single_result)
                    if not single_result:
                        maybe_failed_schema.append(self.schema[i])
                    i += 1
        return check_results, maybe_failed_schema


    def run(self):
        """
        Override the run method to invoke running on a new process
        """
        if self.verbose:
            print(f'Running {self.name} tests...')

        # try running setup if there is one
        if self.setup:
            self.__process_setup()

        final_report = [None] * len(self.tests)

        for test_in, test_out in self.tests.items():
            # increment total num of tests
            self.total += 1

            if self.verbose:
                print(f'#{self.total}')

            # evaluate test input w/ setup vars, if any
            try:
                inp = eval(test_in, self.vars)
            except Exception as err:
                print(f'Issue during evaluation of test input: {err}')
                final_report[self.total - 1] = 'input eval error'
                if self.verbose:
                    print(f'Test input was: {test_in}')
                    print('Vars from execution: {}'.format({k : v for k, v in self.vars.items() if k != '__builtins__'}))
                continue

            
            # checking if function input has more than one arg
            if type(inp) in (list, tuple):
                try:
                    student_out = self.student_function(*inp)
                except Exception as err:
                    print(f'Issue while running student code: {err}')
                    final_report[self.total - 1] = 'student code error'
                    if self.verbose:
                        print(f'Function being run was: {self.name}')
                        print(f'Inputs were: {inp}')
                    continue
            else:
                try:
                    student_out = self.student_function(inp)
                except Exception as err:
                    print(f'Issue while running student code: {err}')
                    final_report[self.total - 1] = 'student code error'
                    if self.verbose:
                        print(f'Function being run was: {self.name}')
                        print(f'Input was: {inp}')
                    continue

            # ans alias for ease of answer checking
            self.vars['ans'] = student_out

            if self.schema:
                format_vals = eval(test_out, self.vars)
                results, maybe_failed_schema = self.__process_schema(format_vals)
                if all(results):
                    self.correct += 1
                    final_report[self.total - 1] = 'PASSED'
                else:
                    # failed at least one of the tests
                    failed_str = " and ".join([", ".join(maybe_failed_schema[:-1]),maybe_failed_schema[-1]] if len(maybe_failed_schema) > 2 else maybe_failed_schema)
                    final_report[self.total - 1] = f'FAILED; failed following assertion(s): {failed_str}'
            else:
                if student_out == test_out:
                    self.correct += 1
                    final_report[self.total - 1] = 'PASSED'
                else:
                    # failed the only test
                    final_report[self.total - 1] = f'FAILED; got {student_out} but expected {test_out}'

        # once done, put the final report on the queue
        self.queue.put((f'{self.correct}/{self.total}', final_report))


    def __str__(self):
        maybe_param_name = lambda arg: arg + ',' if getattr(self, arg) else ''
        str_to_print = ''.join(map(maybe_param_name, ('schema', 'setup', 'tests', 'verbose', 'callback')))
        return f'Testcase<{self.name}> - has ' + ('only tests' if not str_to_print else '(' + str_to_print[:-1] + ')')

    def __repr__(self):
        return f'Testcase<{self.name}>'


def make_test_objs(tests: Dict[Text, Dict[Text, Any]], queue: Queue, verbose: bool) -> List[Testcase]:
    """
    Makes Testcase objects from the tests dictionary made from loading the
    tests json.
    """
    testcases = []
    for func_name, test_params in tests.items():
        try:
            test_params['name'] = func_name
            test_params['verbose'] = verbose
            test_params['queue'] = queue
            testcases.append(Testcase(**test_params))
        except Exception as err:
            print(f'Issue during making of Testcase object for {func_name}: {err}')
            continue
    return testcases



