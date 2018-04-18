"""
student class
"""
from typing import List, Text, Dict, Any
from types import ModuleType
from multiprocessing import Queue

from lib.testcase import Testcase

class Student:

    def __init__(self, module: ModuleType) -> None:
        self.module = module
        self.username: Text = self._get_username_from_module(module)


    def _get_username_from_module(self, module: ModuleType) -> Text:
        """
        Returns the username of the person who submitted, from
        their imported module.

        Note: this relies on the naming convention where the
        assignments submitted are in the format:
            <username>_assignment<asgt_num>.py.
        """
        modname = module.__name__
        return modname[modname.find('.')+1:modname.find('_')]

    def run(self, tests: Dict[Text, Any], queue: Queue, verbose: bool):
        """
        """
        test_cases = []
        for func_name, test_params in tests.items():
            # a little more setup before making new process
            test_params['name'] = func_name
            test_params['verbose'] = verbose
            test_params['queue'] = queue
            test_params['student_function'] = getattr(self.module, func_name)

            # make new testcase obj that runs in new process
            testcase = Testcase(**test_params)
            if verbose:
                print(f'Starting tests on {self.username}')
            testcase.start()

            test_cases.append(testcase)

        return test_cases

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username        

def make_student_objs(modules: List[ModuleType]) -> List[Student]:
    """
    Make all the student objects from their imported modules
    """
    return [Student(m) for m in modules]
