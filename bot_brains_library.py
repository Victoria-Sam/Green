import sys
import time
import traceback

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from connection import Connection


class BotBrainsSignals(QObject):
    '''
    Defines the signals available from a running BotBrains thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    draw_map0
        `object` list that contains map0, edge_labels, map1
        indicate when main window must draw graph

    update_map1
        `object` map1
        indicate when main window must update map layer 1

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    draw_map0 = pyqtSignal(object)
    update_map1 = pyqtSignal(object)


class BotBrains(QRunnable):
    '''
    BotBrains thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up

    :param user_name: string with user_name for login

    '''

    def __init__(self, user_name):
        super(BotBrains, self).__init__()

        # Add the callback signals
        self.signals = BotBrainsSignals()

        self.connection = Connection()
        self.user_name = user_name
        self.map0 = None
        self.map1 = None

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function
        '''
        try:
            result = self.main_loop()
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
            # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

    def main_loop(self):
        '''
        Основный цикл бота: подвинь поезд, заверши ход, обнови карту
        '''
        self.init_bot()

        '''
        Пока что while True, потом до ивента с концом игры
        '''
        while True:
            self.move_trains()
            self.turn()
            self.update_map1()

    def init_bot(self):
        '''
        Логинимся и рисуем начальную карту (0 и 1 слои)
        '''
        response = self.connection.login(self.user_name)
        self.draw_map0()

    def move_trains(self):
        # пойми куда пойти
        print('move train')
        pass

    def turn(self):
        # пока надо, чтобы видеть как будет двигаться поезд
        time.sleep(2)

        response = self.connection.turn()
        print('turn end')

    def draw_map0(self):
        '''
        Получаем 0 и 1 слои и посылаем сигнал в основной поток для рисования
        '''
        self.map0 = self.connection.map0()
        self.map1 = self.connection.map1()

        edge_labels = {
            (edge[0], edge[1]):
                edge[2]['length'] for edge in list(self.map0.edges(data=True))
        }

        # да-да, передается как говно
        self.signals.draw_map0.emit([self.map0, edge_labels, self.map1])

    def update_map1(self):
        '''
        Получаем 1 слой и посылаем сигнал в основной поток для перерисовки
        '''
        self.map1 = self.connection.map1()
        self.signals.update_map1.emit(self.map1)
