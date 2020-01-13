from PyQt5.QtGui import QIntValidator, QValidator
from PyQt5.QtWidgets import QApplication, QGridLayout, QDialog, QLabel, QLineEdit, QPushButton


class SignInPopup(QDialog):
    def __init__(self):
        super(SignInPopup, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(300, 100)
        self.setWindowTitle('Sign in')
        self.__center_window()

        main_layout = QGridLayout()

        # Creating labels
        self.__user_name_label = QLabel('User name')
        self.__user_password_label = QLabel('Password')

        # Creating text boxes
        self.__user_name_text_box = QLineEdit('Green')
        self.__user_password_text_box = QLineEdit('password')
        self.__user_password_text_box.setEchoMode(QLineEdit.Password)

        # Creating buttons
        self.__sign_in_button = QPushButton('Sign in')
        self.__sign_in_button.clicked.connect(self.__sign_in)

        # Adding elements to layout
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


class NewGamePopup(QDialog):
    def __init__(self):
        super(NewGamePopup, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        self.setFixedSize(300, 200)
        self.setWindowTitle('Create new game')
        self.__center_window()

        main_layout = QGridLayout()

        # Creating labels
        self.__user_name_label = QLabel('User name')
        self.__user_password_label = QLabel('Password')
        self.__game_name_label = QLabel('Game name')
        self.__num_turns_label = QLabel('Turns')
        self.__num_players_label = QLabel('Players count')
        self.__error_label = QLabel('Please, enter correct data')
        self.__error_label.setVisible(False)

        # Creating text boxes
        self.__user_name_text_box = QLineEdit('Green')
        self.__user_password_text_box = QLineEdit('password')
        self.__user_password_text_box.setEchoMode(QLineEdit.Password)
        self.__game_name_text_box = QLineEdit('GreenGame')
        self.__num_turns_text_box = QLineEdit('-1')
        self.__num_players_text_box = QLineEdit('1')

        # Creating validators
        self.__num_turns_text_box.setValidator(QIntValidator(-1, 1000000))
        self.__num_turns_text_box.textChanged.connect(self.check_state)
        self.__num_turns_text_box.textChanged.emit(self.__num_turns_text_box.text())
        self.__num_players_text_box.setValidator(QIntValidator(1, 10))
        self.__num_players_text_box.textChanged.connect(self.check_state)
        self.__num_players_text_box.textChanged.emit(self.__num_players_text_box.text())

        # Creating buttons
        self.__create_new_game_button = QPushButton('Create New Game')
        self.__create_new_game_button.clicked.connect(self.__create_new_game)

        # Adding elements to layout
        main_layout.addWidget(self.__user_name_label, 0, 0)
        main_layout.addWidget(self.__user_name_text_box, 0, 1)
        main_layout.addWidget(self.__user_password_label, 1, 0)
        main_layout.addWidget(self.__user_password_text_box, 1, 1)
        main_layout.addWidget(self.__game_name_label, 2, 0)
        main_layout.addWidget(self.__game_name_text_box, 2, 1)
        main_layout.addWidget(self.__num_turns_label, 3, 0)
        main_layout.addWidget(self.__num_turns_text_box, 3, 1)
        main_layout.addWidget(self.__num_players_label, 4, 0)
        main_layout.addWidget(self.__num_players_text_box, 4, 1)
        main_layout.addWidget(self.__create_new_game_button, 5, 0, 2, 2)
        main_layout.addWidget(self.__error_label, 6, 0, 2, 2)

        self.setLayout(main_layout)

    def __center_window(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def check_state(self):
        sender = self.sender()

        if self.validate_text_box(sender):
            color = '#ffffff'  # white
            self.__error_label.setVisible(False)
        else:
            color = '#f6989d'  # red
            self.__error_label.setVisible(True)

        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def validate_text_box(self, text_box):
        validator = text_box.validator()
        state = validator.validate(text_box.text(), 0)[0]

        if state != QValidator.Acceptable:
            return False
        return True

    def validate_text_boxes(self):
        is_valid = True

        if not self.validate_text_box(self.__num_turns_text_box):
            is_valid = False

        if not self.validate_text_box(self.__num_players_text_box):
            is_valid = False

        return is_valid

    def __create_new_game(self):

        if self.validate_text_boxes():
            self.user_name = self.__user_name_text_box.text()
            self.user_password = self.__user_password_text_box.text()
            self.game_name = self.__game_name_text_box.text()
            self.num_turns = self.__num_turns_text_box.text()
            self.num_players = self.__num_players_text_box.text()

            self.accept()
