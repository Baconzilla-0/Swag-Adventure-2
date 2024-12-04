import pygame

class Utils:
    def Text(Screen, Text: str, Font: str, Colour: pygame.color.Color, Size: int, Position: pygame.Vector2): # A function to render text with a specified size, font, and position
        FontFile = pygame.font.SysFont(Font, Size)
        TextSurface = FontFile.render(Text, True, Colour)
        Screen.blit(TextSurface, Position)
    
    def Mouse(Screen, Image):
        # SET_VISIBLE of cursor to False
        pygame.mouse.set_visible(False) 
        # Set the variable cursor_size to 10

        imp = pygame.image.load(Image).convert_alpha()
        image = pygame.transform.scale_by(imp, 3)
        size = image.get_size()
        Screen.blit(image, (pygame.mouse.get_pos()[0] - (size[0] / 2), pygame.mouse.get_pos()[1] - (size[1] / 2)))

    def Clamp(x, max, min):
        if x <= max and x >= min:
            return x
        elif x > max:
            return max
        else:
            return min
        
    def RenderBar(Screen, Position, Size, IntConstrained, FG, BG):
        pygame.draw.rect(Screen, BG, pygame.Rect(Position, Size))

        Width = (IntConstrained.Value / IntConstrained.Max) * Size.x
        pygame.draw.rect(Screen, FG, pygame.Rect(Position, pygame.Vector2(Width, Size.y)))

    def PlaySound(Path, Volume):
        pygame.mixer.music.load(Path)
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play()