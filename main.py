import sys

from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene

from connection import Connection
from graph_widget import GraphWidget
from game import Game


if __name__ == '__main__':
    connection = Connection()
    all_games = connection.games() # dict of current games, key == name
    user_name = 'GreenTeam'
    user_password = ''
    game_name = 'Dream Green'
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create('gtk'))
    screen = GraphWidget()
    screen.show()
    game = Game(app, screen, user_name, connection, user_password, game_name)
    app.exec_()

    Connection().close()
    sys.exit()
