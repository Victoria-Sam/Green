from PyQt5.QtCore import QSize, Qt, QLineF, QRectF, QMarginsF
from PyQt5.QtGui import (QBrush, QPainter,
                         QPen, QColor, QTransform, QPixmap)
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsView,
                             QGraphicsEllipseItem, QGraphicsDropShadowEffect,
                             QGraphicsItem, QGraphicsLineItem,
                             QGraphicsPixmapItem)

colors = {0: QColor('#dbdbdb'),
          1: QColor('#ad3636'),
          2: QColor('#a1ad36'),
          3: QColor('#38ad36')}
icon_address = {1: 'icons/town.png',
                2: 'icons/market.png',
                3: 'icons/storage.png'}


class QTrain(QGraphicsEllipseItem):
    '''
    Now train is showing as circle
    red - our player train
    blue - other player's trains
    '''
    def __init__(self, idx, *args, **kwargs):
        super(QTrain, self).__init__(*args, **kwargs)
        self.idx = idx
        self.icon = None

    def paint(self, painter, options, widget):
        QGraphicsEllipseItem.paint(self, painter, options, widget)
        self.update()


class BestNode(QGraphicsEllipseItem):
    def __init__(self, number, *args, **kwargs):
        super(BestNode, self).__init__(*args, **kwargs)
        self.number = number
        self.lines = []
        self.icon = None

    def paint(self, painter, options, widget):
        QGraphicsEllipseItem.paint(self, painter, options, widget)

        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignCenter, str(self.number))

        self.update()


class BestLine(QGraphicsLineItem):
    def __init__(self, node_parent_1, node_parent_2,
                 weight, idx, *args, **kwargs):
        super(BestLine, self).__init__(*args, **kwargs)
        self.node_parent_1 = node_parent_1
        self.node_parent_2 = node_parent_2
        self.weight = weight
        self.idx = idx

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
            self.boundingRect().bottomRight()).marginsAdded(
                QMarginsF(20, 20, 20, 20)), Qt.AlignCenter, str(self.weight))

        self.update()


class RenderArea(QGraphicsView):

    def __init__(self, scene, parent=None):
        super(RenderArea, self).__init__(scene, parent)

        self.setFrameStyle(QFrame.NoFrame)
        self.setMinimumSize(1150, 600)
        self.antialiased = True
        self.zoom = 0.9

        render_palette = self.palette()
        render_palette.setColor(self.backgroundRole(), QColor('#f0fff0'))
        self.setPalette(render_palette)
        self.setAutoFillBackground(True)

    def update_view(self):
        self.setRenderHint(QPainter.Antialiasing, self.antialiased)
        self.setTransform(QTransform().scale(self.zoom, self.zoom))

    def set_antialiased(self, antialiased):
        self.antialiased = antialiased
        self.update_view()

    def draw_graph(self, pos, edge_labels, game, types={}):
        '''
        Draw map and starting positions for trains
        '''
        self.scene().clear()

        for node, node_pos in pos.items():
            pos[node] = [(self.width() // 2 + node_pos[0] * self.width() // 2),
                         (self.height() - (self.height() // 2 + node_pos[1] *
                          self.height() // 2))]

        for node, node_pos in pos.items():
            best_node = BestNode(node, node_pos[0], node_pos[1], 35, 35)

            best_node.setPen(QPen(Qt.black, 2))
            post_type = types.get(node, 0)

            best_node.setBrush(QBrush(colors[post_type]))

            best_node_effect = QGraphicsDropShadowEffect(self)
            best_node_effect.setBlurRadius(5)
            best_node_effect.setOffset(3)
            best_node.setGraphicsEffect(best_node_effect)
            best_node.setZValue(2)

            if post_type != 0:
                pixmap = QPixmap(icon_address[post_type])
                pixmap = QGraphicsPixmapItem(pixmap.scaled(50, 50))
                pixmap.setPos(node_pos[0] - 8, node_pos[1] - 8)
                pixmap.setZValue(3)
                best_node.icon = pixmap
                self.scene().addItem(pixmap)
            self.scene().addItem(best_node)

        for parent_nodes, info in edge_labels.items():
            best_nodes = list(filter(lambda scene_item: type(scene_item) ==
                              BestNode, self.scene().items()))
            node_parent_1 = list(filter(lambda best_node: best_node.number ==
                                 parent_nodes[0], best_nodes))[0]
            node_parent_2 = list(filter(lambda best_node: best_node.number ==
                                 parent_nodes[1], best_nodes))[0]

            best_line = BestLine(
                node_parent_1, node_parent_2, info[0], info[1],
                QLineF(node_parent_1.boundingRect().center(),
                       node_parent_2.boundingRect().center())
            )
            best_line.setPen(QPen(Qt.black, 2))
            best_line.setZValue(1)

            self.scene().addItem(best_line)

            node_parent_1.lines.append(best_line)
            node_parent_2.lines.append(best_line)

        for train in game.trains:
            lines = list(filter(lambda scene_item: type(scene_item) ==
                                BestLine, self.scene().items()))
            for line in lines:
                if line.idx == train.line_id:
                    current_line = line
                    break
            start_coords = [current_line.node_parent_1.rect().center().x(),
                            current_line.node_parent_1.rect().center().y()]
            end_coords = [current_line.node_parent_2.rect().center().x(),
                          current_line.node_parent_2.rect().center().y()]
            train_coords = [
                start_coords[0] + train.position *
                (end_coords[0] - start_coords[0]) / current_line.weight,
                start_coords[1] + train.position *
                (end_coords[1] - start_coords[1]) / current_line.weight
                ]
            train_visual = QTrain(
                train.train_id, train_coords[0] - 5,
                train_coords[1] - 5, 10, 10)
            train_visual.setZValue(10)
            pen = QPen(QColor("red"))
            pen.setWidth(5)
            if train.player_id == game.player_id:
                train_visual.setPen(pen)
            else:
                pen.setColor(QColor("blue"))
                train_visual.setPen(pen)
            self.scene().addItem(train_visual)

        self.update_view()

    def update_map1(self, game):
        '''
        Set new trains positions each turn
        '''
        all_trains = list(filter(lambda scene_item: type(scene_item) ==
                                 QTrain, self.scene().items()))
        lines = list(filter(lambda scene_item: type(scene_item) ==
                            BestLine, self.scene().items()))
        for train in game.trains:
            train_on_map = [x for x in all_trains if x.idx == train.train_id]
            for line in lines:
                if line.idx == train.line_id:
                    current_line = line
                    break
            start_coords = [current_line.node_parent_1.rect().center().x(),
                            current_line.node_parent_1.rect().center().y()]
            end_coords = [current_line.node_parent_2.rect().center().x(),
                          current_line.node_parent_2.rect().center().y()]
            train_coords = [
                start_coords[0] + train.position *
                (end_coords[0] - start_coords[0]) / current_line.weight,
                start_coords[1] + train.position *
                (end_coords[1] - start_coords[1]) / current_line.weight
                ]
            train_on_map[0].setPos(
                train_coords[0] - 5 - train_on_map[0].rect().x(),
                train_coords[1] - 5 - train_on_map[0].rect().y()
            )
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
