/**
 * Инициализация приложения и интеграция с Telegram Mini App API
 */
document.addEventListener('DOMContentLoaded', () => {
    // Получаем элементы DOM
    const canvas = document.getElementById('game-canvas');
    const playButton = document.getElementById('play-button');
    const restartButton = document.getElementById('restart-button');
    
    // Инициализируем Telegram Mini App
    const tg = window.Telegram.WebApp;
    
    // Сообщаем Telegram, что приложение готово
    tg.ready();
    
    // Настраиваем цвета в соответствии с темой Telegram
    applyTelegramTheme();
    
    // Создаем игру
    const game = new PancakeTowerGame(canvas);
    
    // Обработчик нажатия на кнопку "Играть"
    playButton.addEventListener('click', () => {
        const gameOver = game.dropPancake();
        
        // Если игра окончена, показываем кнопку "Новая игра"
        if (gameOver) {
            playButton.style.display = 'none';
            restartButton.style.display = 'block';
            
            // Отправляем счет в Telegram
            sendScoreToTelegram(game.score);
        }
        
        // Вибрация при нажатии (если поддерживается)
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    });
    
    // Обработчик нажатия на кнопку "Новая игра"
    restartButton.addEventListener('click', () => {
        game.restart();
        restartButton.style.display = 'none';
        playButton.style.display = 'block';
        
        // Вибрация при нажатии (если поддерживается)
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    });
    
    // Обработчик изменения темы Telegram
    tg.onEvent('themeChanged', applyTelegramTheme);
    
    /**
     * Применяет тему Telegram к элементам игры
     */
    function applyTelegramTheme() {
        // Устанавливаем цвета в соответствии с темой Telegram
        document.body.style.backgroundColor = tg.themeParams.bg_color || '#ffffff';
        document.body.style.color = tg.themeParams.text_color || '#000000';
        
        // Настраиваем цвета кнопок
        const buttons = document.querySelectorAll('.tg-button');
        buttons.forEach(button => {
            button.style.backgroundColor = tg.themeParams.button_color || '#2AABEE';
            button.style.color = tg.themeParams.button_text_color || '#ffffff';
        });
        
        // Настраиваем цвет круга со счетом
        const scoreCircle = document.getElementById('score-circle');
        scoreCircle.style.borderColor = tg.themeParams.hint_color || '#c8e6ff';
    }
    
    /**
     * Отправляет счет в Telegram
     * @param {number} score - Счет игрока
     */
    function sendScoreToTelegram(score) {
        // Если доступно Telegram Mini App API
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            // Создаем данные для отправки
            const data = {
                score: score,
                user_id: tg.initDataUnsafe.user.id,
                username: tg.initDataUnsafe.user.username || 'unknown'
            };
            
            // Отправляем данные в Telegram
            tg.sendData(JSON.stringify(data));
        }
    }
    
    // Добавляем обработчик свайпа для мобильных устройств
    let touchStartX = 0;
    let touchEndX = 0;
    
    canvas.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    canvas.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
    
    function handleSwipe() {
        // Если игра окончена, ничего не делаем
        if (game.gameOver) return;
        
        // Вычисляем расстояние свайпа
        const swipeDistance = touchEndX - touchStartX;
        
        // Если свайп достаточно длинный
        if (Math.abs(swipeDistance) > 50) {
            // Перемещаем блин в направлении свайпа
            if (game.currentPancake) {
                game.currentPancake.x += swipeDistance;
                
                // Проверяем границы
                if (game.currentPancake.x < 0) {
                    game.currentPancake.x = 0;
                } else if (game.currentPancake.x + game.currentPancake.width > game.canvas.width) {
                    game.currentPancake.x = game.canvas.width - game.currentPancake.width;
                }
            }
        } else {
            // Короткий тап - опускаем блин
            game.dropPancake();
            
            // Если игра окончена, показываем кнопку "Новая игра"
            if (game.gameOver) {
                playButton.style.display = 'none';
                restartButton.style.display = 'block';
                
                // Отправляем счет в Telegram
                sendScoreToTelegram(game.score);
            }
        }
    }
}); 