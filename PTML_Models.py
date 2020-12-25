from traceback import format_exc
from PTML_Constants import *
import PTML_Sockets
import PTML_Tags

ElementHandlers = {}

IDStart = -1


def PatchType(t, session, Parent):
    def Wrapper(*arguments, **attributes):
        attributes["session"]=session
        if Parent!=None:attributes["PTML_Parent"]=Parent
        element = t(*arguments, **attributes)
        session.Elements.append(element)
        return session.Elements[-1]
    return Wrapper

def ElementAlias(name):
    def Wrapper(t):
        ElementHandlers[name]=t.__name__
        return t
    return Wrapper

class Console:
    @staticmethod
    def log(session, msg):session.SendMessage(f"eval console.log('{str(msg)}')")

class GlobalVariable:
    def __init__(self, session, name, value):
        self.Value = value
        self.Session = session
        self.Name = name

    def __del__(self):
        del self.Value
        del self.Session.GlobalVariables[self.Name]
        del self

class Session:
    def __init__(self, client):
        self.Client = client
        self.Elements = []
        self.IDCounter = IDStart
        self.Route = "/"
        self.GlobalVariables = {}

    def GetElementByPTMLId(self, id):
        for element in self.Elements:
            if element.ID==id:return element
        return None

    def HandleData(self, data):
        data = data.split(" ")
        instruction = data[0]
        arguments = data[1:]
        if instruction=="SetRoute":
            self.Route=" ".join(arguments)
            for data in PTML_Tags.ExecuteOnLoad[self.Route]: self.ExecuteCode(*data)
        if instruction=="call":
            self.ExecuteCode(PTML_Tags.Functions[self.Route][" ".join(arguments)])
        if instruction=="CallLiteral":
            id, attr = arguments
            getattr(self.GetElementByPTMLId(int(id)), attr)()


    def GetElementByID(self, id):
        for element in self.Elements:
            if element.id==id:return element
        return None

    
    def ExecuteCode(self, code, ParentID = "None"):
        log = lambda msg : Console.log(self, msg)
        GetElementById = lambda id : self.GetElementByID(id)
        def CreateGlobal(name, value = None):
            self.GlobalVariables[name]=GlobalVariable(self, name, value)
            return self.GlobalVariables[name]
        Save = []
        exec("\n".join([DYNAMIC_ELEMENT.format(Element_Name = name, Class_Name = ElementHandlers[name], Parent=ParentID) for name in ElementHandlers]))
        for name in self.GlobalVariables:exec(f"{name} = self.GlobalVariables[{name}]", locals(), locals())
        try:exec(code, locals(), locals())
        except Exception as e:
            self.SendMessage(f"throw {format_exc()}")
            raise

    def SendMessage(self, msg):
        PTML_Sockets.Server.send(self.Client, msg)

@ElementAlias("Element")
class Element_Model:
    IDCounter = 0

    def __init__(self, tag, **attributes):
        tag = tag.strip() if type(tag)==str else ""
        if not tag:raise ValueError(f'Invalid tag: "{tag}"')
        self.Session = attributes["session"]
        self.Client = self.Session.Client
        self.Session.IDCounter += 1
        self.ID = self.Session.IDCounter
        attributes["class"] = ("" if not "class" in attributes else attributes["class"]+" ")+f"ptml-id-{self.ID}"
        self._Attributes = attributes
        self.Tag = tag
        self._InnerHTML = ""
        self.End = f"</{tag}>"
        self.Session.SendMessage(f"create {attributes['parent'] if 'parent' in attributes else attributes['PTML_Parent'] if 'PTML_Parent' in attributes else -1} {self.HTMLString}")

    def __add__(self, other):
        self.InnerHTML += other

    def __str__(self):
        return self.HTMLString

    def __getitem__(self, item: str):
        return self._Attributes[item]

    def __setitem__(self, key: str, value):
        self._Attributes[key]=value
        if key=="class":key="className"
        self.Session.SendMessage(f"change {self.ID} {key} {value}")

    def AddClass(self, cl):
        self["class"]+=f"{' ' if self['class'] else ''}{cl}"

    @property
    def HTMLString(self):
        return self.Start+self.InnerHTML+self.End

    @property
    def Start(self):
        return f"<{self.Tag} {' '+' '.join(f'{key}={QUOTE}{self._Attributes[key]}{QUOTE}' for key in self._Attributes if key!='session') if len(self._Attributes)>0 else ''}>"

    @property
    def InnerHTML(self):return self._InnerHTML
    @InnerHTML.setter
    def InnerHTML(self, value):
        self._InnerHTML = str(value)
        self.Session.SendMessage(f"ChangeInner {self.ID} {self.InnerHTML}")

    @property
    def ClassList(self):
        return self._Attributes["class"].split(" ")

    @property
    def id(self):
        return None if not "id" in self._Attributes else self._Attributes["id"]

class CommonProperties(Element_Model):
    def __init__(self, tag, **attributes):
        super().__init__(tag, **attributes)

    @property
    def Text(self): return self.InnerHTML
    @Text.setter
    def Text(self, value): self.InnerHTML = value

@ElementAlias("Paragraph")
class Paragraph_Model(CommonProperties):
    def __init__(self, Text="", **attributes):
        super().__init__("p", **attributes)
        self.Text = Text

@ElementAlias("Button")
class Button_Model(CommonProperties):
    def __init__(self, Text="", OnClick=None, **attributes):
        super().__init__("button", **attributes)
        self.Text = Text
        self._OnClick = None
        self.onclick = OnClick

    @property
    def onclick(self):return self._OnClick
    @onclick.setter
    def onclick(self, value):
        self._OnClick = value
        self.AddClass("ptml-literal-onclick")

