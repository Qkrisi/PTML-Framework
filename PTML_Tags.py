from inspect import getfullargspec
from PTML_Constants import *

Tags = {}

Functions = {}
ExecuteOnLoad = {}



def Tag(name):
    def TagHandler(func):
        def TagWrapper(**kwargs):
            argspec = getfullargspec(func)
            NewArgs = {}
            for arg in argspec.kwonlyargs:
                NewArgs[arg]=kwargs[arg] if arg in kwargs else None
            for arg in kwargs:
                if not arg in IGNORE_ATTRIBUTES and not arg in argspec.kwonlyargs:raise NameError(f"Invalid attribute: {arg}")
            return func(**NewArgs)
        Tags[name]=TagWrapper
        return TagWrapper
    return TagHandler

def UpdateData(data: str) -> str:
    indent = ""
    NewData = ""
    for line in data.split("\n"):
        if line.strip() == "": continue
        l = line
        while len(l) > 0 and l[0].isspace():
            indent += l[0]
            l = l[1:]
        break
    for line in data.split("\n"):
        NewData += line.replace(indent, "", 1) + "\n"
    return NewData

@Tag("pyscript")
def PyScript(*, data, Route, ParentID):
    ExecuteOnLoad[Route].append((UpdateData(data), str(ParentID)))
    return ""

@Tag("pyfunc")
def PyFunction(*, name, data, Route):
    name = name.strip() if name!=None else ""
    if not name:raise ValueError(f"Invalid function name: {name}")
    Functions[Route][name]=UpdateData(data)
    return ""