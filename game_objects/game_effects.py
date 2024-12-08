import random
import pygame


def render_glitch_text(text, font, color='black'):
    base_text = font.render(text, True, color)
    offset_x, offset_y = random.randint(-5, 5), random.randint(-5, 5)
    glitch_text = pygame.Surface((base_text.get_width() + 10, base_text.get_height() + 10), pygame.SRCALPHA)
    glitch_text.blit(base_text, (offset_x, offset_y))
    return glitch_text