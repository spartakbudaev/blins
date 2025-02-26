# Как получить токен для Telegram бота

## На русском языке

1. Откройте Telegram и найдите бота [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям BotFather:
   - Введите имя для вашего бота (например, "Блинная башня")
   - Введите уникальное имя пользователя для бота, которое должно заканчиваться на "bot" (например, "pancake_tower_bot")
4. После успешного создания бота, BotFather отправит вам сообщение с токеном бота
5. Скопируйте этот токен и вставьте его в файл `.env`:
   ```
   BOT_TOKEN=ваш_токен_бота
   ```

## Дополнительные настройки (опционально)

1. Чтобы установить аватар для бота, отправьте команду `/setuserpic` BotFather
2. Чтобы изменить описание бота, отправьте команду `/setdescription`
3. Чтобы изменить приветственное сообщение, отправьте команду `/setdescription`

---

# How to get a Telegram bot token

## In English

1. Open Telegram and find [@BotFather](https://t.me/BotFather)
2. Send the command `/newbot`
3. Follow BotFather's instructions:
   - Enter a name for your bot (e.g., "Pancake Tower")
   - Enter a unique username for the bot, which must end with "bot" (e.g., "pancake_tower_bot")
4. After successfully creating the bot, BotFather will send you a message with the bot token
5. Copy this token and paste it into the `.env` file:
   ```
   BOT_TOKEN=your_bot_token
   ```

## Additional settings (optional)

1. To set an avatar for your bot, send the command `/setuserpic` to BotFather
2. To change the bot description, send the command `/setdescription`
3. To change the welcome message, send the command `/setdescription` 