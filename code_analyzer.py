import re
import os.path
import sys


class CodeAnalyzer(object):
    error_codes = {1: "S001 Too long",
                   2: "S002 Indentation is not a multiple of four",
                   3: "S003 Unnecessary semicolon",
                   4: "S004 At least two spaces required before inline comments",
                   5: "S005 TODO found",
                   6: "S006 More than two blank lines used before this line",
                   7: "S007 Too many spaces after construction_name (def or class)",
                   8: "S008 Class name class_name should be written in CamelCase",
                   9: "S009 Function name function_name should be written in snake_case"}
    template_camel = r"(?:[A-Z][a-z]+)+"
    template_snake = r""

    def __init__(self, file):
        self.file = file
        try:
            with open(self.file) as f:
                self.file_lines = f.readlines()
        except FileNotFoundError:
            print("Path Does not exist")
            self.file_lines = []
        self.errors = []

    @staticmethod
    def sub_quotes(source) -> list:
        return re.findall('"([^"]*)"', source)

    def error_add(self, line, error_code):
        """Adds error code, line is number of line where is the error occurred, error code is self explanatory"""
        self.errors.append([line, error_code])  # line and code

    def check_lines_length(self):
        for counter, line in enumerate(self.file_lines):
            if len(line) > 79:
                self.error_add(counter + 1, 1)

    def check_indent(self):
        for counter, line in enumerate(self.file_lines):
            if line.startswith(" "):
                indent_len = len(line) - len(line.lstrip(" "))
                if indent_len % 4 != 0:
                    self.error_add(counter + 1, 2)

    def check_semicolon(self):
        for counter, line in enumerate(self.file_lines):
            data = line.split("#")[0].rstrip()
            try:
                if data[-1] == ";":
                    self.error_add(counter + 1, 3)
            except IndexError:
                pass

    def check_inline_comment(self):
        for counter, line in enumerate(self.file_lines):
            data = line.split("#")
            try:
                if data[1]:
                    indent_len = len(data[0]) - len(data[0].rstrip(" "))
                    if indent_len < 2 and len(data[0]) > 1:
                        self.error_add(counter + 1, 4)
            except IndexError:
                pass

    def check_todo(self):
        for counter, line in enumerate(self.file_lines):
            if "#" in line and "todo" in line.lower():
                if line.index("#") < line.lower().index("todo"):
                    self.error_add(counter + 1, 5)

    def check_new_lines(self):
        blank_lines_count = 0
        for counter, line in enumerate(self.file_lines):
            if line == "\n":
                blank_lines_count += 1
                continue
            if line != "\n" and blank_lines_count < 3:
                blank_lines_count = 0
                continue
            if line != "\n" and blank_lines_count > 2:
                self.error_add(counter + 1, 6)
                blank_lines_count = 0
                continue

    @staticmethod
    def sub_parentheses(original_string):
        start_index = original_string.find("(")
        if start_index != -1:
            try:
                end_index = original_string.index(")")
            except ValueError:
                print("SyntaxError: '(' was never closed")
                return None
            else:
                return original_string[start_index+1:end_index]
        else:
            return None

    def check_camel_case(self):

        template_camel = r"^(?:[A-Z][a-z]*)+"
        for counter, line in enumerate(self.file_lines):
            line = line.lstrip().rstrip()
            print(f"\nline num ={counter} {line.startswith('Class')} _{line}_")
            if line.startswith("Class"):
                str_inside = self.sub_parentheses(line)
                if str_inside:
                    #print(f"inside ({str_inside})")
                    variable = re.findall(template_camel, str_inside)
                    if not variable:
                        print("there is not camelCase inside parentheses")
                        continue
                """start_index = line.find("(")
                if start_index != -1:
                    try:
                        end_index = line.index(")")
                    except ValueError:
                        print("SyntaxError: '(' was never closed")
                    else:
                        str_inside = line[start_index+1:end_index]
                        print(f"inside ({str_inside})")
                        variable = re.findall(template_camel, str_inside)
                        if not variable:
                            print("there is not camelCase")
                            continue"""


                #another_template = r"\(.*\)"
                line = line.removeprefix("Class").lstrip()
                #print(f"inside of ({re.findall(another_template, line)})")
                #lines = line.split()
                #print(f"split = {lines}")
                variable = re.findall(template_camel, line)
                #print(f"var {variable}")
                if not variable:
                    print("there is not camelCase outside")
                    continue

    def pep_checks_wrapper(self):
        self.check_lines_length()
        self.check_indent()
        self.check_semicolon()
        self.check_inline_comment()
        self.check_todo()
        self.check_new_lines()
        self.check_camel_case()

    def getter_filename(self):
        return self.file

    def __str__(self):
        self.errors.sort()
        for error in self.errors:
            print(f'{self.file}: Line {error[0]}: {CodeAnalyzer.error_codes[error[1]]}')
        return ""


class FileFinder(object):

    def __init__(self, path):
        self.path = path
        self.pats = path
        self.exec = []
        if os.path.isdir(path):
            files = os.listdir(path)
            files.sort()
            for file in files:
                if file.endswith(".py"):
                    self.exec.append(CodeAnalyzer(self.path + '/' + file))
        elif self.path.endswith(".py"):
            if os.path.exists(self.path):
                self.exec.append(CodeAnalyzer(self.path))
        else:
            print("sorry your path is not gonna make it")

    def execute_(self):
        for file in self.exec:
            # print(f"file: {file.getter_filename()}")
            file.pep_checks_wrapper()
            print(file, end="")


if __name__ == "__main__":
    # print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        if i > 0:
            # print(f"i = {i}: {arg}")
            new = FileFinder(arg)
            new.execute_()
            del new
