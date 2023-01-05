"""Reads verilog file and groups it as blocks"""

import re


def load_file_to_string(path, delim="±"):
    file = open(path, "r")
    my_str = ""
    for line in file:
        my_str += line + delim
    return my_str


def clean(my_str):
    my_str = re.sub("\n", "", my_str)
    return re.sub(r"(?s)/\*.*?\*/", "", my_str)


def is_valid(line):
    conditions = [
        not line.strip().startswith("//"),
        not line.strip().startswith("#"),
        line != ""
    ]
    return not (False in conditions)


def clean2(lines):
    new_lines = list()
    for line in lines:
        if is_valid(line):
            new_lines.append(line.strip())
    return new_lines


def file_to_lines(path, delim="±"):
    return clean2(clean(load_file_to_string(path)).split(delim))


def find_keyword(keyword, lines):
    indices = list()
    for i, line in enumerate(lines):
        if keyword in line:
            indices.append(i)
    return indices


def parse_as_blocks(lines):
    """Takes in lines, a list of strings
    returns a list of tuples
    each tuples is of shape (block_start_index, block_end_index, block_string)
    with type (int, int, string)
    """
    if "current_state" in lines and "next_state" in lines:
        return lines
    new_lines = []
    temp_line = ""
    in_always = False
    i_begin = 0
    i_end = 0
    for line in lines:
        if line.split()[0] == "always":
            in_always = True

        if not in_always:
            temp_line += line
            if line[-1] == ";":
                new_lines.append(((i_begin, i_end), temp_line[:-1]))
                i_begin = i_end + 1
                temp_line = ""
        else:
            if line.split()[-1] == "begin":
                temp_line += " ".join(line.split()[:-1]) + "; "
            elif line == "end":
                new_lines.append(((i_begin, i_end), temp_line))
                i_begin = i_end + 1
                temp_line = ""
                in_always = False
            else:
                temp_line += line
        i_end += 1
    return new_lines


def remove_empty_entries(lines):
    new_lines = []
    for line in lines:
        if line:
            new_lines.append(line.strip())
    return new_lines


def print_indexed(lines):
    for i, line in enumerate(lines):
        print(f"{i}: {line}")


def read(path):
    return parse_as_blocks(file_to_lines(path))
