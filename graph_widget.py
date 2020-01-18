import networkx as nx
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QGraphicsScene

from graph_library import RenderArea


class GraphWidget(QWidget):
    def __init__(self, connect_widget):
        super(GraphWidget, self).__init__()

        self.connect_widget = connect_widget
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
        game, edge_labels, types = l[0], l[1], l[2]
        self.render_area.draw_graph(nx.kamada_kawai_layout(game.nx_graph),
                                    edge_labels, game, types)

    def update_map1(self, game):
        self.render_area.update_map1(game)

    def __center_window(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())

    def closeEvent(self, event):
        self.connect_widget.game.event_stop.set()
        self.connect_widget.game.threadpool.clear()
        self.connect_widget.show()
