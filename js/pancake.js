/**
 * Класс, представляющий блин в игре
 */
class Pancake {
    /**
     * Создает новый блин
     * @param {number} x - X-координата блина
     * @param {number} y - Y-координата блина
     * @param {number} width - Ширина блина
     * @param {number} height - Высота блина
     * @param {string} color - Цвет блина
     * @param {boolean} isMoving - Флаг, указывающий, движется ли блин
     */
    constructor(x, y, width, height, color, isMoving = false) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.isMoving = isMoving;
        
        // Параметры движения
        this.direction = 1; // 1 - вправо, -1 - влево
        this.speed = 3; // Скорость движения
        
        // Параметры волнистости блина
        this.waveCount = Math.max(3, Math.floor(width / 20)); // Количество волн
        this.waveHeight = 5; // Увеличиваем высоту волны для более выраженной текстуры
        
        // Счетчик для анимации волн
        this.waveOffset = 0;
        
        // Добавляем случайное смещение для разнообразия
        this.randomOffset = Math.random() * 10;
        
        // Флаг, указывающий, что блин уже уложен в башню
        this.isPlaced = false;
        
        // Флаг для отображения блина как круга в начале движения
        this.isCircle = isMoving && width < 50;
    }
    
    /**
     * Обновляет положение блина
     * @param {number} canvasWidth - Ширина канваса
     */
    update(canvasWidth) {
        // Если блин не движется или уже уложен, ничего не делаем
        if (!this.isMoving || this.isPlaced) return;
        
        // Проверяем, что скорость не равна 0
        if (this.speed === 0) {
            this.speed = 3;
            console.log("Скорость блина была 0, установлена на 3");
        }
        
        // Обновляем положение блина
        const oldX = this.x;
        this.x += this.direction * this.speed;
        
        // Проверяем границы канваса
        if (this.x <= 0) {
            this.x = 0;
            this.direction = 1; // Меняем направление на противоположное
            console.log("Блин достиг левой границы, меняем направление на вправо");
        } else if (this.x + this.width >= canvasWidth) {
            this.x = canvasWidth - this.width;
            this.direction = -1; // Меняем направление на противоположное
            console.log("Блин достиг правой границы, меняем направление на влево");
        }
        
        // Проверяем, изменилась ли позиция
        if (oldX === this.x && this.direction !== 0) {
            // Если позиция не изменилась, но направление не нулевое,
            // принудительно меняем направление и немного сдвигаем блин
            this.direction *= -1;
            this.x += this.direction * 5; // Небольшой сдвиг, чтобы выйти из "мертвой зоны"
            console.log("Блин застрял в update, меняем направление на:", this.direction);
        }
        
        // Обновляем смещение волн для анимации
        this.waveOffset += 0.1;
        if (this.waveOffset > Math.PI * 2) {
            this.waveOffset = 0;
        }
        
        // Если блин был круглым и стал достаточно широким, меняем его форму
        if (this.isCircle && this.width >= 50) {
            this.isCircle = false;
        }
    }
    
    /**
     * Отрисовывает блин
     * @param {CanvasRenderingContext2D} ctx - Контекст канваса
     */
    draw(ctx) {
        // Сохраняем текущее состояние контекста
        ctx.save();
        
        // Устанавливаем цвет блина
        ctx.fillStyle = this.color;
        
        // Если блин должен отображаться как круг
        if (this.isCircle) {
            // Рисуем круг
            ctx.beginPath();
            const centerX = this.x + this.width / 2;
            const centerY = this.y + this.height / 2;
            const radius = Math.min(this.width, this.height) / 2;
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.fill();
            
            // Добавляем тень
            ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
            ctx.shadowBlur = 5;
            ctx.shadowOffsetY = 2;
            
            // Восстанавливаем состояние контекста
            ctx.restore();
            return;
        }
        
        // Рисуем основную форму блина (прямоугольник с волнистыми краями)
        ctx.beginPath();
        
        // Верхняя сторона (волнистая)
        const topWaveStep = this.width / this.waveCount;
        ctx.moveTo(this.x, this.y);
        
        for (let i = 0; i <= this.waveCount; i++) {
            const waveX = this.x + i * topWaveStep;
            let waveY;
            
            if (this.isPlaced || !this.isMoving) {
                // Статичная волна для уложенных блинов
                waveY = this.y + Math.sin(i + this.randomOffset) * (this.waveHeight * 0.5);
            } else {
                // Анимированная волна для движущихся блинов
                waveY = this.y + Math.sin(i + this.waveOffset + this.randomOffset) * (this.waveHeight * 0.5);
            }
            
            ctx.lineTo(waveX, waveY);
        }
        
        // Правая сторона (прямая)
        ctx.lineTo(this.x + this.width, this.y + this.height);
        
        // Нижняя сторона (волнистая)
        const bottomWaveStep = this.width / this.waveCount;
        for (let i = this.waveCount; i >= 0; i--) {
            const waveX = this.x + i * bottomWaveStep;
            
            // Для уложенных блинов используем статичную волну
            let waveY;
            if (this.isPlaced || !this.isMoving) {
                // Статичная волна для уложенных блинов
                waveY = this.y + this.height + 
                    Math.sin(i + this.randomOffset) * this.waveHeight;
            } else {
                // Анимированная волна для движущихся блинов
                waveY = this.y + this.height + 
                    Math.sin(i + this.waveOffset + this.randomOffset) * this.waveHeight;
            }
            
            ctx.lineTo(waveX, waveY);
        }
        
        // Левая сторона (прямая)
        ctx.lineTo(this.x, this.y + this.height);
        
        // Замыкаем путь
        ctx.closePath();
        
        // Заливаем блин
        ctx.fill();
        
        // Добавляем тень
        ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
        ctx.shadowBlur = 5;
        ctx.shadowOffsetY = 2;
        
        // Добавляем обводку
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.lineWidth = 1;
        ctx.stroke();
        
        // Добавляем блики
        this.drawHighlights(ctx);
        
        // Восстанавливаем состояние контекста
        ctx.restore();
    }
    
    /**
     * Рисует блики на блине
     * @param {CanvasRenderingContext2D} ctx - Контекст канваса
     */
    drawHighlights(ctx) {
        // Рисуем блики (маленькие белые круги)
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        
        // Первый блик
        ctx.beginPath();
        ctx.arc(
            this.x + this.width * 0.2,
            this.y + this.height * 0.3,
            3,
            0,
            Math.PI * 2
        );
        ctx.fill();
        
        // Второй блик
        ctx.beginPath();
        ctx.arc(
            this.x + this.width * 0.7,
            this.y + this.height * 0.4,
            2,
            0,
            Math.PI * 2
        );
        ctx.fill();
    }
    
    /**
     * Проверяет перекрытие с другим блином
     * @param {Pancake} otherPancake - Другой блин
     * @returns {Object|null} - Объект с информацией о перекрытии или null, если перекрытия нет
     */
    getOverlap(otherPancake) {
        // Проверяем, есть ли перекрытие по горизонтали
        const left = Math.max(this.x, otherPancake.x);
        const right = Math.min(this.x + this.width, otherPancake.x + otherPancake.width);
        
        if (left >= right) {
            // Нет перекрытия
            return null;
        }
        
        // Есть перекрытие, возвращаем информацию о нем
        return {
            left: left,
            right: right,
            width: right - left
        };
    }
} 