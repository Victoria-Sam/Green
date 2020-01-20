from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QTableWidget, QAbstractItemView, \
    QTableWidgetItem


class RatingsWidget(QWidget):
    def __init__(self, graph_widget):
        super(RatingsWidget, self).__init__()

        self.graph_widget = graph_widget
        self.__init_ui()

    def __init_ui(self):
        self.resize(300, 300)
        self.setMinimumSize(100, 100)
        self.setWindowTitle('Ratings')
        self.__position_window()

        self.ratings_table = RatingsTable()

        main_layout = QGridLayout()
        main_layout.addWidget(self.ratings_table)

        self.setLayout(main_layout)

    def update_ratings(self, ratings):
        self.ratings_table.update_table_data(ratings)

    def __position_window(self):
        frame_gm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).topLeft()
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.center())

    def closeEvent(self, event):
        self.graph_widget.game.ratings_stop.set()


class RatingsTable(QTableWidget):

    def __init__(self, *args):
        QTableWidget.__init__(self, *args)

        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Player', 'Rating'])
        self.setColumnWidth(0, 161)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data = {}

    def update_table_data(self, data):
        self.data.clear()
        self.data.update(data)
        self.set_data()

    def create_table_item(self, text):
        table_item = QTableWidgetItem()
        table_item.setTextAlignment(Qt.AlignCenter)
        table_item.setText(text)
        return table_item

    def set_data(self):
        self.setRowCount(0)
        for row, rating in enumerate(self.data.values()):
            self.insertRow(row)

            self.setItem(
                row, 0, self.create_table_item(rating.name))
            self.setItem(
                row, 1, self.create_table_item(str(rating.rating)))
