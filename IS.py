import flet as ft
import psycopg2
import logging
import string
import random
import re
from decimal import Decimal
from datetime import datetime


# Функция для подключения к базе данных
def connect_db():
    try:
        logging.info("Attempting to connect to the database...")
        conn = psycopg2.connect(
            dbname="steam_sale",  # Имя вашей базы данных
            user="postgres",  # Имя пользователя PostgreSQL
            password="123456789",  # Пароль пользователя
            host="localhost",  # Хост (обычно localhost)
            port="5432"  # Порт (по умолчанию 5432)
        )
        logging.info("Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Operational error: {e}")
        return None
    except psycopg2.ProgrammingError as e:
        logging.error(f"Programming error: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None


def add_user(login, password, email=None, balance=0.00):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (login, password, email, balance) VALUES (%s, %s, %s, %s)",
                       (login, password, email, balance))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"User {login} added successfully.")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")


def add_account(title, login, password, price, guarantee, description, category, owner):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        category_id = cursor.fetchone()
        if not category_id:
            cursor.execute("INSERT INTO categories (name) VALUES (%s)", (category,))
            conn.commit()
            cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
            category_id = cursor.fetchone()
        cursor.execute(
            "INSERT INTO accounts (title, login, password, price, guarantee, description, category_id, owner) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (title, login, password, price, guarantee, description, category_id[0], owner))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f"Account {title} added successfully.")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")


def authenticate_user(login, password):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password, balance FROM users WHERE login = %s", (login,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            if password == stored_password:  # Compare passwords directly
                return result[1]
        return None
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()


class MarketplaceApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Marketplace"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.user_logged_in = False
        self.username = "Анонимус"
        self.balance = 0.0
        self.all_items = []
        self.purchased_items = []
        self.init_ui()
        self.load_user_data()
        self.load_all_accounts()
        page.show_snack_bar = self.show_snack_bar

    def show_snack_bar(self, message):
        snackbar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar = snackbar
        snackbar.open = True
        print(f"Displaying snackbar: {message}")
        self.page.update()

    def init_ui(self):
        # Верхняя панель с кнопками
        self.top_buttons = ft.Row(
            controls=[
                ft.ElevatedButton("Добавить товар", on_click=self.open_add_account_window),
                ft.ElevatedButton("Пополнить", on_click=self.open_top_up_window),
                ft.ElevatedButton("Личный кабинет", on_click=self.open_account_window),
            ],
            alignment=ft.MainAxisAlignment.START,
        )

        # Поле для поиска
        self.filter_input = ft.TextField(
            label="Поиск по названию",
            on_change=self.filter_items,
            expand=True,
        )

        # Фильтры
        self.price_filter = ft.Dropdown(
            label="Цена",
            options=[
                ft.dropdown.Option("Все цены"),
                ft.dropdown.Option("Менее 500₽"),
                ft.dropdown.Option("500₽ - 1000₽"),
                ft.dropdown.Option("Более 1000₽"),
            ],
            on_change=self.filter_items,
        )

        self.guarantee_filter = ft.Dropdown(
            label="Гарантия",
            options=[
                ft.dropdown.Option("Все"),
                ft.dropdown.Option("Без гарантии"),
                ft.dropdown.Option("1 месяц"),
                ft.dropdown.Option("3 месяца"),
                ft.dropdown.Option("6 месяцев"),
                ft.dropdown.Option("1 год"),
            ],
            on_change=self.filter_items,
        )

        # Список товаров
        self.items_list = ft.ListView(expand=True)

        # Основной макет
        self.page.add(
            self.top_buttons,
            ft.Row([self.filter_input, self.price_filter, self.guarantee_filter]),
            self.items_list,
        )

        self.update_items_list()

    def load_user_data(self):
        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE login = %s", (self.username,))
            result = cursor.fetchone()
            if result:
                self.balance = result[0]
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")

    def load_all_accounts(self):
        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT title, price, guarantee, owner, login, password, id FROM accounts")
            accounts = cursor.fetchall()
            self.all_items = [
                {"name": title, "price": str(price) + "₽", "guarantee": guarantee, "owner": owner, "login": login,
                 "password": password, "id": id} for
                title, price, guarantee, owner, login, password, id in accounts
            ]
            cursor.close()
            conn.close()
            self.update_items_list()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")

    def update_items_list(self):
        self.items_list.controls.clear()
        for item in self.all_items:
            self.items_list.controls.append(
                ft.ListTile(
                    title=ft.Text(item["name"]),
                    subtitle=ft.Text(f"{item['price']} - Гарантия: {item['guarantee']}"),
                    trailing=ft.ElevatedButton(
                        "Купить",
                        on_click=lambda e, item=item: self.purchase_item(e, item),

                    )
                )
            )
        self.page.update()

    def filter_items(self, e):
        filter_text = self.filter_input.value.lower()
        selected_price_range = self.price_filter.value
        selected_guarantee = self.guarantee_filter.value

        filtered_items = []
        for item in self.all_items:
            name, price, guarantee = item["name"], item["price"], item["guarantee"]

            # Фильтр по названию
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

            filtered_items.append(item)

        self.items_list.controls.clear()
        for item in filtered_items:
            self.items_list.controls.append(
                ft.ListTile(
                    title=ft.Text(item["name"]),
                    subtitle=ft.Text(f"{item['price']} - Гарантия: {item['guarantee']}"),
                    trailing=ft.ElevatedButton(
                        "Купить",
                        on_click=lambda e, item=item: self.purchase_item(e, item)
                    )
                )
            )
        self.page.update()

    def purchase_item(self, e, item):
        if not self.user_logged_in:
            self.show_snack_bar("Вы должны войти в систему, чтобы купить аккаунт.")
            return
        if item["owner"] == self.username:
            self.show_snack_bar("Вы не можете купить свой аккаунт.")
            return
        price = Decimal(str(float(item["price"][:-1])))
        if self.balance < price:
            self.show_snack_bar("Недостаточно средств для покупки аккаунта.")
            return

        self.balance -= price
        self.purchased_items.append(item)

        try:
            conn = connect_db()
            if conn is None:
                self.show_snack_bar("Failed to connect to the database.")
                return
            cursor = conn.cursor()
            # Обновляем баланс пользователя
            cursor.execute("UPDATE users SET balance = balance - %s WHERE login = %s", (price, self.username))

            # Обновляем баланс продавца
            cursor.execute("UPDATE users SET balance = balance + %s WHERE login = %s", (price, item["owner"]))

            # Добавление в таблицу purchased_accounts
            cursor.execute(
                "INSERT INTO purchased_accounts (user_login, account_title, account_login, account_password, purchase_date) VALUES (%s, %s, %s, %s, %s)",
                (self.username, item["name"], item["login"], item["password"], datetime.now())
            )
            # Удаление аккаунта из базы данных
            cursor.execute("DELETE FROM accounts WHERE id = %s", (item["id"],))
            conn.commit()
            cursor.close()
            conn.close()
            self.load_user_data()
            self.show_snack_bar(
                f"Аккаунт {item['name']} куплен успешно. Логин: {item['login']}, Пароль: {item['password']}")
            self.all_items.remove(item)
            self.update_items_list()
            if self.account_window:
                self.account_window.refresh_content()
        except psycopg2.Error as e:
            self.show_snack_bar(f"Database error: {e}")

    def open_top_up_window(self, e):
        if not self.user_logged_in:
            self.show_snack_bar("Вы должны войти в систему, чтобы пополнить баланс.")
            return
        self.top_up_window = TopUpWindow(self, self.page.show_snack_bar, self)
        self.page.overlay.append(self.top_up_window)
        self.top_up_window.open = True
        self.page.update()

    def open_add_account_window(self, e):
        if not self.user_logged_in:
            self.show_snack_bar("Вы должны войти в систему, чтобы добавить товар.")
            return
        self.add_account_window = AddAccountWindow(self, self.page.show_snack_bar, self)
        self.page.overlay.append(self.add_account_window)
        self.add_account_window.open = True
        self.page.update()

    def open_account_window(self, e):
        self.account_window = PersonalCabinet(self, self.page.show_snack_bar, self)
        self.page.overlay.append(self.account_window)
        self.account_window.open = True
        self.page.update()

    def add_item(self, item):
        self.all_items.append(item)
        self.update_items_list()

    def update_balance(self, new_balance):
        self.balance = new_balance
        self.load_user_data()
        if self.account_window:
            self.account_window.refresh_content()

    def update_user_login_state(self, new_username, new_balance):
        self.username = new_username
        self.balance = new_balance
        self.user_logged_in = True
        self.load_user_data()
        self.page.update()

    def reset_user_login_state(self):
        self.username = "Анонимус"
        self.balance = 0.0
        self.user_logged_in = False
        self.load_user_data()
        self.page.update()


