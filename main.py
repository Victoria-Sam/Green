import sys

from PyQt5.QtWidgets import QApplication, QStyleFactory

from connect_widget import ConnectWidget
from connection import Connection

if __name__ == '__main__':
    connection = Connection()

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    app.setStyle(QStyleFactory.create('gtk'))

    connect_widget = ConnectWidget()
    connect_widget.show()

    app.exec_()

    Connection().close()
    sys.exit()
