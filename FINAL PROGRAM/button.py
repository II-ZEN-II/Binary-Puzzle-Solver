import pygame

pygame.init()

class Button():
    '''A basic UI button'''

    def __init__(self, text, position, dimensions, idle, hovered, clicked, font = pygame.font.SysFont("Arial", 24), font_colour = (0,0,0)):
        self.current_state = 'idle'
        self.text = text
        self.position = position
        self.dimensions = dimensions

        self.button_colour_idle = idle
        self.button_colour_hovered = hovered
        self.button_colour_clicked = clicked
        self.button_colour = self.button_colour_idle

        self.button_rect = pygame.Rect(position, dimensions)
        
        self.font_colour = font_colour
        self.text_surface = font.render(text, True, self.font_colour)
        self.text_rect = self.text_surface.get_rect(center = self.button_rect.center)
    
    def draw(self, surface):
        self.update_colour()
        pygame.draw.rect(surface, self.button_colour, self.button_rect, border_radius=10)
        surface.blit(self.text_surface, self.text_rect)
    
    def update_colour(self):
        if self.current_state == 'clicked':
            self.button_colour = self.button_colour_clicked
        elif self.current_state == 'hovered':
            self.button_colour = self.button_colour_hovered
        else:
            self.button_colour = self.button_colour_idle

    def detect(self, mouse_position, method, *args):
        if not pygame.mouse.get_pressed()[0]:
            self.current_state = 'idle'
            if self.button_rect.collidepoint(mouse_position):
                self.current_state = 'hovered'
        else:
            if self.current_state == 'hovered':
                self.current_state = 'clicked'
                method(*args)
    
