import urllib.request
import pygame
import time


def test_connection(host='http://google.com'):  # проверка подключения игрока к сети
    try:
        urllib.request.urlopen(host)
        return True
    except Exception:
        pygame.init()
        size = width, height = 1200, 600
        screen = pygame.display.set_mode(size)
        screen.fill('black')
        pygame.display.set_caption('OFFLINE ERROR')
        font = pygame.font.Font('../data/fonts/font.ttf', 32)
        text = font.render('No internet connection', True, (0, 0, 0))
        textrect = text.get_rect()
        textrect.center = (width // 2, height // 2)
        while True:
            screen.fill('white')
            screen.blit(text, textrect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                pygame.display.update()
            time.sleep(5)
            return False