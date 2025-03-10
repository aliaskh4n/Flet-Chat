from flask import Flask, request
from flask_socketio import SocketIO, emit
import logging
import sys

class ChatServer:
    """Класс управления серверной частью чата"""
    
    # Константы для валидации
    MAX_MESSAGE_LENGTH = 1000
    MAX_USERNAME_LENGTH = 50
    
    def __init__(self, host="0.0.0.0", port=4000, debug=False):
        """Инициализация сервера чата"""
        # Настройка логирования
        self._setup_logging()
        
        # Создание и настройка Flask и SocketIO
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.host = host
        self.port = port
        self.debug = debug
        
        # Список для хранения подключенных пользователей
        self.users = {}
        
        # Регистрация обработчиков событий SocketIO
        self._register_handlers()
        
    def _setup_logging(self):
        """Настройка логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger("ChatServer")
        
    def _register_handlers(self):
        """Регистрация обработчиков событий SocketIO"""
        @self.socketio.on("connect")
        def handle_connect():
            self._handle_connect()
            
        @self.socketio.on("join")
        def handle_join(data):
            self._handle_join(data)
            
        @self.socketio.on("send_message")
        def handle_message(data):
            self._handle_message(data)
            
        @self.socketio.on("disconnect")
        def handle_disconnect():
            self._handle_disconnect()
    
    def _handle_connect(self):
        """Обработка подключения клиента"""
        client_id = request.sid
        self.logger.info(f"Клиент подключился: {client_id}")
    
    def _handle_join(self, data):
        """Обработка присоединения пользователя к чату"""
        try:
            if not isinstance(data, dict) or "username" not in data:
                return
            
            username = data["username"].strip()
            
            # Валидация имени пользователя
            if not self._validate_username(username):
                return
                
            # Проверка уникальности имени
            if username in self.users.values():
                # Отправляем только этому клиенту сообщение об ошибке
                emit("message", {"type": "error", "text": "Это имя уже используется. Пожалуйста, выберите другое."})
                return
                
            # Связываем сессию с именем пользователя
            self.users[request.sid] = username
            
            # Отправляем сообщение всем о новом пользователе
            emit("message", {"type": "join", "username": username}, broadcast=True)
            
            # Отправляем новому пользователю список активных пользователей
            self._update_user_list()
            
        except Exception as e:
            self.logger.error(f"Ошибка при подключении пользователя: {e}")
    
    def _validate_username(self, username):
        """Проверка валидности имени пользователя"""
        if not username or len(username) > self.MAX_USERNAME_LENGTH:
            emit("message", {"type": "error", "text": f"Имя пользователя должно быть не пустым и не длиннее {self.MAX_USERNAME_LENGTH} символов"})
            return False
        return True
    
    def _handle_message(self, data):
        """Обработка сообщений пользователя"""
        try:
            if not isinstance(data, dict) or "text" not in data:
                return
                
            username = self.users.get(request.sid)
            if not username:
                return
                
            # Валидация текста сообщения
            message_text = data["text"].strip()
            if not self._validate_message(message_text):
                return
                
            # Отправляем сообщение всем клиентам
            emit("message", {
                "type": "message", 
                "username": username, 
                "text": message_text
            }, broadcast=True)
            
        except Exception as e:
            self.logger.error(f"Ошибка при отправке сообщения: {e}")
    
    def _validate_message(self, message_text):
        """Проверка валидности сообщения"""
        if not message_text or len(message_text) > self.MAX_MESSAGE_LENGTH:
            emit("message", {"type": "error", "text": f"Сообщение должно быть не пустым и не длиннее {self.MAX_MESSAGE_LENGTH} символов"})
            return False
        return True
    
    def _handle_disconnect(self):
        """Обработка отключения пользователя"""
        try:
            username = self.users.pop(request.sid, None)
            if username:
                # Уведомляем всех об уходе пользователя
                emit("message", {"type": "leave", "username": username}, broadcast=True)
                self.logger.info(f"Пользователь отключился: {username}")
                # Обновляем список пользователей у всех клиентов
                self._update_user_list()
        except Exception as e:
            self.logger.error(f"Ошибка при отключении пользователя: {e}")
    
    def _update_user_list(self):
        """Обновление списка пользователей"""
        active_users = list(self.users.values())
        emit("user_list", {"users": active_users}, broadcast=True)
    
    def run(self):
        """Запуск сервера"""
        self.logger.info(f"Запуск сервера на порту {self.port}...")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug)


if __name__ == "__main__":
    server = ChatServer(port=4000)
    server.run()