from re import search
import os.path
import sys
import time
import re

import ast


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.stats = {"import": [], "from": [], "class": []}
        self.imports = []

    def visit_ClassDef(self, node):
        print()
        for alias in node.names:
            self.stats["class"].append(alias.name)

    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)

    def report(self):
        print(self.stats)

    def import_list(self):
        return self.imports


class CodeAnalyzer(object):
    error_codes = {1: "S001 Too long",
                   2: "S002 Indentation is not a multiple of four",
                   3: "S003 Unnecessary semicolon",
                   4: "S004 At least two spaces required before inline comments",
                   5: "S005 TODO found",
                   6: "S006 More than two blank lines used before this line",
                   7: "S007 Too many spaces after construction_name (def or class)",
                   8: "S008 Class name class_name should be written in CamelCase",
                   9: "S009 Function name function_name should be written in snake_case",
                   10: "S010 Argument name arg_name should be written in snake_case",
                   11: "S011 Variable var_name should be written in snake_case",
                   12: "S012 The default argument value is mutable"}
    template_camel = r"(^[A-Z][a-z0-9]+)([A-Z][a-z0-9]+)*\s*(\(.*\))?:?$"
    template_snake = r"(^[_a-z0-9]+)(_[a-z0-9]+)*\s*(\(.*\))?:?$"

    def __init__(self, file):
        self.file = file
        try:
            with open(self.file) as f:
                self.file_lines = f.readlines()
            with open(self.file) as f:
                try:
                    self.tree = ast.parse(f.read())
                except SyntaxError:
                    self.tree = []
                    print("error")
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
                # so there can be something implemented
                return None
            else:
                return original_string[start_index + 1:end_index]
        else:
            return None

    def check_camel_case(self):
        for counter, line in enumerate(self.file_lines):
            line = line.strip()
            if line.startswith("class"):
                line = line.removeprefix("class").lstrip()
                if not line or line == ":":
                    print("camel case empty")
                    continue
                if not search(CodeAnalyzer.template_camel, line):
                    self.error_add(counter + 1, 8)
                    continue

    def check_spacing_after_name(self):
        for counter, line in enumerate(self.file_lines):
            line = line.lstrip()
            if line.startswith("class") or line.startswith("def"):
                start_index = line.find(" ")
                if start_index != -1:
                    outline = line[start_index:]
                    indent_len = len(outline) - len(outline.lstrip())
                    if indent_len > 1:
                        self.error_add(counter + 1, 7)

                """if search(r"^def  ", line) is not None or search(r"class  ", line) is not None:
                    self.error_add(counter + 1, 7)"""

    def check_snake_case(self):
        for counter, line in enumerate(self.file_lines):
            line = line.strip(" \n:")
            if line.startswith("def"):
                line = line.removeprefix("def").lstrip()
                if not line or line == ":":
                    print("snake case empty")
                    continue
                if not search(CodeAnalyzer.template_snake, line):
                    self.error_add(counter + 1, 9)
                    continue

    def check_variable_snake(self):
        for counter, line in enumerate(self.file_lines):
            line = line.lstrip()
            if line.startswith("def"):
                line = line+"    pass"
                try:
                    tree = ast.parse(line)
                except SyntaxError as error:
                    print(f"error has occurred: {counter}", error)
                else:
                    body = tree.body[0]
                    #print(body.name, [b.arg for b in body.args.args], [ast.dump(a) for a in  body.args.defaults])
                    defaults_par = [a for a in body.args.defaults if isinstance(a, ast.List)]
                    #print(defaults_par)
                    if defaults_par:
                        self.error_add(counter + 1, 12)
                    #print([search(CodeAnalyzer.template_snake, b.arg) for b in body.args.args])
                    for var_names in body.args.args:
                        if not search(CodeAnalyzer.template_snake, var_names.arg):
                            self.error_add(counter + 1, 10)
                            continue


        """print("tree obj",self.tree)
        #print("tree dump",ast.dump(self.tree))
        # [a.name for a in tree.body[0].names])
        for class_ in self.tree.body:
            print("class obj",class_)
            if isinstance(class_, ast.ClassDef):
                #print("module is instanse of Class")
                for function in class_.body:
                    print("_________")
                    print("funk obj",function)
                    #print("funk dump", ast.dump(function))
                    print("funk.args dump", ast.dump(function.args))
                    if function.args.defaults:
                        print("not empty")
                        self.error_add(counter + 12, 12)
                    for something in function.args.defaults:
                        print("\nfunk.args.defaults dump", ast.dump(something))
                    print("_________")
                    #if ast.dump(function.args.defaults) is not None:
                    #    print(ast.dump(function.args.defaults))"""

    def check_var_assert(self):
        for counter, line in enumerate(self.file_lines):
            line = line.lstrip()
            try:
                tree = ast.parse(line)
            except SyntaxError as error:
                pass
            else:
                if not tree.body:
                    continue
                body = tree.body[0]
                if isinstance(body, ast.Assign):
                    for names in [a.id for a in body.targets if isinstance(a, ast.Name)]:
                        if not search(CodeAnalyzer.template_snake, names):
                            self.error_add(counter + 1, 11)
                            continue

    def pep_checks_wrapper(self):
        """Individually calling a function if actually faster than "for each cycle"""
        self.check_lines_length()
        self.check_indent()
        self.check_semicolon()
        self.check_inline_comment()
        self.check_todo()
        self.check_new_lines()
        self.check_camel_case()
        self.check_snake_case()
        self.check_spacing_after_name()
        self.check_variable_snake()
        self.check_var_assert()

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
                    #print(os.path.join(path, file))
                    self.exec.append(CodeAnalyzer(os.path.join(path, file)))
        elif os.path.isfile(self.path):
            self.exec.append(CodeAnalyzer(self.path))
        else:
            dir_content = os.listdir(self.path)
            print(dir_content)
            print("sorry your path is not gonna make it")

    def execute_(self):
        for file in self.exec:
            # print(f"file: {file.getter_filename()}")
            file.pep_checks_wrapper()
            print(file, end="")

    def execute_time(self):
        for file in self.exec:
            # print(f"file: {file.getter_filename()}")
            file.pep_checks_wrapper()
            #print(file, end="")


def timer(func):
    def wrapper(args_for_function):
        start = time.time()
        for i in range(10000):
            func(args_for_function)
        end = time.time()
        print('func takes', (end - start)/10000, 'seconds')

    return wrapper


@timer
def func1(arg):
    new = FileFinder(arg)
    new.execute_time()
    del new

if __name__ == "__main__":
    #print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        if i > 0:
            #print(f"i = {i}: _{arg}_")
            #func1(arg)
            new = FileFinder(arg)
            new.execute_()
            del new

