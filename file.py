import re
import numpy as np
from reader import read, file_to_lines
PATH = "FullCase.v"
errors = {}
db = {}

IDENTIFIER_REGEX = r"[_a-zA-Z][_a-zA-Z0-9]{0,30}"
MAX_PORT_SIZE = float('inf')


def add_error(obj, err):
    """Add error to db"""
    if isinstance(obj, str):
        entry = obj
        print(f"ERROR: {err} in {entry}")
    else:
        entry = type(obj).__name__ + " " + obj.name
        print(f"ERROR: {err} in {obj.name}")
    errors[entry] = errors.get(entry, "")

    if errors[entry] != "":
        errors[entry] += ", "

    errors[entry] += err


def add_var(name, size, val, net_type):
    """Add var to db"""
    db[name] = {
        "size": size,
        "val": val,
        "net_type": net_type
    }


def get_var(name):
    """Get variable from DB"""
    return db.get(name, None)


class Port:
    """Port class"""

    def __init__(self, code):
        # code = output [2:0] var_name

        # split = ['output', '[2:0]', 'var_name']
        split = code.split()

        self.direction = split[0]  # direction is always first elem
        self.name = split[-1]  # name is always last elem
        self.size = 1  # size is 1 by default
        self.net_type = "wire"  # net_type is wire by default

        split = split[1:-1]

        if len(split) == 1:  # remaining element is either type or range
            rem_elem = split[0]
            if ":" in rem_elem:  # rem_elem = [2:0]
                self.extract_range(rem_elem)
            else:
                self.net_type = rem_elem

        elif len(split) == 2:  # remaining elements are net_type and range
            self.net_type = split[0]  # Net type will always be first
            self.extract_range(split[1])  # Range will always be second

        elif len(split) > 2:
            add_error(self, "Too many passed values!")

        # Assertions
        if self.direction not in ["input", "output", "inout"]:
            add_error(
                self,
                f"Invalid port direction, expected [input, output, input] but got {self.direction}")
        if not self.name.isidentifier():
            add_error(self, f"Invalid port name {self.name}")
        if self.size < 1:
            add_error(
                self, f"Invalid port size {self.size}, size can not be negative")
        if self.size > MAX_PORT_SIZE:
            add_error(
                self, f"Invalid port size {self.size}, size can not be more than {MAX_PORT_SIZE}")
        if self.net_type not in ["wire", "reg"]:
            add_error(
                self, f"Invalid port net type, expected [wire, reg] but got {self.net_type}")

        # Save to memory
        add_var(name=self.name,
                size=self.size,
                val="X",
                net_type=self.net_type)

    def extract_range(self, range_code):
        """Extract range from range code"""
        range_code = range_code[1:-1]  # remove brackets
        range_code = range_code.split(":")  # range_code = [2, 0]
        self.size = abs(int(range_code[0]) -
                        int(range_code[1])) + 1  # size = 2-0

    def __str__(self):
        return f"{self.direction} {self.net_type} [{self.size-1}:0] {self.name}"


class Module:
    """Module class"""
    # code = module counter (input clk,output [2:0] out)

    def __init__(self, code):
        self.name = code.split()[1]

        # ports_init = ['input clk', 'output [2:0] out']
        ports_init = code.split("(")[1][:-1].split(",")
        self.ports = list()
        # port_init = output [2:0] out
        for port_init in ports_init:
            self.ports.append(Port(port_init))

        # Assertions
        if not self.name.isidentifier():
            add_error(self, f"Invalid module name {self.name}")

    def __str__(self):
        my_str = f"module {self.name} ("
        for i, port in enumerate(self.ports):
            my_str += str(port)
            if i != len(self.ports)-1:
                my_str += ", "
        my_str += ")"
        return my_str


