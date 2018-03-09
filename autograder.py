"""
CS51P Autograder (written in python3)

TODO: fix a lot of things

Author(s):
    scevallos (Sebastian)
"""
import subprocess as sub
import configparser
import importlib
from ast import literal_eval
from sys import exit, version_info
from os import listdir, mkdir
from os.path import isdir, exists, join
from types import ModuleType

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


def main():
    """
    write doc string soon
    """
    # setup config parser
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    default = config['DEFAULT']

    # import the assignments as modules
    assignment_names = [f[:-3] for f in listdir(default['SubmissionsFolder']) if 'ass' in f]
    assignment_modules = [importlib.import_module(default['SubmissionsFolder'] + '.' + m) for m in assignment_names]

    # Set up tests
    testcases = literal_eval(default['TestCases'])

    # set up results dir if doesn't exist
    if not(exists(default['GradesFolder']) and isdir(default['GradesFolder'])):
        mkdir(default['GradesFolder'])

    # set up total scores file
    results = open(join(default['GradesFolder'], 'results.txt'), 'w')


    # run tests - TODO: make this its own function w options to 
    # test single person, use only certain test cases, etc.
    for module in assignment_modules:
        # make a file for this submission and open it for writing
        modname = module.__name__
        outfile_name = join(default['GradesFolder'], modname.split('.')[-1]+'.out')
        outfile = open(outfile_name, 'w')
        outfile.write("***TESTING FUNCTIONS***\n")

        # write a line in total results file
        results.write(modname[(modname.find('.') + 1):(modname.find('_'))] + ':\t')

        total_correct = 0
        total_tests = 0

        # Run through all the test cases for this submission
        for func_name, test_in_out in testcases.items():

            func_num_correct = 0 # for this function
            func_test_case_num = 0 # for this functon

            # write the function being tested rn
            outfile.write(func_name + '\n')

            # run through all the test cases for this function
            for test_in, test_out in test_in_out.items():
                # count how many tests are being done here

                func = getattr(module, func_name)
                try: # running student function
                    if type(test_in) is tuple:
                        student_out = func(*test_in)
                    else:
                        student_out = func(test_in)
                    if student_out == test_out:
                        outfile.write('\t#{}: PASSED\n'.format(func_test_case_num))
                        func_num_correct += 1
                    else:
                        outfile.write('\t#{}: FAILED - got {}; excepted {}\n'.format(func_test_case_num, student_out, test_out))
                except Exception as err:
                    outfile.write('\t#{}: ERROR - {}\n'.format(func_test_case_num, err))
                func_test_case_num += 1

            # write down how many test cases for this function were passed
            outfile.write('\tscore: {}/{}\n'.format(func_num_correct, func_test_case_num))
            total_correct += func_num_correct
            total_tests += func_test_case_num

        # write to overall results file
        results.write('{}/{}\n'.format(total_correct, total_tests))

        # write down total score for this submission
        outfile.write('\n\tTOTAL SCORE: {}/{} PASSED\n'.format(total_correct, total_tests))
        outfile.close()
    results.close()

    # Now test functionality of main TODO: also make this its own fn later and less hardcode
    # harcoded below is keywords to expect in output
    kwrds = ('lines', 'words', 'non', 'o', '', '')
    for asgt in assignment_names:
        out_file = open(join(default['GradesFolder'], '{}.out'.format(asgt)), 'a')
        out_file.write('***MAIN_TESTING***\n')
        for i in range(1,4): # TODO: un-hardcode (1,4 bc 3 test cases)
            out_file.write('test{}:\n'.format(i))
            in_file = open(join(default['SubmissionsFolder'], 'in{}.txt'.format(i)))

            p = sub.Popen(['python3.6', join(default['SubmissionsFolder'], asgt + '.py')], stdin=in_file, stdout=sub.PIPE)
            out, err = p.communicate()
            if err:
                # error thrown while running
                out_file.write('Threw error: {}'.format(err))
            else:
                # convert out from byte stream to string
                out_str = out.decode('utf-8')
                out_lines = out_str.split()

                # open answers key
                ans_file = open(join(default['SubmissionsFolder'], 'out{}.txt'.format(i)))
                lines = map(str.strip, ans_file.readlines())
                look_for = map(lambda x: ' '.join(x).strip(), list(zip(lines, kwrds)))

                for look in look_for:
                    kwrd = look.split()[-1]
                    out_file.write('\t{} - '.format(look))
                    if look in out_str:
                        out_file.write('PASSED\n')
                    else:
                        out_file.write('FAILED; Had: ')
                        for out_line in out_lines:
                            if out_line.find(kwrd) != -1:
                                out_file.write(out_line + '\n')
                        out_file.write('\n')
                ans_file.close()
                        


            in_file.close()
        out_file.close()


if __name__=='__main__':
    main()
