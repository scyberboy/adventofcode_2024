#!/usr/bin/env python3
from enum import Enum

import numpy as np
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


# Day 06 specific

class FieldType(Enum):
    EMPTY = "."
    OBSTACLE = "#"
    GUARD_UP = "^"
    GUARD_DOWN = "v"
    GUARD_LEFT = "<"
    GUARD_RIGHT = ">"
    GUARD_START = "S"
    VISITED = "X"
    # CROSSING = "+"
    CROSSING_UP_RIGHT = "^>"
    CROSSING_RIGHT_DOWN = ">v"
    CROSSING_DOWN_LEFT = "v<"
    CROSSING_LEFT_UP = "<^"

    ARTIFICIAL_OBSTACLE = "O"
    # U+25DC	◜	e2 97 9c	UPPER LEFT QUADRANT CIRCULAR ARC
    # U+25DD	◝	e2 97 9d	UPPER RIGHT QUADRANT CIRCULAR ARC
    # U+25DE	◞	e2 97 9e	LOWER RIGHT QUADRANT CIRCULAR ARC
    # U+25DF	◟	e2 97 9f	LOWER LEFT QUADRANT CIRCULAR ARC
    # TURN_UL = "\u25DC"
    TURN_UL = b"\xe2\x97\x9c".decode("utf-8")
    # TURN_UR = "\u25DD"
    TURN_UR = b"\xe2\x97\x9d".decode("utf-8")
    # TURN_LR = "\u25DE"
    TURN_LR = b"\xe2\x97\x9e".decode("utf-8")
    # TURN_LL = "\u25DF"
    TURN_LL = b"\xe2\x97\x9f".decode("utf-8")

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

class Field:
    def __init__(self, value: Optional[FieldType] = FieldType.EMPTY):
        self.value = value

    def __str__(self):
        return str(self.value.value)

    def __repr__(self):
        return str(self.value.value)

class Map:
    # The mapped area itself - 2d array of Field objects
    def __init__(self, data: Optional[list[list[Field]]] = None):
        """
        Numpy's array can be traversed using nditer:
            a = np.arange(6).reshape(2,3)
            it = np.nditer(a, flags=['multi_index'])
            for x in it:
                print("%d <%s>" % (x, it.multi_index), end=' ')

            # 0 <(0, 0)> 1 <(0, 1)> 2 <(0, 2)> 3 <(1, 0)> 4 <(1, 1)> 5 <(1, 2)>

        Numpy's ndenumerate can be used as well:
            a = np.array([[1, 2], [3, 4]])
            for index, x in np.ndenumerate(a):
                print(index, x)

            # (0, 0) 1
            # (0, 1) 2
            # (1, 0) 3
            # (1, 1) 4
        """
        self.map: np.array = np.array(data, dtype=Field) if data else np.zeros(0)

    def find_first(self, values: list[FieldType]) -> Optional[tuple]:
        # print(f"Looking for {values}")
        for index, elem in np.ndenumerate(self.map):
            # print(f"\tChecking, index: {index}, elem: {elem}, elem.value: {elem.value}, type: {type(elem)}")
            if elem.value in values:
                return index

        return None

    def find_all(self, values: list[FieldType]) -> list[tuple]:
        return [index for index, elem in np.ndenumerate(self.map) if elem.value in values]


