import re


class CodeAnalyzer(object):
    error_codes = {1: "S001 Too long",
                   2: "S002 Indentation is not a multiple of four",
                   3: "S003 Unnecessary semicolon",
                   4: "S004 At least two spaces required before inline comments",
                   5: "S005 TODO found",
                   6: "S006 More than two blank lines used before this line"}

    def __init__(self, file):
        try:
            with open(file) as f:
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

    def pep_checks_wrapper(self):
        self.check_lines_length()
        self.check_indent()
        self.check_semicolon()
        self.check_inline_comment()
        self.check_todo()
        self.check_new_lines()


    def __str__(self):
        self.errors.sort()
        for error in self.errors:
            print(f'Line {error[0]}: {CodeAnalyzer.error_codes[error[1]]}')
        return ""


file_to_scan = input()
analyzer = CodeAnalyzer(file_to_scan)
analyzer.pep_checks_wrapper()

print(analyzer, end="")