class Statement:
    """Statement class in always@"""

    def __init__(self, code):
        self.name = code
        self.target = code.split(" = ")[0]  # Target is always first
        self.value = code.split(" = ")[1]
        if self.value[-1] == ";":
            self.value = self.value[:-1]
        self.ready_val = self.compute()
        # Assertions
        if not self.target.isidentifier():
            add_error(self, f"Invalid target name {self.target}")
        if get_var(self.target) is None:
            add_error(self, f"Undefined target {self.target}")
        self.check_overflow()

    def compute(self):
        """Compute evaluate_num on all terms"""
        terms = re.split(r'( \+ | \<\< | \- | \>\> )', self.value)
        for i, _ in enumerate(terms):
            terms[i] = terms[i].strip()
            terms[i] = self.evaluate_num(terms[i])
            if terms[i] == "X":
                terms[i] = "-9999999"
        return eval(" ".join(terms))

    def evaluate_num(self, num):
        """Evaluates the number as an actual string to be evaluated"""
        if "'" not in num and num in ['0', '1']:
            return str(num)

        if "'" in num:
            base = num.split("'")[1][0]
            if base in ['b', 'd', 'h', 'o']:
                if base == 'b':
                    base = 2
                elif base == 'd':
                    base = 10
                elif base == 'h':
                    base = 16
                else:
                    base = 8
            else:
                add_error(
                    self, f"Invalid base, expected [b, d, h, o] but got {base}")
                return str("X")

            num = "".join(num.split("'"))
            return str(int(num[2:], base))

        if num in ["+", "-", "<<", ">>"]:
            return num

        temp_num = num
        num = get_var(num)
        if num is None:
            add_error(self, f"Undefined register {temp_num}")
            return "X"
        elif num["val"] == "X":
            add_error(
                self, f"Uninitialized usage of register {temp_num}")
            return "X"
        else:
            return str(num["val"])

    def __str__(self):
        return self.name

    def check_overflow(self):
        """Checks overflow possibility"""
        size_of_target = get_var(self.target)["size"]
        max_size = 0
        temp_size = 0
        terms = re.split(r'( \+ | \<\< | \- | \>\> )', self.value)
        for i, term in enumerate(terms):
            term = term.strip()
            temp_size = get_var(term)
            if temp_size is None:
                continue
            temp_size = temp_size["size"]
            if temp_size > max_size:
                max_size = temp_size

        if max_size >= size_of_target and (" + " in terms or " << " in terms):
            add_error(self, "Possibility of Overflow")


class Declaration:
    """Declaration Class"""

    def __init__(self, code):
        # code reg [2:0] internalReg = 0;
        # split = ['reg', '[2:0]', 'internalReg', '=', '0']
        split = code.split()
        self.name = None  # name is always last elem before =
        self.size = 1  # size is 1 by default
        self.net_type = split[0]  # Net-type is always first element
        self.value = "X"

        if ":" in code:
            self.extract_range(split[1])  # Second element

        if "=" in code:
            first_part = code.split(" = ")[0]
            second_part = code.split(" = ")[1]
            self.name = first_part.split()[-1]  # Last element
            self.value = int(self.evaluate_num(second_part))
        else:
            self.name = split[-1]

        # Assertions
        if not self.name.isidentifier():
            add_error(self, f"Invalid port name {self.name}")
        if self.size < 1:
            add_error(
                self, f"Invalid port size {self.size}, size can not be negative")
        if self.size > MAX_PORT_SIZE:
            add_error(
                self, f"Invalid port size {self.size}, size can not be more than {MAX_PORT_SIZE}")
        if self.net_type not in ["wire", "reg"]:
            add_error(
                self, f"Invalid port net type, expected [wire, reg] but got {self.net_type}")

        # Save to memory
        add_var(name=self.name,
                size=self.size,
                val=self.value,
                net_type=self.net_type)

    def extract_range(self, range_code):
        """Extract range from range code"""
        range_code = range_code[1:-1]  # remove brackets
        range_code = range_code.split(":")  # range_code = [2, 0]
        self.size = abs(int(range_code[0]) -
                        int(range_code[1])) + 1  # size = 2-0

    def evaluate_num(self, num):
        """Evaluates the number as an actual string to be evaluated"""
        if "'" not in num and num in ['0', '1']:
            return int(num)

        if "'" in num:
            base = num.split("'")[1][0]
            if base in ['b', 'd', 'h', 'o']:
                if base == 'b':
                    base = 2
                elif base == 'd':
                    base = 10
                elif base == 'h':
                    base = 16
                else:
                    base = 8
            else:
                add_error(
                    self, f"Invalid base, expected [b, d, h, o] but got {base}")
                return str("X")

            num = "".join(num.split("'"))
            return int(num[2:], base)

    def __str__(self):
        return f"{self.net_type} [{self.size-1}:0] {self.name} = {self.value}"


