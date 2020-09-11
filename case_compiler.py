#you are supposed to use it, not read it
import sys
sys.traceback=0
try:
    from pyparsing import nestedExpr
except ImportError:
    print("compiler needs 'pyparsing' module to work. Please install it")
    exit()
try:
    import regex as re
except ImportError:
    import re
    print("module 'regex' was not found so 're' was imported instead. If you want to speed up the compilation process please install 'regex' module")


class Compiler:
    def __init__(self,ARG,is_file=False):
        self.read_file_pattern=r'[^\s"]+|"[^"]*"'
        if is_file:
            self.file_name=ARG
            with open(ARG) as opened_file:
                lines=opened_file.readlines()
            self.full_code=self.read(lines)
        else:
            self.file_name=__file__
            self.full_code=self.read(ARG.splitlines())

    def compile(self):
        result=[]
        for x in self.full_code:
            for l in self.parser(x):
                result.append(l)
        return result

    def parser(self,line):
        token=[]
        line_length=len(line)
        i=0
        while i<line_length:
            if line[i]=="pull":
                token=[f"import {line[i+1]}"]
                i+=2
            elif line[i]=="argto" or line[i]=="to":
                f=",".join(token)
                token=[f"{line[i+1]}({f})"]
                i+=2
            elif line[i]=="of":
                f=",".join(token)
                token=[f"{f}({line[i+1]})"]
                i+=2
            elif line[i]=="till":
                #token
                token=[f"range({token[-1]},{line[i+1]})"]
                i+=2
            elif line[i]=="listto":
                f=",".join(token)
                token=[f"{line[i+1]}[{f}]"]
                i+=2
            elif line[i]=="attrto":
                f="".join(token)
                token=[f"{line[i+1]}.{f}"]
                i+=2
            elif line[i]=="paren":
                f=",".join(token)
                token=[f"({f})"]
                i+=1
            elif line[i]=="kwarg":
                f=",".join(token)
                token=[f"{line[i+1]}=({f})"]
                
                i+=2
            elif line[i] in ["add","sub","mul","div","quo","mod","pow","greater","lesser","equals"]:
                op=line[i]
                operators={"add":"+","sub":"-","mul":"*","div":"/","quo":"//","mod":"%","pow":"**","greater":">","lesser":"<","equals":"=="}
                f=",".join(token)
                token=[f"{f}{operators[op]}{line[i+1]}"]
                i+=2
            elif line[i]=="be":
                f=",".join(token)
                token=[f"{f}={','.join(line[i+1:])}"]
                break
            elif line[i]=="as":
                f=",".join(token)
                token=[f"({line[i+1]}:={f})"]
                i+=2
            elif line[i]=="then":
                f=",".join(token)
                s=self.parser(line[i+1:])
                token=[f"({','.join(s)}) if ({f}) else None"]
                break
            elif line[i]=="thenl":
                f=",".join(token)
                s=self.parser(line[i+1:line.index('else')])
                token=[f"({','.join(s)}) if ({f}) else {','.join(self.parser(line[line.index('else')+1:]))}"]
                break
            elif line[i]=="times":
                f=",".join(token)
                token=[f"[({f}) for _ in range(0,{line[i+1]})]"]
                i+=2
            elif line[i]=="if":
                f=",".join(token)
                s=self.parser(line[i+1:])
                token=[f"({f}) if ({','.join(s)}) else None"]
                break
            elif line[i]=="stop":
                break
            else:
                token.append(line[i])
                i+=1
        return token

    def interpreter(self):
        print(f"Case v0.0.1 running on python {sys.version}]")
        while True:
            try:
               line=[input("~> ")]
               for s in self.read(line):
                   for k in self.parser(s):
                       try:
                           print(eval(k))
                       except SyntaxError:
                           exec(k)
            except Exception as err:
                print(err)

    def tokenizer(self,line):
        tokenized_line=[]
        for x in line:
            if x.startswith(","):
                tokenized_line.append(x[:-1])
                tokenized_line.append(",")
            else:
                tokenized_line.append(x)
        return tokenized_line


    def read(self,lines):
            full_code=[]
            for x in lines:
                if not x.startswith("#"):
                    line=re.findall(self.read_file_pattern,x.rstrip())
                    full_code.append(line)
            return full_code

if __name__=="__main__":
    d=Compiler("stop")
    d.interpreter()

#I told you not to read (ノಠ益ಠ)ノ彡┻━┻