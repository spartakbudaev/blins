#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Telegram бот "Блинная башня" с анимацией на основе эмодзи
"""

import os
import logging
import time
import random
import threading
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище активных игр и их потоков анимации
active_games = {}
animation_threads = {}

# Эмодзи для визуализации
PANCAKE_EMOJI = "🥞"
PLATE_EMOJI = "🍽️"
ARROW_LEFT = "⬅️"
ARROW_RIGHT = "➡️"

class EmojiPancakeGame:
    """Класс для игры 'Блинная башня' с эмодзи"""
    
    def __init__(self):
        """Инициализация новой игры"""
        # Базовые параметры игры
        self.score = 0
        self.game_over = False
        self.message_id = None
        self.chat_id = None
        
        # Параметры игрового поля
        self.width = 10  # Ширина игрового поля в символах
        
        # Параметры блинов
        self.pancakes = []  # Уложенные блины
        
        # Параметры для движущегося блина
        self.current_pancake = {
            "x": 0,  # Текущая позиция X
            "width": 5,  # Начальная ширина блина (в символах)
            "direction": 1  # 1 - вправо, -1 - влево
        }
    
    def update_moving_pancake(self):
        """Обновляет положение движущегося блина"""
        # Если игра окончена, ничего не делаем
        if self.game_over:
            return
        
        # Обновляем позицию блина
        self.current_pancake["x"] += self.current_pancake["direction"]
        
        # Проверяем, не достиг ли блин края экрана
        if self.current_pancake["x"] <= 0:
            self.current_pancake["x"] = 0
            self.current_pancake["direction"] = 1  # Меняем направление на вправо
        elif self.current_pancake["x"] + self.current_pancake["width"] >= self.width:
            self.current_pancake["x"] = self.width - self.current_pancake["width"]
            self.current_pancake["direction"] = -1  # Меняем направление на влево
    
    def drop_pancake(self):
        """Опускает текущий блин на башню"""
        # Если игра уже окончена, ничего не делаем
        if self.game_over:
            return True
        
        # Определяем параметры для нового блина
        if not self.pancakes:
            # Первый блин
            pancake_x = self.current_pancake["x"]
            pancake_width = self.current_pancake["width"]
        else:
            # Последующие блины
            prev_pancake = self.pancakes[-1]
            pancake_x = self.current_pancake["x"]
            pancake_width = self.current_pancake["width"]
            
            # Проверяем, не выходит ли блин за пределы предыдущего
            # Вычисляем перекрытие с предыдущим блином
            overlap_left = max(pancake_x, prev_pancake["x"])
            overlap_right = min(pancake_x + pancake_width, prev_pancake["x"] + prev_pancake["width"])
            
            if overlap_right <= overlap_left:
                # Блины не перекрываются - игра окончена
                self.game_over = True
                return True
            
            # Если блин частично свисает, уменьшаем его ширину
            if pancake_x < prev_pancake["x"] or (pancake_x + pancake_width) > (prev_pancake["x"] + prev_pancake["width"]):
                # Вычисляем новую ширину и положение блина
                new_width = overlap_right - overlap_left
                new_x = overlap_left
                
                # Если блин стал слишком узким, игра окончена
                if new_width < 1:
                    self.game_over = True
                    return True
                
                pancake_width = new_width
                pancake_x = new_x
        
        # Добавляем блин в башню
        self.pancakes.append({
            "x": pancake_x,
            "width": pancake_width
        })
        
        # Увеличиваем счет
        self.score += 1
        
        # Создаем новый движущийся блин
        self.current_pancake = {
            "x": random.randint(0, self.width - pancake_width),
            "width": pancake_width,  # Ширина равна ширине предыдущего уложенного блина
            "direction": random.choice([-1, 1])  # Случайное начальное направление
        }
        
        # Проверяем, не достигла ли башня максимальной высоты
        if len(self.pancakes) >= 15:
            self.game_over = True
            return True
        
        return False
    
    def generate_game_text(self):
        """Генерирует текстовое представление игры с эмодзи"""
        # Создаем пустое игровое поле
        field = []
        
        # Добавляем движущийся блин, если игра не окончена
        if not self.game_over:
            moving_line = " " * self.current_pancake["x"] + PANCAKE_EMOJI * self.current_pancake["width"] + " " * (self.width - self.current_pancake["x"] - self.current_pancake["width"])
            
            # Добавляем индикатор направления движения
            if self.current_pancake["direction"] > 0:
                direction_indicator = ARROW_RIGHT
            else:
                direction_indicator = ARROW_LEFT
            
            field.append(moving_line + " " + direction_indicator)
        else:
            field.append(" " * self.width)
        
        # Добавляем пустое пространство между движущимся блином и башней
        empty_lines = max(0, 10 - len(self.pancakes))
        for _ in range(empty_lines):
            field.append(" " * self.width)
        
        # Добавляем блины в башне (в обратном порядке, сверху вниз)
        for pancake in reversed(self.pancakes):
            pancake_line = " " * pancake["x"] + PANCAKE_EMOJI * pancake["width"] + " " * (self.width - pancake["x"] - pancake["width"])
            field.append(pancake_line)
        
        # Добавляем тарелку
        field.append(PLATE_EMOJI)
        
        # Объединяем все строки
        return "\n".join(field)

def start_animation(user_id, context):
    """Запускает анимацию движения блина для конкретного пользователя"""
    if user_id not in active_games or active_games[user_id].game_over:
        return
    
    game = active_games[user_id]
    
    # Обновляем положение блина
    game.update_moving_pancake()
    
    # Генерируем новое текстовое представление
    game_text = game.generate_game_text()
    
    # Обновляем сообщение с новым текстом
    try:
        context.bot.edit_message_text(
            chat_id=game.chat_id,
            message_id=game.message_id,
            text=f"{game_text}\n\nСчёт: {game.score}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Играть", callback_data="play_game")]
            ])
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении сообщения: {e}")
    
    # Планируем следующее обновление через 0.5 секунды
    if user_id in animation_threads and animation_threads[user_id].is_alive():
        animation_threads[user_id] = threading.Timer(0.5, start_animation, args=[user_id, context])
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
    active_games[user_id] = EmojiPancakeGame()
    game = active_games[user_id]
    
    # Генерируем начальное текстовое представление
    game_text = game.generate_game_text()
    
    # Создаем клавиатуру с кнопкой "Играть"
    keyboard = [
        [InlineKeyboardButton("Играть", callback_data="play_game")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем начальное состояние игры
    message = update.message.reply_text(
        f"{game_text}\n\nСчёт: {game.score}",
        reply_markup=reply_markup
    )
    
    # Сохраняем ID сообщения для будущих обновлений
    game.message_id = message.message_id
    game.chat_id = update.effective_chat.id
    
    # Запускаем анимацию
    animation_threads[user_id] = threading.Timer(0.5, start_animation, args=[user_id, context])
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
    query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "play_game":
        if user_id in active_games:
            game = active_games[user_id]
            
            # Останавливаем анимацию
            stop_animation(user_id)
            
            # Опускаем блин
            game_over = game.drop_pancake()
            
            # Генерируем обновленное текстовое представление
            game_text = game.generate_game_text()
            
            # Обновляем клавиатуру в зависимости от состояния игры
            keyboard = [
                [InlineKeyboardButton("Играть", callback_data="play_game")]
            ]
            
            if game_over:
                keyboard = [
                    [InlineKeyboardButton("Новая игра", callback_data="new_game")]
                ]
                caption = f"{game_text}\n\n💥 Игра окончена! 💥\nФинальный счёт: {game.score}"
            else:
                caption = f"{game_text}\n\nСчёт: {game.score}"
                
                # Запускаем анимацию снова, если игра не окончена
                animation_threads[user_id] = threading.Timer(0.5, start_animation, args=[user_id, context])
                animation_threads[user_id].daemon = True
                animation_threads[user_id].start()
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Обновляем сообщение с новым состоянием игры
            context.bot.edit_message_text(
                chat_id=game.chat_id,
                message_id=game.message_id,
                text=caption,
                reply_markup=reply_markup
            )
    
    elif query.data == "new_game":
        # Останавливаем предыдущую анимацию
        stop_animation(user_id)
        
        # Начинаем новую игру
        active_games[user_id] = EmojiPancakeGame()
        game = active_games[user_id]
        
        # Генерируем начальное текстовое представление
        game_text = game.generate_game_text()
        
        # Создаем клавиатуру с кнопкой "Играть"
        keyboard = [
            [InlineKeyboardButton("Играть", callback_data="play_game")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Обновляем сообщение с новым состоянием игры
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            text=f"{game_text}\n\nСчёт: {game.score}",
            reply_markup=reply_markup
        )
        
        # Сохраняем ID сообщения для будущих обновлений
        game.message_id = query.message.message_id
        game.chat_id = update.effective_chat.id
        
        # Запускаем анимацию
        animation_threads[user_id] = threading.Timer(0.5, start_animation, args=[user_id, context])
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
    print("Запуск Telegram бота 'Блинная башня' с анимацией на основе эмодзи")
    print("=" * 50)
    print("\nБот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    updater.start_polling()
    
    # Останавливаем бота при нажатии Ctrl+C
    updater.idle()

if __name__ == "__main__":
    main() 