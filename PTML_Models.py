from traceback import format_exc
from PTML_Constants import *
import PTML_Sockets
import PTML_Tags

ElementHandlers = {}

IDStart = -1

def PatchType(t, session):
    def Wrapper(*arguments, **attributes):
        attributes["session"]=session
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

class Session:
    def __init__(self, client):
        self.Client = client
        self.Elements = []
        self.IDCounter = IDStart
        self.Route = ""

    def HandleData(self, data):
        data = data.split(" ")
        instruction = data[0]
        arguments = data[1:]
        if instruction=="SetRoute":
            self.Route=" ".join(arguments)
            for data in PTML_Tags.ExecuteOnLoad[self.Route]: self.ExecuteCode(data)

    def ExecuteCode(self, code):
        log = lambda msg : Console.log(self, msg)
        exec("\n".join([DYNAMIC_ELEMENT.format(Element_Name = name, Class_Name = ElementHandlers[name]) for name in ElementHandlers]))
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
        self.Tag = tag
        self.Start = f"<{tag} {' '+' '.join(f'{key}={QUOTE}{attributes[key]}{QUOTE}' for key in attributes if key!='session') if len(attributes)>0 else ''}>"
        self._InnerHTML = ""
        self.End = f"</{tag}>"
        self.Session.SendMessage(f"create {self.HTMLString}")

    def __add__(self, other):
        self.InnerHTML += str(other)

    def __str__(self):
        return self.HTMLString

    @property
    def HTMLString(self):
        return self.Start+self.InnerHTML+self.End

    @property
    def InnerHTML(self):return self._InnerHTML
    @InnerHTML.setter
    def InnerHTML(self, value):
        self._InnerHTML = value
        self.Session.SendMessage(f"ChangeInner {self.ID} {self.InnerHTML}")

@ElementAlias("Paragraph")
class Paragraph_Model(Element_Model):
    def __init__(self, Text="", **attributes):
        super().__init__("p", **attributes)
        self.Text = Text

    @property
    def Text(self):return self.InnerHTML
    @Text.setter
    def Text(self, value):self.InnerHTML = value