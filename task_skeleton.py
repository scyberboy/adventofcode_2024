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
    <Description goes here>
    """
    result = "DUMMY(a)"

    return result


def find_solution_b():
    """
    <Description goes here>
    """
    result = "DUMMY(b)"

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
