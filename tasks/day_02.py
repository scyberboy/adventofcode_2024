#!/usr/bin/env python3
import os
import re
import sys
import time
from collections import Counter
from threading import Thread
from typing import Optional

# GLOBALS
input_data = []
prev_time = time.process_time()
input_timeout = 50


# Day 02 specific globals
# for debug purposes (when want to run with PyCharm Debugger):
# sys.stdin = open('../stp_cut.txt', 'r')

# global exec
filename = os.path.basename(__file__)
day_token = re.search(r"\d+", filename)
day_nr = day_token.group() if day_token else "unknown"
print(f"day_nr: {day_nr}")


# MISC

def show_elapsed_time(operation: Optional[str] = None):
    global prev_time
    cur_time = time.process_time()
    diff = cur_time - prev_time
    prev_time = cur_time
    print(" ".join(elem for elem in [f"[{cur_time}]", operation, f"took: {diff:.7f} sec."] if elem))


# READ INPUT
def read_input():
    """
    The unusual data (your puzzle input) consists of many reports, one report per line. Each report is a list of numbers called levels that are separated by spaces. For example:

    7 6 4 2 1
    1 2 7 8 9
    9 7 6 2 1
    1 3 2 4 5
    8 6 4 4 1
    1 3 6 7 9
    This example data contains six reports each containing five levels.
    """
    global input_data

    # print("reading input... START")

    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] '{line}'")

        str_line_list = line.strip().split()
        int_line_list = [int(elem) for elem in str_line_list]
        if len(int_line_list) > 0:
            input_data.append(int_line_list)

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def is_safe(report: list[int]) -> bool:
    """
    So, a report only counts as safe if both of the following are true:
        - The levels are either all increasing or all decreasing.
        - Any two adjacent levels differ by at least one and at most three.
    """
    previous_elem = report[0]
    # direction = 0: neutral, -1: decrease, 1: increase
    desired_direction = 0
    for next_elem in report[1:]:
        diff = next_elem - previous_elem
        if diff == 0 or abs(diff) > 3:
            return False

        if desired_direction == 0:
            desired_direction = diff/abs(diff)
        elif desired_direction != diff/abs(diff):
            return False

        previous_elem = next_elem

    return True


def find_solution_a():
    """
    The engineers are trying to figure out which reports are safe. The Red-Nosed reactor safety systems can only
     tolerate levels that are either gradually increasing or gradually decreasing.
     So, a report only counts as safe if both of the following are true:
        - The levels are either all increasing or all decreasing.
        - Any two adjacent levels differ by at least one and at most three.

    Analyze the unusual data from the engineers. How many reports are safe?
    """
    global input_data

    result = 0
    for report in input_data:
        if is_safe(report):
            result += 1
            # print(f"report: {report} IS SAFE")
        else:
            pass
            # print(f"report: {report} NOT SAFE")

    return result


def is_safe_with_dampener(report: list[int]) -> bool:
    # We need to check all variations of the list with length-1
    # If at least one is safe - consider the original one is safe as well!

    # print(f"Original report: {report}")
    for i in range(0, len(report)):
        local_result = is_safe(report[:i] + report[i + 1:])

        if local_result:
            # print(f"\t Sub-report: {report[:i] + report[i + 1:]} IS SAFE")
            return True
        else:
            # print(f"\t Sub-report: {report[:i] + report[i + 1:]} NOT SAFE")
            pass

    return False

def find_solution_b():
    """
    The engineers are trying to figure out which reports are safe. The Red-Nosed reactor safety systems can only
     tolerate levels that are either gradually increasing or gradually decreasing.
     So, a report only counts as safe if both of the following are true:
        - The levels are either all increasing or all decreasing.
        - Any two adjacent levels differ by at least one and at most three.

    The Problem Dampener is a reactor-mounted module that lets the reactor safety systems tolerate a single bad level
    in what would otherwise be a safe report. It's like the bad level never happened!

    Analyze the unusual data from the engineers. How many reports are safe?
    """
    global input_data

    result = 0
    for report in input_data:
        if is_safe(report):
            result += 1
            # print(f"report: {report} IS SAFE")
        elif is_safe_with_dampener(report):
            result += 1
            # print(f"report: {report} IS SAFE WITH DAMPENER")
        else:
            pass
            # print(f"report: {report} NOT SAFE")

    return result


# MAIN
def do_main():
    show_elapsed_time("Initialization")

    # print("read input")
    controlled_input_read()
    # show_elapsed_time()

    # print("len input_data:", len(input_data))
    # print("input_data", input_data)

    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
