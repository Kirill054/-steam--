import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFrame,
    QScrollArea,
    QMessageBox,
    QDialog
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt


class PersonalCabinet(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.user_logged_in = False
        self.username = ""
        self.balance = 0.0  # Добавляем атрибут для хранения баланса
        self.users = {}  # Словарь для хранения зарегистрированных пользователей

    def init_ui(self):
        # Настройка окна
        self.setWindowTitle("Личный кабинет")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("background-color: #F0F0F0;")

        # Главный макет
        main_layout = QHBoxLayout(self)

        # Левая панель
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        # Кнопки в левой панели
        self.login_button = QPushButton("Вход")
        self.login_button.setStyleSheet("background-color: #90EE90; font-size: 16px;")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setStyleSheet("background-color: #ADD8E6; font-size: 16px;")
        self.register_button.clicked.connect(self.register)

        self.exit_button = QPushButton("Выход")
        self.exit_button.setStyleSheet("background-color: #FF6F61; font-size: 16px;")
        self.exit_button.clicked.connect(self.logout)

        self.back_button = QPushButton("Назад")
        self.back_button.setStyleSheet("background-color: #FFDD00; font-size: 16px;")
        self.back_button.clicked.connect(self.back_to_main_menu)
        self.back_button.setVisible(True)  # Изначально скрыта

        left_panel.addWidget(self.login_button)
        left_panel.addWidget(self.register_button)
        left_panel.addWidget(self.exit_button)
        left_panel.addWidget(self.back_button)  # Кнопка "Назад"
        left_panel.addStretch(1)

        # Правая панель
        self.right_panel = QVBoxLayout()

        # Аватарка и информация о пользователе
        avatar_layout = QHBoxLayout()
        self.avatar_label = QLabel()
        username_label = QLabel("Анонимус")
        self.balance_label = QLabel("Баланс: 0.00 ₽")  # Отображение баланса
        username_label.setFont(QFont("Arial", 16))
        username_label.setStyleSheet("color: black;")
        self.balance_label.setFont(QFont("Arial", 14))
        self.balance_label.setStyleSheet("color: black; padding-left: 10px;")

        avatar_layout.addWidget(self.avatar_label)
        avatar_layout.addWidget(username_label)
        avatar_layout.addWidget(self.balance_label)  # Добавление метки для баланса
        avatar_layout.addStretch(1)

        self.right_panel.addLayout(avatar_layout)

        # Раздел для информации о товарах/аккаунтах
        account_info_label = QLabel("Предложения:")
        account_info_label.setFont(QFont("Arial", 14))
        account_info_label.setStyleSheet("color: black;")
        self.right_panel.addWidget(account_info_label)

        # Прокручиваемая область для товаров
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        account_list_widget = QFrame()
        account_list_widget.setStyleSheet("background-color: white; border: 1px solid #CCC;")
        account_list_layout = QVBoxLayout(account_list_widget)

        for i in range(10):  # Пример отображения 10 товаров
            item_label = QLabel(f"Товар/аккаунт {i + 1}")
            item_label.setStyleSheet("font-size: 14px; padding: 5px;")
            account_list_layout.addWidget(item_label)

        account_list_layout.addStretch(1)
        scroll_area.setWidget(account_list_widget)

        self.right_panel.addWidget(scroll_area)

        # Добавление панелей в главный макет
        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(self.right_panel, 3)

        self.setLayout(main_layout)

    def login(self):
        if not self.user_logged_in:
            self.login_dialog = LoginDialog(self)
            self.login_dialog.show()
        else:
            QMessageBox.information(self, "Уведомление", "Вы уже вошли в аккаунт!")

    def register(self):
        if not self.user_logged_in:
            self.register_dialog = RegisterDialog(self)
            self.register_dialog.show()
        else:
            QMessageBox.information(self, "Уведомление", "Вы уже зарегистрированы и вошли в аккаунт!")

    def logout(self):
        if self.user_logged_in:
            self.user_logged_in = False
            self.username = ""
            self.balance = 0.0  # Сброс баланса при выходе
            self.update_ui()
            QMessageBox.information(self, "Выход", "Вы успешно вышли из аккаунта!")
        else:
            QMessageBox.information(self, "Выход", "Вы не вошли в аккаунт!")

    def update_ui(self):
        """Обновить интерфейс в зависимости от состояния пользователя"""
        # Обновление отображаемого имени и баланса
        username_label = self.right_panel.itemAt(0).itemAt(1).widget()
        balance_label = self.right_panel.itemAt(0).itemAt(2).widget()

        if self.user_logged_in:
            username_label.setText(self.username)
            balance_label.setText(f"Баланс: {self.balance:.2f} ₽")
            self.back_button.setVisible(True)  # Показываем кнопку "Назад"
        else:
            username_label.setText("Анонимус")
            balance_label.setText("Баланс: 0.00 ₽")
            self.back_button.setVisible(False)  # Скрываем кнопку "Назад"

    def back_to_main_menu(self):
        """Возвращение в главное меню"""
        from main1 import MainMenu  # Импортируем главное меню из файла main1.py
        self.close()  # Закрываем текущее окно
        self.main_menu = MainMenu()  # Открываем главное меню
        self.main_menu.show()

    def top_up_balance(self, amount):
        """Метод для пополнения баланса"""
        if self.user_logged_in:
            self.balance += amount
            self.update_ui()
            QMessageBox.information(self, "Пополнение", f"Баланс успешно пополнен на {amount} ₽!")
        else:
            QMessageBox.warning(self, "Ошибка", "Вы должны войти в аккаунт для пополнения баланса!")


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пароль")

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        login_button = QPushButton("Войти")
        login_button.clicked.connect(self.authenticate)

        layout.addWidget(login_button)

        self.setLayout(layout)

    def authenticate(self):
        # Логика для проверки данных
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.parent().users and self.parent().users[username] == password:
            self.parent().username = username
            self.parent().user_logged_in = True
            self.parent().balance = 100.0  # Пример начального баланса
            self.parent().update_ui()
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Пароль")

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)

        register_button = QPushButton("Зарегистрироваться")
        register_button.clicked.connect(self.complete_registration)

        layout.addWidget(register_button)

        self.setLayout(layout)

    def complete_registration(self):
        # Логика для регистрации (здесь можно добавить проверку на уникальность логина)
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            if username not in self.parent().users:
                self.parent().users[username] = password
                self.parent().username = username
                self.parent().user_logged_in = True
                self.parent().balance = 100.0  # Пример начального баланса
                self.parent().update_ui()
                QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже зарегистрирован!")
        else:
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не могут быть пустыми!")


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PersonalCabinet()
    window.show()
    sys.exit(app.exec_())
