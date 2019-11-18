import json
import os.path
import sys

import networkx as nx
from PyQt5.QtCore import QSize, Qt, QLineF, QRectF, QMarginsF
from PyQt5.QtGui import (QBrush, QPainter,
                         QPen, QColor, QTransform)
from PyQt5.QtWidgets import (QApplication, QCheckBox, QGridLayout,
                             QWidget, QGroupBox, QHBoxLayout,
                             QPushButton, QLineEdit, QStyleFactory, QGraphicsScene, QFrame, QGraphicsView,
                             QGraphicsEllipseItem, QGraphicsDropShadowEffect, QGraphicsItem,
                             QGraphicsLineItem)


class BestNode(QGraphicsEllipseItem):
    def __init__(self, number, *args, **kwargs):
        super(BestNode, self).__init__(*args, **kwargs)
        self.number = number
        self.lines = []
        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            for line in self.lines:
                new_pos = value + self.boundingRect().center()

                if line.node_parent_1 == self:
                    line.setLine(QLineF(new_pos, line.line().p2()))
                else:
                    line.setLine(QLineF(line.line().p1(), new_pos))

        return QGraphicsEllipseItem.itemChange(self, change, value)

    def paint(self, painter, options, widget):
        QGraphicsEllipseItem.paint(self, painter, options, widget)

        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.number))

        self.update()


class BestLine(QGraphicsLineItem):
    def __init__(self, node_parent_1, node_parent_2, weight, *args, **kwargs):
        super(BestLine, self).__init__(*args, **kwargs)
        self.node_parent_1 = node_parent_1
        self.node_parent_2 = node_parent_2
        self.weight = weight
        self.setFlags(QGraphicsItem.ItemIsMovable)
        self.setFlags(QGraphicsItem.ItemSendsGeometryChanges)

    def paint(self, painter, options, widget):
        QGraphicsLineItem.paint(self, painter, options, widget)

        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(QPen(Qt.transparent))
        painter.setBrush(QBrush(QColor('#f0fff0')))
        painter.drawEllipse(self.boundingRect().center(), 13, 13)

        painter.setPen(QPen())
        painter.drawText(QRectF(
            self.boundingRect().topLeft(),
            self.boundingRect().bottomRight()).marginsAdded(QMarginsF(20, 20, 20, 20)),
                         Qt.AlignCenter,
                         str(self.weight))

        self.update()


