import threading

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMessageBox

from bot_brains_library import BotBrains


class Game:
    def __init__(self, screen, user_name, user_password,
                 game_name, num_turns=-1, num_players=1):
        self.user_name = user_name
        self.user_password = user_password
        self.name = game_name
        self.num_turns = num_turns
        self.num_players = num_players
        self.threadpool = QThreadPool()
        self.event_stop = threading.Event()
        self.ratings_stop = threading.Event()
        self.screen = screen

        self.map = None
        self.home = None
        self.posts = None

        self.start_bot()

    def start_bot(self):
        # Создаем бота в новом потоке
        bot_brains = BotBrains(self)

        # добавление действий на различные сигналы
        # (finished и result возможно и пригодятся)
        bot_brains.signals.finished.connect(self.thread_complete)
        bot_brains.signals.result.connect(self.print_output)
        bot_brains.signals.error.connect(self.show_error_mesage)
        bot_brains.signals.draw_map0.connect(self.screen.draw_map0)
        bot_brains.signals.update_map1.connect(self.screen.update_map1)
        bot_brains.signals.update_ratings.connect(
            self.screen.connect_widget.ratings_window.update_ratings)
        bot_brains.signals.game_over.connect(
            self.screen.connect_widget.ratings_window.set_game_over_text)

        # Стартуем бота
        self.threadpool.start(bot_brains)

    def print_output(self, s):
        pass
        # print(s)

    def thread_complete(self):
        pass
        # print("THREAD COMPLETE!")

    def show_error_mesage(self, text):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(text)
        msgBox.setWindowTitle("Error")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()