class Always:
    """Always@ Block class"""

    def __init__(self, code):
        # always @(posedge clk); internalReg = internalReg + 1
        code = code[:-1]
        self.name = code.split("; ")[0]  # always @(posedge clk)
        self.statements = []

        terms = code.split("; ")[1:]
        for term in terms:
            if "case" in term:
                in_case = True
                continue
            if in_case and "endcase" in term:
                in_case = False
            self.statements.append(Statement(term))

        # Now let's parse the sensitivity list
        self.sensitivity_list = "*"
        sensitivity_list_str = self.name.split("@")[1][1:-1]
        if sensitivity_list_str != "*":
            self.sensitivity_list = []
            sensitivity_list_str = sensitivity_list_str.split(" or ")
            for elem in sensitivity_list_str:
                temp_elem = elem
                if get_var(elem) is None:
                    add_error(self, f"{temp_elem} is undefined")
                else:
                    self.sensitivity_list.append(elem)

    def __str__(self):
        return self.name


class Assign:
    """Assign block class"""

    def __init__(self, code):
        # assign out = internalReg
        self.name = code
        code = code.split()[1:]
        self.target = code[0]
        self.value = " ".join(code).split(" = ")[1]

        # Assertions
        if get_var(self.target) is None:
            add_error(self, f"Undefined target {self.target}")
        self.check_overflow()

    def check_overflow(self):
        """Checks overflow possibility"""
        size_of_target = get_var(self.target)["size"]
        max_size = 0
        temp_size = 0
        terms = re.split(r'( \+ | \<\< | \- | \>\> )', self.value)
        for term in terms:
            term = term.strip()
            temp_size = get_var(term)
            if temp_size is None:
                continue
            temp_size = temp_size["size"]
            if temp_size > max_size:
                max_size = temp_size

        if max_size >= size_of_target and (" + " in terms or " << " in terms):
            add_error(self, "Possibility of Overflow")

    def __str__(self):
        return f"assign {self.target} = {self.value}"

# class LocalParam:
#     """Local Param Class"""

#     def __init__(self, code):
#         # localparam [2:0] internalReg = 0;
#         split = code.split()
#         self.name = None  # name is always last elem before =
#         self.size = 1  # size is 1 by default
#         self.net_type = split[0]  # Net-type is always first element
#         self.value = "X"

#         if ":" in code:
#             self.extract_range(split[1])  # Second element

#         if "=" in code:
#             first_part = code.split(" = ")[0]
#             second_part = code.split(" = ")[1]
#             self.name = first_part.split()[-1]  # Last element
#             self.value = int(self.evaluate_num(second_part))
#         else:
#             self.name = split[-1]

#         # Assertions
#         if not self.name.isidentifier():
#             add_error(self, f"Invalid port name {self.name}")
#         if self.size < 1:
#             add_error(
#                 self, f"Invalid port size {self.size}, size can not be negative")
#         if self.size > MAX_PORT_SIZE:
#             add_error(
#                 self, f"Invalid port size {self.size}, size can not be more than {MAX_PORT_SIZE}")
#         if self.net_type not in ["wire", "reg"]:
#             add_error(
#                 self, f"Invalid port net type, expected [wire, reg] but got {self.net_type}")

#         # Save to memory
#         add_var(name=self.name,
#                 size=self.size,
#                 val=self.value,
#                 net_type=self.net_type)

#     def extract_range(self, range_code):
#         """Extract range from range code"""
#         range_code = range_code[1:-1]  # remove brackets
#         range_code = range_code.split(":")  # range_code = [2, 0]
#         self.size = abs(int(range_code[0]) -
#                         int(range_code[1])) + 1  # size = 2-0

#     def evaluate_num(self, num):
#         """Evaluates the number as an actual string to be evaluated"""
#         if "'" not in num and num in ['0', '1']:
#             return int(num)

#         if "'" in num:
#             base = num.split("'")[1][0]
#             if base in ['b', 'd', 'h', 'o']:
#                 if base == 'b':
#                     base = 2
#                 elif base == 'd':
#                     base = 10
#                 elif base == 'h':
#                     base = 16
#                 else:
#                     base = 8
#             else:
#                 add_error(
#                     self, f"Invalid base, expected [b, d, h, o] but got {base}")
#                 return str("X")

