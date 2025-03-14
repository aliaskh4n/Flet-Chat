# Документация чат-приложения Flet в стиле Telegram


## Обзор проекта

Flet Chat — это современное чат-приложение, разработанное с использованием технологий Flet и Flask. Приложение предоставляет интуитивно понятный интерфейс в стиле Telegram с темной темой и акцентным цветом <span style="color:#64B9FF">**#64B9FF**</span>, позволяя пользователям обмениваться сообщениями в реальном времени.

Основные особенности приложения:

- **Простая регистрация**: Достаточно ввести имя пользователя для входа в чат
- **Мгновенные сообщения**: Отправка и получение сообщений происходит в режиме реального времени
- **Уведомления о присутствии**: Автоматические уведомления о входе и выходе пользователей
- **Список участников**: Отображение всех активных пользователей в чате с выделением текущего пользователя акцентным цветом
- **Автоматическое переподключение**: Повторные попытки подключения при разрыве соединения
- **Валидация данных**: Проверка длины имени пользователя и сообщений

Архитектура приложения построена на основе клиент-серверной модели с использованием Socket.IO для обеспечения двунаправленной# Документация чат-приложения Flet в стиле Telegram

<div align="center">
  <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; margin-bottom: 30px;">
    <div>
      <img src="https://github.com/aliaskh4n/Flet-Chat/blob/main/images/login-screen.png" alt="Экран входа в чат с полем для имени пользователя и кнопкой входа" width="800"/>
      <p>Экран входа в чат</p>
    </div>
    <div>
      <img src="https://github.com/aliaskh4n/Flet-Chat/blob/main/images/chat-screen.png" alt="Интерфейс чата с панелью пользователей и полем ввода сообщений" width="800"/>
      <p>Интерфейс чата</p>
    </div>
  </div>
</div>


## Обзор проекта

Данный проект представляет собой чат-приложение в стиле Telegram, разработанное с использованием следующих технологий:

- **Клиентская часть**: Flet (фреймворк для создания UI на базе Flutter)
- **Серверная часть**: Flask и Flask-SocketIO
- **Коммуникация**: Socket.IO для двусторонней связи в реальном времени

Приложение имеет следующие ключевые особенности:
- Простой вход по имени пользователя
- Мгновенный обмен сообщениями
- Уведомления о присоединении и выходе пользователей
- Список активных участников чата
- UI в стиле Telegram с темной темой
- Обработка отключения и автоматические попытки переподключения

## Структура проекта

Проект состоит из двух основных файлов:

1. `server.py` - Серверная часть, реализованная на Flask с Flask-SocketIO
2. `client.py` - Клиентская часть, реализованная с использованием Flet

## Серверная часть (server.py)

### Основные компоненты

Класс `ChatServer` управляет всей логикой сервера:

- **Инициализация**: Настройка Flask, SocketIO, логирования
- **Обработчики событий**: Подключение, отключение, вход в чат, отправка сообщений
- **Управление пользователями**: Отслеживание активных пользователей
- **Валидация**: Проверка длины имени пользователя и сообщений

### Основные методы

| Метод | Описание |
|-------|----------|
| `_handle_connect` | Обработка нового подключения клиента |
| `_handle_join` | Обработка входа пользователя в чат |
| `_handle_message` | Обработка и рассылка сообщений |
| `_handle_disconnect` | Обработка отключения пользователя |
| `_update_user_list` | Обновление списка пользователей для всех клиентов |
| `_validate_username` | Проверка корректности имени пользователя |
| `_validate_message` | Проверка корректности сообщения |

### Константы

```python
MAX_MESSAGE_LENGTH = 1000   # Максимальная длина сообщения
MAX_USERNAME_LENGTH = 50    # Максимальная длина имени пользователя
```

## Клиентская часть (client.py)

### Основные компоненты

Класс `FletChatApp` управляет клиентской частью приложения:

- **Инициализация**: Настройка SocketIO клиента, логирования
- **UI**: Создание и управление интерфейсом пользователя
- **Обработчики событий**: Получение сообщений, обновление списка пользователей
- **Управление соединением**: Обработка подключения, отключения, переподключения

### Основные методы

| Метод | Описание |
|-------|----------|
| `_register_socket_handlers` | Регистрация обработчиков событий Socket.IO |
| `_handle_message` | Обработка входящих сообщений |
| `_handle_user_list` | Обновление списка пользователей |
| `_handle_disconnect` | Реакция на разрыв соединения |
| `_connect_to_server` | Подключение к серверу |
| `_retry_connection` | Попытки восстановления соединения |
| `_join_chat` | Вход в чат |
| `_send_message` | Отправка сообщения |
| `_build_ui` | Создание элементов пользовательского интерфейса |

### Константы

```python
COLORS = {
    "bg": "#17212B",               # Основной фон
    "input_bg": "#242F3D",         # Фон для полей ввода
    "hint": "#7D8E9A",             # Цвет подсказок
    "user_msg": "#2B5278",         # Фон сообщений пользователя
    "other_msg": "#182533",        # Фон сообщений других пользователей
    "accent": "#64B9FF",           # Акцентный цвет (основной цвет темы)
    "error": "#E74C3C",            # Цвет ошибок
    "system": "#7D8E9A",           # Цвет системных сообщений
    "timestamp_other": "#7D8E9A",  # Цвет времени в чужих сообщениях
    "timestamp_user": "#A1C886",   # Цвет времени в собственных сообщениях
    "text": "#FFFFFF"              # Цвет текста
}
```