class Room(Map):
    def __init__(self, data: Optional[list[list[Field]]] = None):
        super().__init__(data)
        # other attributes will go here later...
        self.current_position: Optional[tuple[int, int]] = None
        self.guards_path_till_exit: list[tuple[int, int]] = []
        self.possible_artificial_obstacles: list[tuple[int, int]] = []

    def get_current_position(self):
        if self.current_position:
            return self.current_position
        else:
            # Initially, we need to find the starting position...
            starting_position = self.find_first([FieldType.GUARD_UP, FieldType.GUARD_DOWN, FieldType.GUARD_LEFT, FieldType.GUARD_RIGHT])
            if not starting_position:
                raise ValueError("No starting position found!")
            self.current_position = starting_position
            print(f"Starting position: {starting_position}[{self.map[starting_position]}]")
            return starting_position

    def is_valid_position(self, position: tuple[int, int]) -> bool:
        row_index, col_index = position
        if 0 <= row_index < self.map.shape[0] and 0 <= col_index < self.map.shape[1]:
            return True
        else:
            # print(f"Invalid position: {position}, current position: {self.current_position}[{self.map[self.current_position] if self.current_position != position else 'OUT'}]")
            return False

    def move_possible(self, source: tuple[int, int], target: tuple[int, int]):
        if not self.is_valid_position(target):
            return True

        if self.map[target].value not in [FieldType.OBSTACLE, FieldType.ARTIFICIAL_OBSTACLE]:
            # print(f"Move possible from {source} to {target} [{self.map[target].value}]")
            return True

        return False

    def make_step(self):
        """Try to perform a step and return new occupied/current field's coordinates if possible. Else return None
        :returns (next_x, next_y) or None
        """
        curr_idx_row, curr_idx_col = self.get_current_position()
        # print(f"Current element: {self.map[curr_idx_row, curr_idx_col]} ({curr_idx_row}, {curr_idx_col})")

        curr_direction = self.map[curr_idx_row, curr_idx_col].value
        # If a move is not possible (obstacle) try to rotate 90 degrees right and perform it...
        if curr_direction == FieldType.GUARD_UP:
            # try go up
            if self.move_possible((curr_idx_row, curr_idx_col), (curr_idx_row - 1, curr_idx_col)):
                new_idx_row, new_idx_col = (curr_idx_row - 1, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_UP)
            else: # only rotate, don't advance
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_RIGHT)
        elif curr_direction == FieldType.GUARD_RIGHT:
            # try go right
            if self.move_possible((curr_idx_row, curr_idx_col), (curr_idx_row, curr_idx_col + 1)):
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col + 1)
                new_guard_position = Field(FieldType.GUARD_RIGHT)
            else: # only rotate, don't advance
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_DOWN)
        elif curr_direction == FieldType.GUARD_DOWN:
            # try go down
            if self.move_possible((curr_idx_row, curr_idx_col), (curr_idx_row + 1, curr_idx_col)):
                new_idx_row, new_idx_col = (curr_idx_row + 1, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_DOWN)
            else: # only rotate, don't advance
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_LEFT)
        elif curr_direction == FieldType.GUARD_LEFT:
            # try go left
            if self.move_possible((curr_idx_row, curr_idx_col), (curr_idx_row, curr_idx_col - 1)):
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col - 1)
                new_guard_position = Field(FieldType.GUARD_LEFT)
            else: # only rotate, don't advance
                new_idx_row, new_idx_col = (curr_idx_row, curr_idx_col)
                new_guard_position = Field(FieldType.GUARD_UP)
        else:
            raise ValueError(f"Unexpected guard position: {self.map[curr_idx_row, curr_idx_col]}")


        # Check if the new position is valid (is within the map)...
        # If not, return None
        if not self.is_valid_position((new_idx_row, new_idx_col)):
            return None
        # If yes, set the new position
        else:
            self.map[new_idx_row, new_idx_col] = new_guard_position
            self.current_position = (new_idx_row, new_idx_col)

        # if (new_idx_row, new_idx_col) not in self.guards_path_till_exit:
        #     self.guards_path_till_exit.append((new_idx_row, new_idx_col))

        # Keep it unconditional or maybe don't double two consecutive ones...
        # self.guards_path_till_exit.append((new_idx_row, new_idx_col))

        # Yeah, try only not duplicating consecutive ones...
        if (new_idx_row, new_idx_col) not in self.guards_path_till_exit[-1:]:
            self.guards_path_till_exit.append((new_idx_row, new_idx_col))

        return new_idx_row, new_idx_col


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

    # print("reading input...


def controlled_input_read():
    read_input_thread = Thread(target=read_input, daemon=True, )
    read_input_thread.start()
    read_input_thread.join(timeout=input_timeout)
    if read_input_thread.is_alive():
        print(f"Timeout limit ({input_timeout} sec.) reached - exiting")
        sys.exit(1)


