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


# Day 05 specific
rules_list_raw: list[str] = [] # will hold raw input in form of "X|Y"
rules_list_ordered: list[int] = [] # will hold the constructed ordered list of rules
incorrect_updates: list[list[int]] = []

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
        if len(val) > 0:
            if "|" in line:
                rules_list_raw.append(val)
            else:
                input_data.append([int(elem) for elem in val.split(",")])

    # print("reading input... END")


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def __get_middle_elem(input_list: list[int]):
    return input_list[len(input_list) // 2]


def __check_list_in_order(input_list: list[int]) -> bool:
    global rules_list_ordered

    input_list_indexes_in_ordered_rules = []
    for elem in input_list:
        input_list_indexes_in_ordered_rules.append(rules_list_ordered.index(elem))

    # If sorted list of indexes is same as initial one - all good
    sorted_indexes_list = sorted(input_list_indexes_in_ordered_rules)
    # print(f"\tChecking: {input_list}")
    # print(f"\tInput list indexes: {input_list_indexes_in_ordered_rules}")
    # print(f"\tSorted indexes: {sorted_indexes_list}")

    result = sorted_indexes_list == input_list_indexes_in_ordered_rules
    # print(f"\tReturning: {result}")

    return result


def __is_update_correct(input_list):
    is_there_broken_rule = False
    for first, second in zip(input_list, input_list[1:]):
        str_to_check = f"{first}|{second}"
        if str_to_check not in rules_list_raw:
            is_there_broken_rule = True
            # print(f"DEBUG: breaking rule: {str_to_check}")
            break

    return not is_there_broken_rule


def find_solution_a():
    """
    What do you get if you add up the middle page number from those correctly-ordered updates?
    """
    global incorrect_updates

    # K, I got the rules, I got the data
    # Let's check if the lists are correct according to the rules...

    middle_elems_list = []

    for input_list in input_data:
    #     if __check_list_in_order(input_list):
    #         middle_elems_list.append(__get_middle_elem(input_list))
    #         # print(f"GUT -> {input_list}")
    #     # else:
    #     #     print(f"BAD -> {input_list}")

    # New approach - compare each pair N|N+1 with the set of raw rules, if there's a rule for this pair - we're good.
    # If all pairs are good - pronounce the update as GOOD.
        if __is_update_correct(input_list):
            middle_elems_list.append(__get_middle_elem(input_list))
        else:
            # Keep the incorrect updates for part 'b'
            incorrect_updates.append(input_list)

    result = sum(middle_elems_list)

    return result


def __check_and_swap_last_pair_if_need(fixed_update):
    """Return True if the object have been altered"""
    if len(fixed_update) < 2:
        return False

    first, second = fixed_update[-2:]
    str_to_check = f"{first}|{second}"
    if str_to_check in rules_list_raw:
        return False
    else:
        rev_str_to_check = f"{second}|{first}"
        if rev_str_to_check in rules_list_raw:
            fixed_update[-2] = second
            fixed_update[-1] = first
            return True
        else:
            raise Exception("Triple fok")


def find_solution_b():
    """
    Find the updates which are not in the correct order.
    What do you get if you add up the middle page numbers after correctly ordering just those updates?
    """
    fixed_updates = []

    for incorrect_update in incorrect_updates:
        # print(f"Incor update: {incorrect_update}")

        fixed_update = []
        custom_next_pair = False
        prev_first = None
        # Check each pair N|N+1, if it's bad (no rule for it) - try the reverse order N+1|N, if there's such rule - keep the swapped
        for first, second in zip(incorrect_update, incorrect_update[1:]):
            # K, should do it in place somehow...
            if custom_next_pair:
                custom_next_pair = False
                first = prev_first

            str_to_check = f"{first}|{second}"
            if str_to_check in rules_list_raw:
                fixed_update.append(first)
            else:
                rev_str_to_check = f"{second}|{first}"
                if rev_str_to_check in rules_list_raw:
                    fixed_update.append(second)
                    prev_first = first
                    custom_next_pair = True
                else:
                    raise Exception("Fok")

            # print(f"\t ... update: {fixed_update}")
            # but newly constructed last pair may be incorrect - check and alter if needed
            if __check_and_swap_last_pair_if_need(fixed_update):
                # print(f"\t altered update: {fixed_update}")
                pass

        if not custom_next_pair:
            fixed_update.append(second)
        else:
            fixed_update.append(first)

        # print(f"FIXED update: {fixed_update}")
        if __is_update_correct(fixed_update):
            fixed_updates.append(fixed_update)
        else:
            # print(f"Still incorrect: {incorrect_update} -> {fixed_update}")
            # raise Exception("Double Fok")

            # Indeed, we shall give it next chance - put it in the end of the list :D
            # Doing something like semi-recursion...
            incorrect_updates.append(fixed_update)

    middle_elems_list = [__get_middle_elem(update) for update in fixed_updates]

    result = sum(middle_elems_list)

    return result


def __local_debug_conditional(message: str, condition: bool):
    if condition:
        print(message)


def __construct_ordered_rules_list():
    global rules_list_raw, rules_list_ordered

    # Example data:
    # 47|53
    # 97|13
    # 97|61
    # 97|47
    # 75|29
    # 61|13
    # 75|53

    _local_debug_cond_var = False

    for elem in rules_list_raw:
        # _local_debug_cond_var = 9 <= len(rules_list_ordered) <= 12
        # _local_debug_cond_var = (len(rules_list_ordered) < 15)
        _local_debug_cond_var = False

        __local_debug_conditional(f"----------- {elem} ---------------", _local_debug_cond_var)
        __local_debug_conditional(f"... rules_list_ordered: {rules_list_ordered}", _local_debug_cond_var)
        first, second = map(int, elem.split("|"))
        idx_first = rules_list_ordered.index(first) if rules_list_ordered.count(first) else None
        idx_second = rules_list_ordered.index(second) if rules_list_ordered.count(second) else None

        __local_debug_conditional(f"first: {first}({idx_first}) second: {second}({idx_second})", _local_debug_cond_var)

        # Case 1 (both are nonexistent)
        if idx_first is None and idx_second is None:
            rules_list_ordered.append(first)
            rules_list_ordered.append(second)
            __local_debug_conditional(f"Case1", _local_debug_cond_var)
        # Case 2 (first is not, second is present -> add first just before second)
        elif idx_first is None and idx_second is not None:
            rules_list_ordered.insert(idx_second, first)
            __local_debug_conditional(f"Case2", _local_debug_cond_var)
        # Case 3 (first is present, second is not -> add second just after first)
        elif idx_first is not None and idx_second is None:
            rules_list_ordered.insert(idx_first + 1, second)
            __local_debug_conditional(f"Case3", _local_debug_cond_var)
        # Case 4 (both are present) - check correctness and re-arrange if needed
        else:
            if not idx_first < idx_second:
                # 1st approach, use the dumbest strategy - swap
                # rules_list_ordered[idx_second] = first
                # rules_list_ordered[idx_first] = second
                __local_debug_conditional(f"Case4a", True)

                # Naah, this naive way doesn't work ;(
                # Should deal with it smarter - respect the already present stuff...
                # But how?!?

                # 2nd approach - put the first, just in front of the second
                rules_list_ordered.remove(first)
                rules_list_ordered.insert(idx_second, first)
            else:
                __local_debug_conditional(f"Case4b", _local_debug_cond_var)

        # __local_debug_conditional(f"Resulting rules_list_ordered: {rules_list_ordered}", _local_debug_cond_var)

    __local_debug_conditional("-----------------------------", _local_debug_cond_var)
    # Now the global rules_list_ordered should be set properly ;)

# MAIN
def do_main():
    show_elapsed_time()

    # print("read input")
    controlled_input_read()

    show_elapsed_time()
    # print(f"input_data [{len(input_data)}]: {input_data}")
    #
    # print(f"rules_list_raw [{len(rules_list_raw)}]: {rules_list_raw}")

    # Construct the ordered rules list...
    # __construct_ordered_rules_list()
    # print(f"rules_list_ordered [{len(rules_list_ordered)}]: {rules_list_ordered}")

    # Hm... why not parsing the rules until the result is stable?!?
    # cnt = 0
    # while True:
    #     cnt += 1
    #     prev_rules_list = rules_list_ordered.copy()
    #     __construct_ordered_rules_list()
    #     print(f"{cnt} time, rules_list_ordered [{len(rules_list_ordered)}]: {rules_list_ordered}")
    #
    #     if prev_rules_list == rules_list_ordered or cnt > 5:
    #         break

    # K, new approach - use the raw rules list...


    result_a = find_solution_a()
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b()
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
