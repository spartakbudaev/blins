#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот "Блинная башня" с анимированной игрой
"""

import os
import logging
import time
import threading
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

from pancake_game import PancakeGame

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище активных игр и их потоков анимации
active_games = {}
animation_threads = {}
last_update_time = {}  # Словарь для хранения времени последнего обновления для каждого пользователя
UPDATE_INTERVAL = 1.0  # Увеличиваем интервал обновления до 1 секунды

def start_animation(user_id, context):
    """Запускает анимацию движения блина для конкретного пользователя"""
    if user_id not in active_games or active_games[user_id].game_over:
        return
    
    game = active_games[user_id]
    
    # Проверяем, не слишком ли часто обновляем сообщение
    current_time = time.time()
    if user_id in last_update_time and current_time - last_update_time[user_id] < UPDATE_INTERVAL:
        # Если прошло меньше UPDATE_INTERVAL секунд с последнего обновления,
        # просто обновляем положение блина без отправки сообщения
        game.update_moving_pancake()
        
        # Планируем следующее обновление
        if user_id in animation_threads and animation_threads[user_id].is_alive():
            animation_threads[user_id] = threading.Timer(0.2, start_animation, args=[user_id, context])
            animation_threads[user_id].daemon = True
            animation_threads[user_id].start()
        return
    
    # Обновляем положение блина
    game.update_moving_pancake()
    
    # Генерируем новое изображение
    image_path = game.generate_game_image()
    
    # Обновляем сообщение с новым изображением
    try:
        with open(image_path, 'rb') as photo:
            context.bot.edit_message_media(
                chat_id=game.chat_id,
                message_id=game.message_id,
                media=InputMediaPhoto(
                    media=photo,
                    caption=f"Счёт: {game.score}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Играть", callback_data="play_game")]
                ])
            )
        # Обновляем время последнего обновления
        last_update_time[user_id] = current_time
    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения: {e}")
    
    # Удаляем временное изображение
    try:
        os.remove(image_path)
    except:
        pass
    
    # Планируем следующее обновление через 0.2 секунды
    if user_id in animation_threads and animation_threads[user_id].is_alive():
        animation_threads[user_id] = threading.Timer(0.2, start_animation, args=[user_id, context])
        animation_threads[user_id].daemon = True
        animation_threads[user_id].start()

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
    
    # Останавливаем предыдущую анимацию, если она была
    stop_animation(user_id)
    
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
    
    # Инициализируем время последнего обновления
    last_update_time[user_id] = time.time()
    
    # Запускаем анимацию
    animation_threads[user_id] = threading.Timer(0.2, start_animation, args=[user_id, context])
    animation_threads[user_id].daemon = True
    animation_threads[user_id].start()

def stop_animation(user_id):
    """Останавливает анимацию для конкретного пользователя"""
    if user_id in animation_threads and animation_threads[user_id].is_alive():
        animation_threads[user_id].cancel()
        del animation_threads[user_id]

def button_callback(update: Update, context: CallbackContext) -> None:
    """Обрабатывает нажатия кнопок."""
    query = update.callback_query
    query.answer()  # Убираем await, так как функция не асинхронная
    
    user_id = update.effective_user.id
    
    if query.data == "play_game":
        if user_id in active_games:
            game = active_games[user_id]
            
            # Останавливаем анимацию
            stop_animation(user_id)
            
            # Опускаем блин
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
                
                # Инициализируем время последнего обновления
                last_update_time[user_id] = time.time()
                
                # Запускаем анимацию снова, если игра не окончена
                animation_threads[user_id] = threading.Timer(0.2, start_animation, args=[user_id, context])
                animation_threads[user_id].daemon = True
                animation_threads[user_id].start()
            
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
        # Останавливаем предыдущую анимацию
        stop_animation(user_id)
        
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
        
        # Инициализируем время последнего обновления
        last_update_time[user_id] = time.time()
        
        # Запускаем анимацию
        animation_threads[user_id] = threading.Timer(0.2, start_animation, args=[user_id, context])
        animation_threads[user_id].daemon = True
        animation_threads[user_id].start()

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
    print("Запуск Telegram бота 'Блинная башня' с анимацией")
    print("=" * 50)
    print("\nБот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    updater.start_polling()
    
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == "__main__":
    main() 