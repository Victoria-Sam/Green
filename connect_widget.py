from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QGroupBox,\
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QVBoxLayout

from classes_library import game_states
from connection import Connection
from game import Game
from graph_widget import GraphWidget
from popups import SignInPopup, NewGamePopup


class ConnectWidget(QWidget):
    def __init__(self):
        super(ConnectWidget, self).__init__()

        self.__init_ui()

    def __init_ui(self):
        self.resize(840, 500)
        self.setMinimumSize(840, 500)
        self.setWindowTitle('Choose game')
        self.__center_window()

        self.__create_group_box_for_buttons()
        self.games_table = GamesTable()
        self.__refresh_games()

        self.__refresh_games_button = QPushButton('Refresh')
        self.__refresh_games_button.clicked.connect(self.__refresh_games)

        main_layout = QGridLayout()
        main_layout.addWidget(self.games_table, 0, 0)
        main_layout.addWidget(self.__group_box_for_buttons, 0, 1, Qt.AlignTop)
        main_layout.addWidget(self.__refresh_games_button,
                              0, 1, Qt.AlignBottom)

        self.setLayout(main_layout)

    def __center_window(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def __create_group_box_for_buttons(self):
        self.__group_box_for_buttons = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box_layout.setSpacing(10)

        self.__connect_button = QPushButton('Connect')
        self.__connect_button.clicked.connect(self.__connect)

        self.__create_new_game_button = QPushButton('New Game')
        self.__create_new_game_button.clicked.connect(self.__create_new_game)

        group_box_layout.addWidget(self.__connect_button)
        group_box_layout.addWidget(self.__create_new_game_button)

        self.__group_box_for_buttons.setLayout(group_box_layout)

    def __refresh_games(self):
        all_games = Connection().games()
        self.games_table.update_table_data(all_games.games)

    def __connect(self):
        if self.games_table.selectionModel().hasSelection():
            sign_in_popup = SignInPopup()

            if sign_in_popup.exec_():
                self.user_name = sign_in_popup.user_name
                self.user_password = sign_in_popup.user_password
                selected_table_row = self.games_table.currentRow()
                self.game_name = self.games_table.item(
                    selected_table_row, 0).text()

                self.hide()
                self.game_window = GraphWidget(self)
                self.game_window.show()
                self.game = Game(self.game_window, self.user_name,
                                 self.user_password, self.game_name)
        else:
            self.__create_new_game()

    def __create_new_game(self):
        new_game_popup = NewGamePopup()

        if new_game_popup.exec_():
            self.user_name = new_game_popup.user_name
            self.user_password = new_game_popup.user_password
            self.game_name = new_game_popup.game_name
            self.num_turns = new_game_popup.num_turns
            self.num_players = new_game_popup.num_players

            self.hide()
            self.game_window = GraphWidget(self)
            self.game_window.show()
            self.game = Game(self.game_window, self.user_name,
                             self.user_password, self.game_name,
                             self.num_turns, self.num_players)


class GamesTable(QTableWidget):

    def __init__(self, *args):
        QTableWidget.__init__(self, *args)

        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Game name', 'Players count',
                                        'Turns', 'State'])
        self.setColumnWidth(0, 400)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data = {}

    def update_table_data(self, data):
        self.data.clear()
        self.data.update(data)
        self.set_data()

    def create_table_item(self, text):
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(Qt.AlignCenter)
        table_item.setText(text)
        return table_item

    def set_data(self):
        self.setRowCount(0)
        for row, game in enumerate(self.data.values()):
            self.insertRow(row)

            self.setItem(
                row, 0, self.create_table_item(game.name))
            self.setItem(
                ow, 1, self.create_table_item(str(game.num_players)))
            self.setItem(
                row, 2, self.create_table_item(str(game.num_turns)))
            self.setItem(
                row, 3, self.create_table_item(game_states[game.state]))
