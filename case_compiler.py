# you are supposed to use it, not read it

import sys
import platform
import os


# sys.traceback=0
if sys.version_info[0] != 3 and sys.version[1] < 6:
    print("Error: Cannot run on versions below 3.6")
    exit()
if sys.version_info[1] < 8:
    print(
        "Warning: Please run it on version above 3.8 else you wouldn't be able to use some features, namely 'as' statement."
    )
impl = platform.python_implementation()
if impl == "PyPy":
    print(
        "Warning: Perhaps, running on pypy will make the compiler faster, but you will be limiting some of the features ;)"
    )
    import re
if impl not in ("PyPy"):
    try:
        import regex as re
    except ImportError:
        import re

        print(
            "Warning: module 'regex' was not found so 're' was imported instead. If you want to speed up the compilation process please install 'regex' module."
        )


class Compiler:
    def __init__(self, ARG, is_file=True):
        self.read_file_pattern_old = r'[^\s"]+|"[^"]*"'
        self.read_file_pattern = r"((f|u|b)?\"[^\"]*\")|((f|u|b)?\'[^\']*\')|(\([\s\S]*\)(?=[^\)]))|(\([\s\S]*)|(\w*)"
        self.array_tokens = {"LIST": ("[", "]"), "SET": ("{", "}"), "DICT": ("{", "}")}
        self.keeps = {}
        if is_file:
            self.file_name = ARG
            with open(ARG) as opened_file:
                lines = opened_file.readlines()
            self.full_code_with_indent = self.read(lines)
        else:
            self.file_name = __file__
            self.full_code_with_indent = self.read(ARG.splitlines())

    def compile(self):
        result = []
        for line_number, line_with_indent in enumerate(self.full_code_with_indent):
            line, ind = line_with_indent
            try:
                result.append((" " * ind) + (",".join(self.parser(line))))
            except Exception as err:
                raise Exception(f"Error at line {line_number+1}, because of {err}")
        return "\n".join(result)

    def parser(self, line):
        token = []
        line_length = len(line)
        i = 0
        try:
            while i < line_length:
                if line[i] == "import":
                    token = [f"import {', '.join(self.parser(line[i+1:]))}"]
                    break

                elif line[i] in ("+", "*", "-", "/", "**", "%", "<", ">"):
                    token = [f"{(' '+line[i]+' ').join(token)}"]
                    i += 1

                elif line[i] == "is":
                    token = [f"{', '.join(token)} == {line[i+1]}"]
                    i += 2

                # experimental
                elif line[i] == "!":
                    token = token[:-1]
                    token.append(
                        f"{', '.join(self.parser(self.tokenizer(line[i-1])))}()"
                    )
                    i += 1

                elif line[i] == "of" or line[i] == ":":
                    next_tokens = line[i + 1 :]

                    if "does" in next_tokens:
                        if next_tokens[-1] == "does":
                            position = next_tokens.index("does")
                            token = [
                                f"def {', '.join(token)}({', '.join(self.parser(next_tokens[:position]))}):"
                            ]
                            break
                        else:
                            token = [
                                f"{', '.join(token)}({', '.join(self.parser(next_tokens))})"
                            ]
                            break
                    else:
                        token = [
                            f"{', '.join(token)}({', '.join(self.parser(next_tokens))})"
                        ]
                        break

                elif line[i] == "be" or line[i] == "=":
                    token = [
                        f"{', '.join(token)} = {', '.join(self.parser(line[i+1:]))}"
                    ]
                    break

                elif line[i] == ";":
                    token = [f"({', '.join(token)})"]
                    i += 1

                elif line[i] == "does":
                    next_tokens = line[i + 1 :]

                    if "from" in next_tokens:
                        first_from_position = next_tokens.index("from")

                        if "does" in next_tokens[:first_from_position]:
                            position = self.rindex(next_tokens, "from")
                        else:
                            position = next_tokens.index("from")

                        tokens_before_from = next_tokens[:position]
                        tokens_after_from = next_tokens[position + 1 :]
                        token = [
                            f"{','.join(token)}{' = ' if i!=0 else ''}(lambda {','.join(self.parser(tokens_after_from))}: {', '.join(self.parser(tokens_before_from))})"
                        ]
                    else:
                        token = [
                            f"{','.join(token)}{' = ' if i!=0 else ''}(lambda: {','.join(self.parser(next_tokens))})"
                        ]
                    break

                elif line[i] == "while":
                    if i == 0:
                        token = [f"while ({', '.join(self.parser(line[i+1:]))}):"]
                        break

                elif line[i] == "for":
                    if i == 0:
                        token = [f"for {', '.join(self.parser(line[i+1:]))}:"]
                        break
                    else:
                        token = [
                            f"{', '.join(token)} for {', '.join(self.parser(line[i+1:]))}"
                        ]
                        break

                elif line[i] == "in":
                    token = [
                        f"{', '.join(token)} in {', '.join(self.parser(line[i+1:]))}"
                    ]
                    break

                elif line[i] in ("continue", "break"):
                    if line_length == 1:
                        token.append(line[i])
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "return":
                    if i == 0:
                        token = [f"return {', '.join(self.parser(line[i+1:]))}"]
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "then":
                    next_tokens = line[i + 1 :]

                    if next_tokens == []:
                        token = [f"if ({', '.join(self.parser(line[:i]))}):"]
                        break

                    if "else" in next_tokens:
                        first_else_position = next_tokens.index("else")

                        if "then" in next_tokens[:first_else_position]:
                            position = self.rindex(next_tokens, "else")
                        else:
                            position = next_tokens.index("else")

                        tokens_before_else = next_tokens[:position]
                        tokens_after_else = next_tokens[position + 1 :]
                        token = [
                            f"(({', '.join(self.parser(tokens_before_else))}) if ({', '.join(token)}) else ({', '.join(self.parser(tokens_after_else))}))"
                        ]

                    else:
                        token = [
                            f"(({', '.join(self.parser(line[i+1:]))}) if ({', '.join(token)}) else None)"
                        ]
                    break

                elif line[i] == "if":
                    next_tokens = line[i + 1 :]
                    if i == 0:
                        token = [f"if ({', '.join(self.parser(next_tokens))}):"]
                        break

                    if "else" in next_tokens:
                        first_else_position = next_tokens.index("else")

                        if "if" in next_tokens[:first_else_position]:
                            position = self.rindex(next_tokens, "else")
                        else:
                            position = next_tokens.index("else")

                        tokens_before_else = next_tokens[:position]
                        tokens_after_else = next_tokens[position + 1 :]
                        token = [
                            f"({', '.join(token)}) if ({', '.join(self.parser(tokens_before_else))}) else ({', '.join(self.parser(tokens_after_else))})"
                        ]

                    else:
                        token = [
                            f"({', '.join(token)}) if ({', '.join(self.parser(line[i+1:]))}) else None"
                        ]
                    break

                elif line[i] == "switch":
                    if i == 0:
                        self.switch_token = self.parser(line[i + 1 :])
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "case":
                    if i == 0:
                        token = [
                            f"if ({', '.join(self.switch_token)}) == ({', '.join(self.parser(line[i+1:]))}):"
                        ]
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "elcase":
                    if i == 0:
                        token = [
                            f"elif ({', '.join(self.switch_token)}) == ({', '.join(self.parser(line[i+1:]))}):"
                        ]
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "keep":
                    if i == 0:
                        if "as" in line:
                            next_tokens = line[i + 1 :]
                            as_position = self.rindex(next_tokens, "as")
                            name = ", ".join(self.parser(next_tokens[:as_position]))
                            if name.isidentifier():
                                self.keeps[name] = ", ".join(
                                    self.parser(next_tokens[as_position + 1 :])
                                )
                                token = []
                                break
                            else:
                                raise Exception(f"'{name}' is an invalid name.")
                        else:
                            raise Exception("'as' not found.")
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "elif":
                    if i == 0:
                        token = [f"elif ({', '.join(self.parser(line[i+1:]))}):"]
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "else":
                    if line_length == 1:
                        token = ["else:"]
                        break
                    else:
                        raise Exception("invalid syntax.")

                elif line[i] == "times":
                    token = token[:-1]
                    token.append(f"({line[i+1]} for _ in range({line[i-1]}))")
                    i += 2

                elif line[i] in ("SET", "LIST", "DICT"):
                    pre, suf = self.array_tokens[line[i]]
                    if i == 0:
                        token.append(f"{pre}{', '.join(self.parser(line[i+1:]))}{suf}")
                        break
                    else:
                        raise Exception("declaration outside parenthesis.")

                elif line[i] in (".", "\\"):
                    previous_token = token[-1]
                    token = token[:-1]
                    try:
                        next_token = ", ".join(self.parser([line[i + 1]]))
                        if next_token.isidentifier():
                            token.append(f"{previous_token}.{next_token}")
                            i += 2
                        else:
                            raise Exception("invalid attribute name.")
                    except IndexError:
                        raise Exception("invalid syntax.")

                elif line[i].startswith("(") and line[i].endswith(")"):
                    inner = line[i][1:-1]
                    if inner.startswith(":"):
                        inner = inner[1:]
                        if i != 0:
                            previous_token = token[-1]
                            token = token[:-1]
                            token.append(
                                f"{previous_token}[{': '.join(self.parser(self.tokenizer(inner)))}]"
                            )
                            i += 1
                        else:
                            raise Exception("invalid syntax.")
                    if inner.startswith("#"):
                        i += 1
                    else:
                        token.append(
                            f"({', '.join(self.parser(self.tokenizer(inner)))})"
                        )
                        i += 1

                elif line[i] in self.keeps:
                    token.append(self.keeps[line[i]])
                    i += 1

                else:
                    if line[i].isidentifier() or line[i].isdigit():
                        token.append(line[i])
                        i += 1
                    else:
                        raise Exception(f"wierd char '{line[i]}' lol.")
            return token
        except IndexError:
            raise Exception(f"No token after '{line[i]}'")
        except RecursionError:
            raise Exception("Unknown compiler error")
        except Exception as err:
            raise Exception(
                f"token '{line[i]}', with token number {i+1}. This is because of {err}"
            )

    def interpreter(self):
        print(f"Case v0.0.2 running on python {sys.version}]")
        while True:
            try:
                line = [input("~> ")]
                for s in self.read(line):
                    k = ", ".join(self.parser(s[0]))
                    try:
                        print(eval(k))
                    except SyntaxError:
                        exec(k)
            except Exception as err:
                print(err)

    def indent(self, line):
        i = 0
        for x in line:
            if x not in (" ", "\t"):
                return line[i:], i
            else:
                i += 1
        return line[i:], i

    def rindex(self, lst, ele):
        return len(lst) - lst[::-1].index(ele) - 1

    def paren(self, t):
        l = len(t)
        i = 0
        c = 0
        while i < l:
            if t[i] == ")" and c == 0:
                return i
            if t[i] == "(":
                c += 1
            if t[i] == ")":
                c -= 1
            i += 1
        return i

    def tokenizer(self, line):
        result = []
        for token in re.split(self.read_file_pattern, line.strip()):
            if not (token == None or token.split() == []):
                result.append(token)
        return result

    def read_old(self, lines):
        full_code_with_indent = []
        for x in lines:
            y, i = self.indent(x)
            if not y.startswith("#"):
                line = re.findall(self.read_file_pattern_old, y.rstrip())
                full_code_with_indent.append((line, i))
        return full_code_with_indent

    def read(self, lines):
        full_code_with_indent = []
        for x in lines:
            y, i = self.indent(x)
            if not y.startswith("#"):
                full_code_with_indent.append((self.tokenizer(y), i))
        return full_code_with_indent


if __name__ == "__main__":
    arg_length = len(sys.argv)
    if arg_length == 1:
        Comp = Compiler("stop", is_file=False)
        Comp.interpreter()
    elif arg_length in (2, 3):
        if arg_length == 2:
            FILE = sys.argv[1]
        if arg_length == 3:
            FILE = sys.argv[2]
        try:
            Comp = Compiler(FILE)
            result = Comp.compile()
        except Exception as err:
            print(err)
            os.system(
                'notify-send -u normal -a "python" "CaseLang" "Compilation Failed."'
            )
        else:
            print("Compilation Success.")
            os.system(
                'notify-send -u normal -a "python" "CaseLang" "Compilation Success."'
            )

            with open(FILE + ".py", "w") as opened_file:
                opened_file.write(result)
            if sys.argv[1] == "-run":
                exec(result)

    else:
        print("Error: too many/less arguments.")


# I told you not to read (ノಠ益ಠ)ノ彡┻━┻
