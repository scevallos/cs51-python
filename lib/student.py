"""
student class
"""
from typing import List, Text
from types import ModuleType
from lib.testcase import Testcase

class Student:

    def __init__(self, module: ModuleType) -> None:
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

    def test(self, testcase: Testcase):
        """
        Tests this student's submission on the given testcase. This will
        invoke the Testcase object's run method to run the test case on
        a new thread.
        """
        testcase.start()

    def __str__(self):
        return self.username

    def __repr__(self):
        return self.username        

def make_student_objs(modules: List[ModuleType]) -> List[Student]:
    """
    Make all the student objects from their imported modules
    """
    return [Student(m) for m in modules]
