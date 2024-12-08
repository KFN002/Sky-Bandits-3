import sqlite3
import webbrowser
from random import choice


def redirect(plane):   # запуск браузера с инфой: ссылка в бд
    con = sqlite3.connect('./resources/vehicles.db')
    cur = con.cursor()
    web_page = cur.execute(f"""SELECT info_link FROM planes WHERE model = '{plane[0][0]}'""").fetchone()
    con.close()
    webbrowser.open(web_page[0])
    if choice([True, False, False, False]):
        webbrowser.open('https://www.youtube.com/watch?v=VE03Lqm3nbI')
