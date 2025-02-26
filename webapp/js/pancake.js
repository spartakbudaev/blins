/**
 * Класс, представляющий блин в игре
 */
class Pancake {
    /**
     * Создает новый блин
     * @param {number} x - Начальная позиция X
     * @param {number} y - Начальная позиция Y
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
        this.direction = Math.random() > 0.5 ? 1 : -1; // 1 - вправо, -1 - влево
        this.speed = 3;
        this.waveHeight = 4; // Высота волн на краях блина
        this.waveCount = Math.max(3, Math.floor(width / 20)); // Количество волн
    }

    /**
     * Обновляет положение блина
     * @param {number} canvasWidth - Ширина игрового поля
     */
    update(canvasWidth) {
        if (!this.isMoving) return;

        // Обновляем позицию блина
        this.x += this.direction * this.speed;

        // Проверяем, не достиг ли блин края экрана
        if (this.x <= 0) {
            this.x = 0;
            this.direction = 1; // Меняем направление на вправо
        } else if (this.x + this.width >= canvasWidth) {
            this.x = canvasWidth - this.width;
            this.direction = -1; // Меняем направление на влево
        }
    }

    /**
     * Отрисовывает блин на канвасе
     * @param {CanvasRenderingContext2D} ctx - Контекст канваса
     */
    draw(ctx) {
        // Основная форма блина
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);

        // Добавляем волнистые края (верхний и нижний)
        for (let i = 0; i <= this.waveCount; i++) {
            const waveX = this.x + (this.width / this.waveCount) * i;

            // Верхняя волна
            if (i % 2 === 0) {
                ctx.fillRect(waveX - 5, this.y - this.waveHeight, 10, this.waveHeight);
            }

            // Нижняя волна
            if (i % 2 === 1) {
                ctx.fillRect(waveX - 5, this.y + this.height, 10, this.waveHeight);
            }
        }
    }

    /**
     * Проверяет, перекрывается ли этот блин с другим
     * @param {Pancake} otherPancake - Другой блин для проверки перекрытия
     * @returns {Object|null} - Информация о перекрытии или null, если перекрытия нет
     */
    getOverlap(otherPancake) {
        const overlapLeft = Math.max(this.x, otherPancake.x);
        const overlapRight = Math.min(this.x + this.width, otherPancake.x + otherPancake.width);

        if (overlapRight <= overlapLeft) {
            // Блины не перекрываются
            return null;
        }

        return {
            left: overlapLeft,
            right: overlapRight,
            width: overlapRight - overlapLeft
        };
    }
} 