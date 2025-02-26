#!/bin/bash

# Скрипт для настройки деплоя на Render

echo "===== Настройка деплоя на Render ====="
echo ""

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Пожалуйста, установите git и попробуйте снова."
    exit 1
fi

# Проверка наличия репозитория git
if [ ! -d .git ]; then
    echo "📁 Инициализация git репозитория..."
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
    echo "✅ Git репозиторий инициализирован"
else
    echo "✅ Git репозиторий уже существует"
fi

# Проверка наличия файла render.yaml
if [ ! -f render.yaml ]; then
    echo "❌ Файл render.yaml не найден. Пожалуйста, создайте его перед запуском скрипта."
    exit 1
fi

echo ""
echo "===== Инструкции по деплою на Render ====="
echo ""
echo "1. Создайте аккаунт на Render (https://render.com) если у вас его еще нет"
echo "2. Создайте новый репозиторий на GitHub или GitLab"
echo "3. Добавьте удаленный репозиторий:"
echo "   git remote add origin <URL вашего репозитория>"
echo "4. Отправьте код в репозиторий:"
echo "   git push -u origin main"
echo "5. В Render Dashboard выберите 'Blueprint' и укажите ваш репозиторий"
echo "6. Render автоматически обнаружит файл render.yaml и создаст сервисы"
echo "7. Добавьте переменную окружения BOT_TOKEN в настройках сервиса бота"
echo "8. После деплоя, скопируйте URL веб-сервиса и добавьте его в .env файл как RENDER_APP_URL"
echo ""
echo "✅ Настройка завершена! Следуйте инструкциям выше для деплоя на Render."
echo "" 