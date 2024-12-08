import pygame_menu
from pygame_menu import sound, Theme
import pygame
from pygame import mixer
from menu import game_menu
from settings import sc_size, height, width
from utils.data_master import check_player


def start_game(menu):  # проверка введенных данных, запуск следующего меню
    player_info = list(menu.get_input_data().values())

    if len(player_info[0]) >= 4 and len(player_info[1]) >= 4:
        ok, data = check_player(*player_info)
        if not ok:
            menu.reset_value()
        else:
            mixer.music.stop()
            menu.close()
            game_menu.start(data)
    else:
        menu.reset_value()


def start_menu():  # стартовое меню, логин и тд
    pygame.init()
    pygame.display.set_caption('Sky Bandits 3')
    mixer.music.load('./data/music/theme.mp3')
    mixer.music.set_volume(0.2)
    mixer.music.play(-1)   # фоновая музыка

    background = pygame_menu.baseimage.BaseImage('./data/backgrounds/background.jpg')
    surface = pygame.display.set_mode(sc_size)

    my_theme = Theme(background_color=(0, 0, 0, 0), title_background_color=(4, 47, 126),
                     title_font_shadow=True, title_font=pygame_menu.font.FONT_8BIT,
                     widget_padding=25, widget_font=pygame_menu.font.FONT_8BIT,
                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
                     widget_font_color=pygame.Color('white'))
    my_theme.background_color = background
    menu = pygame_menu.Menu('Sky Bandits 3', width, height, theme=my_theme)
    menu.add.image('./data/logos/game_dev_logo.jpg', load_from_file=True,
                   align=pygame_menu.locals.ALIGN_RIGHT)
    menu.add.label('Login or Sign up', font_size=40)
    menu.add.text_input('Name:', font_size=20)
    menu.add.text_input('Password:', font_size=20)
    play_btn = menu.add.button('Play', start_game(menu), font_size=42)
    menu.add.button('Quit', pygame_menu.events.EXIT, font_size=25)
    menu.center_content()
    menu.add.label('Game by KFN001', align=pygame_menu.locals.ALIGN_LEFT,
                   font_color=pygame.Color('grey'), font_size=8)
    engine = sound.Sound(-1)
    engine.set_sound(pygame_menu.sound.SOUND_TYPE_CLICK_MOUSE, './data/music/button.wav')   # звкововой движок
    engine.set_sound(pygame_menu.sound.SOUND_TYPE_KEY_ADDITION, './data/music/button.wav')
    engine.set_sound(pygame_menu.sound.SOUND_TYPE_KEY_DELETION, './data/music/button.wav')

    menu.set_sound(engine, recursive=True)

    running = True
    while running:
        events = pygame.event.get()
        if play_btn.is_selected():
            start_game(menu)  # начало игры
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if menu.is_enabled():
            menu.update(events)
            menu.draw(surface)
        pygame.display.flip()
    exit()


start_menu()
