import pygame
import math
import random
import copy

class Map:
    def Generate(W, H): ## make generation later
        Output = []
        Line = []

        for X in range(W):
            Line.append(random.randint(0,1))

        for Y in range(H):
            Output.append(Line.copy())
            for X in range(W):
                Output[Y][X] = random.randint(0, 1)

        return Output

    class Data: # a placeholder class to store some data constantly instead of erasing it each time a function is called
        Start = None
        End = None
        Drawing = False

    def Draw(Screen): # a debug function that allows drawing with the mouse to create some physics.entity() objects
        MouseButtons = pygame.mouse.get_pressed() # Get a list of mouse buttons which are held
        if MouseButtons[0] and not Map.Data.Drawing:
            Map.Data.Start = pygame.Vector2(pygame.mouse.get_pos()) # define the start of the entity (the position)
            Map.Data.Drawing = True
        elif not MouseButtons[0] and Map.Data.Drawing:
            Map.Data.End = pygame.Vector2(pygame.mouse.get_pos()) # define the end of the entity when the mouse is released

            Physics.Entity(Map.Data.Start, Map.Data.End - Map.Data.Start, 1, "blue", False) # create the entity and calculate the size by doing End - Start

            Map.Data.Drawing = False
        if MouseButtons[0]:
            Pos = pygame.Vector2(pygame.mouse.get_pos())
            pygame.draw.rect(Screen, "red", (Map.Data.Start.x, Map.Data.Start.y, Pos.x - Map.Data.Start.x, Pos.y - Map.Data.Start.y)) # render a preview while the mouse is being dragged
        if MouseButtons[2]:
            print(pygame.mouse.get_pos())

class Particles:
    Emitters = []

    def Update(Screen):
        for Emitter in Particles.Emitters:
            Emitter: Particles.ParticleEmitter
            Emitter.Update(Screen)

    class Particle:
        def __init__(self, Size, Position, Colour, Life, Spread, Style = 1, Velocity = pygame.Vector2(0,0)):
            self.Size = Size
            self.Position = Position
            self.Life = Life
            self.Spread = Spread
            self.Colour = Colour

            Change = pygame.Vector2(random.randint(-self.Spread, self.Spread), random.randint(-self.Spread, self.Spread))
            if Style == 1:
                self.Velocity = Change
            elif Style == 2:
                self.Velocity = Velocity + Change
        def Update(self, Screen):
            #Change = pygame.Vector2(random.randint(-self.Spread, self.Spread), random.randint(-self.Spread, self.Spread))

            #self.Velocity += Change
            self.Position += self.Velocity
            pygame.draw.rect(Screen, self.Colour, pygame.Rect(self.Position, self.Size))

            self.Life -= 1

            if self.Velocity == pygame.Vector2(0, 0):
                self.Life = 0

            self.Velocity.x -= 0.1 * self.Velocity.x 
            self.Velocity.y -= 0.1 * self.Velocity.y
        
    class ParticleEmitter:
        def __init__(self, Size, Position, Colour, Count, Life, Direction = pygame.Vector2(0, 0)):
            self.Size = Size
            self.Position = Position
            self.Direction = Direction
            self.Colour = Colour

            self.Count = Count
            self.Life = Life
            self.Particles = []
            
            Particles.Emitters.append(self)

            for Index in range(Count):
                Spread = 1
                Size = pygame.Vector2(10, 10)
                Position = pygame.Vector2(random.randint(0, math.floor(self.Size.x)), random.randint(0, math.floor(self.Size.y))) + self.Position
                if self.Direction == pygame.Vector2(0,0):
                    Particle = Particles.Particle(Size, Position, self.Colour, self.Life + random.randint(-10, 10), Spread, 1)
                else:
                    Particle = Particles.Particle(Size, Position, self.Colour, self.Life + random.randint(-10, 10), Spread, 2, self.Direction)
                self.Particles.append(Particle)
        def Update(self, Screen):
            Index = 0
            for Particle in self.Particles:
                Particle: Particles.Particle
                Particle.Update(Screen)
                
                if Particle.Life <= 0:
                    #print("Particle Life Reached 0")
                    self.Particles.pop(Index)
                Index += 1

            for Index in range(self.Count - len(self.Particles)):
                Spread = 1
                Size = pygame.Vector2(10, 10)
                Position = pygame.Vector2(random.randint(0, math.floor(self.Size.x)), random.randint(0, math.floor(self.Size.y))) + self.Position
                if self.Direction == pygame.Vector2(0,0):
                    Particle = Particles.Particle(Size, Position, self.Colour, self.Life + random.randint(-10, 10), Spread, 1)
                else:
                    Particle = Particles.Particle(Size, Position, self.Colour, self.Life + random.randint(-10, 10), Spread, 2, self.Direction)
                self.Particles.append(Particle)

