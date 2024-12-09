import os
import games.game_2
import games.game_1
import games.game_3
import games.game_4
import games.sandbox
from utils import data_master
from info.show_info import redirect
from random import choice
from utils.data_master import *


def compare_data(plane, planes_available, all_planes):   # проврека наличия самолета в приобритенных
    planes_available = list(str(planes_available))
    all_planes = list(map(lambda x: x[0], all_planes))
    return planes_available[all_planes.index(plane[0][0])]


def draw_background(plane, buy_btn, pic, planes_available, all_planes):  # подгрузка пикчи самолета, покупка
    result = cursor.execute(f"""SELECT hist_image, price FROM planes WHERE model = '{plane[0][0]}'""").fetchone()

    pic_path = os.path.join(os.getcwd().replace("\\", "/"), result[0])

    pic.set_image(pygame_menu.baseimage.BaseImage(pic_path))
    if compare_data(plane, planes_available, all_planes) == '1':
        buy_btn.set_title('')
    else:
        buy_btn.set_title(f'Buy {result[1]}')


def start_game(plane_status, plane, player_data):   # запуск уровня, подгрузка данных
    if plane_status.get_title() == '':
        plane_data = cursor.execute(f"""SELECT * FROM planes WHERE model = '{plane[0][0]}'""").fetchone()

        mixer.stop()
        mixer.music.load('./data/music/mission.mp3')
        mixer.music.set_volume(0.2)
        mixer.music.play(-1)

        if choice([True, False]):
            if choice([True, False]):
                games.game_1.play(list(plane_data), player_data)
            else:
                games.game_2.play(list(plane_data), player_data)   
        else:
            if choice([True, False]):
                games.game_4.play(list(plane_data), player_data)
            else:
                mixer.stop()
                mixer.music.load('./data/music/kover-vertolet.mp3')
                mixer.music.set_volume(0.8)
                mixer.music.play(-1)
                games.game_3.play(list(plane_data), player_data)


def buy_plane(plane, player_data, planes_available, all_planes, menu):   # покупка самолета
    plane_data = cursor.execute(f"""SELECT id, price FROM planes WHERE model = '{plane[0][0]}'""").fetchone()

    if compare_data(plane, planes_available, all_planes) == '0':
        data_master.change_value(plane_data[1], player_data, plane_data[0])
        menu.close()
        _, user_data = data_master.check_player(*player_data[:2])
        print("data after purchase:", user_data)
        start(user_data)


def start(player_data):
    # меню с выбором самолета, его приобретением

    print("player_data on start:", player_data)
    pygame.init()
    planes = []

    result = cursor.execute("""SELECT model, hist_image, price from planes ORDER BY price""").fetchall()
    for i, j in enumerate(result):
        planes.append((j[0], i))
    money = player_data[2]

    pygame.display.set_caption('Sky Bandits 3')
    mixer.music.load('./data/music/arcade_theme.mp3')
    mixer.music.set_volume(0.2)
    mixer.music.play(-1)

    background = pygame_menu.baseimage.BaseImage('./data/backgrounds/hangar.png')

    surface = pygame.display.set_mode(sc_size)
    my_theme = Theme(background_color=(0, 0, 0, 0), title_background_color=(4, 47, 126),
                     title_font_shadow=True, title_font=pygame_menu.font.FONT_8BIT,
                     widget_padding=25, widget_font=pygame_menu.font.FONT_8BIT,
                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
                     widget_font_color=pygame.Color('white'))
    my_theme.background_color = background

    menu = pygame_menu.Menu('Sky Bandits 3', width, height, theme=my_theme)
    menu.add.label(f'Money {money}', align=pygame_menu.locals.ALIGN_RIGHT, font_size=24)
    current_plane = menu.add.selector('Select Plane', planes, align=pygame_menu.locals.ALIGN_RIGHT, font_size=24)
    pic_place = menu.add.image("data/real_pics/i-15.jpg", load_from_file=True, align=pygame_menu.locals.ALIGN_RIGHT)
    info_btn = menu.add.button('View plane info', align=pygame_menu.locals.ALIGN_RIGHT, font_size=16)
    buy_button = menu.add.button('', buy_plane(current_plane.get_value(),
                                               player_data, player_data[3], planes, menu),
                                 align=pygame_menu.locals.ALIGN_RIGHT, font_size=26)
    start_btn = menu.add.button('Play level', align=pygame_menu.locals.ALIGN_LEFT, font_size=30)
    menu.add.button('Quit', pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_RIGHT, font_size=18)

    engine = sound.Sound(-1)
    engine.set_sound(pygame_menu.sound.SOUND_TYPE_CLICK_MOUSE, './data/music/button.wav')
    menu.set_sound(engine, recursive=True)
    running = True

    while running:
        draw_background(current_plane.get_value(), buy_button, pic_place, player_data[3], planes)
        events = pygame.event.get()

        for event in events:  # проверка кнопок: сделанно именно так, тк встроенные функции не полностью удовлетворяли
            # нужному функционалу

            if event.type == pygame.MOUSEBUTTONDOWN and buy_button._mouseover and event.button == 1:
                buy_plane(current_plane.get_value(), player_data, player_data[3], planes, menu)

            if event.type == pygame.MOUSEBUTTONDOWN and start_btn._mouseover and event.button == 1:
                start_game(buy_button, current_plane.get_value(), player_data)

            if event.type == pygame.MOUSEBUTTONDOWN and info_btn._mouseover and event.button == 1:
                redirect(current_plane.get_value())

            if event.type == pygame.QUIT:
                running = False

        if menu.is_enabled():
            menu.update(events)
            menu.draw(surface)
        pygame.display.flip()
    exit()
