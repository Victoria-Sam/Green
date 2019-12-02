import sys

from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene

from connection import Connection
from graph_widget import GraphWidget
from game import Game


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = GraphWidget()
    screen.show()
    game = Game(app, screen)
    app.exec_()

    Connection().close()
    sys.exit()
