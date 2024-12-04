from Engine import *
from Game import *

import pygame
import math
import copy
import random
import json

def Overlay(List, Pos): # a function which renders several lines of text using the text function in the engine library
    Index = Pos.y # the y position of the text

    for Line in List:
        Utils.Text(Game.Screen, Line, "Roboto Mono", (0, 0, 255), 50, (Pos.x, Index))
        Index += 30 # spaces the text accordingly


class Game:
    State = "Main"
    Fullscreen = False

    class Multiplayer:
        def __init__(self, Name, Address, Port):
            try:
                self.Client = Multiplayer.Client(Address, Port)
                self.Client.connect()
                self.Client.send("get_id")
                self.id = self.Client.recv()

                self.Client.send("get_level")
                self.Level = Game.Level(self.Client.recv(), pygame.Vector2(100, 100), pygame.Vector2(1000, 1000), "B")

                self.Name = Name
            except:
                print("ERROR: Could not connect to provided server, loading singleplayer...")

        def update(self):
            Data = {
                "X": math.floor(Game.Player.Entity.Position.x),
                "Y": math.floor(Game.Player.Entity.Position.y),
                "HP": {"Max": Game.Player.Health.Max, "Value": Game.Player.Health.Value},
                "Name": self.Name,
                "Colour": {"R":Game.Player.Entity.Colour[0], "G":Game.Player.Entity.Colour[1], "B":Game.Player.Entity.Colour[2]}
            }
            self.Client.send(f"move|{json.dumps(Data)}")
            Clients = self.Client.recv()
            del Clients[self.id]

            if Physics.Debug:
                print(Clients)

            for Key in Clients.keys():
                Position = pygame.Vector2(Clients[Key]["X"], Clients[Key]["Y"])
                Rect = pygame.Rect(Position, pygame.Vector2(30, 50))

                Colour = pygame.Color(100, 0, 0)

                try:
                    Colour = pygame.Color(Clients[Key]["Colour"]["R"], Clients[Key]["Colour"]["G"], Clients[Key]["Colour"]["B"])
                except KeyError:
                    pass

                pygame.draw.rect(Game.Screen, Colour, Rect)
                Utils.RenderBar(Game.Screen, Position + pygame.Vector2(-5, -15), pygame.Vector2(40, 10), IntConstrained(Clients[Key]["HP"]["Value"], 0, Clients[Key]["HP"]["Max"]), "green", "red")
                #Utils.Text(Game.Screen, self.Name, "Comic Sans MS", (0, 0, 0), 50, Position - pygame.Vector2(0, 10))
    

    # define the player and its data
    class Player:
        Health = IntConstrained(100, 0, 100)
        Entity = None
        Speed = 60
        JumpHeight = 20
        Client = None

    RespawnPos = pygame.Vector2(10, 10)
    Screen = None # The games' screen
    Clock = None # The clock (this is what controls our framelimit and frame rate counter)
    Running = None
    DT = 0 # Delta time (the time it took between frames being rendered so we can scale all our values so that they are consistant)
    FrameLimit = 120 # the framelimit
    
    def Setup():
        pygame.init()
        pygame.mixer.init()
        Game.Screen = pygame.display.set_mode((1280, 720), pygame.SCALED) #| pygame.FULLSCREEN) # setup the screen for displaying game
        pygame.display.set_caption('Game')
        Game.Clock = pygame.time.Clock() # setup the clock so we can set our framelimit

        SettingsData = Settings.ReadFile("./Settings.json")
        # create the player object
        Game.Player.Entity = Physics.Player(pygame.Vector2(0, 0), pygame.Vector2(30, 50), 1, pygame.Color(SettingsData["PlayerColour"][0], SettingsData["PlayerColour"][1], SettingsData["PlayerColour"][2]), True)

    class Menu:
        Scene = None
        Looping = None
        LastState = None

        def Setup():
            Game.Menu.Scene = Menu.Scene()
            Game.Menu.Looping = True
            Game.Menu.LastState = None

            ## GLOBALS
            Game.Menu.BackButton = Menu.Button(pygame.Vector2(200, 100), pygame.Vector2(980, 520), "Back", Styles.DANGER)

            ## START
            Game.Menu.Image = Menu.Image(pygame.Vector2(600, 200), pygame.Vector2(100, 100), "./Assets/Images/TitleScreen.png")

            Game.Menu.StartButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 300), "Play Game", Styles.SAFETY)
            Game.Menu.MultiplayerButton = Menu.Button(pygame.Vector2(450, 100), pygame.Vector2(550, 300), "Play Online", Styles.SAFETY)
            Game.Menu.OptionsButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 450), "Options")
            Game.Menu.QuitButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 600), "Quit Game")

            ## MULTIPLAYER JOIN
            Game.Menu.AddressInput = Menu.InputBox(pygame.Vector2(400, 100), pygame.Vector2(100, 300), "Address")
            Game.Menu.PortInput = Menu.InputBox(pygame.Vector2(400, 100), pygame.Vector2(100, 450), "Port")
            Game.Menu.JoinButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 600), "Join Game", Styles.SAFETY)

            ## DEATH
            Game.Menu.DieText = Menu.Text(200, pygame.Vector2(100, 100), "U Die :[")
            Game.Menu.RestartButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 300), "Respawn")

            ## OPTIONS
            Game.Menu.OptionsTitle = Menu.Text(200, pygame.Vector2(100, 100), "Options")

            Game.Menu.DebugTickbox = Menu.LabeledTickBox(pygame.Vector2(100, 400), "Debug")
            Game.Menu.FullscreenTickbox = Menu.LabeledTickBox(pygame.Vector2(100, 300), "Fullscreen")
            
            Game.Menu.PlayerColour = Menu.Colourpicker(1, pygame.Vector2(450, 350), Styles.NEUTRAL)
            Game.Menu.ColourLabel = Menu.Text(60, pygame.Vector2(450, 300), "Player Colour")

            Game.Menu.SaveButton = Menu.Button(pygame.Vector2(100, 50), pygame.Vector2(450, 430), "Save", Styles.SAFETY)

            ## PAUSE
            Game.Menu.PauseTitle = Menu.Text(200, pygame.Vector2(100, 100), "Game Paused")
            Game.Menu.ResumeButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 300), "Resume")
            Game.Menu.TitleButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 600), "Main Menu")

            ## WIN SCREEN
            Game.Menu.WinText = Menu.Text(200, pygame.Vector2(100, 100), "You Win!!")
            Game.Menu.PlayAgainButton = Menu.Button(pygame.Vector2(400, 100), pygame.Vector2(100, 300), "Play Again?")

        def Loop():
            Game.Menu.Looping = True
            try:
                pygame.mixer.music.stop()
            except:
                pass

            while Game.Menu.Looping:
                if Game.State == "Main":
                    Game.Menu.Scene.Components = [Game.Menu.StartButton, Game.Menu.OptionsButton, Game.Menu.Image, Game.Menu.QuitButton, Game.Menu.MultiplayerButton]

                    Game.Screen.fill("darkgrey")
         
                elif Game.State == "Options":
                    Game.Menu.Scene.Components = [Game.Menu.SaveButton, Game.Menu.BackButton, Game.Menu.OptionsTitle, Game.Menu.PlayerColour, Game.Menu.ColourLabel, Game.Menu.DebugTickbox, Game.Menu.FullscreenTickbox]
                    #if math.floor(Test.Level * 100) == 46:
                    #    TestText.Text = f"Awesome-Ometer: 46.2"
                    #else:
                    #Game.Menu.TestText.Text = f"Awesome-Ometer: {Utils.Clamp(math.floor(Game.Menu.Test.Level * 100), 100, 0)}"
                
                    Game.Screen.fill("darkgrey")
         
                elif Game.State == "Die":
                    Game.Menu.Scene.Components = [Game.Menu.DieText, Game.Menu.RestartButton]
         
                elif Game.State == "Pause":
                    Game.Menu.Scene.Components = [Game.Menu.PauseTitle, Game.Menu.ResumeButton, Game.Menu.TitleButton, Game.Menu.OptionsButton]

                    Game.Screen.fill("darkgrey")
         
                elif Game.State == "Join":
                    Game.Menu.Scene.Components = [Game.Menu.AddressInput, Game.Menu.PortInput, Game.Menu.JoinButton, Game.Menu.BackButton]
                    
                    Game.Screen.fill("darkgrey")
         
                elif Game.State == "Win":
                    Game.Menu.Scene.Components = [Game.Menu.PlayAgainButton, Game.Menu.WinText]

                    Game.Screen.fill("darkgrey")

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        Game.Menu.Looping = False
                        exit("Game Closed :[")
                    else:
                        if Game.Menu.AddressInput in Game.Menu.Scene.Components:
                            Game.Menu.AddressInput.Update(Game.Screen, event)
                            Game.Menu.PortInput.Update(Game.Screen, event)

                Game.Menu.Scene.Draw(Game.Screen)

                if Game.Menu.QuitButton.Clicked:
                    exit("Game Closed :[")

                if Game.Menu.StartButton.Clicked:
                    Game.State = None
                    Game.Menu.Looping = False
                    Game.Menu.StartButton.Clicked = False

                if Game.Menu.MultiplayerButton.Clicked:
                    LastState = copy.copy(Game.State)
                    Game.State = "Join"
                    Game.Menu.MultiplayerButton.Clicked = False
     
                if Game.Menu.JoinButton.Clicked:
                    Game.State = None
                    Game.Menu.Looping = False
                    Game.Menu.JoinButton.Clicked = False

                    Number = random.randint(0,6)
                    Names = ["HappyBoat0278", "SillyFoot28", "Xx_FatalWound_xX", "Druippingbl00d", "Qu1ckSc0per_Cool", "JohnsMum123", "IFuckingHateGarfield", "Burger"]
                    Game.Player.Client = Game.Multiplayer(Names[Number], Game.Menu.AddressInput.Text, int(Game.Menu.PortInput.Text))
     
                if Game.Menu.RestartButton.Clicked:
                    Game.State = None
                    Game.Menu.Looping = False
                    Game.Menu.RestartButton.Clicked = False
                    Game.Player.Health.Value = 100
                    Game.Player.Entity.Position = copy.copy(Game.RespawnPos) #pygame.Vector2(Game.RespawnPos.x, Game.RespawnPos.y) 

                if Game.Menu.PlayAgainButton.Clicked:
                    Game.State = None
                    Game.Menu.Looping = False
                    Game.Menu.PlayAgainButton.Clicked = False
                    Game.Player.Health.Value = 100
                    Game.Level1.Load()
     

                if Game.Menu.OptionsButton.Clicked:
                    LastState = copy.copy(Game.State)
                    Game.State = "Options"
                    Game.Menu.OptionsButton.Clicked = False
     
                if Game.Menu.BackButton.Clicked:
                    Game.State = LastState
                    Game.Menu.BackButton.Clicked = False
    
                if Game.Menu.ResumeButton.Clicked:
                    Game.State = None
                    Game.Menu.Looping = False
                    Game.Menu.ResumeButton.Clicked = False
    
                if Game.Menu.TitleButton.Clicked:
                    Game.State = "Main"
                    Game.Menu.TitleButton.Clicked = False
                    Game.Player.Health.Value = 100
                    Game.Player.Entity.Position = pygame.Vector2(0, 0)

                Physics.Debug = Game.Menu.DebugTickbox.TickBox.State         
        
                if Game.Menu.FullscreenTickbox.TickBox.State != Game.Fullscreen:
                    if Game.Menu.FullscreenTickbox.TickBox.State:
                        Game.Fullscreen = True
                        Game.Screen = pygame.display.set_mode((1280, 720), pygame.SCALED | pygame.FULLSCREEN)
                        
                    else:
                        Game.Fullscreen = False
                        Game.Screen = pygame.display.set_mode((1280, 720), pygame.SCALED)           
        
                if Game.Menu.SaveButton.Clicked:
                    Game.Player.Entity.Colour = pygame.Color([Game.Menu.PlayerColour.Red, Game.Menu.PlayerColour.Green, Game.Menu.PlayerColour.Blue])
                    Settings.WriteFile("./Settings.json", {"PlayerColour": [Game.Menu.PlayerColour.Red, Game.Menu.PlayerColour.Green, Game.Menu.PlayerColour.Blue], "Fullscreen": Game.Menu.FullscreenTickbox.TickBox.State})
                    Game.Menu.SaveButton.Clicked = False
                pygame.display.flip()
                Game.Clock.tick(Game.FrameLimit)

    class Level:
        def __init__(self, LevelFile, StartPos, EndPos, NextLevel):
            self.StartPos = StartPos
            self.EndPos = EndPos
            self.File = LevelFile
            self.Objects = []
            self.Emitters = []

            self.Next = NextLevel

            

        def Load(self):
            self.End = Physics.LinkableEntity(self.EndPos, pygame.Vector2(50,50), 1, "yellow", False)
            self.Start = Physics.LinkableEntity(self.StartPos, pygame.Vector2(50,50), 1, "orange", False, False)
            self.End.LinkEvent(self.Completed)

            self.Objects.append(self.End)
            self.Objects.append(self.Start)
            Game.RespawnPos = self.StartPos

            with open(self.File, "r") as File:
                LevelJson = File.read()
                LevelData = json.loads(LevelJson)

            for Object in LevelData:
                Pos = pygame.Vector2(Object["Pos"]["X"], Object["Pos"]["Y"])
                Size = pygame.Vector2(Object["Size"]["X"], Object["Size"]["Y"])
                if Object["Type"] == "Normal":
                    Entity = Physics.Entity(Pos, Size, 1, "black", False)
                elif Object["Type"] == "Jump":
                    Entity = Physics.LinkableEntity(Pos, Size, 1, "green", False)
                    Power = Object['Power']
                    def Jump(Touched):
                        Touched.Jump(Power)
                    Entity.LinkEvent(Jump)
                elif Object["Type"] == "Lava":
                    Entity = Physics.LinkableEntity(Pos, Size, 1, "Red", False)
                    Particle = Particles.ParticleEmitter(Size, Pos, "Red", 30, 20, pygame.Vector2(0, -1))
                    self.Emitters.append(Particle)
                    def Lava(Touched):
                        Game.Player.Health.Modify(-5)

                    Entity.LinkEvent(Lava)
                elif Object["Type"] == "Text":
                    Entity = Physics.Text(25, Pos, Object["Text"])
                #if Object["Type"] != "Text":
                self.Objects.append(Entity)

            Game.Player.Entity.SetPos(self.Start.Position)
            Game.Player.Entity.Velocity = pygame.Vector2(0,0)
        def Unload(self):
            for Object in self.Objects:
                Physics.Entities.remove(Object)
            for Emitter in self.Emitters:
                Particles.Emitters.remove(Emitter)
        def Completed(self, Touched):
            self.Unload()
            if self.Next == None:
                Game.State = "Win"
                Game.Menu.Loop()
            else:
                self.Next.Load()

    def LoadSettings():
        SettingsData = Settings.ReadFile("./Settings.json")
        Game.Menu.FullscreenTickbox.TickBox.State = SettingsData["Fullscreen"]
        Game.Menu.PlayerColour.RSlider.Set(SettingsData["PlayerColour"][0] / 255)

        if SettingsData["Fullscreen"]:
            Game.Fullscreen = True
            Game.Screen = pygame.display.set_mode((1280, 720), pygame.SCALED | pygame.FULLSCREEN)
            
        else:
            Game.Fullscreen = False
            Game.Screen = pygame.display.set_mode((1280, 720), pygame.SCALED)

    def Loop():
        
        Game.Running = True # self explanitory

        # ground entity
        Ground = Physics.LinkableEntity(pygame.Vector2(-1280, 720), pygame.Vector2(2560, 30), 1, "blue", False)
        def Kill(Touched):
            Game.Player.Health.Value = 0

        Ground.LinkEvent(Kill)    

        if Game.Player.Client == None: 
            Game.Level1.Load()
        else:
            Game.Player.Client.Level.Load()

        while Game.Running:
            # set the background colour
            Game.Screen.fill("darkgrey")
            
            # tell the physics engine to update all entities
            Physics.Update(Game.Screen)
            Particles.Update(Game.Screen)

            if Game.Player.Client != None:
                Game.Player.Client.update()

            #Map.Draw(Game.Screen) # call the debug drawing function so we can add objects via dragging the mouse

            # stops the game if we close the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.Running = False
                    exit("Game Closed :[")

            # detects keys pressed
            keys = pygame.key.get_pressed()
                
            if keys[pygame.K_SPACE] or keys[pygame.K_w]:
                Game.Player.Entity.Jump(Game.Player.JumpHeight)
            if keys[pygame.K_a]:
                Game.Player.Entity.Impulse(pygame.Vector2(-Game.Player.Speed, 0) * Game.DT) # moves the player left
            if keys[pygame.K_d]:
               Game.Player.Entity.Impulse(pygame.Vector2(Game.Player.Speed, 0) * Game.DT) # moves the player right
            if keys[pygame.K_ESCAPE]:
                Game.State = "Pause"
                Game.Menu.Loop()
            if Physics.Debug:
                if keys[pygame.K_x]:
                    Data = []
                    for Entity in Physics.Entities:
                        EntityData = {
                            "Pos": {"X": Entity.Position.x, "Y": Entity.Position.y},
                            "Size": {"X": Entity.Size.x, "Y": Entity.Size.y},
                            "Type": "Normal"
                        }
                        Data.append(EntityData)

                    Settings.WriteFile("./Level.json", Data)

            # Render the players hud
            Utils.RenderBar(Game.Screen, pygame.Vector2(10, 10), pygame.Vector2(200, 20), Game.Player.Health, "green", "red")
            #Utils.Text(Game.Screen, f"FPS: {math.floor(Game.Clock.get_fps())}", "Comic Sans MS", "green", 50, pygame.Vector2(10,100))
            
            if Physics.Debug:
                Debug = [
                    f"FPS: {math.floor(Game.Clock.get_fps())}",
                    f"Position X: {math.floor(Game.Player.Entity.Position.x)}, Y: {math.floor(Game.Player.Entity.Position.y)}",
                    f"Velocity X: {math.floor(Game.Player.Entity.Velocity.x)}, Y: {Game.Player.Entity.Velocity.y}",
                    f"Jump: {Game.Player.Entity.Jumping}",
                ]
                Overlay(Debug, pygame.Vector2(10, 10))
                
                
                def TouchList():
                    List = []
                    for Key in Game.Player.Entity.Touching.keys():
                        List.append(f"{Key}: {Game.Player.Entity.Touching[Key]}")

                    Overlay(List, pygame.Vector2(10, 300))
                TouchList()

            #Code to change the mouse cursor using a dumb method
            #Utils.Mouse(Game.Screen, r"./Assets/Sprites/Stationary.png")

            if Game.Player.Health.Value == 0:
                Game.State = "Die"
                Game.Menu.Loop()

            

            pygame.display.flip()

            Game.Clock.tick(Game.FrameLimit)  # limits FPS

            Game.DT = Game.Clock.tick(Game.FrameLimit) / 1000

        pygame.quit()

        if Game.Player.Client != None:
            Game.Player.Client.disconnect()

# define each game level
Game.Level5 = Game.Level("./Levels/Level5.json", pygame.Vector2(100, 350), pygame.Vector2(1000, 350), None)
Game.Level4 = Game.Level("./Levels/Level4.json", pygame.Vector2(1179, 120), pygame.Vector2(1169, 352), Game.Level5)
Game.Level3 = Game.Level("./Levels/Level3.json", pygame.Vector2(34, 202), pygame.Vector2(1202, 635), Game.Level4)
Game.Level2 = Game.Level("./Levels/Level2.json", pygame.Vector2(27, 286), pygame.Vector2(1202, 180), Game.Level3)
Game.Level1 = Game.Level("./Levels/Level1.json", pygame.Vector2(27, 286), pygame.Vector2(1202, 180), Game.Level2)

Game.Setup()
Game.Menu.Setup()
Game.LoadSettings()
Game.Menu.Loop()

Game.Loop() # initiate the gameloop