/**
 * Инициализация приложения и интеграция с Telegram Mini App API
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM загружен, инициализация приложения");
    
    // Получаем элементы DOM
    const canvas = document.getElementById('game-canvas');
    const playButton = document.getElementById('play-button');
    const restartButton = document.getElementById('restart-button');
    const gameInstruction = document.getElementById('game-instruction');
    
    console.log("Элементы DOM получены:", {
        canvas: canvas ? "найден" : "не найден",
        playButton: playButton ? "найден" : "не найден",
        restartButton: restartButton ? "найден" : "не найден",
        gameInstruction: gameInstruction ? "найден" : "не найден"
    });
    
    // Инициализируем Telegram Mini App
    const tg = window.Telegram ? window.Telegram.WebApp : null;
    console.log("Telegram Mini App API:", tg ? "доступен" : "не доступен");
    
    if (tg) {
        console.log("Telegram Mini App данные:", {
            initData: tg.initData ? "присутствует" : "отсутствует",
            initDataUnsafe: tg.initDataUnsafe ? "присутствует" : "отсутствует",
            version: tg.version || "неизвестно"
        });
        
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            console.log("Данные пользователя:", {
                id: tg.initDataUnsafe.user.id,
                username: tg.initDataUnsafe.user.username || "отсутствует",
                first_name: tg.initDataUnsafe.user.first_name || "отсутствует"
            });
        }
    }
    
    // Сообщаем Telegram, что приложение готово
    if (tg) {
        tg.ready();
        console.log("Отправлен сигнал ready в Telegram Mini App");
        
        // Расширяем окно на весь экран
        tg.expand();
        console.log("Окно расширено на весь экран");
    }
    
    // Настраиваем цвета в соответствии с темой Telegram
    applyTelegramTheme();
    
    // Создаем игру
    console.log("Создание игры...");
    const game = new PancakeTowerGame(canvas);
    console.log("Игра создана");
    
    // Флаг, указывающий, началась ли игра
    let gameStarted = false;
    
    // Явно запускаем игровой цикл
    console.log("Явный запуск игрового цикла");
    game.startGameLoop();
    
    // Функция для опускания блина
    const dropPancakeAndCheckGameOver = () => {
        // Если игра уже окончена или идет анимация падения, ничего не делаем
        if (game.gameOver || game.isAnimatingDrop) return;
        
        // Опускаем блин
        const gameOver = game.dropPancake();
        
        // Если игра окончена, показываем кнопку "Новая игра"
        if (gameOver) {
            console.log("Игра окончена");
            restartButton.style.display = 'block';
            
            // Отправляем счет в Telegram
            sendScoreToTelegram(game.score);
        }
        
        // Вибрация при нажатии (если поддерживается)
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    };
    
    // Обработчик нажатия на кнопку "Играть"
    playButton.addEventListener('click', () => {
        console.log("Нажата кнопка 'Играть'");
        
        // Кнопка "Играть" остается видимой
        // playButton.style.display = 'none'; - удаляем эту строку
        
        // Скрываем инструкцию
        if (gameInstruction) {
            gameInstruction.style.opacity = '0';
        }
        
        // Устанавливаем флаг начала игры
        gameStarted = true;
        
        // Опускаем первый блин
        dropPancakeAndCheckGameOver();
    });
    
    // Обработчик нажатия на кнопку "Новая игра"
    restartButton.addEventListener('click', () => {
        console.log("Нажата кнопка 'Новая игра'");
        game.restart();
        restartButton.style.display = 'none';
        gameStarted = true;
        
        // Скрываем инструкцию
        if (gameInstruction) {
            gameInstruction.style.opacity = '0';
        }
        
        // Вибрация при нажатии (если поддерживается)
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    });
    
    // Обработчик клика по канвасу (для опускания блина)
    canvas.addEventListener('click', () => {
        // Если игра началась, опускаем блин
        if (gameStarted && !game.gameOver) {
            console.log("Клик по канвасу, опускаем блин");
            dropPancakeAndCheckGameOver();
        }
    });
    
    // Обработчик изменения темы Telegram
    if (tg) {
        tg.onEvent('themeChanged', applyTelegramTheme);
    }
    
    /**
     * Применяет тему Telegram к элементам игры
     */
    function applyTelegramTheme() {
        console.log("Применение темы Telegram");
        
        if (!tg) {
            console.log("Telegram Mini App API не доступен, используем стандартные цвета");
            return;
        }
        
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
        if (scoreCircle) {
            scoreCircle.style.borderColor = tg.themeParams.hint_color || '#c8e6ff';
        }
    }
    
    /**
     * Отправляет счет в Telegram
     * @param {number} score - Счет игрока
     */
    function sendScoreToTelegram(score) {
        console.log("Отправка счета в Telegram:", score);
        
        // Если доступно Telegram Mini App API
        if (tg) {
            console.log("Telegram Mini App API доступен");
            
            try {
                // Создаем данные для отправки
                const data = {
                    score: score,
                    timestamp: Date.now() // Добавляем временную метку
                };
                
                // Добавляем данные пользователя, если они доступны
                if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                    data.user_id = tg.initDataUnsafe.user.id;
                    data.username = tg.initDataUnsafe.user.username || tg.initDataUnsafe.user.first_name || 'unknown';
                    console.log("Данные пользователя добавлены:", {
                        user_id: data.user_id,
                        username: data.username
                    });
                } else {
                    console.log("Данные пользователя недоступны");
                }
                
                // Отправляем данные в Telegram
                const jsonData = JSON.stringify(data);
                console.log("Отправляемые данные (JSON):", jsonData);
                
                // Проверяем, доступен ли метод sendData
                if (typeof tg.sendData === 'function') {
                    tg.sendData(jsonData);
                    console.log("Данные успешно отправлены в Telegram");
                } else {
                    console.error("Метод tg.sendData не является функцией");
                    alert("Ошибка при отправке данных в Telegram: метод sendData недоступен");
                }
                
                // Показываем уведомление пользователю
                if (tg.showPopup) {
                    tg.showPopup({
                        title: "Игра завершена",
                        message: `Ваш счет: ${score} блинов`,
                        buttons: [{type: "ok"}]
                    });
                }
            } catch (error) {
                console.error("Ошибка при отправке данных в Telegram:", error);
                alert(`Ошибка при отправке данных в Telegram: ${error.message}`);
            }
        } else {
            console.log("Telegram Mini App API не доступен");
            
            // Для тестирования вне Telegram
            alert(`Игра окончена! Ваш счет: ${score} блинов`);
        }
    }
    
    // Добавляем обработчик свайпа для мобильных устройств
    let touchStartX = 0;
    let touchEndX = 0;
    
    canvas.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        console.log("Начало свайпа, позиция:", touchStartX);
    });
    
    canvas.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        console.log("Конец свайпа, позиция:", touchEndX);
        
        // Если игра не началась, ничего не делаем
        if (!gameStarted) return;
        
        handleSwipe();
    });
    
    function handleSwipe() {
        // Если игра окончена или идет анимация падения, ничего не делаем
        if (game.gameOver || game.isAnimatingDrop) {
            console.log("Игра окончена или идет анимация, свайп игнорируется");
            return;
        }
        
        // Вычисляем расстояние свайпа
        const swipeDistance = touchEndX - touchStartX;
        console.log("Расстояние свайпа:", swipeDistance);
        
        // Если свайп достаточно длинный
        if (Math.abs(swipeDistance) > 50) {
            console.log("Длинный свайп, перемещаем блин");
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
            console.log("Короткий тап, опускаем блин");
            // Короткий тап - опускаем блин
            dropPancakeAndCheckGameOver();
        }
    }
}); 