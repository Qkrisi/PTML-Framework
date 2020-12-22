from websock import WebSocketServer
from threading import Thread
import PTML_Models

Sessions = {}
Server = None

def NewConnection(client):
    Sessions[client]=PTML_Models.Session(client)

def RemoveConnection(client):
    del Sessions[client]

def HandleData(client, data):
    Sessions[client].HandleData(data)

def Start(ip, port):
    global Server
    Server = WebSocketServer(ip, port, on_connection_open=NewConnection, on_connection_close=RemoveConnection, on_data_receive=HandleData)
    Thread(target = Server.serve_forever).start()