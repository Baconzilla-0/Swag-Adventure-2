import pygame

class Configs:
    class Ranged:
        def __init__(self, Damage, Clip: dict, Spread: int, Rate: int, Amount: int, Bounce: bool, Sprite):
            self.Clip = Clip
            self.Spread = Spread
            self.Rate = Rate
            self.Amount = Amount
            self.Bounce = Bounce
            self.Sprite = pygame.image.load(Sprite)
    class Melee:
        def __init__(self, Speed: int, Sprite):
            self.Speed = Speed
            
            self.Sprite = pygame.image.load(Sprite)

class Items:
    class Item:
        def __init__(self, Name, Description, StackSize, Modifiers, Sprite):
            self.Name = Name
            self.Description = Description
            self.Stack = StackSize
            self.Modifiers = Modifiers
            self.Sprite = pygame.image.load(Sprite)
        
class Weapons:
    class Ranged(Items.Item):
        def __init__(self, Name, Description, WeaponConfig: Configs.Ranged, StackSize = 1, Modifiers = None, Sprite = None):
            super().__init__(Name, Description, StackSize, Modifiers, Sprite)

            self.Config = WeaponConfig
    class Melee(Items.Item):
        def __init__(self, Name, Description, MeleeConfig: Configs.Melee, StackSize = 1, Modifiers = None, Sprite = None):
            super().__init__(Name, Description, StackSize, Modifiers, Sprite)

            self.Config = MeleeConfig