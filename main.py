import socket
import sys

import networkx as nx
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QGridLayout, QGraphicsScene, QPushButton, QLineEdit, QDialog, QLabel, QGroupBox, QHBoxLayout, \
    QCheckBox

from graph_library import RenderArea
from server_connection import message_to_server, JsonParser


class SignInPopup(QDialog):
    def __init__(self):
        super(SignInPopup, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(300, 100)
        self.setWindowTitle('Sign in')
        self.__center_window()

        main_layout = QGridLayout()

        self.__user_name_label = QLabel('User name')
        self.__user_password_label = QLabel('Password')
        self.__user_name_text_box = QLineEdit('B3RL_BUHO_HA_CEbR')
        self.__user_password_text_box = QLineEdit('password')
        self.__user_password_text_box.setEchoMode(QLineEdit.Password)
        self.__sign_in_button = QPushButton('Sign in')
        self.__sign_in_button.clicked.connect(self.__sign_in)

        main_layout.addWidget(self.__user_name_label, 0, 0)
        main_layout.addWidget(self.__user_name_text_box, 0, 1)
        main_layout.addWidget(self.__user_password_label, 1, 0)
        main_layout.addWidget(self.__user_password_text_box, 1, 1)
        main_layout.addWidget(self.__sign_in_button, 2, 0, 2, 2)

        self.setLayout(main_layout)

    def __center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def __sign_in(self):
        self.user_name = self.__user_name_text_box.text()
        self.user_password = self.__user_password_text_box.text()
        self.accept()


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()

        self.sock = None
        self.user_name = None
        self.user_password = None

        self.__init_ui()

    def __init_ui(self):
        self.resize(1200, 675)
        self.setMinimumSize(640, 480)
        self.setWindowTitle('Magnificent Graph')
        self.__center_window()

        self.__scene = QGraphicsScene()
        self.render_area = RenderArea(self.__scene, self)
        self.__create_group_box_for_buttons()

        main_layout = QGridLayout()
        main_layout.addWidget(self.render_area, 0, 0, 1, 4)
        main_layout.addWidget(self.__group_box_for_buttons, 1, 0)

        self.setLayout(main_layout)

    def __center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def __create_group_box_for_buttons(self):
        self.__group_box_for_buttons = QGroupBox()
        group_box_layout = QHBoxLayout()
        group_box_layout.setSpacing(10)

        self.__connect_button = QPushButton('Connect')
        self.__connect_button.clicked.connect(self.__connect)

        self.__antialiasing_check_box = QCheckBox('Antialiasing')
        self.__antialiasing_check_box.toggled.connect(self.render_area.set_antialiased)
        self.__antialiasing_check_box.setChecked(True)

        group_box_layout.addWidget(self.__connect_button)
        group_box_layout.addWidget(self.__antialiasing_check_box)

        self.__group_box_for_buttons.setLayout(group_box_layout)

    def __connect(self):
        sign_in_popup = SignInPopup()

        if sign_in_popup.exec_():
            self.__reconnect()

            self.user_name = sign_in_popup.user_name
            self.user_password = sign_in_popup.user_password

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

    def __reconnect(self):
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        self.sock = socket.socket()
        self.sock.connect(('wgforge-srv.wargaming.net', 443))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = GraphWidget()
    screen.show()
    app.exec_()
    screen.sock.close()
    sys.exit()
