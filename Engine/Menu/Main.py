import math

import pygame
from ..Utils import *
from .Styles import Styles

class Menu:
    class Scene:
        def __init__(self):
            self.Components = []
        def Draw(self, Screen):
            for Component in self.Components:
                Component: Menu.Component
                Component.Update(Screen)
                #print(Component)
    class Component:
        def __init__(self, Size: pygame.Vector2, Position: pygame.Vector2, Colours: dict):
            self.Size = Size
            self.Position = Position

            self.Clicked = False
            self.MouseDown = False
            self.MouseUp = False

            for Key in Colours.keys():
                self.__setattr__(f"{Key}Colour", Colours[Key])

        def SetPos(self, X, Y):
            self.Position = pygame.Vector2(X, Y)

        def Update(self, Screen):
            self.Clicked = False
            self.MouseUp = False

            if pygame.mouse.get_pressed()[0]:
                if pygame.Rect(self.Position, self.Size).collidepoint(pygame.mouse.get_pos()):
                    self.MouseDown = True
                    return None
            if not pygame.mouse.get_pressed()[0]:
                if self.MouseDown:
                    self.Clicked = True  
                    self.MouseUp = True
                    self.MouseDown = False
            
            
    class Text(Component):
        def __init__(self, Size, Position, Text: str, Colours = {"Text": pygame.Color(255, 255, 255)}):
            super().__init__(pygame.Vector2(Size, 1), Position, Colours)
            
            self.Text = Text

        def Update(self, Screen):
            Utils.Text(Screen, self.Text, "MS Trebuchet", self.TextColour, int(self.Size.x), self.Position)

    class Button(Component):
        def __init__(self, Size, Position, Text: str, Colours = Styles.NEUTRAL):
            super().__init__(Size, Position, Colours)
            
            self.Text = Text

        def Update(self, Screen):
            super().Update(Screen)

            if pygame.Rect(self.Position, self.Size).collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(Screen, self.HoverColour, pygame.Rect(self.Position, self.Size))
            else:
                pygame.draw.rect(Screen, self.IdleColour, pygame.Rect(self.Position, self.Size))
                
            Font = "MS Trebuchet"
            FontFile = pygame.font.SysFont(Font, int(self.Size.y))
            TextSurface = FontFile.render(self.Text, True, self.TextColour)
            Rect = TextSurface.get_rect()

            Pos = self.Position + pygame.Vector2(0, self.Size.y / 6)
            Screen.blit(TextSurface, Pos)

    class Slider(Component):
        def __init__(self, HandleSize, BarLength, Position, Colours = {"Handle": pygame.Color(50, 50, 50), "Back": pygame.Color(100, 100, 100)}):
            super().__init__(HandleSize, Position, Colours)
            self.Held = False
            self.MouseOffset = pygame.Vector2(0, 0)
            self.BarLength = BarLength
            self.InitPos = Position
            self.Level = 0

        def Update(self, Screen):
            Size = pygame.Vector2(self.BarLength, self.Size.y)
            pygame.draw.rect(Screen, self.BackColour, pygame.Rect(self.InitPos, Size))
            pygame.draw.rect(Screen, self.HandleColour, pygame.Rect(self.Position, self.Size))
            super().Update(Screen)

            if self.MouseDown and not self.Held:
                self.Held = True
                self.MouseOffset = pygame.Vector2(pygame.mouse.get_pos()) - self.Position
            elif self.MouseDown and self.Held:
                Pos = pygame.Vector2(pygame.mouse.get_pos())
                self.Level = ((self.Position.x - self.InitPos.x) / (self.BarLength - self.Size.x))
                if self.Level <= 1.0 and self.Level >= 0.0:
                    self.SetPos(Pos.x - (self.Size.x/2), self.Position.y)
            elif not self.MouseDown and self.Held:
                self.Held = False

            self.Level = ((self.Position.x - self.InitPos.x) / (self.BarLength - self.Size.x))

            if self.Level > 1.0:
                self.Position.x = (self.BarLength - self.Size.x) + self.InitPos.x
            if self.Level < 0.0:
                self.Position.x = self.InitPos.x

        def Set(self, Level):
            NewPosX = (Level * (self.BarLength - self.Size.x))
            Pos = pygame.Vector2(NewPosX + self.InitPos.x, self.Position.y)
            self.Level = ((self.Position.x - self.InitPos.x) / (self.BarLength - self.Size.x))
            self.SetPos(Pos.x - (self.Size.x/2), self.Position.y)
            if self.Level > 1.0:
                self.Position.x = (self.BarLength - self.Size.x) + self.InitPos.x
            if self.Level < 0.0:
                self.Position.x = self.InitPos.x
    class TickBox(Component):
        def __init__(self, Size, Position, State = False, Colours = {"Back": pygame.Color(45, 45, 45)}):
            super().__init__(Size, Position, Colours)
            self.State = State

        def Update(self, Screen):
            super().Update(Screen)

            Rect = pygame.Rect(self.Position, self.Size)
            pygame.draw.rect(Screen, self.BackColour, Rect)

            if self.Clicked:
                if self.State:
                    self.State = False
                else:
                    self.State = True

                print(f"StateChanged! Now: {self.State}, {self.Clicked}")
            if self.State:
                imp = pygame.image.load("./Assets/Menu/Ding.png").convert_alpha()
            else:
                imp = pygame.image.load("./Assets/Menu/BaBow.png").convert_alpha()
            image = pygame.transform.scale_by(imp, 3)
            self.Size = pygame.Vector2(image.get_size())
            Screen.blit(image, self.Position)

    class Image(Component):
        def __init__(self, Size, Position, Path):
            super().__init__(Size, Position, {})

            self.Image = pygame.image.load(Path).convert_alpha()
        def Update(self, Screen):
            
            imp = self.Image
            image = pygame.transform.scale(imp, self.Size)
            Screen.blit(image, self.Position)

    class InputBox(Component):
        def __init__(self, Size, Position, Text: str, Colours = {"Text": pygame.Color(255, 255, 255), "Back": pygame.Color(45, 45, 45)}):
            super().__init__(pygame.Vector2(Size.x, Size.y), Position, Colours)
            
            self.PlaceHolder = Text
            self.Text = self.PlaceHolder
            self.Selected = False

        def Update(self, Screen, Event = None):
            super().Update(Screen)

            if self.Clicked:
                self.Selected = True
                self.Text = ""
            elif pygame.mouse.get_pressed()[0]:
                if not pygame.Rect(self.Position, self.Size).collidepoint(pygame.mouse.get_pos()):
                    self.Selected = False
                    if self.Text == "":
                        self.Text = self.PlaceHolder

            if self.Selected:
                if Event != None:
                    if Event.type == pygame.KEYDOWN:
                        # Check for backspace
                        if Event.key == pygame.K_BACKSPACE:
                            self.Text = self.Text[:-1]
                        elif Event.key == pygame.K_RETURN:
                            self.Selected = False
                        else:
                            self.Text += Event.unicode
                            
            Rect = pygame.Rect(self.Position, self.Size)
            pygame.draw.rect(Screen, self.BackColour, Rect)

            Utils.Text(Screen, self.Text, "MS Trebuchet", self.TextColour, int(self.Size.y), self.Position)

    class List(Component):
        def __init__(self, Size, Position, List: list, TextSize = 40, Selectable = True, Colours = {"Text": pygame.Color(255, 255, 255), "Back": pygame.Color(45, 45, 45), "Item": pygame.Color(60, 60, 60)}):
            super().__init__(pygame.Vector2(Size.x, Size.y), Position, Colours)

            self.List = List
            self.Selectable = Selectable
            self.TextSize = TextSize
        def SetList(self, List):
            self.List = List

        def Update(self, Screen):
            super().Update(Screen)
            pygame.draw.rect(Screen, self.BackColour, pygame.Rect(self.Position, self.Size))

            Index = 0
            for Item in self.List:
                Utils.Text(Screen, str(Item), "MS Trebuchet", self.TextColour, self.TextSize, pygame.Vector2(self.Position.x, (self.TextSize * Index) + self.Position.y))
                print(Item)
                Index += 1
    class LabeledTickBox(Component):
        def __init__(self, Position: pygame.Vector2, Text, State = False, Colours = Styles.NEUTRAL):
            super().__init__(pygame.Vector2(0,0), Position, Colours)

            self.TickBox = Menu.TickBox(pygame.Vector2(0,0), pygame.Vector2(self.Position.x, self.Position.y), State, Colours)
            self.Label = Menu.Text(60, pygame.Vector2(self.Position.x + 60, self.Position.y), Text, Colours)
        def Update(self, Screen):
            self.TickBox.Update(Screen)
            self.Label.Update(Screen)

    class Rect(Component):
        def __init__(self, Size: pygame.Vector2, Position: pygame.Vector2, Colours: dict):
            super().__init__(Size, Position, Colours)
        
        def Update(self, Screen):
            super().Update(Screen)
            pygame.draw.rect(Screen, self.BackColour, pygame.Rect(self.Position, self.Size))
        
    class Colourpicker(Component):
        def __init__(self, Size: int, Position: pygame.Vector2, Colours: dict):
            super().__init__(Size, Position, Colours)
            
            self.RSlider = Menu.Slider(pygame.Vector2(20, 20), 200, pygame.Vector2(40, 0) + self.Position, {"Handle": pygame.Color(255, 0, 0), "Back": pygame.Color(100, 100, 100)})
            self.GSlider = Menu.Slider(pygame.Vector2(20, 20), 200, pygame.Vector2(40, 25) + self.Position, {"Handle": pygame.Color(0, 255, 0), "Back": pygame.Color(100, 100, 100)})
            self.BSlider = Menu.Slider(pygame.Vector2(20, 20), 200, pygame.Vector2(40, 50) + self.Position, {"Handle": pygame.Color(0, 0, 255), "Back": pygame.Color(100, 100, 100)})

            self.ColourRect = Menu.Rect(pygame.Vector2(35, 70), pygame.Vector2(0, 0) + self.Position, Styles.NEUTRAL)

        def Update(self, Screen):
            self.RSlider.Update(Screen)
            self.GSlider.Update(Screen)
            self.BSlider.Update(Screen)
            
            self.Red = Utils.Clamp((self.RSlider.Level) * 255, 255, 0)
            self.Green = Utils.Clamp((self.GSlider.Level) * 255, 255, 0)
            self.Blue = Utils.Clamp((self.BSlider.Level) * 255, 255, 0)

            self.Red, self.Green, self.Blue = math.floor(self.Red), math.floor(self.Green), math.floor(self.Blue)

            self.ColourRect.BackColour = pygame.Color(self.Red, self.Green, self.Blue)
            self.ColourRect.Update(Screen)