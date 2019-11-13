import sys
import json
import os.path
import networkx as nx
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QStyleFactory, \
    QDesktopWidget, QGridLayout, QGroupBox, QVBoxLayout, QPushButton,\
    QLineEdit, QFileDialog
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg\
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg \
    import NavigationToolbar2QT as NavigationToolbar


class GraphWidget(QWidget):
    def __init__(self):
        super(GraphWidget, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 1200, 675)
        self.center()
        self.setWindowTitle('Graph Plot')
        grid = QGridLayout()
        self.rows = 9
        self.cols = 1
        self.setLayout(grid)
        self.create_vertical_group_box()
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid.addWidget(self.toolbar, 0, 0)
        grid.addWidget(self.canvas, 1, 0, 7, 1)
        grid.addLayout(buttonLayout, 8, 0)
        self.show()

    def choose_file_and_plot(self):
        self.textbox.setText(
            QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        )
        self.plot()

    def create_vertical_group_box(self):
        self.verticalGroupBox = QGroupBox()
        layout = QVBoxLayout()
        button = QPushButton('Build a graph by manually entered file path')
        file_button = QPushButton(
            'Select the path to the graph file using the '
            + 'file manager and build the graph'
        )
        button.setObjectName('path_plot')
        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)
        layout.addWidget(button)
        layout.addWidget(file_button)
        layout.setSpacing(10)
        self.verticalGroupBox.setLayout(layout)
        button.clicked.connect(self.plot)
        file_button.clicked.connect(self.choose_file_and_plot)

    def plot(self):
        self.figure.clf()
        textboxValue = self.textbox.text()
        if os.path.isfile(textboxValue):
            with open(textboxValue) as json_file:
                json_data = json.load(json_file)
            nodes = json_data['points']
            vertex = json_data['lines']
            g = nx.Graph()
            g.add_nodes_from([x['idx'] for x in nodes])
            g.add_edges_from(
                [x['points']+[{'length': x['length']}] for x in vertex]
            )
            nx.draw_kamada_kawai(g, with_labels=True, font_weight='bold')
            edge_labels = {
                (x[0], x[1]): x[2]['length'] for x in list(g.edges(data=True))
            }
            nx.draw_networkx_edge_labels(
                g, pos=nx.kamada_kawai_layout(g),
                edge_labels=edge_labels, label_pos=0.3
            )
        else:
            plt.gcf().text(x=0.45, y=0.5, s='Wrong file path')
        self.canvas.draw_idle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, qKeyEvent):
        if qKeyEvent.key() == Qt.Key_Return or qKeyEvent.key() == Qt.Key_Enter:
            self.plot()
        else:
            super().keyPressEvent(qKeyEvent)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create("gtk"))
    screen = GraphWidget()
    screen.show()
    sys.exit(app.exec_())
