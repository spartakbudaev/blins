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
        this.canvas.height = container.clientHeight * 0.7;
        
        // Перерисовываем игру после изменения размера
        if (this.pancakes && this.pancakes.length > 0) {
            this.draw();
        }
    }
    
    /**
     * Создает новый движущийся блин
     */
    createMovingPancake() {
        const plateX = (this.canvas.width - this.plateWidth) / 2;
        
        // Определяем ширину нового блина
        let pancakeWidth;
        let pancakeX;
        
        if (this.pancakes.length === 0) {
            // Первый блин - стандартного размера
            pancakeWidth = this.plateWidth - 20;
            pancakeX = plateX + 10;
        } else {
            // Последующие блины случайной ширины
            const lastPancake = this.pancakes[this.pancakes.length - 1];
            const minWidth = Math.max(50, lastPancake.width - 30);
            const maxWidth = Math.min(lastPancake.width + 10, this.plateWidth);
            pancakeWidth = minWidth + Math.random() * (maxWidth - minWidth);
            
            // Случайное начальное положение
            pancakeX = Math.random() * (this.canvas.width - pancakeWidth);
        }
        
        // Высота блина
        const pancakeHeight = 20;
        
        // Цвет блина (случайный из палитры)
        const pancakeColor = this.pancakeColors[Math.floor(Math.random() * this.pancakeColors.length)];
        
        // Создаем блин
        this.currentPancake = new Pancake(
            pancakeX,
            150, // Высота, на которой движется блин
            pancakeWidth,
            pancakeHeight,
            pancakeColor,
            true // Блин движется
        );
        
        // Увеличиваем скорость с ростом счета
        this.currentPancake.speed = 3 + Math.min(this.score / 5, 10);
    }
    
    /**
     * Запускает игровой цикл
     */
    startGameLoop() {
        const gameLoop = (timestamp) => {
            // Вычисляем дельту времени
            const deltaTime = timestamp - this.lastTime;
            this.lastTime = timestamp;
            
            // Обновляем состояние игры
            this.update(deltaTime);
            
            // Отрисовываем игру
            this.draw();
            
            // Продолжаем цикл, если игра не окончена
            if (!this.gameOver) {
                this.animationId = requestAnimationFrame(gameLoop);
            }
        };
        
        this.animationId = requestAnimationFrame(gameLoop);
    }
    
    /**
     * Останавливает игровой цикл
     */
    stopGameLoop() {
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
        if (this.currentPancake) {
            this.currentPancake.update(this.canvas.width);
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
        
        // Рисуем тарелку
        const plateX = (this.canvas.width - this.plateWidth) / 2;
        this.ctx.fillStyle = this.plateColor;
        this.ctx.fillRect(plateX, this.plateY, this.plateWidth, this.plateHeight);
        
        // Рисуем все блины в башне
        for (const pancake of this.pancakes) {
            pancake.draw(this.ctx);
        }
        
        // Рисуем движущийся блин, если игра не окончена
        if (!this.gameOver && this.currentPancake) {
            this.currentPancake.draw(this.ctx);
        }
        
        // Обновляем счет
        document.getElementById('score').textContent = this.score;
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
        if (this.gameOver || !this.currentPancake) return true;
        
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
                
                // Если блин стал слишком узким, игра окончена
                if (newWidth < 30) {
                    this.gameOver = true;
                    return true;
                }
                
                // Обновляем размеры блина
                this.currentPancake.width = newWidth;
                this.currentPancake.x = newX;
                
                // Пересчитываем количество волн
                this.currentPancake.waveCount = Math.max(3, Math.floor(newWidth / 20));
            }
        }
        
        // Останавливаем движение блина и устанавливаем его на башню
        this.currentPancake.isMoving = false;
        this.currentPancake.y = pancakeY;
        
        // Добавляем блин в башню
        this.pancakes.push(this.currentPancake);
        
        // Увеличиваем счет
        this.score += 1;
        
        // Проверяем, не достигла ли башня верха экрана
        if (pancakeY < 50) {
            this.gameOver = true;
            return true;
        }
        
        // Создаем новый движущийся блин
        this.createMovingPancake();
        
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
        
        // Создаем новый движущийся блин
        this.createMovingPancake();
        
        // Запускаем игровой цикл
        this.startGameLoop();
    }
} 