> **Примечание:** Основной акцентный цвет приложения `#64B9FF` используется для выделения интерактивных элементов, аватаров, кнопок и имён пользователей.

SERVER_URL = "http://localhost:4000"  # URL сервера
MAX_RECONNECT_ATTEMPTS = 3            # Максимальное количество попыток переподключения
RECONNECT_DELAY = 2                   # Задержка между попытками переподключения (сек)
```

## Внешний вид и компоненты UI

### Цветовая схема

Приложение использует темную цветовую схему в стиле Telegram с акцентным цветом <span style="color:#64B9FF">**#64B9FF**</span>. Этот яркий голубой цвет используется для:

- Кнопки отправки сообщений
- Выделения имен пользователей в сообщениях
- Обозначения текущего пользователя в списке
- Аватаров и интерактивных элементов
- Подсказок и выделений в интерфейсе

### Экран входа

Экран входа (`join_view`) содержит:
- Логотип (иконка чата в акцентном цвете <span style="color:#64B9FF">#64B9FF</span>)
- Название приложения "Flet Chat"
- Поле для ввода имени пользователя с обводкой акцентного цвета
- Кнопка "Войти в чат" в акцентном цвете <span style="color:#64B9FF">#64B9FF</span>
- Отображение ошибок валидации

### Экран чата

Экран чата (`chat_view`) содержит:
- Верхний бар с названием приложения
- Боковая панель со списком активных пользователей (текущий пользователь выделен цветом <span style="color:#64B9FF">#64B9FF</span>)
- Основная область с сообщениями
- Панель ввода сообщения и кнопка отправки в акцентном цвете

### Типы сообщений

В приложении реализованы следующие типы сообщений:
1. **Обычные сообщения** - отображаются в "пузырях" с указанием имени отправителя и времени
2. **Сообщения пользователя** - отображаются справа с другим цветом фона
3. **Системные сообщения** - информация о подключении/отключении пользователей
4. **Сообщения об ошибках** - уведомления о проблемах соединения или ошибках

## Коммуникация между клиентом и сервером

### События Socket.IO

| Событие | Отправитель | Получатель | Данные | Описание |
|---------|-------------|------------|--------|----------|
| `connect` | Клиент | Сервер | - | Установка соединения |
| `join` | Клиент | Сервер | `{"username": "..."}` | Вход в чат |
| `send_message` | Клиент | Сервер | `{"text": "..."}` | Отправка сообщения |
| `disconnect` | Клиент | Сервер | - | Разрыв соединения |
| `message` | Сервер | Клиент(ы) | `{"type": "...", ...}` | Различные типы сообщений |
| `user_list` | Сервер | Клиент(ы) | `{"users": ["...", ...]}` | Список активных пользователей |

### Типы сообщений от сервера

| Тип | Поля | Описание |
|-----|------|----------|
| `message` | `username`, `text` | Обычное сообщение от пользователя |
| `join` | `username` | Пользователь присоединился к чату |
| `leave` | `username` | Пользователь покинул чат |
| `error` | `text` | Сообщение об ошибке |

## Обработка ошибок и восстановление соединения

### Клиентская сторона

- **Обработка отключения**: Отображение системного сообщения с ошибкой
- **Автоматическое переподключение**: До 3-х попыток с интервалом в 2 секунды
- **Валидация ввода**: Проверка имени пользователя и длины сообщения
- **Обработка ошибок сервера**: Отображение сообщений об ошибках

### Серверная сторона

- **Валидация входных данных**: Проверка корректности формата и содержимого
- **Обработка потери соединения**: Корректное удаление пользователя из списка
- **Логирование**: Запись информации о подключениях и ошибках

## Запуск приложения

### Запуск сервера

```bash
python server.py
```

Сервер будет запущен на 0.0.0.0:4000.

### Запуск клиента

```bash
python client.py
```

## Возможные улучшения

1. **Аутентификация**: Добавление полноценной регистрации и входа пользователей
2. **История сообщений**: Сохранение и загрузка истории чата
3. **Приватные сообщения**: Возможность отправки личных сообщений
4. **Файловый обмен**: Добавление возможности передачи файлов
5. **Шифрование**: Реализация end-to-end шифрования сообщений
6. **Статус прочтения**: Индикаторы доставки и прочтения сообщений
7. **Расширенное форматирование текста**: Поддержка markdown или других способов форматирования
8. **Поддержка эмодзи**: Добавление выбора и отображения эмодзи
9. **Уведомления**: Системные уведомления о новых сообщениях

## Диаграмма взаимодействия компонентов

```
+-------------+                   +-------------+
|             |  1. Соединение    |             |
|             |------------------>|             |
|             |                   |             |
|             |  2. Событие join  |             |
|   Клиент    |------------------>|   Сервер    |
|   (Flet)    |                   |   (Flask)   |
|             |  3. Сообщения     |             |
|             |<----------------->|             |
|             |                   |             |
|             |  4. Список        |             |
|             |      пользователей|             |
|             |<------------------|             |
+-------------+                   +-------------+
```

## Заключение

Данное приложение представляет собой хорошую основу для чата в реальном времени с чистым и современным интерфейсом. Комбинация Flet для UI и Flask-SocketIO для коммуникации обеспечивает эффективное решение для создания кроссплатформенных чат-приложений с минимальными зависимостями.
