import sys
import time
import traceback
import networkx as nx

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from connection import Connection
from classes_library import Line, Point, Graph, Map


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

    def __init__(self, game):
        super(BotBrains, self).__init__()

        # Add the callback signals
        self.signals = BotBrainsSignals()
        self.game = game

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
            self.update_map1()
            self.move_trains(1, 1, 1)
            self.turn()

    def init_bot(self):
        '''
        Логинимся и рисуем начальную карту (0 слой)
        '''
        login_response = self.game.connection.login(self.game.user_name)
        self.game.home = login_response.home
        self.game.player_id = login_response.player_id
        self.nx_graph = nx.Graph()
        self.draw_map0()

    def draw_map0(self):
        '''
        Получаем 0 и 1 слои и посылаем сигнал в основной поток для рисования
        '''
        map_0_response = self.game.connection.map0()  # it's response now
        if map_0_response.result_code == 0:
            self.game.map = map_0_response.graph_map
        self.game.nx_graph = nx.Graph()
        for point in self.game.map.graph.points:
            self.game.nx_graph.add_node(point.idx)
        for line in self.game.map.graph.lines:
            self.game.nx_graph.add_edge(line.points[0].idx, line.points[1].idx,
                                        length=line.length, idx=line.idx)

        map_1_response, post_types = self.game.connection.map1()
        if map_1_response.result_code == 0:
            self.game.posts = map_1_response.posts
            self.game.trains = map_1_response.trains
        edge_labels = {
            (edge[0], edge[1]):
                [edge[2]['length'], edge[2]['idx']] for edge in list(
                    self.game.nx_graph.edges(data=True))
        }

        self.signals.draw_map0.emit(
            [self.game, edge_labels, post_types])

    def update_map1(self):
        '''
        Получаем 1 слой и посылаем сигнал в основной поток для перерисовки
        '''
        map_1_response, _ = self.game.connection.map1()
        if map_1_response.result_code == 0:
            self.game.posts = map_1_response.posts
            self.game.trains = map_1_response.trains
        self.signals.update_map1.emit(self.game)

    def move_trains(self, line_idx, speed, train_idx):
        # пойми куда пойти
        self.game.connection.move(line_idx, speed, train_idx)

    def turn(self):
        # пока надо, чтобы видеть как будет двигаться поезд
        time.sleep(2)

        response = self.game.connection.turn()
        print('turn end')
