#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Прямой запуск Telegram бота "Блинная башня"
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from game import PancakeGame

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище активных игр
active_games = {}

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
    active_games[user_id] = PancakeGame()
    game = active_games[user_id]
    
    # Генерируем начальное изображение игры
    image_path = game.generate_game_image()
    
    # Создаем клавиатуру с кнопкой "Играть"
    keyboard = [
        [InlineKeyboardButton("Играть", callback_data="play_game")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем начальное состояние игры
    with open(image_path, 'rb') as photo:
        message = update.message.reply_photo(
            photo=photo,
            caption=f"Счёт: {game.score}",
            reply_markup=reply_markup
        )
    
    # Сохраняем ID сообщения для будущих обновлений
    game.message_id = message.message_id
    game.chat_id = update.effective_chat.id
    
    # Удаляем временное изображение
    os.remove(image_path)

def button_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия кнопок."""
    query = update.callback_query
    query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "play_game":
        if user_id in active_games:
            game = active_games[user_id]
            
            # Добавляем блин
            game_over = game.drop_pancake()
            
            # Генерируем обновленное изображение игры
            image_path = game.generate_game_image()
            
            # Обновляем клавиатуру в зависимости от состояния игры
            keyboard = [
                [InlineKeyboardButton("Играть", callback_data="play_game")]
            ]
            
            if game_over:
                keyboard = [
                    [InlineKeyboardButton("Новая игра", callback_data="new_game")]
                ]
                caption = f"Игра окончена! Финальный счёт: {game.score}"
            else:
                caption = f"Счёт: {game.score}"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Обновляем сообщение с новым состоянием игры
            with open(image_path, 'rb') as photo:
                context.bot.edit_message_media(
                    chat_id=game.chat_id,
                    message_id=game.message_id,
                    media=InputMediaPhoto(
                        media=photo,
                        caption=caption
                    ),
                    reply_markup=reply_markup
                )
            
            # Удаляем временное изображение
            os.remove(image_path)
    
    elif query.data == "new_game":
        # Начинаем новую игру
        active_games[user_id] = PancakeGame()
        game = active_games[user_id]
        
        # Генерируем начальное изображение игры
        image_path = game.generate_game_image()
        
        # Создаем клавиатуру с кнопкой "Играть"
        keyboard = [
            [InlineKeyboardButton("Играть", callback_data="play_game")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Обновляем сообщение с новым состоянием игры
        with open(image_path, 'rb') as photo:
            context.bot.edit_message_media(
                chat_id=update.effective_chat.id,
                message_id=query.message.message_id,
                media=InputMediaPhoto(
                    media=photo,
                    caption=f"Счёт: {game.score}"
                ),
                reply_markup=reply_markup
            )
        
        # Сохраняем ID сообщения для будущих обновлений
        game.message_id = query.message.message_id
        game.chat_id = update.effective_chat.id
        
        # Удаляем временное изображение
        os.remove(image_path)

def main():
    """Запускает бота."""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Получаем токен бота
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("Токен бота не найден в переменных окружения!")
        exit(1)
    
    # Создаем директорию для временных файлов, если её нет
    os.makedirs("temp", exist_ok=True)
    
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
    print("Запуск Telegram бота 'Блинная башня'")
    print("=" * 50)
    print("\nБот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    updater.start_polling()
    
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == "__main__":
    main() 