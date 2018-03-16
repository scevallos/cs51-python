# CS51-Python Autograding
## How-to use:
1. Clone this repo.
2. Copy all the assignments into a directory within your working directory (e.g. you can use the `scripts/copy_asgts` script for this; note that it has to be copied into the dropbox, and run from there).
3. Configure the `config.ini` file as you wish (see 'How-to setup the config file' section).
4. Write tests to a json file, following testing specification (see 'How-to write tests' section).
5. Run the autograder (definitely using Python 3, and probably using 3.6 to make sure you can run the assignments) with `python3 autograder.py`.

## How-to setup the config file
The config file is parsed using the [configparser](https://docs.python.org/3/library/configparser.html "configparser") library, and thus, follows standard INI file specifications. For autograding, the file must be called `config.ini` and be in the same directory as `autograder.py`. The file must look as follows:
```
[DEFAULT]
AssignmentsFolder = <path/to/dir/w/asgts>
GradesFolder = <path/to/dir/where/output/will/be>
AssignmentNumber = <some_integer>
TestsFile = <path_to_json_test_file>
WhoToTest = <*|username|username_1 username_2 ... username_n>
FuncsToTest = <*|func_name|func_1 func_2 ... func_n>
ResultsFile = <yes|no>
```

Each of the above values are used as follows:
* **AssignmentsFolder**: This directory should exist before running the autograder and should contain the assigments to be graded. The Python files should be in the format `<username>_assignment<asgt_num>.py`, where `username` is the student who submitted the file, and `asgt_num` is an integer indicating the assignment number.
* **GradesFolder**: This directory doesn't *have* to exist before running the autograder; it will be made if it doesn't exist. In this directory, each student's output and resulting score will be written to a text file in the form `<username>_assignment<asgt_num>.out`. If the **ResultsFile** variable is set to yes, this is also where the `results.txt` file will be written.
* **AssignmentNumber**: This is an integer representing the assignment number of what is to be graded. This is used to distinguish previous assignment python files in the assignments folder from each other (i.e. only assigments that follow the naming convention, with the integer specified here in the name, will be graded)
* **TestsFile**: This is a path to a json file containing the tests to be run for this assignment. The specification for writing tests is in the "How to write tests" section.
* **WhoToTest**: This is either `*`, indicating that all the assignments that match the convention in the assignments folder are to be graded; `<username>`, where username is a student's username, indicating that only this student is to be graded; or a sequence of usernames separated by a space, indicating that only these students' assignments are to be graded.
* **FuncsToTest**: This is either `*`, indicating that the autograder should run all the tests in the tests file; `<function_name>`, indicating that only the tests for the specified function should be run; or a sequence of function names separated by a space, inficating that only these functions' tests should be run.
* **ResultsFile**: This is either `yes` or `no`, indicating whether or not a `results.txt` file should be produced. This results file contains the total score of each student, and is helpful to see generally how the class did, but individual results can be found in each student's respective result file.

## How-to write tests
tbd