#             num = "".join(num.split("'"))
#             return int(num[2:], base)

#     def __str__(self):
#         return f"{self.net_type} [{self.size-1}:0] {self.name} = {self.value}"


file = read(PATH)


def is_fsm(file):
    """Check whether the file has FSM states"""
    current_state = False
    next_state = False
    for line in file:
        line = line[1]
        if "current_state" in line:
            current_state = True
        if "next_state" in line:
            next_state = True
        if current_state and next_state:
            return True
    return False


def extract_states(line, states):
    """Extract states from line"""
    state = line.split()[2:][0]
    states[state] = False


def check_unreachable_states(file, states):
    """Detect unreachable states"""
    # Then extract all states
    for line in file:
        if line.split()[0] == "localparam":
            extract_states(line, states)

    # Then check if all states are indexed
    for line in file:
        if "next_state" in line and "=" in line:
            case_name = line.split(":")[0]
            state = line.split(" = ")[-1][:-1]
            if state in states and state != case_name:
                states[state] = True

    # Now let's check if there is any state that is unreachable
    for state, reachable in states.items():
        if not reachable:
            add_error(f"State {state}", "Unreachable state")


if is_fsm(file):
    file = file_to_lines(PATH)
    states = {}
    check_unreachable_states(file, states)
    exit()


blocks = {}
for indices, block in file:
    first_word = block.split()[0]

    if first_word == "module":
        blocks["module"] = Module(block)

    if first_word in ["reg", "wire"]:
        decl = Declaration(block)
        blocks[f"decl_{decl.name}"] = decl

    if first_word == "always":
        blocks[f"always_{indices[0]}"] = Always(block)

    if first_word == "assign":
        assi = Assign(block)
        blocks[f"assign_{assi.name}"] = assi


class MultiDrivenCheck:
    """Checking multi-driven bus/regs"""

    def __init__(self):
        self.assigned = []

    def in_assigned(self, name):
        if name in self.assigned:
            add_error(get_var(name)['net_type'] +
                      " " + name, "Multi-Driven Bus/Reg")
            return True
        return False

    def __add__(self, other):
        if isinstance(other, str):
            to_check = other
        else:
            to_check = other.target
        if not self.in_assigned(to_check):
            self.assigned.append(to_check)
        return self


def check_case(always_block_param):
    temp_always = always_block_param
    always = []
    case_type = None
    for i, line in enumerate(temp_always.split(";")):
        if "case" in line or "casex" in line or "casez" in line:
            x = re.split(r'\)', line)
            x[0] = x[0] + ")"
            for e in x:
                always.append(e.strip())
            if case_type is None:
                if "case " in line:
                    case_type = "case"
                elif "casex " in line:
                    case_type = "casex"
                elif "casez " in line:
                    case_type = "casez"
                else:
                    add_error(always_block_param[1].split(";")[0], "UNKNOWN CASE TYPE")
                    return None, None
            continue
        always.append(line.strip())

    def get_case_var(lines):
        for line in lines:
            if "case" in line:
                return line.split()[1][1:-1]
        add_error("always_block_X", "DIDNT FIND ANY CASE VARIABLE!")
        return False

    # Check if default exists
    for line in always_block_param:
        if "default:" in line:
            return True

    case_var = get_case_var(always)
    case_var_size = get_var(case_var)["size"]

    def generate_possible_combinations(size):
        # We use base 4 as possible vals are 0 1 X Z
        def to_base_4(num):
            if num == 0:
                return [0]
            digits = []
            while num:
                digits.append(int(num % 4))
                num //= 4
            return digits[::-1]

        combinations = []
        for i in range(4**size):
            combinations.append(i)
        
        cases = []
        for comb in combinations:
            mystr = ""
            to_base = to_base_4(comb)
            for digit in to_base:
                if digit == 2:
                    mystr += "X"
                elif digit == 3:
                    mystr += "Z"
                else:
                    mystr += str(digit)
            while len(mystr) < size:
                mystr = "0" + mystr
            cases.append(mystr)
        return cases

    # Now we generate all possible combinations
    all_combs = generate_possible_combinations(case_var_size)

    # Let's build our switch statement's cases
    cases = []
    count = False
    for line in always:
        if "case" in line:
            count = True
            continue

        if not count:
            continue

        if "default" in line or "endcase" in line:
            count = False
            continue
        num = re.split(r'\'|:', line)[1][1:]
    #     if "X" in num:
    #         num = num.replace("X", "2")
    #     if "Z" in num:
    #         num = num.replace("Z", "3")
    #      cases.append(int(num, 4))
        cases.append(num)

    # Frequency should be a list of all zeros with size 4**size_of_x
    def compare_nums(num1, num2):
        num1, num2 = [*num1], [*num2]

        if len(num1) != len(num2):
            return False

        for i, _ in enumerate(num1):
            d1 = num1[i]
            d2 = num2[i]
            if d1 == d2 or d1 == "?" or d2 == "?":
                continue

            if case_type == "casex":
                if d1 in ["X", "Z"] or d2 in ["X", "Z"]:
                    continue

            if case_type == "casez":
                if d1 in ["?", "Z"] or d2 in ["?", "Z"]:
                    continue

            return False
        return True
    # Exhaustive Testing of compare_nums
    # for case in ["case", "casex", "casez"]:
    #     for num1 in ["0", "1", "X", "Z", "?"]:
    #         for num2 in ["0", "1", "X", "Z", "?"]:
    #             print(
    #                 f"{case} {num1}={num2}: {1 if compare_nums(num1, num2, case) else 0}")
    #         print()
    freq = np.zeros(4**case_var_size, dtype=int)
    all_combs = generate_possible_combinations(case_var_size)
    for case in cases:
        for i, comb in enumerate(all_combs):
            freq[i] += int(compare_nums(case, comb))

    # If there is any number is frequency that is greater than 1, then it was repeated
    # return max(freq) <= 1
    return freq, cases


