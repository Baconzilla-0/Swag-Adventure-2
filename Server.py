from Engine import Multiplayer
from Engine import Menu
from Engine import Styles
import pygame
import threading
import sys
import subprocess
import json

class Info:
    Address = None
    Port = None
    Players = []
    GameServer = None

class Gui:
    Screen = None # The servers' screen
    Clock = None # The clock (this is what controls our framelimit and frame rate counter)
    Running = None
    FrameLimit = 30 # the framelimit
    Scene = None

    def Setup():
        pygame.init()
        Gui.Screen = pygame.display.set_mode((400, 350)) #| pygame.FULLSCREEN) # setup the screen for displaying game
        pygame.display.set_caption('Game Server')
        Gui.Clock = pygame.time.Clock() # setup the clock so we can set our framelimit

    def Loop():
        Gui.Running = True
        Gui.Scene = Menu.Scene()

        AddressInput = Menu.InputBox(pygame.Vector2(200, 50), pygame.Vector2(100, 50), "Address")
        PortInput = Menu.InputBox(pygame.Vector2(200, 50), pygame.Vector2(100, 150), "Port")
        StartButton = Menu.Button(pygame.Vector2(200, 50), pygame.Vector2(100, 250), "Start Server", Styles.SAFETY)

        Title = Menu.Text(50, pygame.Vector2(10, 10), "Silly Server")
        Address = Menu.Text(30, pygame.Vector2(10, 50), f"Address: {Info.Address}")
        Port = Menu.Text(30, pygame.Vector2(10, 90), f"Port: {Info.Port}")
        PlayerList = Menu.List(pygame.Vector2(400, 150), pygame.Vector2(0, 250), Info.Players, 30)

        Gui.Scene.Components = [AddressInput, PortInput, StartButton]

        while Gui.Running:
            PlayerList.SetList(Info.Players)

            Gui.Screen.fill("darkgrey")
            Gui.Scene.Draw(Gui.Screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Info.GameServer.destroy()
                    sys.exit("Server Closed :[")
                else:
                    if AddressInput in Gui.Scene.Components:
                        AddressInput.Update(Gui.Screen, event)
                        PortInput.Update(Gui.Screen, event)
                    
            if StartButton.Clicked:
                Info.Address = AddressInput.Text
                Info.Port = PortInput.Text
                
                Address.Text = f"Address: {Info.Address}"
                Port.Text = f"Port: {Info.Port}"

                Gui.Scene.Components = [Title, Address, Port, PlayerList]
                StartButton.Clicked = False
                Main()
            pygame.display.flip()
            Gui.Clock.tick(Gui.FrameLimit)
Gui.Setup()

def Main():
    Info.GameServer = Multiplayer.Server(Info.Address, int(Info.Port))

    @Info.GameServer.event
    def on_connection(connection, address, id, clients, globals):
        print("New connection")
        return {"X" : 0, "Y" : 0, "Name":"noname"}

    @Info.GameServer.event
    def on_disconnection(connection, address, id, clients, globals):
        print(f"Client {id} disconnected")

    @Info.GameServer.event
    def on_recv(connection, address, id, clients, globals, data: str):
        data = data.split("|", 1)
        #print(data)
        if data[0] == "move":
            PlayerData = json.loads(data[1])
            print(PlayerData)
            clients[id] = PlayerData

            Info.Players = []
            for Key in clients.keys():
                Info.Players.append(clients[Key])
            return clients

        if data[0] == "get_id":
            return id

        if data[0] == "get_level":
            return "./Server/ServerLevel.json"

        if data[0] == "close":
            Info.GameServer.disconnect(connection)
            return None

    Thread = threading.Thread(target=Info.GameServer.listen)
    Thread.start()
    
Gui.Loop()