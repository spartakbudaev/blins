/**
 * Основной класс игры "Блинная башня"
 */
class PancakeTowerGame {
    /**
     * Создает новую игру
     * @param {HTMLCanvasElement} canvas - Элемент canvas для отрисовки игры
     */
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.resizeCanvas();
        
        // Параметры игры
        this.score = 0;
        this.gameOver = false;
        this.pancakes = []; // Уложенные блины
        this.plateY = this.canvas.height - 100; // Позиция тарелки
        this.plateWidth = Math.min(300, this.canvas.width * 0.7);
        this.plateHeight = 30;
        this.plateColor = '#FF9678'; // Цвет тарелки (розовый)
        
        // Параметры камеры и анимации
        this.cameraOffsetY = 0; // Смещение камеры по вертикали
        this.targetCameraOffsetY = 0; // Целевое смещение камеры
        this.cameraSpeed = 0.1; // Скорость движения камеры
        this.thirdScreenHeight = this.canvas.height / 3; // Треть высоты экрана
        
        // Параметры анимации падения блина
        this.droppingPancake = null; // Падающий блин
        this.targetY = 0; // Целевая позиция Y для падающего блина
        this.dropSpeed = 10; // Скорость падения блина
        this.isAnimatingDrop = false; // Флаг анимации падения
        
        // Цвета блинов (от светлого к темному)
        this.pancakeColors = [
            '#FFE032', // Светло-желтый
            '#FFC832', // Желтый
            '#FFB432', // Темно-желтый
            '#FFA032', // Оранжево-желтый
            '#FF8C32'  // Светло-оранжевый
        ];
        
        // Создаем движущийся блин
        this.createMovingPancake();
        
        // Запускаем игровой цикл
        this.lastTime = 0;
        this.animationId = null;
        this.startGameLoop();
        
        // Обработчик изменения размера окна
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    /**
     * Изменяет размер канваса в соответствии с размером окна
     */
    resizeCanvas() {
        // Проверяем, что canvas и его родительский элемент существуют
        if (!this.canvas || !this.canvas.parentElement) return;
        
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight * 0.9; // Увеличиваем до 90% высоты контейнера
        
        // Обновляем треть высоты экрана
        this.thirdScreenHeight = this.canvas.height / 3;
        
        // Обновляем позицию тарелки
        this.plateY = this.canvas.height - 100;
        
        // Перерисовываем игру после изменения размера
        if (this.pancakes && this.pancakes.length > 0) {
            this.draw();
        }
    }
    
    /**
     * Создает новый движущийся блин
     */
    createMovingPancake() {
        // Определяем размеры блина
        let pancakeWidth;
        
        if (this.pancakes.length > 0) {
            // Если есть предыдущие блины, используем ширину последнего блина
            const lastPancake = this.pancakes[this.pancakes.length - 1];
            pancakeWidth = lastPancake.width;
            console.log("Новый блин наследует ширину предыдущего:", pancakeWidth);
        } else {
            // Для первого блина используем стандартную ширину
            pancakeWidth = Math.min(200, this.canvas.width * 0.5);
            console.log("Первый блин с шириной:", pancakeWidth);
        }
        
        const pancakeHeight = 20;
        
        // Определяем начальную позицию блина
        const pancakeX = (this.canvas.width - pancakeWidth) / 2;
        const pancakeY = 50;
        
        // Выбираем случайный цвет блина
        const colorIndex = Math.floor(Math.random() * this.pancakeColors.length);
        const pancakeColor = this.pancakeColors[colorIndex];
        
        // Для первого блина в игре или после сброса
        if (this.score === 0 || this.pancakes.length === 0) {
            // Создаем новый блин обычного размера
            this.currentPancake = new Pancake(
                pancakeX,
                pancakeY,
                pancakeWidth,
                pancakeHeight,
                pancakeColor,
                true // Устанавливаем флаг isMoving в true
            );
        } else {
            // Для последующих блинов начинаем с маленького круглого блина
            // который будет расти до размера последнего блина в башне
            const smallSize = 40;
            this.currentPancake = new Pancake(
                (this.canvas.width - smallSize) / 2,
                pancakeY,
                smallSize,
                pancakeHeight,
                pancakeColor,
                true // Устанавливаем флаг isMoving в true
            );
            
            // Устанавливаем флаг для отображения как круг
            this.currentPancake.isCircle = true;
            
            // Анимируем рост блина до размера последнего блина
            this.animateGrowth(this.currentPancake, pancakeWidth);
        }
        
        // Устанавливаем случайное направление и скорость
        this.currentPancake.direction = Math.random() > 0.5 ? 1 : -1;
        
        // Увеличиваем скорость с ростом счета (но не слишком сильно)
        const baseSpeed = 3;
        const speedIncrease = Math.min(this.score / 5, 7); // Ограничиваем максимальное увеличение скорости
        this.currentPancake.speed = baseSpeed + speedIncrease;
        
        console.log("Создан новый блин:", {
            x: this.currentPancake.x,
            y: this.currentPancake.y,
            width: this.currentPancake.width,
            height: this.currentPancake.height,
            speed: this.currentPancake.speed,
            direction: this.currentPancake.direction,
            isMoving: this.currentPancake.isMoving,
            isCircle: this.currentPancake.isCircle
        });
    }
    
