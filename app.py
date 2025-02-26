#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask-приложение для размещения веб-игры "Блинная башня" на Heroku
"""

import os
import json
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__, static_folder='webapp')

# Хранилище результатов игры (в реальном приложении лучше использовать базу данных)
game_results = {}

@app.route('/')
def index():
    """Главная страница приложения"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Обработка запросов к статическим файлам"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/save-score', methods=['POST'])
def save_score():
    """API для сохранения результатов игры"""
    try:
        data = request.json
        user_id = data.get('user_id')
        username = data.get('username', 'Аноним')
        score = data.get('score', 0)
        
        if user_id:
            game_results[user_id] = {
                "username": username,
                "score": score
            }
            return jsonify({"success": True, "message": "Результат сохранен"})
        else:
            return jsonify({"success": False, "message": "Не указан ID пользователя"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """API для получения таблицы лидеров"""
    try:
        # Сортируем результаты по убыванию счета
        sorted_results = sorted(
            game_results.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        # Возвращаем топ-10 результатов
        return jsonify({
            "success": True,
            "leaderboard": sorted_results[:10]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # Определяем порт (Heroku предоставляет порт через переменную окружения PORT)
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 