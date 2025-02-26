#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Текстовая версия Telegram бота "Блинная башня"
"""

import os
import logging
import random
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище активных игр
active_games = {}

# Эмодзи для визуализации башни
PANCAKE_EMOJI = "🥞"
PLATE_EMOJI = "🍽️"

def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при команде /start."""
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в игру 'Блинная башня'!\n\n"
        f"Нажми /play, чтобы начать игру."
    )

def play_command(update: Update, context: CallbackContext) -> None:
    """Начинает новую игру при команде /play."""
    user_id = update.effective_user.id
    
    # Создаем новую игру для этого пользователя
    active_games[user_id] = {
        "score": 0,
        "tower_height": 0,
        "game_over": False
    }
    
    # Создаем клавиатуру с кнопкой "Играть"
    keyboard = [
        [InlineKeyboardButton("Играть", callback_data="play_game")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем начальное состояние игры
    message = update.message.reply_text(
        f"{PLATE_EMOJI}\n\nСчёт: 0",
        reply_markup=reply_markup
    )

def button_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия кнопок."""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "play_game":
        if user_id in active_games:
            game = active_games[user_id]
            
            # Если игра уже окончена, ничего не делаем
            if game["game_over"]:
                return
            
            # Увеличиваем счет
            game["score"] += 1
            game["tower_height"] += 1
            
            # Проверяем, не закончилась ли игра
            game_over = False
            
            # Шанс на падение башни увеличивается с высотой
            fall_chance = min(0.05 * (game["tower_height"] // 5), 0.5)
            
            if game["tower_height"] > 1 and random.random() < fall_chance:
                game_over = True
                game["game_over"] = True
            
            # Обновляем клавиатуру в зависимости от состояния игры
            keyboard = [
                [InlineKeyboardButton("Играть", callback_data="play_game")]
            ]
            
            # Создаем визуальное представление башни
            tower = PANCAKE_EMOJI * game["tower_height"]
            
            if game_over:
                keyboard = [
                    [InlineKeyboardButton("Новая игра", callback_data="new_game")]
                ]
                caption = f"💥 Башня упала! 💥\n\n{PLATE_EMOJI}\n\nФинальный счёт: {game['score']}"
            else:
                caption = f"{tower}\n{PLATE_EMOJI}\n\nСчёт: {game['score']}"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Обновляем сообщение с новым состоянием игры
            query.edit_message_text(
                text=caption,
                reply_markup=reply_markup
            )
    
    elif query.data == "new_game":
        # Начинаем новую игру
        active_games[user_id] = {
            "score": 0,
            "tower_height": 0,
            "game_over": False
        }
        
        # Создаем клавиатуру с кнопкой "Играть"
        keyboard = [
            [InlineKeyboardButton("Играть", callback_data="play_game")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Обновляем сообщение с новым состоянием игры
        query.edit_message_text(
            text=f"{PLATE_EMOJI}\n\nСчёт: 0",
            reply_markup=reply_markup
        )

def main():
    """Запускает бота."""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен бота
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("Токен бота не найден в переменных окружения!")
        exit(1)
    
    # Создаем Updater и передаем ему токен бота
    updater = Updater(token)
    
    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("play", play_command))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    
    # Запускаем бота
    print("=" * 50)
    print("Запуск Telegram бота 'Блинная башня' (текстовая версия)")
    print("=" * 50)
    print("\nБот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    updater.start_polling()
    
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == "__main__":
    main() 