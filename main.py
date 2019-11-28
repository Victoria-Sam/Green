import sys

import networkx as nx
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene

from connection import Connection
from bot_brains_library import BotBrains
from graph_library import RenderArea
from game import Game


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.__init_ui()

    def __init_ui(self):
        self.resize(1200, 675)
        self.setMinimumSize(1200, 675)
        self.setWindowTitle('Magnificent Graph')
        self.__center_window()

        self.__scene = QGraphicsScene()
        self.render_area = RenderArea(self.__scene, self)

        main_layout = QGridLayout()
        main_layout.addWidget(self.render_area, 0, 0, 1, 4)

        self.setLayout(main_layout)

    def draw_map0(self, l):
        nx_graph, edge_labels, types = l[0], l[1], l[2]
        self.render_area.draw_graph(nx.kamada_kawai_layout(nx_graph),
                                    edge_labels, types)

    def update_map1(self, map1):
        self.render_area.update_map1(map1)

    def __center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


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
