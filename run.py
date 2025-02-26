#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для запуска Telegram бота "Блинная башня"
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Проверяет наличие всех необходимых зависимостей и файлов"""
    # Проверка наличия файла .env
    if not os.path.exists('.env'):
        logger.error('Файл .env не найден! Создайте файл .env с токеном бота (BOT_TOKEN=ваш_токен)')
        return False
    
    # Проверка наличия токена бота
    load_dotenv()
    if not os.getenv('BOT_TOKEN'):
        logger.error('Токен бота не найден в файле .env! Добавьте BOT_TOKEN=ваш_токен в файл .env')
        return False
    
    # Проверка наличия директории для временных файлов
    if not os.path.exists('temp'):
        try:
            os.makedirs('temp')
            logger.info('Создана директория для временных файлов: temp/')
        except Exception as e:
            logger.error(f'Не удалось создать директорию для временных файлов: {e}')
            return False
    
    return True

def main():
    """Основная функция для запуска бота"""
    print("=" * 50)
    print("Запуск Telegram бота 'Блинная башня'")
    print("=" * 50)
    
    # Проверка требований
    if not check_requirements():
        print("\nОшибка: не все требования выполнены. Исправьте ошибки и попробуйте снова.")
        sys.exit(1)
    
    # Импортируем основной модуль бота
    try:
        # Прямой запуск основного модуля
        from bot import main as run_bot
        print("\nЗапуск бота...")
        run_bot()
    except ImportError as e:
        logger.error(f'Ошибка импорта модуля бота: {e}')
        print("\nОшибка: не удалось импортировать модуль бота. Проверьте наличие файла bot.py.")
        sys.exit(1)
    except Exception as e:
        logger.error(f'Ошибка при запуске бота: {e}')
        print(f"\nОшибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 