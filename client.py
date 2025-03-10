import flet as ft
import socketio
import time
import datetime
import logging
import sys
import traceback


class TelegramChatApp:
    """Класс приложения чата в стиле Telegram"""
    
    # Константы для UI
    COLORS = {
        "bg": "#17212B",
        "input_bg": "#242F3D",
        "hint": "#7D8E9A",
        "user_msg": "#2B5278",
        "other_msg": "#182533",
        "accent": "#64B9FF",
        "error": "#E74C3C",
        "system": "#7D8E9A",
        "timestamp_other": "#7D8E9A",
        "timestamp_user": "#A1C886",
        "text": "#FFFFFF"
    }
    
    # Настройки подключения
    SERVER_URL = "http://localhost:4000"
    MAX_RECONNECT_ATTEMPTS = 3
    RECONNECT_DELAY = 2  # секунды
    
    def __init__(self):
        """Инициализация приложения чата"""
        # Настройка логирования
        self._setup_logging()
        
        # Инициализация SocketIO клиента
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        
        # Состояние приложения
        self.username = None
        self.page = None
        
        # Основные UI элементы, которые будут созданы позже
        self.message_list = None
        self.message_input = None
        self.users_list = None
        self.loading_indicator = None
        self.username_input = None
        self.username_error = None
        self.join_view = None
        self.chat_view = None
        
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger("TelegramChat")

    def _register_socket_handlers(self):
        """Регистрация обработчиков событий Socket.IO"""
        @self.sio.on("message")
        def on_message(data):
            self._handle_message(data)

        @self.sio.on("user_list")
        def on_user_list(data):
            self._handle_user_list(data)

        @self.sio.on("disconnect")
        def on_disconnect():
            self._handle_disconnect()
    
    def _handle_message(self, data):
        """Обработка полученных сообщений"""
        try:
            if data["type"] == "message":
                timestamp = datetime.datetime.now().strftime("%H:%M")
                is_current_user = data["username"] == self.username
                self.message_list.controls.append(
                    self._create_message_bubble(data["username"], data["text"], is_current_user, timestamp)
                )
            elif data["type"] == "join":
                self.message_list.controls.append(
                    self._create_system_message(f"{data['username']} присоединился к чату")
                )
            elif data["type"] == "leave":
                self.message_list.controls.append(
                    self._create_system_message(f"{data['username']} покинул чат")
                )
            elif data["type"] == "error":
                self.message_list.controls.append(
                    self._create_system_message(data["text"], is_error=True)
                )
            self.page.update()
        except Exception as e:
            self.logger.error(f"Ошибка обработки сообщения: {e}")
    
    def _handle_user_list(self, data):
        """Обработка обновления списка пользователей"""
        try:
            self._update_users_list(data["users"])
        except Exception as e:
            self.logger.error(f"Ошибка обновления списка пользователей: {e}")
    
    def _handle_disconnect(self):
        """Обработка разрыва соединения с сервером"""
        try:
            self.message_list.controls.append(
                self._create_system_message("Соединение с сервером разорвано", is_error=True)
            )
            self.page.update()
            self._retry_connection()
        except Exception as e:
            self.logger.error(f"Ошибка при обработке отключения: {e}")
    
    def _create_message_bubble(self, username, text, is_current_user, timestamp):
        """Создание пузыря сообщения"""
        if is_current_user:
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(text, color=self.COLORS["text"], selectable=True),
                            ft.Container(height=4),
                            ft.Text(timestamp, color=self.COLORS["timestamp_user"], size=12, text_align=ft.TextAlign.RIGHT)
                        ]),
                        bgcolor=self.COLORS["user_msg"],
                        padding=12,
                        border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_left=12, bottom_right=3),
                        width=300
                    )
                ]),
                margin=ft.margin.only(left=50, right=10, top=5, bottom=5),
                alignment=ft.alignment.center_right
            )
        else:
            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text(username, style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=self.COLORS["accent"])),
                            ft.Container(height=4),
                            ft.Text(text, color=self.COLORS["text"], selectable=True),
                            ft.Container(height=4),
                            ft.Text(timestamp, color=self.COLORS["timestamp_other"], size=12, text_align=ft.TextAlign.RIGHT)
                        ]),
                        bgcolor=self.COLORS["other_msg"],
                        padding=12,
                        border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_left=3, bottom_right=12),
                        width=300
                    )
                ]),
                margin=ft.margin.only(left=10, right=50, top=5, bottom=5),
                alignment=ft.alignment.center_left
            )
    
    def _create_system_message(self, text, is_error=False):
        """Создание системного сообщения"""
        return ft.Container(
            content=ft.Text(
                text, 
                italic=True, 
                color=self.COLORS["error"] if is_error else self.COLORS["system"], 
                text_align=ft.TextAlign.CENTER
            ),
            margin=ft.margin.symmetric(vertical=5),
            alignment=ft.alignment.center
        )
    
    def _update_users_list(self, users_data):
        """Обновление списка пользователей"""
        self.users_list.controls.clear()
        for user in users_data:
            container = ft.Container(
                content=ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(user[0].upper(), weight=ft.FontWeight.BOLD),
                            bgcolor=self.COLORS["accent"],
                            color=self.COLORS["text"],
                            radius=16
                        ),
                        ft.Container(width=10),
                        ft.Text(user, color=self.COLORS["text"])
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=5,
                border_radius=5,
                bgcolor=self.COLORS["accent"] if user == self.username else self.COLORS["input_bg"]
            )
            self.users_list.controls.append(container)
        self.page.update()
    
    def _connect_to_server(self):
        """Подключение к серверу"""
        self.page.overlay.append(self.loading_indicator)
        self.page.update()
        try:
            self.sio.connect(self.SERVER_URL)
        except Exception as e:
            self.message_list.controls.append(
                self._create_system_message(f"Ошибка подключения: {e}", is_error=True)
            )
            self.page.update()
            self._retry_connection()
        finally:
            self.page.overlay.remove(self.loading_indicator)
            self.page.update()
    
    def _retry_connection(self):
        """Повторные попытки подключения к серверу"""
        self.message_list.controls.append(
            self._create_system_message("Попытка переподключения...")
        )
        self.page.update()
        
        for attempt in range(self.MAX_RECONNECT_ATTEMPTS):
            try:
                if not self.sio.connected:
                    self.sio.connect(self.SERVER_URL)
                    self.message_list.controls.append(
                        self._create_system_message("Подключение восстановлено!")
                    )
                    if self.username:
                        self.sio.emit("join", {"username": self.username})
                    self.page.update()
                    return
            except Exception:
                pass
            time.sleep(self.RECONNECT_DELAY)
        
        self.message_list.controls.append(
            self._create_system_message("Не удалось подключиться к серверу", is_error=True)
        )
        self.page.update()
    
    def _join_chat(self, e=None):
        """Функция входа в чат"""
        username = self.username_input.value.strip()
        
        if not username:
            self.username_error.value = "Имя не может быть пустым"
            self.username_error.visible = True
            self.page.update()
            return
            
        if len(username) > 50:
            self.username_error.value = "Имя не должно превышать 50 символов"
            self.username_error.visible = True
            self.page.update()
            return
        
        self.username = username
        self.username_error.visible = False
        
        if not self.sio.connected:
            self._retry_connection()
            if not self.sio.connected:
                self.message_list.controls.append(
                    self._create_system_message("Невозможно подключиться к серверу", is_error=True)
                )
                self.page.update()
                return
                
        self.sio.emit("join", {"username": username})
        self.page.views.clear()
        self.page.views.append(self.chat_view)
        self.page.update()
        self.page.go("/chat")
    
    def _send_message(self, e=None):
        """Отправка сообщения"""
        text = self.message_input.value.strip()
        if not text:
            return
            
        if not self.sio.connected:
            self.message_list.controls.append(
                self._create_system_message("Нет подключения к серверу", is_error=True)
            )
            self.page.update()
            self._retry_connection()
            return
            
        try:
            self.sio.emit("send_message", {"text": text})
            self.message_input.value = ""
            self.page.update()
        except Exception as e:
            self.message_list.controls.append(
                self._create_system_message(f"Ошибка отправки: {e}", is_error=True)
            )
            self.page.update()
    
    def _route_change(self, e):
        """Обработчик изменения маршрута"""
        if self.page.route == "/join" or self.page.route == "/":
            self.page.views.clear()
            self.page.views.append(self.join_view)
        elif self.page.route == "/chat":
            if self.username:
                self.page.views.clear()
                self.page.views.append(self.chat_view)
            else:
                self.page.go("/join")
        self.page.update()
    
    def _build_ui(self):
        """Создание пользовательского интерфейса"""
        # Инициализация основных UI-компонентов
        self.message_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        self.users_list = ft.ListView(width=200, spacing=5)
        self.loading_indicator = ft.ProgressRing(width=16, height=16, color=self.COLORS["accent"])

        # Поле ввода сообщения
        self.message_input = ft.TextField(
            hint_text="Введите сообщение...", 
            expand=True,
            border_radius=20,
            filled=True,
            bgcolor=self.COLORS["input_bg"],
            text_style=ft.TextStyle(color=self.COLORS["text"]),
            hint_style=ft.TextStyle(color=self.COLORS["hint"])
        )
        self.message_input.on_submit = self._send_message
        
        # Создание кнопки отправки
        send_button = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=self.COLORS["text"],
            bgcolor=self.COLORS["accent"]
        )
        send_button.on_click = self._send_message
        
        # Создание UI входа
        logo = ft.Container(
            content=ft.Icon(ft.Icons.CHAT, size=80, color=self.COLORS["accent"]),
            padding=8,
            border_radius=40,
            bgcolor=self.COLORS["input_bg"]
        )

        self.username_input = ft.TextField(
            label="Введите имя",
            width=300,
            border_color=self.COLORS["accent"],
            border_radius=10,
            prefix_icon=ft.Icons.PERSON,
            text_style=ft.TextStyle(color=self.COLORS["text"]),
            focused_border_color=self.COLORS["accent"]
        )
        self.username_input.on_submit = self._join_chat
        
        self.username_error = ft.Text(color=self.COLORS["error"], visible=False)
        
        login_button = ft.ElevatedButton(
            "Войти в чат",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=self.COLORS["accent"],
                color=self.COLORS["text"]
            ),
            width=300,
            height=40
        )
        login_button.on_click = self._join_chat
        
        # Создание экрана входа
        self.join_view = ft.View(
            "/join",
            [
                ft.Container(
                    content=ft.Column(
                        [
                            logo,
                            ft.Container(height=20),
                            ft.Text("Flet Chat", size=28, weight=ft.FontWeight.BOLD, color=self.COLORS["text"]),
                            ft.Text("Вход в чат", size=16, color=self.COLORS["hint"]),
                            ft.Container(height=30),
                            self.username_input,
                            self.username_error,
                            ft.Container(height=20),
                            ft.Container(content=login_button, padding=10)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=30,
                    border_radius=20,
                    bgcolor=self.COLORS["input_bg"],
                    width=400,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.2, "#000000"),
                        offset=ft.Offset(2, 2),
                    )
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            bgcolor=self.COLORS["bg"]
        )
        
        # Создание экрана чата
        self.chat_view = ft.View(
            "/chat",
            [
                # Верхний бар
                ft.Container(
                    content=ft.Row(
                        [ft.Text("Flet Chat", weight=ft.FontWeight.BOLD, color=self.COLORS["text"], size=18), ft.Container(expand=True)],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
                    bgcolor=self.COLORS["bg"],
                    border=ft.border.only(bottom=ft.BorderSide(1, self.COLORS["input_bg"]))
                ),
                # Основной контент
                ft.Row(
                    [
                        # Боковая панель с пользователями
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Text("Участники чата", color=self.COLORS["text"], size=14, weight=ft.FontWeight.BOLD),
                                        padding=10,
                                        border=ft.border.only(bottom=ft.BorderSide(1, self.COLORS["input_bg"]))
                                    ),
                                    ft.Container(content=self.users_list, expand=True)
                                ],
                                spacing=0,
                                tight=True
                            ),
                            width=200,
                            bgcolor=self.COLORS["bg"],
                            border=ft.border.only(right=ft.BorderSide(1, self.COLORS["input_bg"]))
                        ),
                        # Чат
                        ft.Container(
                            content=ft.Column(
                                [
                                    # Список сообщений
                                    ft.Container(content=self.message_list, expand=True, bgcolor=self.COLORS["bg"]),
                                    # Панель ввода сообщений
                                    ft.Container(
                                        content=ft.Row(
                                            [self.message_input, send_button],
                                            spacing=10,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                                        ),
                                        padding=10,
                                        bgcolor=self.COLORS["bg"],
                                        border=ft.border.only(top=ft.BorderSide(1, self.COLORS["input_bg"]))
                                    )
                                ],
                                spacing=0,
                                tight=True
                            ),
                            expand=True
                        )
                    ],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            ],
            bgcolor=self.COLORS["bg"]
        )
    
    def main(self, page: ft.Page):
        """Основная функция приложения"""
        self.page = page
        
        # Базовые настройки страницы
        page.theme_mode = ft.ThemeMode.DARK
        page.title = "Telegram-подобный чат"
        page.bgcolor = self.COLORS["bg"]
        page.window_width, page.window_height = 800, 600
        page.window_min_width, page.window_min_height = 500, 500
        page.route = "/"
        
        # Создание UI
        self._build_ui()
        
        # Регистрация обработчиков событий
        self._register_socket_handlers()
        page.on_route_change = self._route_change
        
        # Инициализация
        page.go("/join")
        self._connect_to_server()
        
    def run(self):
        """Запуск приложения"""
        ft.app(target=self.main)


if __name__ == "__main__":
    app = TelegramChatApp()
    app.run()