class TopUpWindow(ft.AlertDialog):
    def __init__(self, parent, show_snack_bar, app):  # Принимаем app
        super().__init__()
        self.parent = parent
        self.show_snack_bar = show_snack_bar
        self.title = ft.Text("Пополнение баланса")
        self.app = app  # Сохраняем экземпляр MarketplaceApp
        self.card_number_input = ft.TextField(
            label="Номер карты",
            hint_text="16-значный номер карты",
            input_filter=ft.InputFilter(regex_string=r"[0-9]", replacement_string=""),
            max_length=16
        )
        self.card_expiry_input = ft.TextField(
            label="Срок действия карты (MM/YY)",
            hint_text="MM/YY",
            input_filter=ft.InputFilter(regex_string=r"[0-9/]", replacement_string=""),
            max_length=5
        )
        self.card_cvv_input = ft.TextField(
            label="CVV-код",
            hint_text="3-значный CVV",
            password=True,
            input_filter=ft.InputFilter(regex_string=r"[0-9]", replacement_string=""),
            max_length=3
        )
        self.amount_input = ft.TextField(
            label="Сумма в рублях",
            hint_text="Введите сумму",
            input_filter=ft.InputFilter(regex_string=r"[0-9]", replacement_string=""),
            max_length=9
        )

        self.content = ft.Column(
            controls=[
                self.amount_input,
                self.card_number_input,
                self.card_expiry_input,
                self.card_cvv_input
            ],
            tight=True,
        )
        self.actions = [
            ft.TextButton("Пополнить", on_click=self.top_up_balance),
            ft.TextButton("Отмена", on_click=self.close_dialog),
        ]

    def top_up_balance(self, e):
        amount = self.amount_input.value
        card_number = self.card_number_input.value
        card_expiry = self.card_expiry_input.value
        card_cvv = self.card_cvv_input.value

        if not (amount and card_number and card_expiry and card_cvv):
            self.show_snack_bar("Пожалуйста, заполните все поля.")
            return

        if len(card_number) != 16:
            self.show_snack_bar("Номер карты должен содержать 16 цифр.")
            return

        if not re.match(r"^\d{2}/\d{2}$", card_expiry):
            self.show_snack_bar("Неверный формат срока действия карты (MM/YY).")
            return

        month = int(card_expiry[:2])
        year = int(card_expiry[3:])
        current_year = datetime.now().year % 100
        if month < 1 or month > 12:
            self.show_snack_bar("Неверный месяц в сроке действия карты.")
            return

        if year < current_year:
            self.show_snack_bar("Срок действия карты закончился.")
            return

        if len(card_cvv) != 3:
            self.show_snack_bar("CVV-код должен содержать 3 цифры.")
            return

        try:
            amount = int(amount)
            conn = connect_db()
            if conn is None:
                self.show_snack_bar("Failed to connect to the database.")
                return
            cursor = conn.cursor()
            # Добавляем запись в таблицу payments
            cursor.execute(
                "INSERT INTO payments (user_login, amount, card_number, card_expiry, card_cvv) VALUES (%s, %s, %s, %s, %s)",
                (self.app.username, amount, card_number, card_expiry, card_cvv)
            )

            # Добавляем запись в таблицу transactions
            cursor.execute(
                "INSERT INTO transactions (user_login, amount, transaction_type) VALUES (%s, %s, %s)",
                (self.app.username, amount, "deposit")
            )
            # Обновляем баланс пользователя
            cursor.execute("UPDATE users SET balance = balance + %s WHERE login = %s", (amount, self.app.username))
            conn.commit()
            cursor.close()
            conn.close()
            self.app.update_balance(self.app.balance + amount)
            self.show_snack_bar("Баланс пополнен успешно.")
            self.close_dialog(e)
        except psycopg2.Error as e:
            self.show_snack_bar(f"Database error: {e}")
        except ValueError:
            self.show_snack_bar("Неверный формат суммы.")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def close_dialog(self, e):
        self.open = False
        self.parent.page.update()


