import sys
import json
import os.path
import socket
from server_connection import message_to_server, JsonParser
import networkx as nx
from graph_library import RenderArea
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QDesktopWidget, QGridLayout, QGraphicsScene, QGroupBox, QVBoxLayout,\
    QPushButton, QLineEdit, QFileDialog
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg\
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg \
    import NavigationToolbar2QT as NavigationToolbar


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()
        self.sock = socket.socket()
        self.sock.connect(('wgforge-srv.wargaming.net', 443))
        self.init_ui()

    def init_ui(self):
        self.resize(1200, 675)
        self.setMinimumSize(640, 480)
        self.setWindowTitle('Magnificent Graph')
        self.center_window()

        self.scene = QGraphicsScene()
        self.render_area = RenderArea(self.scene, self)

        main_layout = QGridLayout()
        main_layout.addWidget(self.render_area, 0, 0, 1, 4)
        self.setLayout(main_layout)
        message_to_server(self.sock, 'LOGIN', name="Boris"  )
        g = JsonParser.json_to_graph(
            message_to_server(self.sock, 'MAP', layer=0))
        # print(message_to_server(self.sock, 'MAP', layer=1))
        edge_labels = {
                (edge[0], edge[1]):
                edge[2]['length'] for edge in list(g.edges(data=True))
            }
        types = JsonParser.json_to_posts_types(message_to_server(self.sock, 'MAP', layer=1))
        # print(self.render_area.width())
        self.render_area.draw_graph(nx.kamada_kawai_layout(g), edge_labels, types = types)

    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
                QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = GraphWidget()
    screen.show()
    screen.sock.close()
    sys.exit(app.exec_())

