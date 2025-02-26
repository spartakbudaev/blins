#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот "Блинная башня" для работы с веб-приложением на Heroku
"""

import os
import logging
import json
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters

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
HEROKU_APP_URL = os.getenv("HEROKU_APP_URL")  # URL вашего приложения на Heroku

# Хранилище результатов игры
game_results = {}

def start(update: Update, context: CallbackContext) -> None:
    """Обрабатывает команду /start"""
    user = update.effective_user
    
    # Создаем кнопку для запуска веб-приложения
    keyboard = [
        [InlineKeyboardButton(
            "Играть в Блинную башню", 
            web_app=WebAppInfo(url=HEROKU_APP_URL)
        )]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем приветственное сообщение
    update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в игру 'Блинная башня'!\n\n"
        f"Нажми на кнопку ниже, чтобы начать игру.",
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
        f"Чтобы начать игру, нажмите на кнопку 'Играть в Блинную башню' в меню."
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
    # Проверяем наличие токена бота и URL приложения
    if not BOT_TOKEN:
        logger.error("Токен бота не найден в переменных окружения!")
        return
    
    if not HEROKU_APP_URL:
        logger.error("URL приложения Heroku не найден в переменных окружения!")
        return
    
    # Выводим информацию о запуске
    print("=" * 50)
    print("Запуск Telegram бота 'Блинная башня' с веб-приложением на Heroku")
    print("=" * 50)
    print(f"\nВеб-приложение доступно по адресу: {HEROKU_APP_URL}")
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