def is_full(freq):
    return 0 not in freq


def is_parallel(freq, cases):
    def base_4_to_dec(num):
        dec = 0
        W = []
        for i in range(len(num)):
            W.append(4**i)
        num = [*num]
        num.reverse()
        for i, w in enumerate(W):
            x = num[i]
            if x == "X":
                x = 2
            elif x == "Z":
                x = 3
            else:
                x = int(x)
            dec += x*w
        return dec

    for case in cases:
        index = base_4_to_dec(case)
        if freq[index] > 1:
            return False
    return True




def multi_driven_checker():
    global_multi_driven = MultiDrivenCheck()
    always_keys = []
    for key, block in blocks.items():
        if "assign" in key:
            global_multi_driven += block
            continue

        if "decl" in key and block.value != "X":
            global_multi_driven += block
            continue

        if "always" in key:
            always_keys.append(key)

    for always_key in always_keys:
        local_multi_driven = MultiDrivenCheck()

        # Our always block
        always_block = blocks[always_key]

        # Let's add all elements of the global to the local
        for statement in always_block.statements:
            local_multi_driven += statement.target

        current_sensitivity_list = always_block.sensitivity_list

        # Is sensitivity lis a wildcard?
        wild_card = current_sensitivity_list == "*"

        # Add all variables in the sensitivity list to the local scope
        for other_always_key in always_keys:
            CHECK = False

            if other_always_key == always_key:
                continue

            other_always_block = blocks[other_always_key]

            other_sensitivity_list = other_always_block.sensitivity_list

            if wild_card is True:
                CHECK = True
            else:
                for elem in other_sensitivity_list:
                    if elem in current_sensitivity_list:
                        CHECK = True
                        break

            if not CHECK:
                continue

            for statement in other_always_block.statements:
                if statement.target in local_multi_driven.assigned:
                    name = f"{get_var(statement.target)['net_type']} {statement.target}"
                    add_error(name, "Multi-Driven Bus/Reg")


def full_case_checker():
    for block in file:
        if "always @(" in block[1]:
            freq, cases = check_case(always_block_param=block[1])
            full = is_full(freq)
            if not full:
                add_error(block[1].split(";")[0], "NOT FULL")


def parallel_case_checker():
    for block in file:
        if "always @(" in block[1]:
            freq, cases = check_case(always_block_param=block[1])
            parallel = is_parallel(freq, cases)
            if not parallel:
                add_error(block[1].split(";")[0], "NOT PARALLEL")
