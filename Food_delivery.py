import sys
import json
import re
import os
from abc import ABC, abstractmethod
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_database()
        return cls._instance

    def _init_database(self):
        self.users_file = "users.json"
        self.restaurants_file = "restaurants.json"
        self.orders_file = "orders.json"
        self.initialize_files()

    def initialize_files(self):
        for file in [self.users_file, self.restaurants_file, self.orders_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    json.dump([], f)

    def load_users(self):
        with open(self.users_file, 'r') as f:
            return json.load(f)

    def save_users(self, users):
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)

    def load_restaurants(self):
        with open(self.restaurants_file, 'r') as f:
            return json.load(f)

    def save_restaurants(self, restaurants):
        with open(self.restaurants_file, 'w') as f:
            json.dump(restaurants, f, indent=2)
            
    def load_orders(self):
        with open(self.orders_file, 'r') as f:
            return json.load(f)
            
    def save_orders(self, orders):
        with open(self.orders_file, 'w') as f:
            json.dump(orders, f, indent=2)

class AbstractUser(ABC):
    def __init__(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.birth_date = data['birth_date']
        self.email = data['email']
        self.login = data['login']
        self.password = data['password']
        self.address = data['address']
        self.role = data.get('role', 'user')

class RegularUser(AbstractUser):
    pass

class AdminUser(AbstractUser):
    pass

class UserCreator(ABC):
    @abstractmethod
    def create_user(self, user_data) -> AbstractUser:
        pass

class RegularUserCreator(UserCreator):
    def create_user(self, user_data) -> AbstractUser:
        return RegularUser(user_data)

class AdminUserCreator(UserCreator):
    def create_user(self, user_data) -> AbstractUser:
        return AdminUser(user_data)

class UserSystemFacade:
    def __init__(self):
        self.db = Database()
        self.regular_creator = RegularUserCreator()
        self.admin_creator = AdminUserCreator()

    def register_user(self, user_data):
        users = self.db.load_users()
        if any(u['login'] == user_data['login'] for u in users):
            return False, "Логин уже существует"
        if user_data['password'] != user_data['repeat_password']:
            return False, "Пароли не совпадают"
        if not re.match(r'^[A-Za-z0-9]+$', user_data['password']):
            return False, "Пароль должен содержать только латинские буквы и цифры"
        user_data.pop('repeat_password')
        user_data['role'] = 'user'
        users.append(user_data)
        self.db.save_users(users)
        return True, "Регистрация прошла успешно"

    def login_user(self, login, password):
        users = self.db.load_users()
        user_data = next((u for u in users if u['login'] == login and u['password'] == password), None)
        if not user_data:
            return None
        if user_data.get('role') == 'admin':
            return self.admin_creator.create_user(user_data)
        else:
            return self.regular_creator.create_user(user_data)

class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class SearchSubject(Subject):
    def __init__(self):
        super().__init__()
        self.results = []

    def update_results(self, results):
        self.results = results
        self.notify(results)

class UserBuilder:
    def __init__(self):
        self.user_data = {
            'first_name': '',
            'last_name': '',
            'birth_date': '',
            'email': '',
            'login': '',
            'password': '',
            'repeat_password': '',
            'address': ''
        }

    def set_first_name(self, first_name):
        self.user_data['first_name'] = first_name
        return self

    def set_last_name(self, last_name):
        self.user_data['last_name'] = last_name
        return self

    def set_birth_date(self, birth_date):
        self.user_data['birth_date'] = birth_date
        return self

    def set_email(self, email):
        self.user_data['email'] = email
        return self

    def set_login(self, login):
        self.user_data['login'] = login
        return self

    def set_password(self, password):
        self.user_data['password'] = password
        return self

    def set_repeat_password(self, repeat_password):
        self.user_data['repeat_password'] = repeat_password
        return self

    def set_address(self, address):
        self.user_data['address'] = address
        return self

    def build(self):
        return self.user_data

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, items):
        pass

class SortByName(SortStrategy):
    def sort(self, items):
        return sorted(items, key=lambda x: x['name'])

class SortByRating(SortStrategy):
    def sort(self, items):
        return sorted(items, key=lambda x: x.get('rating', 4.0), reverse=True)

