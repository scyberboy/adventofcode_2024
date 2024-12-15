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
def find_counts(input_data: list[str], inp_str = "XMAS", reverse: bool = False) -> int:
    str_to_find = inp_str if not reverse else inp_str[::-1]
    pattern = re.compile(str_to_find)
    result = sum([len(re.findall(pattern, line)) for line in input_data])
    return result


def transpond_to_vertical(input_data: list[str]) -> list[str]:
    """We assume all rows have equal length (respectively columns)"""
    transformed_data = ["".join([line[i] for line in input_data]) for i in range(len(input_data[0]))]
    return transformed_data


def transpond_to_diagonal(input_data: list[str], reverse: bool = False, min_line_len: int = 4) -> tuple[list[str], list[list[tuple[int, int]]]]:
    """The straight diagonal will be top left to bottom right, and the reverse diagonal will be bottom left to top right."""
    # Sample input data:
    # MMMSXX
    # MSAMXM
    # AMXSXM
    # MSAMAS
    # XMASAM
    # SMAXAA

    # The shortest new line length should be 4 (as the length of XMAS|SAMX)
    # We assume all rows in original input_data have equal length (respectively columns)
    transformed_data = []

    original_data_indexes: list[list[tuple[int, int]]] = []

    if not reverse: # top left to bottom right
        # first, the main diagonal and all "upper" parts
        # print("main + 'upper'")
        for i in range(0, len(input_data[0]) - min_line_len + 1):
            transformed_data.append("".join([input_data[j][i + j] for j in range(0, len(input_data) - i)]))
            indexes = [(j, i + j) for j in range(0, len(input_data) - i)]
            original_data_indexes.append(indexes)

        # print(f"transformed_data: {transformed_data}")
        limit = len(transformed_data)

        # second, all "lower" parts
        # print("lower")
        for i in range(0, len(input_data[0]) - min_line_len):
            # print(f"i: {i}")
            # print(f"j: {range(i + 1, len(input_data))}")
            elems = [input_data[j][j - i - 1] for j in range(i + 1, len(input_data))]
            # print(f"elems: {elems}")
            elem = "".join(elems)
            # print(f"\telem: {elem}")
            transformed_data.append(elem)
            indexes = [(j, j - i - 1) for j in range(i + 1, len(input_data))]
            original_data_indexes.append(indexes)

    else: # bottom left to top right
        # first, the main diagonal and all "lower" parts
        # print("REVERSE: main + 'lower'")
        for i in range(0, len(input_data[0]) - min_line_len + 1):
            transformed_data.append("".join([input_data[j][i + len(input_data) - 1 - j] for j in range(len(input_data) - 1, i - 1, -1)]))
            indexes = [(j, i + len(input_data) - 1 - j) for j in range(len(input_data) - 1, i - 1, -1)]
            original_data_indexes.append(indexes)

        # print(f"transformed_data: {transformed_data}")
        limit = len(transformed_data)

        # second, all "upper" parts
        # print("REVERSE: upper")
        for i in range(0, len(input_data[0]) - min_line_len):
            # print(f"i: {i}")
            # print(f"j: {range(i + 1, len(input_data))}")
            elems = [input_data[j][len(input_data) - 2 - j - i] for j in range(len(input_data) - i - 2, -1, -1)]
            # print(f"elems: {elems}")
            elem = "".join(elems)
            # print(f"\telem: {elem}")
            transformed_data.append(elem)
            indexes = [(j, len(input_data) - 2 - j - i) for j in range(len(input_data) - i - 2, -1, -1)]
            original_data_indexes.append(indexes)

    # print(f"transformed_data: {transformed_data[limit:]}")

    return transformed_data, original_data_indexes


