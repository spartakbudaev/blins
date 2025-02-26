#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Игра "Блинная башня" с правильной механикой движения блинов
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class PancakeGame:
    """Класс для игры 'Блинная башня'"""
    
    def __init__(self):
        """Инициализация новой игры"""
        # Базовые параметры игры
        self.score = 0
        self.game_over = False
        self.message_id = None
        self.chat_id = None
        
        # Параметры игрового поля
        self.width = 600
        self.height = 800
        self.bg_color = (255, 255, 255)
        
        # Параметры блинов
        self.pancakes = []  # Уложенные блины
        self.plate_y = self.height - 100  # Позиция тарелки
        self.plate_width = 300
        self.plate_height = 30
        self.plate_color = (255, 150, 120)  # Цвет тарелки (розовый)
        
        # Параметры для движущегося блина
        self.current_pancake = {
            "x": 0,  # Текущая позиция X
            "y": 200,  # Высота, на которой движется блин
            "width": self.plate_width - 20,  # Начальная ширина блина
            "height": 20,  # Высота блина
            "direction": 1,  # 1 - вправо, -1 - влево
            "speed": 5,  # Скорость движения
            "color": (255, 220, 50)  # Цвет блина
        }
        
        # Цвета блинов (от светлого к темному)
        self.pancake_colors = [
            (255, 220, 50),   # Светло-желтый
            (255, 200, 50),   # Желтый
            (255, 180, 50),   # Темно-желтый
            (255, 160, 50),   # Оранжево-желтый
            (255, 140, 50),   # Светло-оранжевый
        ]
        
        # Создаем директорию для временных файлов, если её нет
        os.makedirs("temp", exist_ok=True)
    
    def update_moving_pancake(self):
        """Обновляет положение движущегося блина"""
        # Если игра окончена, ничего не делаем
        if self.game_over:
            return
        
        # Обновляем позицию блина
        self.current_pancake["x"] += self.current_pancake["direction"] * self.current_pancake["speed"]
        
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
        
        # Определяем Y-координату для нового блина
        if not self.pancakes:
            # Первый блин на тарелке
            pancake_y = self.plate_y - self.current_pancake["height"]
            pancake_x = self.current_pancake["x"]
            pancake_width = self.current_pancake["width"]
        else:
            # Последующие блины на предыдущем
            prev_pancake = self.pancakes[-1]
            pancake_y = prev_pancake["y"] - self.current_pancake["height"]
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
                if new_width < 30:
                    self.game_over = True
                    return True
                
                pancake_width = new_width
                pancake_x = new_x
        
        # Добавляем блин в башню
        self.pancakes.append({
            "x": pancake_x,
            "y": pancake_y,
            "width": pancake_width,
            "height": self.current_pancake["height"],
            "color": self.current_pancake["color"]
        })
        
        # Увеличиваем счет
        self.score += 1
        
        # Создаем новый движущийся блин
        self.current_pancake = {
            "x": random.randint(0, self.width - pancake_width),
            "y": 200,  # Высота, на которой движется блин
            "width": pancake_width,  # Ширина равна ширине предыдущего уложенного блина
            "height": 20,  # Высота блина
            "direction": random.choice([-1, 1]),  # Случайное начальное направление
            "speed": 5 + min(self.score // 5, 10),  # Скорость увеличивается с ростом счета
            "color": random.choice(self.pancake_colors)  # Случайный цвет из палитры
        }
        
        # Проверяем, не достигла ли башня верха экрана
        if pancake_y < 100:
            self.game_over = True
            return True
        
        return False
    
    def generate_game_image(self):
        """Генерирует изображение текущего состояния игры"""
        # Создаем новое изображение
        image = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(image)
        
        # Добавляем декоративные элементы фона
        self._draw_background(draw)
        
        # Рисуем счет в центре верхней части
        self._draw_score(draw)
        
        # Рисуем тарелку
        plate_x = (self.width - self.plate_width) // 2
        draw.rectangle(
            [(plate_x, self.plate_y), (plate_x + self.plate_width, self.plate_y + self.plate_height)],
            fill=self.plate_color,
            outline=None
        )
        
        # Рисуем все блины в башне
        for pancake in self.pancakes:
            self._draw_pancake(draw, pancake)
        
        # Рисуем движущийся блин, если игра не окончена
        if not self.game_over:
            self._draw_pancake(draw, self.current_pancake)
        
        # Сохраняем изображение во временный файл
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        image_path = f"temp/game_{timestamp}.png"
        image.save(image_path)
        
        return image_path
    
    def _draw_background(self, draw):
        """Рисует декоративные элементы фона"""
        # Добавляем светло-голубые декоративные элементы
        light_blue = (230, 240, 255, 128)
        
        # Рисуем несколько декоративных элементов
        # Банка с медом
        draw.ellipse([(50, 150), (150, 250)], fill=light_blue)
        draw.rectangle([(70, 100), (130, 150)], fill=light_blue)
        
        # Чашка
        draw.ellipse([(50, 650), (150, 700)], fill=light_blue)
        draw.rectangle([(50, 600), (150, 650)], fill=light_blue)
        draw.arc([(150, 620), (180, 670)], 270, 90, fill=light_blue, width=5)
        
        # Пчела
        draw.ellipse([(100, 300), (140, 340)], fill=light_blue)
        
        # Кривая линия (как на скриншотах)
        points = []
        for i in range(0, 361, 10):
            x = 300 + 250 * (i / 360)
            y = 400 + 200 * (1 - abs((i - 180) / 180))
            points.append((x, y))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill=light_blue, width=3)
    
    def _draw_score(self, draw):
        """Рисует счет в центре верхней части экрана"""
        # Создаем круг для счета
        circle_radius = 50
        circle_center = (self.width // 2, 200)
        draw.ellipse(
            [(circle_center[0] - circle_radius, circle_center[1] - circle_radius),
             (circle_center[0] + circle_radius, circle_center[1] + circle_radius)],
            outline=(200, 220, 255),
            fill=(255, 255, 255),
            width=2
        )
        
        # Рисуем текст счета
        # Примечание: в реальном приложении нужно установить шрифт
        # Здесь используем стандартный шрифт
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()
        
        # Центрируем текст
        text = str(self.score)
        
        # В новых версиях Pillow используем get_text_width вместо textlength
        try:
            # Для новых версий Pillow
            text_bbox = font.getbbox(text)
            text_width = text_bbox[2] - text_bbox[0]
        except AttributeError:
            try:
                # Для более старых версий Pillow
                text_width = draw.textlength(text, font=font)
            except AttributeError:
                # Для еще более старых версий
                text_width = font.getsize(text)[0]
        
        text_position = (circle_center[0] - text_width // 2, circle_center[1] - 18)
        
        draw.text(text_position, text, fill=(0, 0, 0), font=font)
    
    def _draw_pancake(self, draw, pancake):
        """Рисует блин с волнистыми краями"""
        x, y, width, height = pancake["x"], pancake["y"], pancake["width"], pancake["height"]
        color = pancake.get("color", (255, 220, 50))  # Используем цвет блина или значение по умолчанию
        
        # Основная форма блина
        draw.rectangle([(x, y), (x + width, y + height)], fill=color)
        
        # Добавляем волнистые края (верхний и нижний)
        wave_height = 4
        wave_count = max(3, width // 20)  # Количество волн зависит от ширины блина
        
        for i in range(wave_count + 1):
            wave_x = x + (width / wave_count) * i
            
            # Верхняя волна
            if i % 2 == 0:
                draw.rectangle([(wave_x - 5, y - wave_height), (wave_x + 5, y)], fill=color)
            
            # Нижняя волна
            if i % 2 == 1:
                draw.rectangle([(wave_x - 5, y + height), (wave_x + 5, y + height + wave_height)], fill=color) 