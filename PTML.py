from flask import Flask
from html.parser import HTMLParser
from os import path, listdir, remove
from PTML_Constants import *
import PTML_Tags
import PTML_Sockets

SelfModule = __import__(__name__)

WSPort = -1

def UpdateAttributes(attributes):
    attrib = []
    cl = ""
    for attribute in attributes:
        if attribute[0]=="class":cl=attribute[1]
    for attribute in attributes:
        if attribute[0]=="class":continue
        add = True
        for key in PTML_Tags.Functions:
            if attribute[1]==f"{key}()":
                cl+=f" ptml-attribute-{attribute[0]}-{key}"
                add = False
                break
        if add:attrib.append(attribute)
    if cl!="":attrib.append(("class", cl))
    return attrib

class PTML_Parser(HTMLParser):
    def __init__(self, file):
        super().__init__()
        self.File = file
        self.CurretTag = ""
        self.Datas = {}

    def handle_starttag(self, tag, attrs):
        attrs = UpdateAttributes(attrs)
        if not tag in PTML_Tags.Tags:
            self.File.write(f"<{tag}{' '+' '.join(name+'='+QUOTE+value+QUOTE for name, value in attrs) if len(attrs)>0 else ''}>")
            self.CurretTag = ""
            if tag=="head":self.File.write(f"\n<script>const WSPort={WSPort}</script>\n")
            return
        if not tag in self.Datas:self.Datas[tag]=[]
        self.CurretTag = tag
        self.Datas[tag].append([attrs, ""])

    def handle_endtag(self, tag):
        if not tag in PTML_Tags.Tags:
            self.File.write(f"</{tag}>")
            return
        self.CurretTag = ""
        kwargs = {}
        data = self.Datas[tag].pop(-1)
        for attribute in data[0]:
            kwargs[attribute[0]]=attribute[1]
        kwargs["data"]=data[1]
        self.File.write(PTML_Tags.Tags[tag](**kwargs) + "\n")


    def handle_data(self, data):
        if self.CurretTag=="":
            self.File.write(data)
            return
        self.Datas[self.CurretTag][-1][1]+=data

def ReadFromStatic(_path = "index.html", _separator = "\n") -> str:
	if not path.isfile(_path):return "Invalid path"
	with open(_path,"r") as f:
		content = f.readlines()
	return _separator.join(content)

def Parse(input, out):
    with open(out, "w") as WriteFile:
        Parser = PTML_Parser(WriteFile)
        with open(input, "r") as ReadFile:
            Parser.feed("\n".join(ReadFile.readlines()))

def ListFiles(Directory):
    for member in listdir(Directory):
        _path = path.join(Directory, member)
        if path.isfile(path.join(Directory, member)):yield _path
        else:yield from ListFiles(_path)

def Run(Directory, AppName, ip="localhost", HTTPPort=5000, WebSocketPort=5001):
    global WSPort
    app = Flask(AppName)
    Counter = 0
    RemoveAfter = []
    WSPort=WebSocketPort
    @app.route("/PTML.js")
    def PTML_Script():
        return ReadFromStatic("PTML.js")
    for _path in ListFiles(Directory):
        Counter+=1
        directory = path.dirname(_path)
        file = path.basename(_path)
        Parsed = directory+f"/{path.splitext(file)[0]}_ptml.html"
        use_ptml = False
        if path.splitext(file)[1]==".ptml":
            use_ptml = True
            Parse(_path, Parsed)
            RemoveAfter.append(Parsed)
        exec(DYNAMIC_ROUTE.format(Path="/"+directory.replace(Directory, "", 1)+path.splitext(file)[0], Counter=Counter, Parsed=Parsed if use_ptml else _path))
    PTML_Sockets.Start(ip, WebSocketPort)
    app.run(host=ip, port=HTTPPort)
    for file in RemoveAfter:remove(file)

Run("Test", "Testing")