class SortContext:
    def __init__(self, strategy):
        self._strategy = strategy

    def set_strategy(self, strategy):
        self._strategy = strategy

    def execute_sort(self, items):
        return self._strategy.sort(items)

class Restaurant:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.rating = data.get('rating', 4.5)
        self.menu = [MenuItem(item) for item in data['menu']]

class MenuItem:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.price = data['price']
        self.category = data.get('category', 'Основное блюдо')

class FoodDeliveryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FoodExpress - Доставка вкусной еды")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow { background-color: #f8f9fa; }
            QWidget { font-family: 'Segoe UI'; font-size: 12pt; }
            QPushButton {
                background-color: #4CAF50; color: white; border-radius: 8px;
                padding: 10px 20px; font-weight: bold; border: none; font-size: 12pt;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton#secondary { background-color: #2196F3; }
            QPushButton#secondary:hover { background-color: #0b7dda; }
            QPushButton#danger { background-color: #f44336; }
            QPushButton#danger:hover { background-color: #d32f2f; }
            QLineEdit, QComboBox, QDateEdit {
                padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 12pt;
            }
            QLabel { color: #333; font-size: 12pt; }
            QListWidget {
                background-color: white; border: 1px solid #ddd; border-radius: 8px; font-size: 11pt;
            }
            QFrame#header { background-color: #4CAF50; border: none; padding: 15px; }
            QFrame#card {
                background-color: white; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0;
            }
            QLabel#title { font-size: 24pt; font-weight: bold; color: white; }
            QLabel#section { font-size: 16pt; font-weight: bold; color: #333; padding: 10px 0; }
        """)
        
        self.db = Database()
        self.user_system = UserSystemFacade()
        self.search_subject = SearchSubject()
        self.search_subject.attach(self)
        
        self.current_user = None
        self.current_restaurant = None
        self.cart = []
        
        self.init_ui()
        self.show_login()

    def init_ui(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_page = self.create_login_page()
        self.register_page = self.create_register_page()
        self.main_page = self.create_main_page()
        self.restaurant_page = self.create_restaurant_page()
        self.cart_page = self.create_cart_page()
        self.order_confirmation_page = self.create_order_confirmation_page()
        self.admin_page = self.create_admin_page()
        
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.restaurant_page)
        self.stacked_widget.addWidget(self.cart_page)
        self.stacked_widget.addWidget(self.order_confirmation_page)
        self.stacked_widget.addWidget(self.admin_page)

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout()
        title = QLabel("FoodExpress")
        title.setObjectName("title")
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        form_container = QFrame()
        form_container.setObjectName("card")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        form_title = QLabel("Вход в аккаунт")
        form_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #333;")
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        
        password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.handle_login)
        
        register_btn = QPushButton("Создать аккаунт")
        register_btn.setObjectName("secondary")
        register_btn.clicked.connect(self.show_register)
        
        form_layout.addWidget(form_title)
        form_layout.addWidget(login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(login_btn)
        form_layout.addWidget(register_btn)
        
        form_container.setLayout(form_layout)
        layout.addWidget(form_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        page.setLayout(layout)
        return page

    def create_register_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout()
        title = QLabel("FoodExpress")
        title.setObjectName("title")
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.show_login)
        header_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignRight)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        form_container = QFrame()
        form_container.setObjectName("card")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        form_title = QLabel("Создание аккаунта")
        form_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #333;")
        form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate.currentDate().addYears(-18))
        self.email_input = QLineEdit()
        self.login_input_reg = QLineEdit()
        self.password_input_reg = QLineEdit()
        self.password_input_reg.setEchoMode(QLineEdit.EchoMode.Password)
        self.repeat_password_input = QLineEdit()
        self.repeat_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.address_input = QLineEdit()
        
        grid_layout.addWidget(QLabel("Имя:"), 0, 0)
        grid_layout.addWidget(self.first_name_input, 0, 1)
        grid_layout.addWidget(QLabel("Фамилия:"), 0, 2)
        grid_layout.addWidget(self.last_name_input, 0, 3)
        grid_layout.addWidget(QLabel("Дата рождения:"), 1, 0)
        grid_layout.addWidget(self.birth_date_input, 1, 1)
        grid_layout.addWidget(QLabel("Email:"), 1, 2)
        grid_layout.addWidget(self.email_input, 1, 3)
        grid_layout.addWidget(QLabel("Логин:"), 2, 0)
        grid_layout.addWidget(self.login_input_reg, 2, 1, 1, 3)
        grid_layout.addWidget(QLabel("Пароль:"), 3, 0)
        grid_layout.addWidget(self.password_input_reg, 3, 1, 1, 3)
        grid_layout.addWidget(QLabel("Повторите пароль:"), 4, 0)
        grid_layout.addWidget(self.repeat_password_input, 4, 1, 1, 3)
        grid_layout.addWidget(QLabel("Адрес доставки:"), 5, 0)
        grid_layout.addWidget(self.address_input, 5, 1, 1, 3)
        
        register_btn = QPushButton("Зарегистрироваться")
        register_btn.clicked.connect(self.handle_register)
        
        form_layout.addWidget(form_title)
        form_layout.addLayout(grid_layout)
        form_layout.addWidget(register_btn)
        
        form_container.setLayout(form_layout)
        layout.addWidget(form_container)
        
        page.setLayout(layout)
        return page

    def create_main_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QFrame()
        header_layout = QHBoxLayout()
        
        self.welcome_label = QLabel()
        self.welcome_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333;")
        
        cart_btn = QPushButton("🛒 Корзина")
        cart_btn.setObjectName("secondary")
        cart_btn.clicked.connect(self.show_cart)
        
        logout_btn = QPushButton("Выйти")
        logout_btn.setObjectName("danger")
        logout_btn.clicked.connect(self.logout)
        
        header_layout.addWidget(self.welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(cart_btn)
        header_layout.addWidget(logout_btn)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        search_frame = QFrame()
        search_frame.setObjectName("card")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск ресторанов или блюд...")
        self.search_input.textChanged.connect(self.handle_search)
        
        search_btn = QPushButton("Поиск")
        search_btn.clicked.connect(self.handle_search)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Сортировать по названию")
        self.sort_combo.addItem("Сортировать по рейтингу")
        self.sort_combo.currentIndexChanged.connect(self.load_restaurants)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(self.sort_combo)
        search_frame.setLayout(search_layout)
        layout.addWidget(search_frame)
        
        self.search_results_label = QLabel("Результаты поиска:")
        self.search_results_label.setObjectName("section")
        self.search_results_label.hide()
        
        self.search_results_list = QListWidget()
        self.search_results_list.hide()
        self.search_results_list.itemClicked.connect(self.handle_search_result_click)
        
        restaurant_section = QLabel("Популярные рестораны")
        restaurant_section.setObjectName("section")
        
        self.restaurant_list = QListWidget()
        self.restaurant_list.setViewMode(QListWidget.ViewMode.ListMode)
        self.restaurant_list.setSpacing(15)
        self.restaurant_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.restaurant_list.itemClicked.connect(self.show_restaurant)
        
        layout.addWidget(self.search_results_label)
        layout.addWidget(self.search_results_list)
        layout.addWidget(restaurant_section)
        layout.addWidget(self.restaurant_list)
        
        page.setLayout(layout)
        return page

    def create_restaurant_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QFrame()
        header_layout = QHBoxLayout()
        
        self.restaurant_title = QLabel()
        self.restaurant_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #FF5722;")
        
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.show_main)
        
        cart_btn = QPushButton("Корзина")
        cart_btn.setObjectName("secondary")
        cart_btn.clicked.connect(self.show_cart)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.restaurant_title)
        header_layout.addStretch()
        header_layout.addWidget(cart_btn)
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        self.menu_tabs = QTabWidget()
        layout.addWidget(self.menu_tabs)
        
        page.setLayout(layout)
        return page

    def create_cart_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QFrame()
        header_layout = QHBoxLayout()
        
        cart_title = QLabel("Ваша корзина")
        cart_title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #333;")
        
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.show_main)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(cart_title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        self.cart_list = QListWidget()
        layout.addWidget(self.cart_list)
        
        self.total_label = QLabel("Итого: 0.00 ₽")
        self.total_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        checkout_btn = QPushButton("Оформить заказ")
        checkout_btn.clicked.connect(self.show_order_confirmation)
        
        layout.addWidget(self.total_label)
        layout.addWidget(checkout_btn)
        
        page.setLayout(layout)
        return page

    def create_order_confirmation_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QFrame()
        header_layout = QHBoxLayout()
        
        title = QLabel("Подтверждение заказа")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #333;")
        
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.show_cart)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        summary_frame = QFrame()
        summary_frame.setObjectName("card")
        summary_layout = QVBoxLayout()
        
        self.order_summary = QLabel()
        self.order_summary.setStyleSheet("font-size: 14pt;")
        
        self.delivery_address = QLabel()
        self.delivery_address.setStyleSheet("font-size: 14pt;")
        
        payment_layout = QHBoxLayout()
        payment_label = QLabel("Способ оплаты:")
        self.payment_combo = QComboBox()
        self.payment_combo.addItem("Наличными при получении")
        self.payment_combo.addItem("Банковская карта")
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_combo)
        
        summary_layout.addWidget(QLabel("Сводка заказа:"))
        summary_layout.addWidget(self.order_summary)
        summary_layout.addSpacing(10)
        summary_layout.addWidget(QLabel("Адрес доставки:"))
        summary_layout.addWidget(self.delivery_address)
        summary_layout.addSpacing(10)
        summary_layout.addLayout(payment_layout)
        summary_layout.addSpacing(20)
        
        confirm_btn = QPushButton("Подтвердить заказ")
        confirm_btn.clicked.connect(self.confirm_order)
        
        summary_layout.addWidget(confirm_btn)
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        page.setLayout(layout)
        return page

    def create_admin_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QFrame()
        header_layout = QHBoxLayout()
        
        title = QLabel("Панель администратора")
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #333;")
        
        back_btn = QPushButton("Назад")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.logout)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header.setLayout(header_layout)
        layout.addWidget(header)
        
        content = QLabel(
            "Добро пожаловать в панель администратора!\n\n"
            "Здесь вы можете управлять ресторанами, пользователями и заказами."
        )
        content.setStyleSheet("font-size: 14pt;")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        users_btn = QPushButton("Управление пользователями")
        users_btn.setObjectName("secondary")
        
        restaurants_btn = QPushButton("Управление ресторанами")
        restaurants_btn.setObjectName("secondary")
        
        orders_btn = QPushButton("Просмотр заказов")
        orders_btn.setObjectName("secondary")
        
        layout.addWidget(content)
        layout.addStretch()
        layout.addWidget(users_btn)
        layout.addWidget(restaurants_btn)
        layout.addWidget(orders_btn)
        layout.addStretch()
        
        page.setLayout(layout)
        return page

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        
        user = self.user_system.login_user(login, password)
        if user:
            self.current_user = user
            
            if user.role == 'admin':
                self.show_admin_page()
            else:
                self.show_main()
        else:
            QMessageBox.warning(self, "Ошибка входа", "Неверный логин или пароль")

    def handle_register(self):
        builder = UserBuilder()
        user_data = (builder
            .set_first_name(self.first_name_input.text())
            .set_last_name(self.last_name_input.text())
            .set_birth_date(self.birth_date_input.date().toString("yyyy-MM-dd"))
            .set_email(self.email_input.text())
            .set_login(self.login_input_reg.text())
            .set_password(self.password_input_reg.text())
            .set_repeat_password(self.repeat_password_input.text())
            .set_address(self.address_input.text())
            .build())
        
        required_fields = [
            ('first_name', "Имя"),
            ('last_name', "Фамилия"),
            ('email', "Email"),
            ('login', "Логин"),
            ('password', "Пароль"),
            ('repeat_password', "Повторите пароль"),
            ('address', "Адрес доставки")
        ]
        
        empty_fields = []
        for field, field_name in required_fields:
            if not user_data[field].strip():
                empty_fields.append(field_name)
        
        if empty_fields:
            QMessageBox.warning(
                self, 
                "Ошибка регистрации", 
                f"Пожалуйста, заполните следующие поля:\n{', '.join(empty_fields)}"
            )
            return
        
        success, message = self.user_system.register_user(user_data)
        if success:
            QMessageBox.information(self, "Успешно", message)
            self.show_login()
        else:
            QMessageBox.warning(self, "Ошибка регистрации", message)

    def handle_search(self):
        query = self.search_input.text().lower()
        if not query:
            self.search_results_label.hide()
            self.search_results_list.hide()
            self.search_results_list.clear()
            return
            
        restaurants = self.db.load_restaurants()
        results = []
        
        for restaurant in restaurants:
            if query in restaurant['name'].lower():
                results.append({
                    'type': 'restaurant',
                    'id': restaurant['id'],
                    'name': restaurant['name'],
                    'description': restaurant['description'],
                    'rating': restaurant.get('rating', 4.5)
                })
            
            for item in restaurant['menu']:
                if query in item['name'].lower():
                    results.append({
                        'type': 'dish',
                        'restaurant_id': restaurant['id'],
                        'restaurant_name': restaurant['name'],
                        'name': item['name'],
                        'description': item['description'],
                        'price': item['price']
                    })
        
        self.search_subject.update_results(results)

    def update(self, results):
        self.search_results_label.show()
        self.search_results_list.show()
        self.search_results_list.clear()
        
        if not results:
            self.search_results_list.addItem("Ничего не найдено")
            return
            
        for item in results:
            if item['type'] == 'restaurant':
                list_item = QListWidgetItem(
                    f"🍴 Ресторан: {item['name']}\n"
                    f"{item['description']}\n"
                    f"Рейтинг: ★ {item['rating']}"
                )
                list_item.setData(Qt.ItemDataRole.UserRole, {
                    'type': 'restaurant', 
                    'id': item['id']
                })
            else:
                list_item = QListWidgetItem(
                    f"🍲 Блюдо: {item['name']} - {item['price']:.2f} ₽\n"
                    f"Ресторан: {item['restaurant_name']}\n"
                    f"{item['description']}"
                )
                list_item.setData(Qt.ItemDataRole.UserRole, {
                    'type': 'dish', 
                    'restaurant_id': item['restaurant_id']
                })
            
            list_item.setSizeHint(QSize(100, 100))
            self.search_results_list.addItem(list_item)

    def handle_search_result_click(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data['type'] == 'restaurant':
            self.show_restaurant_by_id(data['id'])
        else:
            self.show_restaurant_by_id(data['restaurant_id'])

    def show_restaurant(self, item):
        restaurant_id = item.data(Qt.ItemDataRole.UserRole)['id']
        self.show_restaurant_by_id(restaurant_id)

    def show_restaurant_by_id(self, restaurant_id):
        restaurants = self.db.load_restaurants()
        restaurant_data = next((r for r in restaurants if r['id'] == restaurant_id), None)
        
        if restaurant_data:
            self.current_restaurant = Restaurant(restaurant_data)
            self.restaurant_title.setText(self.current_restaurant.name)
            self.menu_tabs.clear()
            
            categories = {}
            for item in self.current_restaurant.menu:
                if item.category not in categories:
                    categories[item.category] = []
                categories[item.category].append(item)
            
            for category, items in categories.items():
                tab = QWidget()
                layout = QVBoxLayout()
                
                list_widget = QListWidget()
                list_widget.setStyleSheet("font-size: 11pt;")
                
                for item in items:
                    list_item = QListWidgetItem(
                        f"{item.name} - {item.price:.2f} ₽\n"
                        f"{item.description}"
                    )
                    list_item.setData(Qt.ItemDataRole.UserRole, {
                        'id': item.id,
                        'name': item.name,
                        'price': item.price,
                        'restaurant': self.current_restaurant.name
                    })
                    list_item.setSizeHint(QSize(100, 80))
                    list_widget.addItem(list_item)
                
                list_widget.itemDoubleClicked.connect(self.add_to_cart)
                layout.addWidget(list_widget)
                tab.setLayout(layout)
                self.menu_tabs.addTab(tab, category)
            
            self.stacked_widget.setCurrentWidget(self.restaurant_page)

    def add_to_cart(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        self.cart.append(data)
        QMessageBox.information(self, "Добавлено в корзину", f"{data['name']} добавлено в вашу корзину!")
        self.update_cart()

    def update_cart(self):
        self.cart_list.clear()
        total = 0
        
        for item in self.cart:
            list_item = QListWidgetItem(
                f"{item['name']} - {item['price']:.2f} ₽\n"
                f"Ресторан: {item['restaurant']}"
            )
            self.cart_list.addItem(list_item)
            total += item['price']
        
        self.total_label.setText(f"Итого: {total:.2f} ₽")

    def show_order_confirmation(self):
        if not self.cart:
            QMessageBox.warning(self, "Корзина пуста", "Ваша корзина пуста!")
            return
            
        summary = ""
        total = 0
        for item in self.cart:
            summary += f"• {item['name']} - {item['price']:.2f} ₽\n"
            total += item['price']
        
        summary += f"\nИтого: {total:.2f} ₽"
        
        self.order_summary.setText(summary)
        self.delivery_address.setText(self.current_user.address)
        self.stacked_widget.setCurrentWidget(self.order_confirmation_page)

    def confirm_order(self):
        payment_method = self.payment_combo.currentText()
        
        order = {
            'user': self.current_user.login,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'items': self.cart,
            'address': self.current_user.address,
            'payment_method': payment_method,
            'status': 'В обработке'
        }
        
        orders = self.db.load_orders()
        orders.append(order)
        self.db.save_orders(orders)
        
        self.cart = []
        
        QMessageBox.information(self, "Заказ подтвержден", 
                               f"Ваш заказ успешно оформлен!\n"
                               f"Способ оплаты: {payment_method}")
        self.show_main()

    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.login_input.clear()
        self.password_input.clear()

    def show_register(self):
        self.stacked_widget.setCurrentWidget(self.register_page)
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.birth_date_input.setDate(QDate.currentDate().addYears(-18))
        self.email_input.clear()
        self.login_input_reg.clear()
        self.password_input_reg.clear()
        self.repeat_password_input.clear()
        self.address_input.clear()

    def show_main(self):
        if self.current_user:
            self.welcome_label.setText(f"Добро пожаловать, {self.current_user.first_name}!")
            self.load_restaurants()
            self.search_input.clear()
            self.search_results_label.hide()
            self.search_results_list.hide()
            self.stacked_widget.setCurrentWidget(self.main_page)

    def show_cart(self):
        self.update_cart()
        self.stacked_widget.setCurrentWidget(self.cart_page)
        
    def show_admin_page(self):
        self.stacked_widget.setCurrentWidget(self.admin_page)

    def logout(self):
        self.current_user = None
        self.cart = []
        self.show_login()

    def load_restaurants(self):
        self.restaurant_list.clear()
        restaurants = self.db.load_restaurants()
        
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:
            context = SortContext(SortByName())
        else:
            context = SortContext(SortByRating())
        
        sorted_restaurants = context.execute_sort(restaurants)
        
        for restaurant in sorted_restaurants:
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            
            icon_label = QLabel()
            pixmap = QPixmap("restaurant_icon.png").scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio)
            icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(80, 80)
            
            info_layout = QVBoxLayout()
            name_label = QLabel(restaurant['name'])
            name_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
            
            desc_label = QLabel(restaurant['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #555;")
            
            rating_label = QLabel(f"★ {restaurant.get('rating', 4.5)}")
            rating_label.setStyleSheet("color: #FF9800; font-weight: bold;")
            
            info_layout.addWidget(name_label)
            info_layout.addWidget(desc_label)
            info_layout.addWidget(rating_label)
            info_layout.addStretch()
            
            layout.addWidget(icon_label)
            layout.addLayout(info_layout)
            widget.setLayout(layout)
            
            # Create list item
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(100, 120))
            list_item.setData(Qt.ItemDataRole.UserRole, {'type': 'restaurant', 'id': restaurant['id']})
            
            self.restaurant_list.addItem(list_item)
            self.restaurant_list.setItemWidget(list_item, widget)

if __name__ == "__main__":
    if not os.path.exists("restaurant_icon.png"):
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.rectangle([20, 20, 80, 80], fill=(255, 165, 0))
        d.ellipse([30, 30, 70, 70], fill=(255, 255, 255))
        img.save('restaurant_icon.png')
    
    db = Database()
    users = db.load_users()
    if not any(u.get('role') == 'admin' for u in users):
        admin_user = {
            "first_name": "Admin",
            "last_name": "Admin",
            "birth_date": "2000-01-01",
            "email": "admin@example.com",
            "login": "admin",
            "password": "admin123",
            "address": "Admin Office",
            "role": "admin"
        }
        users.append(admin_user)
        db.save_users(users)

    app = QApplication(sys.argv)
    window = FoodDeliveryApp()
    window.show()
    sys.exit(app.exec())
