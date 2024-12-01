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
input_timeout = 5


# Day 01 specific globals
left_list = list()
right_list = list()


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
    global input_data

    # print("reading input... START")

    cnt = 0
    for line in sys.stdin:
        cnt += 1
        # print(f"[{cnt}] '{line}'")

        val = line.strip().split()
        if len(val) > 0:
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
def find_solution_a():
    """
    Pair up the smallest number in the left list with the smallest number in the right list,
     then the second-smallest left number with the second-smallest right number, and so on.
    To find the total distance between the left list and the right list, add up the distances between all the pairs you found.
    What is the total distance between your lists?
    """
    global input_data, left_list, right_list

    # split the columns to two lists
    for elem in input_data:
        left_elem, right_elem = elem
        # print(f"{left_elem}, {right_elem}")

        left_list.append(int(left_elem))
        right_list.append(int(right_elem))

    # Now sort them
    left_list.sort()
    right_list.sort()

    # Now, zip them again to find the distance between each pair
    total_distance = 0
    for left_elem, right_elem in zip(left_list, right_list):
        distance = abs(left_elem - right_elem)
        total_distance += distance

    result = total_distance

    return result


def find_solution_b():
    """
    Calculate a total similarity score by adding up each number in the left list after multiplying it by the number of
     times that number appears in the right list.
    What is the similarity score?
    """
    global left_list, right_list

    left_counter = Counter(left_list)

    similarity_score = 0
    for value, count in left_counter.items():
        similarity_score += count * value * right_list.count(value)

    result = similarity_score

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