class RenderArea(QGraphicsView):

    def __init__(self, scene, parent=None):
        super(RenderArea, self).__init__(scene, parent)

        self.setFrameStyle(QFrame.NoFrame)
        self.antialiased = False
        self.zoom = 0.9

        render_palette = self.palette()
        render_palette.setColor(self.backgroundRole(), QColor('#f0fff0'))
        self.setPalette(render_palette)
        self.setAutoFillBackground(True)

    def update_view(self):
        self.setRenderHint(QPainter.Antialiasing, self.antialiased)
        self.setTransform(QTransform().scale(self.zoom, self.zoom))

    def minimumSizeHint(self):
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        screen_geometry = QApplication.desktop().screenGeometry(screen)
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        return QSize(screen_width, screen_height)

    def set_antialiased(self, antialiased):
        self.antialiased = antialiased
        self.update_view()

    def draw_graph(self, pos, edge_labels):
        self.scene().clear()

        for node, node_pos in pos.items():
            pos[node] = [(10*self.width() // 2 + 10*node_pos[0] * self.width() // 2),
                         (10*self.height() - (10*self.height() // 2 + node_pos[1] * 10*self.height() // 2))]

        for node, node_pos in pos.items():
            best_node = BestNode(node, node_pos[0], node_pos[1], 35, 35)

            best_node.setPen(QPen(Qt.black, 2))
            best_node.setBrush(QBrush(QColor('#dbdbdb')))

            best_node_effect = QGraphicsDropShadowEffect(self)
            best_node_effect.setBlurRadius(5)
            best_node_effect.setOffset(3)
            best_node.setGraphicsEffect(best_node_effect)
            best_node.setZValue(2)
            best_node.setFlag(QGraphicsItem.ItemIsMovable)

            self.scene().addItem(best_node)

        for parent_nodes, weight in edge_labels.items():
            best_nodes = list(filter(lambda scene_item: type(scene_item) == BestNode, self.scene().items()))
            node_parent_1 = list(filter(lambda best_node: best_node.number == parent_nodes[0], best_nodes))[0]
            node_parent_2 = list(filter(lambda best_node: best_node.number == parent_nodes[1], best_nodes))[0]

            best_line = BestLine(node_parent_1, node_parent_2, weight, QLineF(node_parent_1.boundingRect().center(),
                                                                              node_parent_2.boundingRect().center()))
            best_line.setPen(QPen(Qt.black, 2))
            best_line.setZValue(1)

            self.scene().addItem(best_line)

            node_parent_1.lines.append(best_line)
            node_parent_2.lines.append(best_line)

        self.update_view()

    def wheelEvent(self, event):
        moose = event.angleDelta().y() / 120
        if moose > 0:
            self.zoom_in()
        elif moose < 0:
            self.zoom_out()

    def zoom_in(self):
        self.zoom *= 1.05
        self.update_view()

    def zoom_out(self):
        self.zoom /= 1.05
        self.update_view()


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.init_UI()

    def init_UI(self):

        self.resize(1200, 675)
        self.setMinimumSize(640, 480)
        self.setWindowTitle('Magnificent Graph')
        self.center_window()

        self.scene = QGraphicsScene()
        self.render_area = RenderArea(self.scene, self)
        self.create_group_box_for_draw_graph_buttons()
        self.create_group_box_for_support_buttons()

        main_layout = QGridLayout()
        main_layout.addWidget(self.render_area, 0, 0, 1, 4)
        main_layout.addWidget(self.group_box_for_draw_graph_buttons, 1, 0, 1, 4)
        main_layout.addWidget(self.group_box_for_support_buttons, 2, 0)

        self.setLayout(main_layout)

    def center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def create_group_box_for_draw_graph_buttons(self):
        self.group_box_for_draw_graph_buttons = QGroupBox('Enter graph')
        group_box_layout = QHBoxLayout()
        group_box_layout.setSpacing(10)

        self.graph_path_textbox = QLineEdit()
        self.graph_path_textbox.setText('small_graph.json')
        draw_button = QPushButton('Draw')
        draw_button.clicked.connect(self.draw_graph)

        group_box_layout.addWidget(self.graph_path_textbox)
        group_box_layout.addWidget(draw_button)

        self.group_box_for_draw_graph_buttons.setLayout(group_box_layout)

    def create_group_box_for_support_buttons(self):
        self.group_box_for_support_buttons = QGroupBox('Options')
        group_box_layout = QHBoxLayout()
        group_box_layout.setSpacing(10)

        antialiasing_check_box = QCheckBox('Antialiasing')
        antialiasing_check_box.toggled.connect(self.render_area.set_antialiased)
        antialiasing_check_box.setChecked(True)

        group_box_layout.addWidget(antialiasing_check_box)

        self.group_box_for_support_buttons.setLayout(group_box_layout)

    def draw_graph(self):
        graph_path = self.graph_path_textbox.text()
        if os.path.isfile(graph_path):

            with open(graph_path) as json_file:
                json_data = json.load(json_file)
            nodes = json_data['points']
            edges = json_data['lines']

            graph = nx.Graph()
            graph.add_nodes_from([node['idx'] for node in nodes])
            graph.add_edges_from(
                [edge['points'] + [{'length': edge['length']}] for edge in edges]
            )

            self.edge_labels = {
                (edge[0], edge[1]): edge[2]['length'] for edge in list(graph.edges(data=True))
            }

            self.pos = nx.kamada_kawai_layout(graph)
            self.render_area.draw_graph(self.pos, self.edge_labels)

        else:
            print('ERROR')
