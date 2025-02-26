#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот "Блинная башня" с интеграцией веб-приложения
"""

import os
import logging
import json
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from pyngrok import ngrok, conf

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Глобальные переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = None  # Будет заполнено после запуска сервера
LOCAL_URL = None   # Локальный URL для тестирования
HTTPS_URL_AVAILABLE = False  # Флаг доступности HTTPS URL

# Список портов для проверки (расширенный)
WEB_SERVER_PORTS = [8080, 8000, 8888, 9000, 9090, 9001, 9002, 8090, 8001, 8002, 7000, 7001]

# Хранилище результатов игры
game_results = {}

# Обработчик для веб-сервера
class WebAppHandler(SimpleHTTPRequestHandler):
    """Обработчик HTTP-запросов для веб-приложения"""
    
    def __init__(self, *args, **kwargs):
        # Устанавливаем директорию с веб-приложением
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp")
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        # Отключаем логирование HTTP-запросов
        pass

def find_available_port():
    """Находит доступный порт для веб-сервера"""
    for port in WEB_SERVER_PORTS:
        try:
            # Проверяем, свободен ли порт
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                logger.info(f"Найден доступный порт: {port}")
                return port
        except OSError:
            logger.warning(f"Порт {port} уже используется, пробуем следующий...")
    
    # Если все порты заняты, возвращаем None
    logger.error("Не удалось найти свободный порт")
    return None

def start_web_server():
    """Запускает веб-сервер для приложения"""
    global LOCAL_URL
    
    # Находим доступный порт
    port = find_available_port()
    if port is None:
        return None
    
    try:
        # Запускаем веб-сервер в отдельном потоке
        handler = WebAppHandler
        httpd = HTTPServer(("", port), handler)
        
        # Сохраняем локальный URL
        LOCAL_URL = f"http://localhost:{port}"
        
        logger.info(f"Запуск веб-сервера на порту {port}")
        
        # Запускаем сервер в отдельном потоке
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return port
    except Exception as e:
        logger.error(f"Ошибка при запуске веб-сервера: {e}")
        return None

def start_ngrok():
    """Запускает ngrok туннель для веб-сервера"""
    global WEBAPP_URL, HTTPS_URL_AVAILABLE, LOCAL_URL
    
    # Проверяем, установлен ли локальный URL
    if LOCAL_URL is None:
        logger.error("Локальный URL не установлен, невозможно запустить ngrok")
        return None
    
    # Получаем порт из локального URL
    try:
        port = int(LOCAL_URL.split(":")[-1])
    except (ValueError, IndexError):
        logger.error(f"Не удалось извлечь порт из локального URL: {LOCAL_URL}")
        return None
    
    try:
        # Получаем токен ngrok из переменных окружения
        ngrok_token = os.getenv("NGROK_TOKEN")
        if ngrok_token:
            # Устанавливаем токен для ngrok
            conf.get_default().auth_token = ngrok_token
            logger.info("Используется токен ngrok из переменных окружения")
        else:
            logger.warning("Токен ngrok не найден в переменных окружения. Попытка запуска без токена...")
        
        # Запускаем ngrok туннель
        public_url = ngrok.connect(port).public_url
        WEBAPP_URL = public_url
        HTTPS_URL_AVAILABLE = True
        logger.info(f"Ngrok туннель запущен: {WEBAPP_URL}")
        return WEBAPP_URL
    except Exception as e:
        logger.error(f"Ошибка при запуске ngrok туннеля: {e}")
        
        # Если не удалось запустить ngrok, устанавливаем флаг недоступности HTTPS
        HTTPS_URL_AVAILABLE = False
        WEBAPP_URL = LOCAL_URL
        logger.info(f"Веб-приложение доступно только локально: {LOCAL_URL}")
        return None

def start(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /start"""
    user = update.effective_user
    
    # Создаем кнопку для запуска веб-приложения
    if HTTPS_URL_AVAILABLE and WEBAPP_URL:
        # Если доступен HTTPS URL, используем его для веб-приложения
        keyboard = [
            [InlineKeyboardButton(
                "Играть в Блинную башню", 
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ]
        
        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в игру 'Блинная башня'!\n\n"
            f"Нажми на кнопку ниже, чтобы начать игру."
        )
    else:
        # Если HTTPS URL недоступен, показываем сообщение с локальным URL
        keyboard = [
            [InlineKeyboardButton("О игре", callback_data="about_game")]
        ]
        
        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            f"Добро пожаловать в игру 'Блинная башня'!\n\n"
            f"⚠️ Веб-приложение доступно только локально.\n"
            f"Вы можете открыть его в браузере по адресу:\n"
            f"{LOCAL_URL}\n\n"
            f"Для работы через Telegram требуется HTTPS URL."
        )
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем приветственное сообщение
    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

