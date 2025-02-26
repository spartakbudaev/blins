#!/bin/bash

# Скрипт для подготовки проекта к деплою на Heroku

# Проверяем, установлен ли Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "Heroku CLI не установлен. Пожалуйста, установите его: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Запрашиваем имя приложения
read -p "Введите имя для вашего Heroku приложения: " APP_NAME

# Проверяем, авторизован ли пользователь в Heroku
heroku auth:whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "Вы не авторизованы в Heroku. Запускаем процесс авторизации..."
    heroku login
fi

# Создаем приложение на Heroku
echo "Создаем приложение $APP_NAME на Heroku..."
heroku create $APP_NAME

# Получаем URL приложения
APP_URL="https://$APP_NAME.herokuapp.com"
echo "URL вашего приложения: $APP_URL"

# Обновляем .env файл
echo "Обновляем .env файл с URL приложения..."
sed -i '' "s|HEROKU_APP_URL=.*|HEROKU_APP_URL=$APP_URL|g" .env

# Запрашиваем токен бота
read -p "Введите токен вашего Telegram бота: " BOT_TOKEN

# Устанавливаем переменные окружения на Heroku
echo "Устанавливаем переменные окружения на Heroku..."
heroku config:set BOT_TOKEN=$BOT_TOKEN -a $APP_NAME

# Инициализируем Git репозиторий, если он еще не инициализирован
if [ ! -d .git ]; then
    echo "Инициализируем Git репозиторий..."
    git init
    git add .
    git commit -m "Initial commit"
fi

# Добавляем Heroku remote
echo "Добавляем Heroku remote..."
heroku git:remote -a $APP_NAME

echo "Все готово! Теперь вы можете отправить код на Heroku командой:"
echo "git push heroku main"
echo ""
echo "После деплоя запустите бота командой:"
echo "python heroku_bot.py" 