# SOLUTIONS
def __simulate_guards_path_till_exit(a_room):
    cnt_dummy_guard = 0
    while new_position_indexes := a_room.make_step():
        cnt_dummy_guard += 1
        # if cnt_dummy_guard > 100:
        #     break

        # Mark the new position as visited and increase the rooms counter...

        # After step
        # print(f"room at step {cnt_dummy_guard}:\n{a_room.map.view()}")


def find_solution_a(a_room:Room):
    """
    Predict the path of the guard. How many distinct positions will the guard visit before leaving the mapped area?
    """

    # K, we have the Room (with map)
    # We should now simulate the guards walking (path), probably marking the visited fields and update the room's counter...
    __simulate_guards_path_till_exit(a_room)

    # When out of loop - we are at the exit...
    with np.printoptions(threshold=sys.maxsize, linewidth=265):
        print(f"Final room:\n{a_room.map.view()}")

    # We need the number of fields which have been visited (unique)
    # result = len(a_room.find_all([FieldType.VISITED]))
    result = len(a_room.find_all([FieldType.GUARD_UP, FieldType.GUARD_DOWN, FieldType.GUARD_LEFT, FieldType.GUARD_RIGHT,
                                  FieldType.CROSSING_UP_RIGHT, FieldType.CROSSING_RIGHT_DOWN, FieldType.CROSSING_DOWN_LEFT, FieldType.CROSSING_LEFT_UP,
                                  FieldType.TURN_UL, FieldType.TURN_UR, FieldType.TURN_LR, FieldType.TURN_LL]))

    return result


def __determine_guard_direction(offset_pos):
    if offset_pos[0] == 0 and offset_pos[1] == 1:
        return FieldType.GUARD_RIGHT
    elif offset_pos[0] == 0 and offset_pos[1] == -1:
        return FieldType.GUARD_LEFT
    elif offset_pos[0] == 1 and offset_pos[1] == 0:
        return FieldType.GUARD_DOWN
    elif offset_pos[0] == -1 and offset_pos[1] == 0:
        return FieldType.GUARD_UP
    else:
        raise ValueError(f"Unexpected offset position: {offset_pos}")


def __is_in_loop(b_room, new_position, current_visited_indexes, current_visited_directions):
    new_position_index = -1
    # print(f"Entering __is_in_loop for {new_position}, current_visited_indexes: {current_visited_indexes}, current_visited_directions: {current_visited_directions}")
    try:
        while (new_position_index := current_visited_indexes.index(new_position, new_position_index + 1)) != -1:
            # print(f"new_position existing index: {new_position_index}")
            existing_direction = current_visited_directions[new_position_index]
            # print(f"existing_direction: {existing_direction}, new_position's direction: {b_room.map[new_position].value}")
            if existing_direction == b_room.map[new_position].value:
                return True
    except ValueError:
        # print("ValueError...")
        return False

    # print(f"Leaving __is_in_loop - no hit/break")

    return False