def about_game(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатие на кнопку 'О игре'"""
    query = update.callback_query
    query.answer()
    
    query.edit_message_text(
        "🎮 Блинная башня - это игра, где нужно построить как можно более высокую башню из блинов.\n\n"
        "Правила игры:\n"
        "1. Блин движется из стороны в сторону\n"
        "2. Нажмите кнопку 'Играть', чтобы опустить блин\n"
        "3. Старайтесь сложить блины ровно друг на друга\n"
        "4. Если блин упадет с башни, игра окончена\n\n"
        "Чтобы начать игру, откройте веб-приложение в браузере по адресу:\n"
        f"{LOCAL_URL}"
    )

def handle_message(update: Update, context: CallbackContext) -> None:
    """Обрабатывает сообщения от пользователя"""
    # Проверяем, содержит ли сообщение данные от веб-приложения
    if hasattr(update.effective_message, 'web_app_data') and update.effective_message.web_app_data:
        # Получаем данные от веб-приложения
        try:
            data = json.loads(update.effective_message.web_app_data.data)
            
            # Сохраняем результат игры
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            
            game_results[user_id] = {
                "username": username,
                "score": data.get("score", 0)
            }
            
            # Отправляем сообщение с результатом
            update.message.reply_text(
                f"🎮 Игра завершена!\n\n"
                f"Твой результат: {data.get('score', 0)} блинов\n\n"
                f"Хочешь сыграть еще раз? Используй команду /start"
            )
        except json.JSONDecodeError:
            update.message.reply_text(
                "Произошла ошибка при обработке данных игры. Пожалуйста, попробуйте еще раз."
            )
    else:
        # Если это обычное сообщение, отправляем подсказку
        update.message.reply_text(
            "Используй команду /start, чтобы начать игру, или /help для получения справки."
        )

def leaderboard(update: Update, context: CallbackContext) -> None:
    """Показывает таблицу лидеров"""
    # Сортируем результаты по убыванию счета
    sorted_results = sorted(
        game_results.values(),
        key=lambda x: x["score"],
        reverse=True
    )
    
    # Формируем сообщение с таблицей лидеров
    if sorted_results:
        message = "🏆 Таблица лидеров 🏆\n\n"
        
        for i, result in enumerate(sorted_results[:10], 1):
            message += f"{i}. {result['username']}: {result['score']} блинов\n"
    else:
        message = "Таблица лидеров пуста. Будь первым, кто сыграет в игру!"
    
    # Отправляем сообщение
    update.message.reply_text(message)

def help_command(update: Update, context: CallbackContext) -> None:
    """Показывает справку по командам бота"""
    update.message.reply_text(
        "🔍 Справка по командам:\n\n"
        "/start - Начать игру\n"
        "/leaderboard - Показать таблицу лидеров\n"
        "/help - Показать эту справку\n\n"
        "Игра 'Блинная башня' - это игра, где нужно построить как можно более высокую башню из блинов."
    )

def main():
    """Основная функция для запуска бота"""
    global WEBAPP_URL, HTTPS_URL_AVAILABLE, LOCAL_URL
    
    # Проверяем наличие токена бота
    if not BOT_TOKEN:
        logger.error("Токен бота не найден в переменных окружения!")
        return
    
    # Запускаем веб-сервер
    port = start_web_server()
    if port is None:
        logger.error("Не удалось запустить веб-сервер!")
        return
    
    # Устанавливаем локальный URL
    LOCAL_URL = f"http://localhost:{port}"
    
    # Пробуем запустить ngrok
    try:
        ngrok_url = start_ngrok()
        if ngrok_url:
            WEBAPP_URL = ngrok_url
            HTTPS_URL_AVAILABLE = True
        else:
            WEBAPP_URL = LOCAL_URL
            HTTPS_URL_AVAILABLE = False
    except Exception as e:
        logger.error(f"Ошибка при запуске ngrok: {e}")
        WEBAPP_URL = LOCAL_URL
        HTTPS_URL_AVAILABLE = False
    
    # Выводим информацию о запуске
    print("=" * 50)
    print("Запуск Telegram бота 'Блинная башня' с веб-приложением")
    print("=" * 50)
    
    if HTTPS_URL_AVAILABLE:
        print(f"\nВеб-приложение доступно по адресу: {WEBAPP_URL}")
        print(f"Локальный доступ: {LOCAL_URL}")
    else:
        print(f"\nВеб-приложение доступно только локально: {LOCAL_URL}")
        print("\nВНИМАНИЕ: Для работы в Telegram нужен HTTPS URL.")
        print("Для использования ngrok добавьте в файл .env строку:")
        print("NGROK_TOKEN=ваш_токен_ngrok")
        print("\nПолучить токен можно на сайте: https://dashboard.ngrok.com/get-started/your-authtoken")
    
    print("\nБот запущен! Нажмите Ctrl+C для остановки.")
    
    # Создаем Updater и передаем ему токен бота
    try:
        updater = Updater(BOT_TOKEN)
        
        # Получаем диспетчер для регистрации обработчиков
        dispatcher = updater.dispatcher
        
        # Добавляем обработчики команд
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("leaderboard", leaderboard))
        dispatcher.add_handler(CommandHandler("help", help_command))
        
        # Добавляем обработчик сообщений
        dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
        
        # Добавляем обработчик кнопок
        dispatcher.add_handler(CallbackQueryHandler(about_game, pattern="about_game"))
        
        # Запускаем бота
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        print(f"Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    main() 