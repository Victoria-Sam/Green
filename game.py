from connection import Connection
from PyQt5.QtCore import QThreadPool
from bot_brains_library import BotBrains


class Game:
    def __init__(self, app, screen):
        self.user_name = 'Boris'
        self.user_password = 'password'
        self.connection = Connection()

        self.threadpool = QThreadPool()
        self.app = app
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
        bot_brains.signals.draw_map0.connect(self.screen.draw_map0)
        bot_brains.signals.update_map1.connect(self.screen.update_map1)

        # Стартуем бота
        self.threadpool.start(bot_brains)

    def print_output(self, s):
        pass
        # print(s)

    def thread_complete(self):
        pass
        # print("THREAD COMPLETE!")

    def closeEvent(self, event):
        self.threadpool.clear()
        event.accept()