def find_solution_b(a_room:Room):
    """
    You need to get the guard stuck in a loop by adding a single new obstruction. How many different positions could you choose for this obstruction?
    """
    # I have the map from part "a"

    # Try some slicing...
    # Show only row 5
    # print(f"Row 5:\n{b_room.map[5]}")

    # Show only column 4
    # print(f"Column 4:\n{b_room.map[:, 4]}")

    # Colum 3, from row 8 to row 3
    # print(f"Column 3, from row 8 to row 3:\n{b_room.map[8::-1, 3]}")

    # Explicitly call is_artificial_obstacle_candidate for each field parth of guards path
    b_room = Room()

    print(f"A room guards_path_till_exit: ({len(a_room.guards_path_till_exit)}) {a_room.guards_path_till_exit}")
    cnt = 0
    unsuccessful_candidates = set()
    for from_pos, to_pos in zip(a_room.guards_path_till_exit, a_room.guards_path_till_exit[1:]):
        # print(f"Checking ({cnt}) {from_pos} -> {to_pos}")

        # If the candidate was already check at earlier stage and was NOK - skip it
        if to_pos in unsuccessful_candidates:
            cnt += 1
            continue

        is_successful = False

        # Set artificial obstacle, perform steps, if hit the current position - it's a loop
        b_room.map = a_room.map.copy()
        b_room.map[to_pos] = Field(FieldType.ARTIFICIAL_OBSTACLE)
        b_room.current_position = from_pos

        offset_pos = (to_pos[0] - from_pos[0], to_pos[1] - from_pos[1])
        b_room.map[from_pos] = Field(__determine_guard_direction(offset_pos))

        current_visited_indexes: list[tuple[int, int]] = [from_pos]
        current_visited_directions: list[FieldType] = [b_room.map[from_pos].value]

        while new_position := b_room.make_step():
            # print(f"current_visited_indexes: {current_visited_indexes}")
            # print(f"current_visited_directions: {current_visited_directions}")
            # print(f"new_position: {new_position} {b_room.map[new_position].value}")
            if new_position in current_visited_indexes:
                # Are we in a loop?
                # print(f"We met it before - check the positions")

                if __is_in_loop(b_room, new_position, current_visited_indexes, current_visited_directions):
                    # We are in a loop
                    # print(f"Same position - we should be in loop")
                    b_room.possible_artificial_obstacles.append(to_pos)
                    is_successful = True
                    break
                else:
                    # Not in a loop
                    # print(f"Different position - save it")
                    current_visited_indexes.append(new_position)
                    current_visited_directions.append(b_room.map[new_position].value)

            else:
                # Not in a loop
                # print(f"Never met it before - save it")
                current_visited_indexes.append(new_position)
                current_visited_directions.append(b_room.map[new_position].value)

        if not is_successful:
            unsuccessful_candidates.add(to_pos)

        # show_elapsed_time(f"DONE Checking ({cnt}) {from_pos} -> {to_pos}")
        # print(f"\tCurrent possible artificial obstacles for room B: ({len(b_room.possible_artificial_obstacles)}) {b_room.possible_artificial_obstacles}\n")
        cnt += 1

    # Restore the a_room original layout
    b_room.map = a_room.map.copy()

    print(f"List of possible artificial obstacles ({len(b_room.possible_artificial_obstacles)}):{b_room.possible_artificial_obstacles}")
    candidates_set = set(b_room.possible_artificial_obstacles)
    print(f"Set of possible artificial obstacles ({len(candidates_set)}):{candidates_set}")

    # Fill-in the artificial obstacles
    for position in candidates_set:
        b_room.map[position] = Field(FieldType.ARTIFICIAL_OBSTACLE)

    with np.printoptions(threshold=sys.maxsize, linewidth=265):
        print(f"Room B with artificial obstacles:\n{b_room.map.view()}")

    # Show also the vanilla room with artificial obstacles
    vanilla_data = [[Field(FieldType(char)) for char in line] for line in input_data]
    vanilla_room = Room(vanilla_data)
    for position in candidates_set:
        vanilla_room.map[position] = Field(FieldType.ARTIFICIAL_OBSTACLE)

    with np.printoptions(threshold=sys.maxsize, linewidth=265):
        print(f"Vanilla room with artificial obstacles:\n{vanilla_room.map.view()}")


    result = len(candidates_set)

    return result


# MAIN
def do_main():
    show_elapsed_time()

    # print("read input")
    controlled_input_read()

    show_elapsed_time()
    # print("len input_data:", len(input_data))
    # print("    input_data:", input_data)

    # Set the data for Room and Map (as 2-dimensional array), using Field classes...
    my_data = [[Field(FieldType(char)) for char in line] for line in input_data]
    my_room = Room(my_data)
    # my_room.map = np.array(my_data, dtype=Field)
    # print(f"shape: {my_room.map.shape}")
    # print(f"nr dimensions: {my_room.map.ndim}")
    # print(f"my_room:\n{my_room.map.view()}")
    with np.printoptions(threshold=sys.maxsize, linewidth=265):
        print(f"Initial room:\n{my_room.map.view()}")
    # print(f"my_room[6][4]: {my_room.map[6][4]}")
    # print(f"my_room[6,4]: {my_room.map[6,4]}")
    # empty_room = Room()
    # print(f"empty_room.map: {empty_room.map.view()}")

    result_a = find_solution_a(my_room)
    print(f"result_a: {result_a}")
    show_elapsed_time()

    result_b = find_solution_b(my_room)
    print(f"result_b: {result_b}")
    show_elapsed_time()


if __name__ == "__main__":
    # execute only if run as a script
    do_main()