class AddAccountWindow(ft.AlertDialog):
    def __init__(self, parent, show_snack_bar, app):
        super().__init__()
        self.parent = parent
        self.show_snack_bar = show_snack_bar
        self.title = ft.Text("Добавление аккаунта")
        self.app = app
        self.content = ft.Column(
            controls=[
                ft.TextField(label="Заголовок", hint_text="Введите заголовок аккаунта", max_length=100),
                ft.TextField(label="Логин", hint_text="Введите логин", max_length=50),
                ft.TextField(label="Пароль", hint_text="Введите пароль", password=True, max_length=255),
                ft.TextField(label="Цена (₽)", hint_text="Введите цену"),
                ft.Dropdown(
                    label="Гарантия",
                    options=[
                        ft.dropdown.Option("Без гарантии"),
                        ft.dropdown.Option("1 месяц"),
                        ft.dropdown.Option("3 месяца"),
                        ft.dropdown.Option("6 месяц"),
                        ft.dropdown.Option("1 год"),
                    ],
                ),
                ft.TextField(label="Описание товара", hint_text="Введите описание"),
                ft.Dropdown(
                    label="Категория",
                    options=[
                        ft.dropdown.Option("Игры"),
                        ft.dropdown.Option("Программы"),
                    ],
                ),
            ],
            tight=True,
        )
        self.actions = [
            ft.TextButton("Добавить аккаунт", on_click=self.add_account),
            ft.TextButton("Отмена", on_click=self.close_dialog),
        ]

    def add_account(self, e):
        title = self.content.controls[0].value
        login = self.content.controls[1].value
        password = self.content.controls[2].value
        price = self.content.controls[3].value
        guarantee = self.content.controls[4].value
        description = self.content.controls[5].value
        category = self.content.controls[6].value

        if not (title and login and password and price.isdigit() and guarantee and category):
            self.show_snack_bar("Пожалуйста, заполните все поля.")
            return

        try:
            add_account(title, login, password, price, guarantee, description, category, self.app.username)
            self.app.add_item({
                "name": title,
                "price": price + "₽",
                "guarantee": guarantee
            })
            self.app.load_all_accounts()
            self.show_snack_bar("Аккаунт добавлен успешно.")
            self.close_dialog(e)
        except Exception as e:
            self.show_snack_bar(f"Ошибка: {e}")

    def close_dialog(self, e):
        self.open = False
        self.parent.page.update()


class PersonalCabinet(ft.AlertDialog):
    def __init__(self, parent, show_snack_bar, app):
        super().__init__()
        self.parent = parent
        self.show_snack_bar = show_snack_bar
        self.title = ft.Text("Личный кабинет")
        self.app = app  # Сохраняем ссылку на MarketplaceApp
        self.my_accounts_list = ft.ListView(expand=True)
        self.bought_accounts_list = ft.ListView(expand=True)
        self.content = ft.Column(
            controls=[
                ft.Text(self.parent.username, size=20),
                ft.Text(f"Баланс: {self.parent.balance} ₽", size=16),
                ft.ElevatedButton("Вход", on_click=self.login),
                ft.ElevatedButton("Регистрация", on_click=self.register),
                ft.ElevatedButton("Выход", on_click=self.logout),
                ft.Text("Мои аккаунты", size=18),
                self.my_accounts_list,
                ft.Text("Купленные аккаунты", size=18),
                self.bought_accounts_list,
            ],
            tight=True,
        )
        self.refresh_content()

    def refresh_content(self):
        self.content.controls[0].text = self.parent.username
        self.content.controls[1].text = f"Баланс: {self.parent.balance} ₽"
        self.update_my_accounts_list()
        self.update_bought_accounts_list()
        self.parent.page.update()

    def update_my_accounts_list(self):
        self.my_accounts_list.controls.clear()
        my_accounts = [item for item in self.app.all_items if item["owner"] == self.app.username]
        for item in my_accounts:
            self.my_accounts_list.controls.append(
                ft.ListTile(
                    title=ft.Text(item["name"]),
                    subtitle=ft.Text(f"{item['price']} - Гарантия: {item['guarantee']}"),
                )
            )

    def update_bought_accounts_list(self):
        self.bought_accounts_list.controls.clear()
        try:
            conn = connect_db()
            if conn is None:
                self.show_snack_bar("Failed to connect to the database.")
                return
            cursor = conn.cursor()
            cursor.execute(
                "SELECT account_title, account_login, account_password FROM purchased_accounts WHERE user_login = %s",
                (self.app.username,))
            bought_accounts = cursor.fetchall()
            cursor.close()
            conn.close()

            for account in bought_accounts:
                self.bought_accounts_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(account[0]),
                        subtitle=ft.Text(f"Логин: {account[1]}, Пароль: {account[2]}"),
                    )
                )
        except psycopg2.Error as e:
            self.show_snack_bar(f"Database error: {e}")

    def login(self, e):
        self.login_dialog = LoginDialog(self.app, self.show_snack_bar)
        self.parent.page.overlay.append(self.login_dialog)
        self.login_dialog.open = True
        self.parent.page.update()

    def register(self, e):
        self.register_dialog = RegisterDialog(self.parent, self.show_snack_bar)
        self.parent.page.overlay.append(self.register_dialog)
        self.register_dialog.open = True
        self.parent.page.update()

    def logout(self, e):
        self.app.reset_user_login_state()  # Используем app для сброса состояния
        self.show_snack_bar("Вы вышли из системы.")
        self.refresh_content()
        self.close_dialog(e)

    def close_dialog(self, e):
        self.open = False
        self.parent.page.update()

    def load_user_data(self):
        try:
            conn = connect_db()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE login = %s", (self.parent.username,))
            result = cursor.fetchone()
            if result:
                self.parent.balance = result[0]
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")


