import sys
import traceback

import networkx as nx
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from connection import Connection
from dijkstra import the_best_way


class BotBrainsSignals(QObject):
    '''
    Defines the signals available from a running BotBrains thread.

    Supported signals are:

    finished
        No data

    error
        `object` error text

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
    error = pyqtSignal(object)
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

        # Add the game parametres
        self.game = game
        self.game.hijack_probability = 0.25
        self.game.parasites_probability = 0.25
        self.game.refugees_probability = 0.5
        self.current_ways = {}
        self.market_train = {}
        self.trains_for_armor = {}

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
            self.signals.error.emit(str((exctype, value, traceback.format_exc())))
        else:
            self.signals.result.emit(result)
            # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

    def main_loop(self):
        '''
        Основный цикл бота: подвинь поезд, заверши ход, обнови карту
        '''
        res = self.init_bot()
        self.potencial_product = {}
        self.game_end = False

        if res:
            while not self.game_end and not self.game.event_stop.is_set():
                self.update_map1()
                self.find_trains_way()
                self.upgrate_trains()
                self.turn()

            if self.game_end or self.game.event_stop.is_set():
                Connection().logout()
                Connection().reconnect()

    def get_city(self, idx):
        return self.game.posts[idx]

    def init_bot(self):
        '''
        Логинимся и рисуем начальную карту (0 слой)
        '''
        login_response = Connection().login(self.game.user_name,
                                            self.game.user_password,
                                            self.game.name,
                                            self.game.num_turns,
                                            self.game.num_players
                                            )

        if login_response.result_code != 0:
            self.signals.error.emit('%s %s' % (login_response.result_code, login_response.error))
            login_response = Connection().player()

        if login_response.result_code == 0:
            self.game.home = login_response.home
            self.game.player_id = login_response.player_id
            self.game.own_trains = login_response.trains
            self.game.hijackers_cd = 0
            self.game.parasites_cd = 0
            self.game.refugees_cd = 0
            self.nx_graph = nx.Graph()
            self.draw_map0()
        else:
            self.signals.error.emit('%s %s' % (login_response.result_code, login_response.error))
            return False
        return True

    def upgrate_trains(self):
        for idx, train in self.game.trains.items():
            if train.next_level_price < self.game.home.town.armor and \
                    self.game.home.town.armor - train.next_level_price > 50:
                Connection().upgrade([], [train.train_id])
                self.game.home.town.armor -= train.next_level_price

    def get_best_ways(self, best_way):
        best_ways_markets = {}
        best_ways_storages = {}
        for key, val in best_way.items():
            if val[-2].points[1].point_type == 2 or \
               val[-2].points[0].point_type == 2:
                best_ways_markets[key] = val
            else:
                if val[-2].points[1].point_type == 3 or \
                   val[-2].points[0].point_type == 3:
                    best_ways_storages[key] = val
        return (best_ways_markets, best_ways_storages)

    def draw_map0(self):
        '''
        Получаем 0 и 1 слои и посылаем сигнал в основной поток для рисования
        '''
        map_0_response = Connection().map0()  # it's response now
        if map_0_response.result_code == 0:
            self.game.map = map_0_response.graph_map
        self.game.nx_graph = nx.Graph()
        for point in self.game.map.graph.points.values():
            self.game.nx_graph.add_node(point.idx)
        for line in self.game.map.graph.lines.values():
            self.game.nx_graph.add_edge(line.points[0].idx,
                                        line.points[1].idx,
                                        length=line.length, idx=line.idx)
        map_1_response, post_types = Connection().map1()
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
        player_response = Connection().player()
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
            elif event.event_type == 100:
                self.game_end = True
        map_1_response, _ = Connection().map1()
        if map_1_response.result_code == 0:
            self.game.posts = map_1_response.posts
            self.game.trains = map_1_response.trains
            self.game.home.town = self.game.posts[self.game.home.idx]
        self.signals.update_map1.emit(self.game)

    def check_line(self, line, start_point):
        for idx, train in self.game.trains.items():
            if train.line_id == line.idx and train.speed != 0:
                return False
        finish_point = line.points[0] if line.points[1].idx == start_point.idx else line.points[1]
        if finish_point.point_type == 1:
            return True
        for idx, train in self.game.trains.items():
            if train.speed != 0:
                line1 = self.game.map.graph.lines[train.line_id]
                point1 = line1.points[0] if train.speed == -1 else line1.points[0]
                distance = train.position if train.speed == -1 else line1.length - train.position
                if point1.idx == finish_point.idx and distance == line.length:
                    return False
        return True

    def move_trains(self, line_idx, train, start_point):
        line = self.game.map.graph.lines[line_idx]
        rtrain = self.game.trains[train]
        if self.check_line(line, start_point):
            if line.points[0].idx == start_point.idx:
                Connection().move(line.idx, 1, train)
                rtrain.speed = 1
                rtrain.position = 0
                rtrain.line_id = line.idx
            else:
                Connection().move(line.idx, -1, train)
                rtrain.speed = -1
                rtrain.position = line.length
                rtrain.line_id = line.idx

    def turn(self):
        response = Connection().turn()
        # print('turn end')

    def next_line(self, train, line):
        train_line = self.game.map.graph.lines[train.line_id]
        train_point = train_line.points[0 if train.position == 0 else 1]
        if self.game.map.graph.lines[line.idx].points[0].idx == \
                train_point.idx:
            speed = 1
        else:
            speed = -1

        self.move_trains(line.idx, train.train_id, train_point)

    def start_way(self, train, best_ways_markets, best_ways_storages, way_home):
        shortest = 1000000000
        best_way_storage = None
        best_storage = None
        for key, val in best_ways_storages.items():
            if not best_way_storage or best_way_storage[-1] > val[-1]:
                best_way_storage = val
                best_storage = key
        best_market, best_way = self.choose_way(best_storage,
                                                best_way_storage,
                                                train, best_ways_markets, way_home)
        if best_way:
            best_way = best_way[0:-1]
            if self.market_train.get(best_market) != None:
                self.market_train[best_market] = self.market_train[best_market] + 1
            else:
                self.market_train[best_market] = 1
            self.next_line(train, best_way[0])

    def choose_way(self, best_storage, best_way_storage, train, best_ways_markets, way_home):
        best_way_market = None
        best_market = None
        for key, val in best_ways_markets.items():
            market = self.get_city(key)
            amount_trains = self.market_train.get(key)
            if amount_trains == None or amount_trains < 2:
                if not best_way_market:
                    best_way_market = val
                    best_market = market
                if self.isEnough(best_way_storage, market, val, train, way_home):
                    if best_storage and best_way_storage:
                        return (best_storage, best_way_storage)
                if min(best_market.product, train.goods_capacity) - \
                        2 * best_way_market[-1] < \
                        min(market.product, train.goods_capacity) - 2 * val[-1]:
                    best_market = market
                    best_way_market = val
        if best_market and best_way_market:
            return (best_market.point_id, best_way_market)
        return (None, None)

    def isEnough(self, best_way_storage, market, way_market, train, way_home):
        potencial = self.potencial_product
        if (self.trains_for_armor.get(train.train_id) or len(self.trains_for_armor) + self.trains_with_armor < 1) and \
            self.game.home.town.product_capacity - self.game.home.town.product < potencial:
            if not self.trains_for_armor.get(train.train_id):
                self.trains_for_armor[train.train_id] = 1
            return True
        if self.trains_for_armor.get(train.train_id):
            self.trains_for_armor.pop(train.train_id)
        return False

    def move_home(self, train):
        start_line = self.game.map.graph.lines[train.line_id]
        start_point = start_line.points[0] if train.position == 0 else start_line.points[1]
        way = the_best_way(self.game.map.graph, start_point.idx, train.train_id, self.game.trains).get(
            self.game.home.idx)
        if way:
            self.move_trains(way[0].idx, train.train_id, start_point)

    def move_for_goods(self, train):
        start_line = self.game.map.graph.lines[train.line_id]
        start_point = start_line.points[0] if train.position == 0 else start_line.points[1]
        ways = the_best_way(self.game.map.graph, start_point.idx, train.train_id, self.game.trains)
        best_ways_markets, best_ways_storages = self.get_best_ways(ways)
        way_home = ways.get(self.game.home.idx)
        if way_home:
            self.start_way(train, best_ways_markets, best_ways_storages, way_home[-1])
        else:
            self.start_way(train, best_ways_markets, best_ways_storages, 100000)

    def find_trains_way(self):
        self.market_train = {}
        self.potencial_product = 0
        self.trains_with_armor = 0
        for idx, train in self.game.trains.items():
            if train.goods_type == 2:
                self.potencial_product += train.goods
            if train.goods_type == 1:
                if self.trains_for_armor.get(idx):
                    self.trains_for_armor.pop(idx)
                self.trains_with_armor += 1
        for idx, train in self.game.trains.items():
            if train.cooldown == 0:
                if (train.speed == 0):
                    if train.goods == 0:
                        self.move_for_goods(train)
                    else:
                        self.move_home(train)
