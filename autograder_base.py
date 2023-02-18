import pandas as pd
import numpy as np
import filecmp
import os
import platform
import re
import termcolor


"""
* 
* Autograder Base
* Contains common functions across all autograding scripts to be called
* Functions:
*       - gen_filenames()
*       - grade_problem()
*       - autograde()
*
"""


# To get debug messages
DEBUG = True

# Colors for console printing,
W = '\033[0m'   # white (normal)
R = '\033[31m'  # red
O = '\033[33m'  # orange
Y = '\033[93m'  # yellow
G = '\033[32m'  # green

# -----------------------------------------
# generate file names from a given template
# FORMAT LIKE THIS: "test_{index}.txt"
def gen_filenames(template, n):
    filenames = []
    for i in range(1, n + 1):
        filename = template.format(index=i)
        filenames.append(filename)
    return filenames

# -----------------------------------------------------------------
# this will take a problem, run the student code, then compare with
#   expected output. it will return the points earned
def grade_problem(student_dir, t_output, t_res, commands, exact):
    # how many tests to run
    n = len(commands)

    # array of scores to return
    scores = []
    for i in range(n):
        scores.append(0)

    # array of times to return
    times = []
    for i in range(n):
        times.append(-1)

    # try to make and run the code
    try:
        # alert what directory doesn't have a makefile (dont copy it)
        if not os.path.isfile(os.path.join(student_dir, "Makefile")):
            print(f"\n{R}ERROR: Missing Makefile when trying to test in {student_dir}! {W}")
            print(f"{R}       Skipping testing for {commands[0][0]}...{W}")
            return [scores, times]

        # run makefile
        command = f"(cd {student_dir} && make)"
        err = os.system(command)
        if err != 0:
            print(f"{R}Error making the program {commands[0][0]}{W}")
            return [scores, times]

        # run and analyze the problem
        for i in range(0, n):

            print(f"{G}Testing for {commands[i][0]}'s output: {t_res[i]}{W}")

            # generate the command and run the program
            #   ex. ./Problem_1/parallel_mult_mat_mat in.csv 10 10 ...
            command = f"(cd {student_dir} && ./{str(commands[i][0])}"
            if platform.system() == "Windows":
                command = command.replace('/', '\\')
            for j in range(1, len(commands[0]) - 1):
                command = f"{command} {str(commands[i][j])}"
            command = f"{command} {str(commands[i][-1])})"
            print(command)
            err = os.system(command)

            # skip over if cant run the program...
            if err != 0:
                print(f"{R}\nError running the program {commands[i][0]}{W}")
                continue

            # get data from csv result and expected outputs
            try:
                result = np.genfromtxt(os.path.join(student_dir, t_res[i]), delimiter=",", dtype=float, encoding='ISO-8859-1')
            except Exception as err:
                print(f"{R}Error finding program's output file: {os.path.join(student_dir, t_res[i])}")
                print(f"{O}{err}{W}")
                continue

            try:
                expected = np.genfromtxt(t_output[i], delimiter=",", dtype=float, encoding='ISO-8859-1')
            except Exception as err:
                print(f"{R}Error finding the expected output file: ")
                print(f"{O}{err}{W}")
                continue

            # compare file dims
            matches = False
            if False:
                print(f"{R}Output file {t_output[i]}'s dimensions are different from expected result's!{W}")
                continue

            # compare the files by simply looking at the text
            elif exact:
                if DEBUG:
                    print(f"{O}Testing exact values...{W}")
                matches = filecmp.cmp(
                    t_output[i],
                    os.path.join(student_dir, t_res[i]),
                    shallow=False
                )

            # compare by considering value-errors
            else:
                if DEBUG:
                    print(f"{O}Testing approximate values...{W}")
                diff = np.sum(np.absolute(expected - result))
                diff = diff / np.ravel(expected).shape[0]
                print(f"{R}DIFF: {diff}{W}")
                if diff < 0.1:
                    matches = True

            if not matches:
                print(f"{R}TRY AGAIN{W}")
                # if there is an error running the command,
                #   try placing the num_threads at the end
                command = f"(cd {student_dir} && ./{commands[i][0]}"
                if platform.system() == "Windows":
                    command = command.replace('/', '\\')
                for j in range(1, len(commands[0]) - 3):
                    command = f"{command} {commands[i][j]}"
                command = f"{command} {commands[i][-2]}"
                command = f"{command} {commands[i][-1]}"
                command = f"{command} {commands[i][-3]})"
                err = os.system(command)

                # skip over if cant run the program...
                if err != 0:
                    print(f"{R}Error running the program {commands[i][0]}{W}")
                    continue

                # get data from csv result and expected outputs
                try:
                    result = np.genfromtxt(os.path.join(student_dir, t_res[i]), delimiter=",", dtype=float, encoding='ISO-8859-1')
                except Exception as err:
                    print(f"{R}Error finding program's output file: {os.path.join(student_dir, t_res[i])}")
                    print(f"{O}{err}{W}")
                    continue

                try:
                    expected = np.genfromtxt(t_output[i], delimiter=",", dtype=float, encoding='ISO-8859-1')
                except Exception as err:
                    print(f"{R}Error finding the expected output file: {t_output[i]}")
                    print(f"{O}{err}{W}")
                    continue

                # compare file dims
                matches = False
                if False: #expected.shape != result.shape:
                    print(f"{R}Output file {t_output[i]}'s dimensions are different from expected result's!{W}")
                    continue


                # compare the files by simply looking at the text
                elif exact:
                    if DEBUG:
                        print(f"{O}Testing exact values...{W}")
                    matches = filecmp.cmp(
                        t_output[i],
                        os.path.join(student_dir, t_res[i]),
                        shallow=False
                    )

                # compare by considering value-errors
                else:
                    if DEBUG:
                        print(f"{O}Testing approximate values...{W}")
                    diff = np.sum(np.absolute(expected - result))
                    diff = diff / np.ravel(expected).shape[0]
                    print(f"{R}DIFF: {diff}{W}")
                    if diff < 0.1:
                        matches = True


            # give final score
            if matches:
                scores[i] = 1
            else:
                if DEBUG:
                    print(f"{R}The expected output: {t_output[i]} does not match the result!{W}")

            try:
                t = np.genfromtxt(os.path.join(student_dir, commands[i][-1]), delimiter=',')
            except Exception as err:
                print(f"{R}Error finding program's time file: {commands[i][-1]}{W}")
                continue
            times[i] = t

            if DEBUG:
                print(f"{Y}    Test result {i} = {scores[i]}")
                print(f"{Y}    Time result {i} = {times[i]}s\n{W}")

    # catch the weird stuff
    except Exception as err:
        print(f"\n{R}Unexpected error!")
        print(f"{Y}{err}{W}")

    return [scores, times]


# ------------------------------------------
# this will autograde one project submission
def autograde(in_this_dir, in_test_dir, test_names, in_student_name, grade_func):
    # for mass grading purposes, ignore if individually grading
    #   getting the abs path resolves some issues...
    this_dir = os.path.abspath(in_this_dir)
    test_dir = os.path.abspath(in_test_dir)
    student_name = in_student_name

    # Print the test dir and project dir
    if DEBUG:
        print(f"{G} --> Test dir: {test_dir} {W}")
        print(f"{G} --> Project dir: {this_dir} {W}")

    # student grade
    grade = pd.DataFrame(
        np.nan,
        index=[student_name],
        columns=[i for i in test_names]
    )

    # student timing
    time = pd.DataFrame(
        np.nan,
        index=[student_name],
        columns=[i for i in test_names]
    )

    # Perform the function defined by the individual problem
    res = grade_func()