class LoginDialog(ft.AlertDialog):
    def __init__(self, app, show_snack_bar):  # Принимаем app
        super().__init__()
        self.app = app  # Сохраняем ссылку на app
        self.show_snack_bar = show_snack_bar
        self.title = ft.Text("Вход")
        self.content = ft.Column(
            controls=[
                ft.TextField(label="Логин", hint_text="Введите логин", max_length=20),
                ft.TextField(label="Пароль", hint_text="Введите пароль", password=True, max_length=255),
            ],
            tight=True,
        )
        self.actions = [
            ft.TextButton("Войти", on_click=self.authenticate),
            ft.TextButton("Отмена", on_click=self.close_dialog),
        ]

    def authenticate(self, e):
        login = self.content.controls[0].value
        password = self.content.controls[1].value

        if not (login and password):
            self.show_snack_bar("Пожалуйста, заполните все поля.")
            return

        print("before authentication")
        balance = authenticate_user(login, password)
        print("after authentication")
        if balance is not None:

            self.app.update_user_login_state(login, balance)
            # Use the passed in object's show_snack_bar function
            self.show_snack_bar("Вы вошли в систему.")
            self.close_dialog(e)

            # Update the content
            if self.app.account_window:
                self.app.account_window.refresh_content()
        else:
            self.show_snack_bar("Неверный логин или пароль!")

    def close_dialog(self, e):
        self.open = False
        self.app.page.update()


class RegisterDialog(ft.AlertDialog):
    def __init__(self, parent, show_snack_bar):
        super().__init__()
        self.parent = parent
        self.show_snack_bar = show_snack_bar
        self.title = ft.Text("Регистрация")
        self.content = ft.Column(
            controls=[
                ft.TextField(label="Логин", hint_text="Введите логин", max_length=20),
                ft.TextField(label="Пароль", hint_text="Введите пароль", password=True, max_length=255),
                ft.TextField(label="Подтвердите пароль", hint_text="Введите пароль еще раз", password=True,
                             max_length=255),
                ft.TextField(label="Email", hint_text="Введите email", max_length=100),
            ],
            tight=True,
        )
        self.actions = [
            ft.TextButton("Зарегистрироваться", on_click=self.complete_registration),
            ft.TextButton("Отмена", on_click=self.close_dialog),
        ]

    def complete_registration(self, e):
        login = self.content.controls[0].value
        password = self.content.controls[1].value
        confirm_password = self.content.controls[2].value
        email = self.content.controls[3].value
        print(f"Login: {login}, Password: {password}, Confirm: {confirm_password}, Email: {email}")

        if not (login and password and confirm_password and email):
            self.show_snack_bar("Пожалуйста, заполните все поля.")
            return

        if password != confirm_password:
            self.show_snack_bar("Пароли не совпадают.")
            return

        try:
            conn = connect_db()
            if conn is None:
                self.show_snack_bar("Failed to connect to the database.")
                return
            logging.info("Database connection successful.")

            cursor = conn.cursor()

            # Проверка, существует ли пользователь
            logging.info(f"Checking for user with login: {login}")
            cursor.execute("SELECT login FROM users WHERE login = %s", (login,))
            if cursor.fetchone():
                logging.info("User with that login already exists.")
                self.show_snack_bar("Пользователь с таким логином уже существует!")
            else:
                # Добавление нового пользователя
                logging.info(f"Adding new user with login: {login}")
                cursor.execute("INSERT INTO users (login, password, email, balance) VALUES (%s, %s, %s, %s)",
                               (login, password, email, 0.00))
                conn.commit()
                logging.info(f"Registration for user {login} successful")
                self.parent.update_user_login_state(login, 0.0)
                self.show_snack_bar("Регистрация прошла успешно!")
                self.close_dialog(e)
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            self.show_snack_bar(f"Ошибка базы данных: {e}")
        except Exception as e:
            logging.error(f"Exception: {e}")
        finally:
            if conn:
                cursor.close()
                conn.close()

    def close_dialog(self, e):
        self.open = False
        self.parent.page.update()


def main(page: ft.Page):
    app = MarketplaceApp(page)


ft.app(target=main)