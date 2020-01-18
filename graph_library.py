from PyQt5.QtCore import QSize, Qt, QLineF, QRectF, QMarginsF
from PyQt5.QtGui import (QBrush, QPainter, QFont,
                         QPen, QColor, QTransform, QPixmap)
from PyQt5.QtWidgets import (QApplication, QFrame, QGraphicsView,
                             QGraphicsEllipseItem, QGraphicsDropShadowEffect,
                             QGraphicsItem, QGraphicsLineItem,
                             QGraphicsTextItem, QGraphicsPixmapItem,
                             QGraphicsSimpleTextItem)

colors = {0: QColor('#dbdbdb'),
          1: QColor('#ad3636'),
          2: QColor('#a1ad36'),
          3: QColor('#38ad36')}

icon_address = {1: 'icons/town.png',
                2: 'icons/market.png',
                3: 'icons/storage.png',
                4: 'icons/train.png',
                5: 'icons/population.png',
                6: 'icons/product.png',
                7: 'icons/armor.png'}

post_size = 30
item_size = 20
icon_offset = 1


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
        self.type = None
        self.lines = []
        self.icon = None
        self.population_icon = None
        self.population_text = None
        self.armor_icon = None
        self.armor_text = None
        self.product_icon = None
        self.product_text = None

    def paint(self, painter, options, widget):
        QGraphicsEllipseItem.paint(self, painter, options, widget)

        font = painter.font()
        font.setPointSize(9)
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
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(QPen(Qt.transparent))
        painter.setBrush(QBrush(QColor('#f0fff0')))
        painter.drawEllipse(self.boundingRect().center(), 10, 10)

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

    def draw_graph(self, edge_labels, game, types={}):
        '''
        Draw map and starting positions for trains
        '''
        self.scene().clear()
        for node, node_pos in game.coordinates.items():
            game.coordinates[node] = [(self.width() // 2 +
                                       node_pos[0] * self.width() // 2),
                                      (self.height() - (self.height() // 2 +
                                       node_pos[1] * self.height() // 2))]

        for node, node_pos in game.coordinates.items():
            best_node = BestNode(node, node_pos[0], node_pos[1], 25, 25)

            best_node.setPen(QPen(Qt.black, 2))
            post_type = types.get(node, 0)

            best_node.setBrush(QBrush(colors[post_type]))

            best_node_effect = QGraphicsDropShadowEffect(self)
            best_node_effect.setBlurRadius(3)
            best_node_effect.setOffset(2)
            best_node.setGraphicsEffect(best_node_effect)
            best_node.setZValue(2)

            if post_type != 0:
                pixmap = QPixmap(icon_address[post_type])
                pixmap = QGraphicsPixmapItem(
                    pixmap.scaled(post_size, post_size))
                pixmap.setPos(node_pos[0] - icon_offset,
                              node_pos[1] - icon_offset)
                pixmap.setZValue(3)
                best_node.icon = pixmap
                self.scene().addItem(pixmap)
                current_post = game.posts[best_node.number]
                x_ppl_offset = 3
                x_offset = -3
                y_ppl_offset = 4
                y_offset = 3
                if post_type == 1:
                    pixmap_ppl = QPixmap(icon_address[5])
                    pixmap_ppl = QGraphicsPixmapItem(
                        pixmap_ppl.scaled(post_size, item_size))
                    pixmap_ppl.setPos(node_pos[0] - icon_offset,
                                      node_pos[1] - icon_offset + post_size)
                    pixmap_ppl.setZValue(6)
                    best_node.population_icon = pixmap_ppl
                    best_node.type = 1
                    self.scene().addItem(pixmap_ppl)

                    ppl_text = QGraphicsTextItem()
                    ppl_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            "color: #ffffff'>") +
                        str(current_post.population) + "/" +
                        str(current_post.population_capacity) +
                        str("</div>"))
                    ppl_text.setFont(QFont("Times", 6, 100, 0))
                    ppl_text.setZValue(7)
                    ppl_text.setPos(pixmap_ppl.x() + x_ppl_offset,
                                    pixmap_ppl.y() + y_ppl_offset)
                    self.scene().addItem(ppl_text)
                    best_node.population_text = ppl_text

                if post_type == 1 or post_type == 2:
                    pixmap_prod = QPixmap(icon_address[6])
                    pixmap_prod = QGraphicsPixmapItem(
                        pixmap_prod.scaled(post_size, item_size))
                    if post_type == 1:
                        pixmap_prod.setPos(
                            node_pos[0] - icon_offset,
                            node_pos[1] - icon_offset + post_size + item_size)
                    else:
                        pixmap_prod.setPos(
                            node_pos[0] - icon_offset,
                            node_pos[1] - icon_offset + post_size)
                        best_node.type = 2
                    pixmap_prod.setZValue(6)
                    best_node.product_icon = pixmap_prod
                    self.scene().addItem(pixmap_prod)

                    prod_text = QGraphicsTextItem()
                    prod_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            " color: #ffffff'>") +
                        str(current_post.product) + "/" +
                        str(current_post.product_capacity) + str("</div>"))

                    prod_text.setFont(QFont("Times", 5, 200, 0))
                    prod_text.setZValue(7)
                    prod_text.setPos(pixmap_prod.x() + x_offset,
                                     pixmap_prod.y() + y_offset)
                    self.scene().addItem(prod_text)
                    best_node.product_text = prod_text

                if post_type == 1 or post_type == 3:
                    pixmap_armor = QPixmap(icon_address[7])
                    pixmap_armor = QGraphicsPixmapItem(
                        pixmap_armor.scaled(post_size, item_size))
                    if post_type == 1:
                        pixmap_armor.setPos(
                            node_pos[0] - icon_offset,
                            node_pos[1] - icon_offset +
                            post_size + 2 * item_size)
                    else:
                        pixmap_armor.setPos(
                            node_pos[0] - icon_offset,
                            node_pos[1] - icon_offset + post_size)
                        best_node.type = 3
                    pixmap_armor.setZValue(6)
                    best_node.armor_icon = pixmap_armor
                    self.scene().addItem(pixmap_armor)

                    armor_text = QGraphicsTextItem()
                    armor_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            " color: #ffffff'>") +
                        str(current_post.armor) + "/" +
                        str(current_post.armor_capacity) + str("</div>"))
                    armor_text.setFont(QFont("Times", 5, 200, 0))
                    armor_text.setZValue(7)
                    armor_text.setPos(pixmap_armor.x() + x_offset,
                                      pixmap_armor.y() + y_offset)
                    self.scene().addItem(armor_text)
                    best_node.armor_text = armor_text

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

        for train in game.trains.values():
            self.draw_train(train, game.player_id)

        self.update_view()

    def draw_train(self, train, player_id):
        lines = {x.idx: x for x in list(filter(
            lambda scene_item: type(scene_item) == BestLine,
            self.scene().items()))}
        current_line = lines[train.line_id]
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
        train_size = 12
        offset = 6
        train_visual = QTrain(
            train.train_id,
            train_coords[0] - train_size / 2 - offset / 2,
            train_coords[1] - train_size / 2 - offset / 2,
            train_size + offset,
            train_size + offset)
        train_pixmap = QPixmap(icon_address[4])
        train_pixmap = QGraphicsPixmapItem(
            train_pixmap.scaled(train_size, train_size))
        train_pixmap.setPos(train_coords[0] - train_size / 2,
                            train_coords[1] - train_size / 2, )
        train_pixmap.setZValue(5)
        train_visual.icon = train_pixmap
        train_visual.setZValue(4)
        pen = QPen(QColor("red"))
        pen.setWidth(1)
        if train.player_id == player_id:
            train_visual.setPen(pen)
        else:
            pen.setColor(QColor("blue"))
            train_visual.setPen(pen)
        self.scene().addItem(train_visual)
        self.scene().addItem(train_pixmap)
        return train_visual

    def update_map1(self, game):
        '''
        Set new trains positions each turn
        '''
        all_trains = {x.idx: x for x in list(filter(
            lambda scene_item: type(scene_item) == QTrain,
            self.scene().items()))}

        for train in game.trains.values():
            if train.train_id not in all_trains.keys():
                train_visual = self.draw_train(train, game.player_id)
                all_trains[train.train_id] = train_visual

        lines = {x.idx: x for x in list(filter(
            lambda scene_item: type(scene_item) == BestLine,
            self.scene().items()))}
        all_nodes = {x.number: x for x in list(filter(
            lambda scene_item: type(scene_item) == BestNode,
            self.scene().items()))}
        post_nodes = [x for x in all_nodes.values() if x.type is not None]
        for post_node in post_nodes:
            current_post = game.posts[post_node.number]
            if post_node.type == 1:
                post_node.population_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            " color: #ffffff'>") +
                        str(current_post.population) + "/" +
                        str(current_post.population_capacity) +
                        str("</div>"))

            if post_node.type == 1 or post_node.type == 2:
                post_node.product_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            " color: #ffffff'>") +
                        str(current_post.product) + "/" +
                        str(current_post.product_capacity) + str("</div>"))

            if post_node.type == 1 or post_node.type == 3:
                post_node.armor_text.setHtml(
                        str("<div style='background-color: #000000;" +
                            " color: #ffffff'>") +
                        str(current_post.armor) + "/" +
                        str(current_post.armor_capacity) + str("</div>"))
        train_size = 12
        offset = 6
        for train in game.trains.values():
            train_on_map = all_trains[train.train_id]
            current_line = lines[train.line_id]
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
            train_on_map.setPos(
                train_coords[0] - train_size/2 - offset/2 -
                train_on_map.rect().x(),
                train_coords[1] - train_size/2 - offset/2 -
                train_on_map.rect().y()
            )
            train_on_map.icon.setPos(
                train_coords[0] - train_size/2,
                train_coords[1] - train_size/2
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
