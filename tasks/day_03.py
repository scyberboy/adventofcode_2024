#!/usr/bin/env python3

import os
import re
import sys
import time
from threading import Thread
from typing import Optional

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

        # val = line.strip()
        # if len(val) > 0:
        input_data.append(line.strip())

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def find_solution_a():
    """
    Scan the corrupted memory for uncorrupted mul instructions. What do you get if you add up all the results of the multiplications?
    """
    global input_data

    # It does that with instructions like mul(X,Y), where X and Y are each 1-3 digit numbers.
    mul_pattern = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
    # print(f"re.findall(mul_pattern, input_data): {re.findall(mul_pattern, input_data[0])}")
    all_mulls = [mull for line in input_data for mull in re.findall(mul_pattern, line)]
    # print(f"all_mulls: {all_mulls}")
    total_sum = 0
    for mull in all_mulls:
        total_sum += int(mull[0]) * int(mull[1])
    # print(f"total_sum: {total_sum}")

    result = total_sum

    return result


def find_solution_b():
    """
    There are two new instructions you'll need to handle:

    The do() instruction enables future mul instructions.
    The don't() instruction disables future mul instructions.
    Only the most recent do() or don't() instruction applies. At the beginning of the program, mul instructions are enabled.
    """
    global input_data

    # It does that with instructions like mul(X,Y), where X and Y are each 1-3 digit numbers.
    mul_pattern = re.compile(r"mul\((\d{1,3}),(\d{1,3})\)")
    # print(f"re.findall(mul_pattern, input_data): {re.findall(mul_pattern, input_data[0])}")
    split_pattern = re.compile(r"don't\(\).*?do\(\)")
    # Use the split pattern to effectively trim the data between don't() and do()
    altered_data = split_pattern.split("".join(input_data))
    all_mulls = [mull for line in altered_data for mull in mul_pattern.findall(line)]
    # print(f"all_mulls: {all_mulls}")
    total_sum = 0
    for mull in all_mulls:
        total_sum += int(mull[0]) * int(mull[1])
    # print(f"total_sum: {total_sum}")

    result = total_sum

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
