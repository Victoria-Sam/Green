import socket
import sys

import networkx as nx
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene, QPushButton, QLineEdit, QDialog, QLabel, QGroupBox, QHBoxLayout, \
    QCheckBox

from graph_library import RenderArea
from server_connection import message_to_server, JsonParser


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.user_name = 'Boris'
        self.user_password = 'password'

        self.sock = socket.socket()
        self.sock.connect(('wgforge-srv.wargaming.net', 443))

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

        message_to_server(self.sock, 'LOGIN', name=self.user_name)
        nx_graph = JsonParser.json_to_graph(
            message_to_server(self.sock, 'MAP', layer=0))
        # print(message_to_server(self.sock, 'MAP', layer=1))
        edge_labels = {
            (edge[0], edge[1]):
                edge[2]['length'] for edge in list(nx_graph.edges(data=True))
        }
        types = JsonParser.json_to_posts_types(message_to_server(self.sock, 'MAP', layer=1))
        self.render_area.draw_graph(nx.kamada_kawai_layout(nx_graph), edge_labels, types=types)

    def __center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = GraphWidget()
    screen.show()
    app.exec_()
    screen.sock.close()
    sys.exit()