    /**
     * Анимирует рост блина от маленького круга до нормального размера
     * @param {Pancake} pancake - Блин для анимации
     * @param {number} targetWidth - Целевая ширина блина
     */
    animateGrowth(pancake, targetWidth) {
        const growthDuration = 500; // Длительность анимации в мс
        const startTime = performance.now();
        const startWidth = pancake.width;
        const startX = pancake.x;
        const targetX = (this.canvas.width - targetWidth) / 2;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / growthDuration, 1);
            
            // Используем функцию плавного перехода
            const easedProgress = this.easeOutQuad(progress);
            
            // Обновляем ширину и положение блина
            pancake.width = startWidth + (targetWidth - startWidth) * easedProgress;
            pancake.x = startX + (targetX - startX) * easedProgress;
            
            // Обновляем количество волн
            pancake.waveCount = Math.max(3, Math.floor(pancake.width / 20));
            
            // Продолжаем анимацию, если она не завершена
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Анимация завершена, блин больше не круг
                pancake.isCircle = false;
            }
        };
        
        // Запускаем анимацию
        requestAnimationFrame(animate);
    }
    
    /**
     * Функция плавного перехода (easing function)
     * @param {number} t - Прогресс анимации (от 0 до 1)
     * @returns {number} - Скорректированный прогресс
     */
    easeOutQuad(t) {
        return t * (2 - t);
    }
    
    /**
     * Запускает игровой цикл
     */
    startGameLoop() {
        console.log("Запуск игрового цикла");
        
        // Останавливаем предыдущий цикл, если он был
        this.stopGameLoop();
        
        // Сбрасываем время
        this.lastTime = performance.now();
        console.log("Время сброшено:", this.lastTime);
        
        // Принудительно запускаем первое обновление
        this.update(16); // 16 мс - примерно 60 FPS
        this.draw();
        
        const gameLoop = (timestamp) => {
            // Вычисляем deltaTime
            const deltaTime = timestamp - this.lastTime;
            this.lastTime = timestamp;
            
            // Обновляем состояние игры
            this.update(deltaTime);
            
            // Отрисовываем игру
            this.draw();
            
            // Продолжаем цикл, если игра не окончена
            if (!this.gameOver) {
                this.animationId = requestAnimationFrame(gameLoop);
            } else {
                console.log("Игра окончена, останавливаем цикл");
            }
        };
        
        // Запускаем первый кадр
        console.log("Запускаем первый кадр игрового цикла");
        this.animationId = requestAnimationFrame(gameLoop);
    }
    
    /**
     * Останавливает игровой цикл
     */
    stopGameLoop() {
        console.log("Остановка игрового цикла");
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }
    
    /**
     * Обновляет состояние игры
     * @param {number} deltaTime - Время, прошедшее с последнего обновления
     */
    update(deltaTime) {
        if (this.gameOver) return;
        
        // Обновляем положение движущегося блина
        if (this.currentPancake && !this.isAnimatingDrop) {
            // Убеждаемся, что блин отмечен как движущийся
            this.currentPancake.isMoving = true;
            
            // Принудительно устанавливаем скорость, если она равна 0
            if (this.currentPancake.speed === 0) {
                this.currentPancake.speed = 3;
                console.log("Скорость блина была 0, установлена на 3");
            }
            
            // Обновляем позицию блина
            const oldX = this.currentPancake.x;
            this.currentPancake.update(this.canvas.width);
            
            // Проверяем, изменилась ли позиция
            if (oldX === this.currentPancake.x && this.currentPancake.direction !== 0) {
                // Если позиция не изменилась, но направление не нулевое,
                // принудительно меняем направление
                this.currentPancake.direction *= -1;
                console.log("Блин застрял, меняем направление на:", this.currentPancake.direction);
            }
        }
        
        // Обновляем анимацию падения блина
        if (this.isAnimatingDrop && this.droppingPancake) {
            // Плавно перемещаем блин к целевой позиции
            const distanceToTarget = this.targetY - this.droppingPancake.y;
            
            if (Math.abs(distanceToTarget) > 1) {
                // Блин еще не достиг цели, продолжаем анимацию
                const step = Math.sign(distanceToTarget) * this.dropSpeed;
                this.droppingPancake.y += step;
                
                // Проверяем, не перескочили ли мы цель
                if ((step > 0 && this.droppingPancake.y > this.targetY) || 
                    (step < 0 && this.droppingPancake.y < this.targetY)) {
                    this.droppingPancake.y = this.targetY;
                }
            } else {
                // Блин достиг цели, завершаем анимацию
                this.droppingPancake.y = this.targetY;
                this.droppingPancake.isMoving = false; // Останавливаем блин
                this.droppingPancake.isPlaced = true; // Помечаем блин как уложенный
                this.isAnimatingDrop = false;
                
                // Добавляем блин в башню
                this.pancakes.push(this.droppingPancake);
                this.droppingPancake = null;
                
                // Создаем новый движущийся блин с небольшой задержкой
                setTimeout(() => {
                    this.createMovingPancake();
                }, 100);
            }
        }
        
        // Плавно обновляем смещение камеры
        if (Math.abs(this.targetCameraOffsetY - this.cameraOffsetY) > 0.1) {
            // Используем deltaTime для плавного движения камеры
            const cameraStep = (this.targetCameraOffsetY - this.cameraOffsetY) * 
                               Math.min(this.cameraSpeed * (deltaTime / 16), 1);
            this.cameraOffsetY += cameraStep;
        } else {
            this.cameraOffsetY = this.targetCameraOffsetY;
        }
    }
    
    /**
     * Отрисовывает игру
     */
    draw() {
        // Очищаем канвас
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Рисуем фон
        this.drawBackground();
        
        // Сохраняем текущее состояние контекста
        this.ctx.save();
        
        // Применяем смещение камеры (отрицательное, чтобы камера двигалась вниз)
        this.ctx.translate(0, -this.cameraOffsetY);
        
        // Рисуем тарелку
        this.ctx.fillStyle = '#FF69B4'; // Розовый цвет
        this.ctx.fillRect(
            (this.canvas.width - this.plateWidth) / 2,
            this.plateY,
            this.plateWidth,
            this.plateHeight
        );
        
        // Рисуем блины в башне
        for (const pancake of this.pancakes) {
            pancake.draw(this.ctx);
        }
        
        // Рисуем падающий блин
        if (this.droppingPancake) {
            this.droppingPancake.draw(this.ctx);
        }
        
        // Восстанавливаем состояние контекста
        this.ctx.restore();
        
        // Рисуем текущий движущийся блин (поверх всего)
        if (this.currentPancake && !this.isAnimatingDrop) {
            this.currentPancake.draw(this.ctx);
        }
        
        // Обновляем счет
        document.getElementById('score-value').textContent = this.score;
    }
    
    /**
     * Рисует декоративные элементы фона
     */
    drawBackground() {
        // Добавляем светло-голубые декоративные элементы
        this.ctx.fillStyle = 'rgba(230, 240, 255, 0.5)';
        
        // Банка с медом
        this.ctx.beginPath();
        this.ctx.ellipse(50, 150, 50, 50, 0, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillRect(30, 100, 40, 50);
        
        // Чашка
        this.ctx.beginPath();
        this.ctx.ellipse(50, 650, 50, 25, 0, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.fillRect(0, 600, 100, 50);
        
        // Кривая линия
        this.ctx.beginPath();
        this.ctx.moveTo(this.canvas.width - 100, 200);
        this.ctx.bezierCurveTo(
            this.canvas.width - 50, 300,
            this.canvas.width - 150, 400,
            this.canvas.width - 50, 500
        );
        this.ctx.lineWidth = 3;
        this.ctx.strokeStyle = 'rgba(230, 240, 255, 0.8)';
        this.ctx.stroke();
    }
    
    /**
     * Опускает текущий блин на башню
     * @returns {boolean} - true, если игра окончена, иначе false
     */
    dropPancake() {
        if (this.gameOver || !this.currentPancake || this.isAnimatingDrop) return true;
        
        // Определяем Y-координату для нового блина
        let pancakeY;
        
        if (this.pancakes.length === 0) {
            // Первый блин на тарелке
            pancakeY = this.plateY - this.currentPancake.height;
        } else {
            // Последующие блины на предыдущем
            const prevPancake = this.pancakes[this.pancakes.length - 1];
            pancakeY = prevPancake.y - this.currentPancake.height;
            
            // Проверяем, не выходит ли блин за пределы предыдущего
            const overlap = this.currentPancake.getOverlap(prevPancake);
            
            if (!overlap) {
                // Блины не перекрываются - игра окончена
                this.gameOver = true;
                return true;
            }
            
            // Если блин частично свисает, уменьшаем его ширину
            if (this.currentPancake.x < prevPancake.x || 
                (this.currentPancake.x + this.currentPancake.width) > (prevPancake.x + prevPancake.width)) {
                
                // Вычисляем новую ширину и положение блина
                const newWidth = overlap.width;
                const newX = overlap.left;
                
                // Более агрессивное сужение блина для соответствия фотографиям
                const narrowingFactor = 0.85; // Фактор сужения (85% от перекрытия)
                const adjustedWidth = Math.max(30, newWidth * narrowingFactor);
                const adjustedX = newX + (newWidth - adjustedWidth) / 2;
                
                // Если блин стал слишком узким, игра окончена
                if (adjustedWidth < 30) {
                    this.gameOver = true;
                    return true;
                }
                
                // Обновляем размеры блина
                this.currentPancake.width = adjustedWidth;
                this.currentPancake.x = adjustedX;
                
                // Пересчитываем количество волн
                this.currentPancake.waveCount = Math.max(3, Math.floor(adjustedWidth / 20));
            }
        }
        
        // Начинаем анимацию падения блина
        this.droppingPancake = this.currentPancake;
        this.targetY = pancakeY;
        this.isAnimatingDrop = true;
        this.currentPancake = null;
        
        // Увеличиваем счет
        this.score += 1;
        
        // Проверяем, не достигла ли башня верха экрана
        if (pancakeY < 50) {
            this.gameOver = true;
            return true;
        }
        
        // Проверяем, не достигла ли башня трети экрана
        // Вычисляем верхнюю точку башни с учетом смещения камеры
        const towerTopY = pancakeY;
        
        // Если верхняя точка башни выше трети экрана, смещаем камеру вниз
        if (towerTopY - this.cameraOffsetY < this.thirdScreenHeight) {
            // Вычисляем, насколько нужно сместить камеру
            const additionalOffset = this.thirdScreenHeight - (towerTopY - this.cameraOffsetY);
            this.targetCameraOffsetY += additionalOffset;
            console.log("Смещаем камеру вниз на", additionalOffset, "пикселей");
        }
        
        return false;
    }
    
    /**
     * Начинает новую игру
     */
    restart() {
        // Сбрасываем параметры игры
        this.score = 0;
        this.gameOver = false;
        this.pancakes = [];
        this.cameraOffsetY = 0;
        this.targetCameraOffsetY = 0;
        this.isAnimatingDrop = false;
        this.droppingPancake = null;
        
        // Создаем новый движущийся блин
        this.createMovingPancake();
        
        // Запускаем игровой цикл
        this.startGameLoop();
    }
} 