class Physics: # a very basic physics implementation
    Entities = [] 
    
    Debug = False

    def Update(Screen):
        for Entity in Physics.Entities: #draw pass
            Entity.Tick(Screen) # updates all entities
            Entity.Draw(Screen) # displays them onscreen

    
    class Entity: # the entity class
        def __init__(self, Position: pygame.Vector2, Size: pygame.Vector2, Mass, Colour, Gravity: bool, Collision = True, Image = None):
            self.Position = Position
            self.Size = Size

            self.Mass = Mass
            self.Velocity = pygame.Vector2(0, 0)
            self.Colour = Colour
            self.Gravity = Gravity
            self.CanCollide = Collision
            self.Rect = pygame.Rect(self.Position.x, self.Position.y, self.Size.x, self.Size.y)
            try:
                self.Image = pygame.image.load(Image)
            except:
                self.Image = None

            Physics.Entities.append(self)

            
            self.Touching = {
                "Top": False,
                "Bottom": False,
                "Left": False,
                "Right": False,

                "Air": False
            }

        def Tick(self, Screen): # updates the entity
            if self.Gravity:
                self.Position.x += self.Velocity.x
                self.Position.y += self.Velocity.y

                self.Rect = pygame.Rect(self.Position.x, self.Position.y, self.Size.x, self.Size.y)

                self.Collision(Screen)

                #self.Velocity.x = 0
                #self.Velocity.y = 0

                self.Velocity.x -= 0.1 * self.Velocity.x 
                self.Velocity.y -= 0.1 * self.Velocity.y

            self.Rect = pygame.Rect(self.Position.x, self.Position.y, self.Size.x, self.Size.y)

        def Draw(self, Screen):
            if self.Image == None:
                pygame.draw.rect(Screen, self.Colour, self.Rect)
            else:
                image = pygame.transform.scale(self.Image, self.Size)
                Screen.blit(image, self.Position)

            #imp = pygame.image.load(r".\Assets\Sprites\Stationary.png").convert_alpha()
            #image = pygame.transform.scale_by(imp, 3)
            #size = image.get_size()
            #Screen.blit(image, self.Position)
        
        def Impulse(self, Vector: pygame.Vector2): # allows you to modify the velocity of the entity
            self.Velocity.x += Vector.x
            self.Velocity.y += Vector.y

        def Collision(self, Screen): # checks if the player is withing the bounds of an object
            self.Touching = {
                "Top": False,
                "Bottom": False,
                "Left": False,
                "Right": False,

                "Air": True
            }

            def Check(Target: pygame.Rect, Collide: pygame.Rect, Ent: Physics.Entity = None):
                    if Ent.CanCollide != True:
                        return
                    elif Target.colliderect(Collide):
                        self.Touching["Air"] = False

                        Padding = 2
                        if Collide.top + Padding > Target.bottom and Collide.top - Padding < Target.bottom: 
                            #Target.Position.y = Collide.top - Target.height
                            self.Touching["Top"] = True
                        if Collide.bottom + Padding > Target.top and Collide.bottom - Padding < Target.top:
                            #Target.Position.y = Collide.bottom
                            self.Touching["Bottom"] = True
                        if Collide.left + Padding > Target.right and Collide.left - Padding < Target.right:
                            #Target.Position.x = Collide.left - Target.width
                            self.Touching["Left"] = True
                            
                            '''
                            if Ent.Gravity:
                                Ent.Velocity.x = self.Velocity.x
                                Ent.Position.x = Target.right
                                #self.Velocity.x /= 2
                            '''

                        if Collide.right + Padding > Target.left and Collide.right - Padding < Target.left:
                            #Target.Position.x = Collide.Rect.right
                            self.Touching["Right"] = True

                            '''
                            if Ent.Gravity:
                                Ent.Velocity.x = self.Velocity.x
                                Ent.Position.x = Target.left - self.Size.x
                                #self.Velocity.x /= 2
                            '''

                    if self.Touching["Top"]:
                        if self.Velocity.y > 0:
                            self.Velocity.y = 0
                            self.Position.y = (Collide.top - self.Size.y)
                    if self.Touching["Bottom"]:
                        if self.Velocity.y < 0:
                            self.Velocity.y = 0
                            self.Position.y = (Collide.bottom)
                    if self.Touching["Left"]:
                        if self.Velocity.x > 0:
                            #self.Position.x -= self.Velocity.x
                            self.Velocity.x = 0
                            self.Position.x = (Collide.left - self.Size.x)
                    if self.Touching["Right"]:
                        if self.Velocity.x < 0:
                            self.Velocity.x = 0
                            self.Position.x = (Collide.right)
            for Entity in Physics.Entities: # indexes through all the games entities
                Entity: Physics.Entity

                if Entity == self: # exits the loop if we are trying to collide the player with itself (that would break everything)
                    continue
                
                Predicted = pygame.Rect(self.Position.x + self.Velocity.x, self.Position.y + self.Velocity.y, self.Size.x, self.Size.y)
                PredictedHalf = pygame.Rect(self.Position.x + (self.Velocity.x / 2), self.Position.y + (self.Velocity.y / 2), self.Size.x, self.Size.y)

                Check(self.Rect, Entity.Rect, Entity)

                #Check(Predicted, Entity.Rect, Entity)

                Dist = pygame.Vector2(Predicted.center) - pygame.Vector2(self.Rect.center)

                UnitX = 0
                UnitY = 0

                try:
                    UnitX = Dist.x / Dist.length()
                except:
                    pass

                try:
                    UnitY = Dist.y / Dist.length()
                except:
                    pass
                
                Unit = pygame.Vector2(UnitX, UnitY)

                for Range in range(math.floor(Dist.length())):
                        Rect = pygame.Rect(self.Position + (Unit * Range), self.Size)

                        if Physics.Debug:
                            pygame.draw.rect(Screen, "pink", Rect, 1)

                        Check(Rect, Entity.Rect, Entity)

                for Range in range(math.floor(Dist.length())):
                        Rect = pygame.Rect(self.Position - (Unit * Range), self.Size)

                        if Physics.Debug:
                            pygame.draw.rect(Screen, "pink", Rect, 1)

                        Check(Rect, Entity.Rect, Entity)

                LargeRect = Entity.Rect.inflate(10, 10)
                if self.Rect.colliderect(LargeRect):
                    if type(Entity) == Physics.LinkableEntity:
                        Entity: Physics.LinkableEntity
                        Entity.Trigger(self)

                if Physics.Debug:
                    
                    '''
                    for Range in range(math.floor(Dist.length() * 1.3)):
                        Rect = pygame.Rect(self.Position - (Unit * Range), self.Size)

                        pygame.draw.rect(Screen, "pink", Rect, 1)

                        Check(Rect, Entity.Rect, Entity)
                    '''
                    
                    Rad = 2

                    for Range in range(math.floor(Dist.length() * 10)):
                        Rect = pygame.Rect(self.Position + (((Unit - pygame.Vector2(0, UnitY)) * 5) * Range), self.Size)

                        pygame.draw.circle(Screen, "red", Rect.center, Rad)

                        #Check(Rect, Entity.Rect, Entity)
                    for Range in range(math.floor(Dist.length() * 10)):
                        Rect = pygame.Rect(self.Position + (((Unit - pygame.Vector2(UnitX, 0)) * 5) * Range), self.Size)

                        pygame.draw.circle(Screen, "blue", Rect.center, Rad)

                        #Check(Rect, Entity.Rect, Entity)
                    for Range in range(math.floor(Dist.length() * 10)):
                        Rect = pygame.Rect(self.Position + (((Unit.normalize()) * 5) * Range), self.Size)

                        pygame.draw.circle(Screen, "green", Rect.center, Rad)

                        #Check(Rect, Entity.Rect, Entity)


                    print(f"Diff: {Dist.length()}")


                '''
                Dist = pygame.Vector2(0, 10)
                Unit = pygame.Vector2(0, 1)

                for Range in range(math.floor(Dist.length())):
                        Rect = pygame.Rect(self.Position + (Unit * Range), self.Size)
                        
                        if Physics.Debug:
                            pygame.draw.rect(Screen, "pink", Rect, 1)

                        Check(Rect, Entity.Rect, Entity)
                '''
                # inverts the velocity if we cant figure out how the player got here as a last resort
                #self.Position.x -= self.Velocity.x 
                #self.Position.y -= self.Velocity.y 
            if not self.Touching["Top"]:
                self.Velocity.y += 0.5

        def SetColour(self, Colour: pygame.Color):
            self.Colour = Colour
        
        def SetPos(self, Pos):
            self.Position = pygame.Vector2(Pos.x, Pos.y)

    class Player(Entity): # the player class
        def __init__(self, Position: pygame.Vector2, Size: pygame.Vector2, Mass, Colour, Gravity: bool, Image = None):
            super().__init__(Position, Size, Mass, Colour, Gravity, True, Image)

            self.Jumping = False

        def Collision(self, Screen): # checks if the player is withing the bounds of an object
            super().Collision(Screen)

        def Jump(self, Power): # a function which propells the player upwards when called
            ##Touching = self.Collision()

            if self.Touching["Top"]:
                print(f"Trying To Jump with power: {Power}")
                
                self.Jumping = True
                self.Impulse(pygame.Vector2(0, -Power))
            if self.Touching["Top"]:
                self.Jumping = False

    class LinkableEntity(Entity):
        def __init__(self, Position: pygame.Vector2, Size: pygame.Vector2, Mass, Colour, Gravity: bool, Collision = True, Image = None):
            super().__init__(Position, Size, Mass, Colour, Gravity, Collision, Image)

            self.Event = None
            self.Cooldown = 0

        def LinkEvent(self, Function):
            self.Event = Function

        def UnlinkEvent(self):
            self.Event = None

        def Trigger(self, Touched):

            if self.Cooldown < 1:
                self.Cooldown += 1
            else:
                self.Cooldown = 0
                if self.Event != None:
                    self.Event(Touched)

    class Text:
        def __init__(self, Size, Position, Text: str):
            self.Size = Size
            self.Position = Position
            self.CanCollide = False
            self.Text = Text

            Physics.Entities.append(self)

            self.Rect = pygame.Rect(self.Position.x, self.Position.y, self.Size, self.Size)
        def Tick(self, Screen):
            self.Rect = pygame.Rect(self.Position.x, self.Position.y, self.Size, self.Size)
        def Draw(self, Screen):
            def Text(Screen, Text: str, Font: str, Colour: pygame.color.Color, Size: int, Position: pygame.Vector2): # A function to render text with a specified size, font, and position
                FontFile = pygame.font.SysFont(Font, Size)
                TextSurface = FontFile.render(Text, True, Colour)
                Screen.blit(TextSurface, Position)
            Text(Screen, self.Text, "MS Trebuchet", pygame.Color(0,0,0), int(self.Size), self.Position)