def find_solution_a():
    """
    This word search allows words to be horizontal, vertical, diagonal, written backwards, or even overlapping other words.
    It's a little unusual, though, as you don't merely need to find one instance of XMAS - you need to find all of them.
    """
    # For example:
    #
    # MMMSXXMASM
    # MSAMXMSMSA
    # AMXSXMAAMM
    # MSAMASMSMX
    # XMASAMXAMM
    # XXAMMXXAMA
    # SMSMSASXSS
    # SAXAMASAAA
    # MAMMMXMMMM
    # MXMXAXMASX
    # In this word search, XMAS occurs a total of 18 times;

    # Horizontals
    # 1. Left to right is easy - simple re.findall()
    # 2. Backwards almost as easy - re.findall() with reversed string
    # Verticals
    # 1. Top to bottom - re.findall(), but on some clever constructed column based string
    # 2. Bottom to top - re.findall(), but on some clever constructed column based reversed string
    # Diagonals
    # 1. Top left to bottom right - re.findall(), but on some clever constructed diagonal string
    # 2. Top right to bottom left - re.findall(), but on some clever constructed diagonal reversed string
    # 3. Bottom left to top right - re.findall(), but on some clever constructed diagonal string
    # 4. Bottom right to top left - re.findall(), but on some clever constructed diagonal reversed string

    # Or alternatively, in normal case we can search for "XMAS", but on reverse cases we can search for "SAMX"
    # This way we'll only need 4 inputs - horizontal, vertical, and 2 diagonals

    # Indeed, we should respect the bounds of a line, column, diagonal, etc.
    horizontal_counts_lr = find_counts(input_data, reverse=False)
    horizontal_counts_rl = find_counts(input_data, reverse=True)

    # DEBUG
    # print(f"input_data:\n\t{"\n\t".join(input_data)}")
    # print(f"vertical input_data:\n\t{"\n\t".join(transpond_to_vertical(input_data))}")
    # return "blah"

    vertical_count_tb = find_counts(transpond_to_vertical(input_data), reverse=False)
    vertical_count_bt = find_counts(transpond_to_vertical(input_data), reverse=True)


    diagonal_count_tl_br = find_counts(transpond_to_diagonal(input_data, reverse=False)[0], reverse=False)

    # DEBUG
    # print(f"1st diagonal input_data:\n\t{"\n\t".join(transpond_to_diagonal(input_data, reverse=False))}")
    # return "shi"

    diagonal_count_br_tl = find_counts(transpond_to_diagonal(input_data, reverse=False)[0], reverse=True)
    diagonal_count_bl_tr = find_counts(transpond_to_diagonal(input_data, reverse=True)[0], reverse=False)

    # DEBUG
    # print(f"2nd diagonal input_data:\n\t{"\n\t".join(transpond_to_diagonal(input_data, reverse=True))}")
    # return "cra"

    diagonal_count_tr_bl = find_counts(transpond_to_diagonal(input_data, reverse=True)[0], reverse=True)


    result = horizontal_counts_lr + horizontal_counts_rl + vertical_count_tb + vertical_count_bt + diagonal_count_tl_br + diagonal_count_br_tl + diagonal_count_tr_bl + diagonal_count_bl_tr

    return result


def find_indexes_of_a_in_mas_and_sam(tl_br_diagonal_data: list[str], tl_br_original_data_indexes: list[list[tuple[int, int]]]) -> list[tuple[int, int]]:
    strings_to_find = ["MAS", "SAM"]
    indexes_of_a_in_mas_and_sam = []

    try:
        for string_to_find in strings_to_find:
            # print(f"Looking for {string_to_find}")
            for line_index, line in enumerate(tl_br_diagonal_data):
                # print(f"processing [{line_index}]: {line}")
                if string_to_find in line:
                    cur_index = -1
                    while ( cur_index := line.find(string_to_find, cur_index + 1) ) != -1:
                        # print(f"cur_index: {cur_index}")
                        indexes_of_a_in_mas_and_sam.append(tl_br_original_data_indexes[line_index][cur_index + 1])
                        # print(f" len: {len(indexes_of_a_in_mas_and_sam)}, indexes_of_a_in_mas_and_sam: {indexes_of_a_in_mas_and_sam}")
    except ValueError:
        pass

    return indexes_of_a_in_mas_and_sam


def find_solution_b():
    """
    Looking for the instructions, you flip over the word search to find that this isn't actually an XMAS puzzle; it's an X-MAS puzzle in which you're supposed to find two MAS in the shape of an X. One way to achieve that is like this:

    M.S
    .A.
    M.S

    Irrelevant characters have again been replaced with . in the above diagram.
    Within the X, each MAS can be written forwards or backwards.
    """

    # DEBUG
    # print(f"input_data:\n\t{"\n\t".join(input_data)}")

    # We need only diagonals here then...
    tl_br_diagonal_data, tl_br_original_data_indexes = transpond_to_diagonal(input_data, reverse=False, min_line_len=3)
    # print(f"tl_br_diagonal_data:\n\t{"\n\t".join(tl_br_diagonal_data)}")
    # print(f"tl_br_original_data_indexes: {tl_br_original_data_indexes}")

    indexes_of_a_in_mas_and_sam_for_tl_br = find_indexes_of_a_in_mas_and_sam(tl_br_diagonal_data, tl_br_original_data_indexes)
    # print(f"indexes_of_a_in_mas_and_sam_for_tl_br: {indexes_of_a_in_mas_and_sam_for_tl_br}")

    bl_tr_diagonal_data, bl_tr_original_data_indexes = transpond_to_diagonal(input_data, reverse=True, min_line_len=3)
    # print(f"bl_tr_diagonal_data:\n\t{"\n\t".join(bl_tr_diagonal_data)}")
    # print(f"bl_tr_original_data_indexes: {bl_tr_original_data_indexes}")

    indexes_of_a_in_mas_and_sam_for_bl_tr = find_indexes_of_a_in_mas_and_sam(bl_tr_diagonal_data, bl_tr_original_data_indexes)
    # print(f"indexes_of_a_in_mas_and_sam_for_bl_tr: {indexes_of_a_in_mas_and_sam_for_bl_tr}")

    # Now find the intersections :)
    common_indexes = set(indexes_of_a_in_mas_and_sam_for_tl_br) & set(indexes_of_a_in_mas_and_sam_for_bl_tr)
    # print(f"common elems: {common_indexes}")

    result = len(common_indexes)

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
