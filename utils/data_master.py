import sqlite3
import pygame_menu
from pygame_menu import sound, Theme
import pygame
from pygame import mixer
from menu import game_menu
from settings import *

conn = sqlite3.connect('./resources/vehicles.db')
cursor = conn.cursor()


def check_player(name: str, password: str) -> (bool, list[any]):
    """
    Check player's name and password for authentication.
    If the player doesn't exist, create a new account.
    """
    cursor.execute("SELECT * FROM users WHERE login = ?", (name,))
    player_data = cursor.fetchone()
    if player_data and player_data[2] == password:
        return True, player_data[1:]
    elif player_data and player_data[2] != password:
        return False, player_data
    else:
        cursor.execute("INSERT INTO users (login, password, money, planes, max_score, last_plane) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, password, 0, "1" + "0" * 7, 0, 1))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE login = ?", (name,))
        return True, cursor.fetchone()[1:]

def update_last_plane(player_data, plane_id):
    cursor.execute("UPDATE users SET last_plane = ? WHERE login = ?", (plane_id, player_data[0]))
    conn.commit()

def change_value(price, player_data, plane_id):
    """
    Purchase a plane and deduct its price from the player's money.
    """
    print(player_data)
    if player_data[2] - price < 0:
        return False

    new_planes = ''.join('1' if idx + 1 == int(plane_id) else val for idx, val in enumerate(player_data[3]))
    print(new_planes)

    cursor.execute("UPDATE users SET money = ?, planes = ? WHERE login = ?",
                   (player_data[2] - price,
                    new_planes,
                    player_data[0]))
    conn.commit()
    return True


def change_score_money(player_data, score):
    """
    Update player's money and maximum score.
    """
    new_max_score = max(player_data[4], score)
    cursor.execute("UPDATE users SET money = ?, max_score = ? WHERE login = ?",
                   (player_data[2] + score, new_max_score, player_data[0]))
    conn.commit()


def show_info(player_data):

    """
    Show leaderboard and provide buttons for additional actions.
    """

    cursor.execute("SELECT login, max_score FROM users ORDER BY max_score DESC LIMIT 10")
    leaderboard_data = cursor.fetchall()

    pygame.init()
    pygame.display.set_caption('Results')
    win = mixer.Sound('./data/music/win.mp3')
    win.set_volume(0.5)
    win.play()

    mixer.music.load('./data/music/theme.mp3')
    mixer.music.set_volume(0.2)
    mixer.music.play(-1)
    background = pygame_menu.baseimage.BaseImage('./data/backgrounds/background.jpg')
    surface = pygame.display.set_mode(sc_size)

    my_theme = Theme(background_color=(0, 0, 0, 0), title_background_color=(4, 47, 126),
                     title_font_shadow=True, title_font=pygame_menu.font.FONT_8BIT,
                     widget_padding=25, widget_font=pygame_menu.font.FONT_8BIT,
                     title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE,
                     widget_font_color=pygame.Color('white'))
    my_theme.background_color = background
    menu = pygame_menu.Menu('Sky Bandits 3', width, height, theme=my_theme)
    menu.add.label('GAME OVER', font_size=50)
    menu.add.label('Leaderboard')
    table = menu.add.table(font_size=30, border_color=pygame.Color('white'), border_width=3)
    for gamer in list(map(lambda x: (x[0], x[1]), leaderboard_data)):
        table.add_row(gamer)
    continue_btn = menu.add.button('Continue', font_size=35)
    menu.add.button('Quit', pygame_menu.events.EXIT, font_size=30)
    menu.center_content()
    engine = sound.Sound(-1)
    engine.set_sound(pygame_menu.sound.SOUND_TYPE_CLICK_MOUSE, './data/music/button.wav')
    menu.set_sound(engine, recursive=True)

    while True:
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN and continue_btn._mouseover and event.button == 1:
                win.stop()
                game_menu.start(player_data)

            if event.type == pygame.QUIT:
                exit()

        if menu.is_enabled():
            menu.update(events)
            menu.draw(surface)
        pygame.display.flip()
