import sys
import time
import traceback
import networkx as nx

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from connection import Connection
from classes_library import Line, Point, Graph, Map, Market, get_line, \
    get_point
from dijkstra import the_best_way


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
        self.game.hijack_probability = 0.25
        self.game.parasites_probability = 0.25
        self.game.refugees_probability = 0.5
        self.current_ways = {}
        self.markets = None
        self.market_train = {}

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
        self.potencial_product = {}
        self.game_end = False
        '''
        Пока что while True, потом до ивента с концом игры
        '''
        self.get_best_ways(the_best_way(
            self.game.map.graph,
            self.game.home.idx)
        )
        while not self.game_end:
            self.update_map1()
            self.find_trains_way()
            # time.sleep(0.5)
            self.turn()

    def get_city(self, idx):
        return self.game.posts[idx]

    def init_bot(self):
        '''
        Логинимся и рисуем начальную карту (0 слой)
        '''
        login_response = self.game.connection.login(self.game.user_name)
        self.game.home = login_response.home
        self.game.player_id = login_response.player_id
        self.game.own_trains = login_response.trains
        self.game.hijackers_cd = 0
        self.game.parasites_cd = 0
        self.game.refugees_cd = 0
        self.nx_graph = nx.Graph()
        self.draw_map0()

    def get_best_ways(self, best_way):
        self.best_ways_markets = {}
        self.best_ways_storages = {}
        for key, val in best_way.items():
            if val[-2].points[1].point_type == 2 or \
               val[-2].points[0].point_type == 2:
                self.best_ways_markets[key] = val
            else:
                self.best_ways_storages[key] = val

    def draw_map0(self):
        '''
        Получаем 0 и 1 слои и посылаем сигнал в основной поток для рисования
        '''
        map_0_response = self.game.connection.map0()  # it's response now
        if map_0_response.result_code == 0:
            self.game.map = map_0_response.graph_map
        self.game.nx_graph = nx.Graph()
        for point in self.game.map.graph.points.values():
            self.game.nx_graph.add_node(point.idx)
        for line in self.game.map.graph.lines.values():
            self.game.nx_graph.add_edge(line.points[0].idx,
                                        line.points[1].idx,
                                        length=line.length, idx=line.idx)
        map_1_response, post_types = self.game.connection.map1()
        if map_1_response.result_code == 0:
            self.game.posts = map_1_response.posts
            self.game.trains = map_1_response.trains
        for current_point in self.game.map.graph.points.values():
            if current_point.post_id is not None:
                current_point.point_type = post_types[current_point.idx]
        for line in self.game.map.graph.lines.values():
            for temp_point in line.points:
                if temp_point.post_id is not None:
                    temp_point.point_type = post_types[temp_point.idx]
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
        Также обновляем информацию о своих поездах
        '''
        player_response = self.game.connection.player()
        if player_response.result_code == 0:
            self.game.own_trains = player_response.trains
        if self.game.hijackers_cd != 0:
            self.game.hijackers_cd -= 1
        if self.game.parasites_cd != 0:
            self.game.parasites_cd -= 1
        if self.game.refugees_cd != 0:
            self.game.refugees_cd -= 1
        for event in player_response.town.events:
            if event.event_type == 2:
                self.game.hijackers_cd += event.hijackers_power * 2
            elif event.event_type == 3:
                self.game.parasites_cd += event.parasites_power * 2
            elif event.event_type == 4:
                self.game.refugees_cd += event.refugees_number * 25
        map_1_response, _ = self.game.connection.map1()
        if map_1_response.result_code == 0:
            self.game.posts = map_1_response.posts
            self.game.trains = map_1_response.trains
            self.game.home.town = self.game.posts[self.game.home.idx]
            # output = open('output.txt', 'w')        # test info
            # print(self.game.trains, '\n', file=output)
            # !!! Тут должны быть апгрейды(вроде как)
            # if map_1_response.trains[0].next_level_price is not None:
            #     if self.game.home.town.armor >=\
            #             map_1_response.trains[0].next_level_price:
            #         self.game.connection.upgrade(
            #             [], [map_1_response.trains[0].train_id])
        self.signals.update_map1.emit(self.game)

    def move_trains(self, line_idx, speed, train_idx):
        # пойми куда пойти
        self.game.connection.move(line_idx, speed, train_idx)

    def turn(self):
        response = self.game.connection.turn()
        # print('turn end')

    def next_line(self, train):
        line = self.current_ways[train.train_id].pop(0)
        if isinstance(line, list):
            line = line[0]
        # print(line)
        train_line = get_line(self.game.map.graph, train.line_id)
        train_point = train_line.points[0 if train.position == 0 else 1]
        if get_line(self.game.map.graph, line.idx).points[0].idx == \
                train_point.idx:
            speed = 1
        else:
            speed = -1
        self.move_trains(line.idx, speed, train.train_id)

    def start_way(self, train):
        shortest = 1000000000
        best_way_storage = None
        best_storage = None
        for key, val in self.best_ways_storages.items():
            if not best_way_storage or best_way_storage[-1] > val[-1]:
                best_way_storage = val
                best_storage = key
        best_market, best_way = self.choose_way(best_storage,
                                                best_way_storage,
                                                train)
        best_way = best_way[0:-1]
        if best_way:
            self.market_train[best_market] = train.train_id
            self.current_ways[train.train_id] = best_way
            self.current_ways[train.train_id] += best_way[::-1]
            self.current_ways[train.train_id].append(best_market)
            self.next_line(train)

    def choose_way(self, best_storage, best_way_storage, train):
        best_way_market = None
        best_market = None
        for key, val in self.best_ways_markets.items():
            if not self.market_train.get(key):
                market = self.get_city(key)
                if not best_way_market:
                    best_way_market = val
                    best_market = market
                if self.isEnough(best_way_storage, market, val, train):
                    return (best_storage, best_way_storage)
                if min(best_market.product, train.goods_capacity) -\
                    2*best_way_market[-1] <\
                        min(market.product, train.goods_capacity) - 2*val[-1]:
                    best_market = market
                    best_way_market = val
        self.potencial_product[train.train_id] = min(best_market.product,
                                                     train.goods_capacity)
        return (best_market.point_id, best_way_market)

    def isEnough(self, best_way_storage, market, way_market, train):
        potencial = sum(self.potencial_product.values())
        flag1 = (self.game.home.town.product + potencial) /\
            (self.game.home.town.population+2) >\
            2*best_way_storage[-1] + 2 * way_market[-1]
        flag2 = min(market.product, train.goods_capacity) > 2*way_market[-1]
        return flag1 and flag2

    def find_trains_way(self):
        for idx, train in self.game.trains.items():
            if train.cooldown == 0:
                if self.current_ways.get(train.train_id):
                    if(train.speed == 0):
                        if len(self.current_ways[train.train_id]) != 1:
                            self.next_line(train)
                        else:
                            self.market_train.pop(
                                self.current_ways[train.train_id].pop(0))
                            self.current_ways.pop(train.train_id)
                            if self.potencial_product.get(train.train_id):
                                self.potencial_product.pop(train.train_id)
                            self.start_way(train)
                else:
                    self.start_way(train)
