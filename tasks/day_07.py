#!/usr/bin/env python3
import itertools
import os
import re
import sys
import time
from threading import Thread
from typing import Optional

import more_itertools as mit

# GLOBALS
input_data = []
prev_time = time.process_time()
input_timeout = 5

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
    global input_data

    # print("reading input... START")

    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] {line}")

        val = line.strip()
        # if len(val) > 0:
        val = list(mit.flatten([elem.strip().split(" ") for elem in val.split(":")]))
        input_data.append(val)

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def __compute(operation_sequence: tuple, operands: list[int]) -> int:
    assert len(operation_sequence) == len(operands) - 1, "Number of operands must be one more than number of operators"

    result = operands[0]
    for op, operand in zip(operation_sequence, operands[1:]):
        if op == '+':
            result += operand
        elif op == '*':
            result *= operand
        elif op == "||":
            result = int(str(result) + str(operand))
        else:
            assert False, "Unknown operator"

    return result


def __has_solution(operands: list[int], desired_result: int, possible_operators: list[str]) -> bool:
    # First create the list of all possible operators sequence/combinations for the number of given operands
    operation_sequences = list(itertools.product(possible_operators, repeat=len(operands) - 1))
    # Use my_li2 = ["+", "*", "||"]
    # list(product(my_li2, repeat=2))
    # [('+', '+'), ('+', '*'), ('+', '||'), ('*', '+'), ('*', '*'), ('*', '||'), ('||', '+'), ('||', '*'), ('||', '||')]

    # Example case:
    # operands: [81, 40, 27] ; desired_result: 3267
    # [('+', '+'), ('+', '*'), ('*', '+'), ('*', '*')]

    nr_solutions = 0
    for operation_sequence in operation_sequences:
        answer = __compute(operation_sequence, operands)
        if answer == desired_result:
            nr_solutions += 1
            # quick break (at first solution found) - comment for debugging...
            break
            # print(f"Equation {desired_result} = {operands} ({operation_sequence}), HAVE a solution (#{nr_solutions})")

    return nr_solutions > 0

def solve_equations(possible_operators):
    solvable_equations_results = []
    for equation in input_data:
        desired_result = int(equation[0])
        operands = list(map(int, equation[1:]))
        # print(f"operands: {operands} - desired_result: {desired_result}")
        if __has_solution(operands, desired_result, possible_operators):
            solvable_equations_results.append(desired_result)

    return solvable_equations_results

def find_solution_a():
    """
    Determine which equations could possibly be true. What is their total calibration result?
    """
    possible_operators = ['+', '*']
    equations_results = solve_equations(possible_operators)

    result = sum(equations_results)

    return result

def find_solution_b():
    """
    sing your new knowledge of elephant hiding spots, determine which equations could possibly be true.
    What is their total calibration result?
    """
    possible_operators = ['+', '*', "||"]
    equations_results = solve_equations(possible_operators)

    result = sum(equations_results)

    return result


# MAIN
def do_main():
    show_elapsed_time()

    # print("read input")
    controlled_input_read()

    show_elapsed_time()
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
