import asyncio
import sys

import networkx as nx
import quamash
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene

from Connection import Connection
from bot_brains import BotBrains
from graph_library import RenderArea


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.user_name = 'Boris'
        self.user_password = 'password'

        self.bot_brains = BotBrains(self, self.user_name)

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

        self.bot_brains.start()

    def draw_map0(self, nx_graph, edge_labels, types):
        self.render_area.draw_graph(nx.kamada_kawai_layout(nx_graph), edge_labels, types)

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
    app.setStyle(QStyleFactory.create("gtk"))

    loop = quamash.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        screen = GraphWidget()
        screen.show()
        loop.run_forever()

    Connection().close()
    loop.stop()
    loop.close()
    sys.exit()
