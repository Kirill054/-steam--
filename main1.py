from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QScrollArea, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
import sys
import subprocess

class TopUpWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Пополнение баланса")
        self.setGeometry(200, 200, 400, 400)

        # Основной макет
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Заголовок
        title_label = QLabel("Пополнение баланса")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Поле ввода суммы
        amount_label = QLabel("Введите сумму пополнения:")
        main_layout.addWidget(amount_label)

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма в рублях")
        self.amount_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.amount_input)

        # Поле ввода номера карты
        card_number_label = QLabel("Введите номер карты:")
        main_layout.addWidget(card_number_label)

        self.card_number_input = QLineEdit()
        self.card_number_input.setPlaceholderText("16-значный номер карты")
        self.card_number_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.card_number_input)

        # Поле ввода даты окончания карты
        card_expiry_label = QLabel("Введите срок действия карты (MM/YY):")
        main_layout.addWidget(card_expiry_label)

        self.card_expiry_input = QLineEdit()
        self.card_expiry_input.setPlaceholderText("MM/YY")
        self.card_expiry_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.card_expiry_input)

        # Поле ввода CVV-кода
        card_cvv_label = QLabel("Введите CVV-код карты:")
        main_layout.addWidget(card_cvv_label)

        self.card_cvv_input = QLineEdit()
        self.card_cvv_input.setPlaceholderText("3-значный CVV")
        self.card_cvv_input.setEchoMode(QLineEdit.Password)  # Скрытие символов
        self.card_cvv_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.card_cvv_input)

        # Кнопка "Пополнить"
        top_up_button = QPushButton("Пополнить")
        top_up_button.setStyleSheet("background-color: #4caf50; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        top_up_button.clicked.connect(self.top_up_balance)
        main_layout.addWidget(top_up_button)

        # Кнопка "Отмена"
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        cancel_button.clicked.connect(self.close)
        main_layout.addWidget(cancel_button)

    def top_up_balance(self):
        # Получение введенных данных
        amount = self.amount_input.text()
        card_number = self.card_number_input.text()
        card_expiry = self.card_expiry_input.text()
        card_cvv = self.card_cvv_input.text()

        # Проверка на корректность данных
        try:
            if not amount or float(amount) <= 0:
                raise ValueError("Введите корректную сумму.")

            if not card_number or len(card_number) != 16 or not card_number.isdigit():
                raise ValueError("Введите корректный 16-значный номер карты.")

            if not card_expiry or len(card_expiry) != 5 or card_expiry[2] != '/' or not card_expiry[:2].isdigit() or not card_expiry[3:].isdigit():
                raise ValueError("Введите корректный срок действия карты (MM/YY).")

            if not card_cvv or len(card_cvv) != 3 or not card_cvv.isdigit():
                raise ValueError("Введите корректный 3-значный CVV-код.")

            # Успешное пополнение
            QMessageBox.information(self, "Успех", f"Ваш баланс успешно пополнен на {float(amount):.2f}₽!")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

class AddAccountWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Добавление аккаунта")
        self.setGeometry(200, 200, 500, 500)

        # Основной макет
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Заголовок окна
        title_label = QLabel("Добавление нового аккаунта")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Поле для заголовка
        account_title_label = QLabel("Заголовок:")
        main_layout.addWidget(account_title_label)

        self.account_title_input = QLineEdit()
        self.account_title_input.setPlaceholderText("Введите заголовок аккаунта")
        self.account_title_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.account_title_input)

        # Поле для логина
        login_label = QLabel("Логин:")
        main_layout.addWidget(login_label)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин от аккаунта")
        self.login_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.login_input)

        # Поле для пароля
        password_label = QLabel("Пароль:")
        main_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль от аккаунта")
        self.password_input.setEchoMode(QLineEdit.Password)  # Скрытие символов
        self.password_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.password_input)

        # Поле для цены
        price_label = QLabel("Цена (₽):")
        main_layout.addWidget(price_label)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Введите цену")
        self.price_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.price_input)

        # Поле для длительности гарантии
        guarantee_label = QLabel("Длительность гарантии:")
        main_layout.addWidget(guarantee_label)

        self.guarantee_combo = QComboBox()
        self.guarantee_combo.addItems(["Без гарантии", "1 месяц", "3 месяца", "6 месяцев", "1 год"])
        self.guarantee_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.guarantee_combo)

        # Поле для описания товара
        description_label = QLabel("Описание товара:")
        main_layout.addWidget(description_label)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Введите описание товара")
        self.description_input.setStyleSheet("padding: 5px; font-size: 14px;")
        main_layout.addWidget(self.description_input)

        # Кнопка "Добавить аккаунт"
        add_account_button = QPushButton("Добавить аккаунт")
        add_account_button.setStyleSheet("background-color: #4caf50; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        add_account_button.clicked.connect(self.add_account)
        main_layout.addWidget(add_account_button)

        # Кнопка "Отмена"
        cancel_button = QPushButton("Отмена")
        cancel_button.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; font-weight: bold; padding: 10px;")
        cancel_button.clicked.connect(self.close)
        main_layout.addWidget(cancel_button)

    def add_account(self):
        # Получение введенных данных
        account_title = self.account_title_input.text()
        login = self.login_input.text()
        password = self.password_input.text()
        price = self.price_input.text()
        guarantee = self.guarantee_combo.currentText()
        description = self.description_input.text()

        # Проверка на корректность данных
        try:
            if not account_title or not login or not password or not price or not description:
                raise ValueError("Все поля должны быть заполнены.")

            if not price.isdigit() or int(price) <= 0:
                raise ValueError("Введите корректную цену.")

            # Успешное добавление аккаунта
            QMessageBox.information(self, "Успех", f"Аккаунт '{account_title}' успешно добавлен.")
            self.close()

        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Marketplace")
        self.setGeometry(100, 100, 900, 600)

        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Основной макет
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Левая панель (Фильтры)
        self.create_filters(main_layout)

        # Правая панель (Список товаров)
        self.create_items_list(main_layout)

        # Список данных товаров (для фильтрации)
        self.all_items = [
            {"name": "Личный аккаунт, GTA 5, Counter-Strike Complete (CS 2 Prime)", "price": "1500₽", "guarantee": "1 год"},
            {"name": "DayZ | Phasmophobia | Cyberpunk 2077", "price": "450₽", "guarantee": "3 месяца"},
            {"name": "Rust", "price": "250₽", "guarantee": "1 месяц"},
            {"name": "Call of Duty: Black Ops III VAC", "price": "150₽", "guarantee": "Без гарантии"},
            {"name": "One Piece Pirate Warriors 3", "price": "250₽", "guarantee": "6 месяцев"},
        ]
        self.update_items_list()

    def create_filters(self, layout):
        # Панель фильтров
        filter_layout = QVBoxLayout()  # Вертикальный макет для фильтров
        filter_layout.setSpacing(5)  # Уменьшаем расстояние между элементами

        # Поле для поиска по названию
        search_layout = QHBoxLayout()  # Горизонтальный макет для текста и поля ввода
        filter_label = QLabel("Поиск по названию:")
        search_layout.addWidget(filter_label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Введите название товара")
        self.filter_input.textChanged.connect(self.filter_items)
        self.filter_input.setStyleSheet("padding: 5px; font-size: 14px;")
        search_layout.addWidget(self.filter_input)

        # Добавляем горизонтальный макет поиска в вертикальный макет фильтров
        filter_layout.addLayout(search_layout)

        # Фильтр по цене
        price_layout = QHBoxLayout()  # Горизонтальный макет для метки и выпадающего списка
        price_label = QLabel("Цена:")
        price_layout.addWidget(price_label)

        self.price_filter_combo = QComboBox()
        self.price_filter_combo.addItems(["Все цены", "Менее 500₽", "500₽ - 1000₽", "Более 1000₽"])
        self.price_filter_combo.currentIndexChanged.connect(self.filter_items)
        self.price_filter_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        price_layout.addWidget(self.price_filter_combo)

        # Добавляем горизонтальный макет для цены в основной вертикальный макет фильтров
        filter_layout.addLayout(price_layout)

        # Фильтр по гарантии
        guarantee_layout = QHBoxLayout()  # Горизонтальный макет для метки и выпадающего списка
        guarantee_label = QLabel("Гарантия:")
        guarantee_layout.addWidget(guarantee_label)

        self.guarantee_filter_combo = QComboBox()
        self.guarantee_filter_combo.addItems(["Все", "Без гарантии", "1 месяц", "3 месяца", "6 месяцев", "1 год"])
        self.guarantee_filter_combo.currentIndexChanged.connect(self.filter_items)
        self.guarantee_filter_combo.setStyleSheet("padding: 5px; font-size: 14px;")
        guarantee_layout.addWidget(self.guarantee_filter_combo)

        # Добавляем горизонтальный макет для гарантии в основной вертикальный макет фильтров
        filter_layout.addLayout(guarantee_layout)

        # Убираем внешние отступы
        filter_layout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(filter_layout)

    def create_items_list(self, layout):
        # Главный макет для товаров
        item_layout = QVBoxLayout()

        # Верхняя панель (кнопки "Добавить товар", "Пополнить" и "Личный кабинет")
        top_buttons = QHBoxLayout()
        add_item_btn = QPushButton("Добавить товар")
        add_item_btn.setStyleSheet("background-color: #3a89ff; color: white; font-weight: bold;")
        add_item_btn.clicked.connect(self.open_add_account_window)
        top_buttons.addWidget(add_item_btn)

        replenish_btn = QPushButton("Пополнить")
        replenish_btn.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold;")
        replenish_btn.clicked.connect(self.open_top_up_window)
        top_buttons.addWidget(replenish_btn)

        # Добавляем кнопку "Личный кабинет"
        account_btn = QPushButton("Личный кабинет")
        account_btn.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        account_btn.clicked.connect(self.open_account_window)  # Функция открытия личного кабинета
        top_buttons.addWidget(account_btn)

        def open_personal_cabinet(self):
            """Открытие личного кабинета и закрытие главного меню"""
            from personal_cabinet import PersonalCabinet  # Импортируем личный кабинет
            self.close()  # Закрываем главное меню
            self.personal_cabinet_window = PersonalCabinet()  # Создаем окно личного кабинета
            self.personal_cabinet_window.show()

        top_buttons.addStretch()
        item_layout.addLayout(top_buttons)

        # Список товаров
        self.items_list = QListWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.items_list)
        item_layout.addWidget(scroll_area)

        # Добавление товаров в основное окно
        items_widget = QWidget()
        items_widget.setLayout(item_layout)
        layout.addWidget(items_widget)

    def update_items_list(self):
        self.items_list.clear()
        for item in self.all_items:
            self.add_item(item["name"], item["price"], item["guarantee"])

    def add_item(self, name, price, guarantee):
        item = QListWidgetItem(f"{name} - {price} - Гарантия: {guarantee}")
        self.items_list.addItem(item)

    def filter_items(self):
        filter_text = self.filter_input.text().lower()
        selected_price_range = self.price_filter_combo.currentText()
        selected_guarantee = self.guarantee_filter_combo.currentText()

        self.items_list.clear()

        for item in self.all_items:
            name, price, guarantee = item["name"], item["price"], item["guarantee"]

            # Фильтр по названию товара
            if filter_text and filter_text not in name.lower():
                continue

            # Фильтр по цене
            item_price = int(price[:-1])
            if selected_price_range == "Менее 500₽" and item_price >= 500:
                continue
            elif selected_price_range == "500₽ - 1000₽" and not (500 <= item_price <= 1000):
                continue
            elif selected_price_range == "Более 1000₽" and item_price <= 1000:
                continue

            # Фильтр по гарантии
            if selected_guarantee != "Все" and guarantee != selected_guarantee:
                continue

            self.add_item(name, price, guarantee)

    def open_top_up_window(self):
        self.top_up_window = TopUpWindow()
        self.top_up_window.show()

    def open_add_account_window(self):
        self.add_account_window = AddAccountWindow()
        self.add_account_window.show()

    def open_account_window(self):
        """Открытие окна личного кабинета"""
        try:
            subprocess.Popen([sys.executable, "profile.py"])
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть личный кабинет: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
