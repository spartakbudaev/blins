import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from game import PancakeGame

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store active games
active_games = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в игру 'Блинная башня'!\n\n"
        f"Нажми /play, чтобы начать игру."
    )

async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a new game when the command /play is issued."""
    user_id = update.effective_user.id
    
    # Create a new game for this user
    active_games[user_id] = PancakeGame()
    game = active_games[user_id]
    
    # Generate initial game image
    image_path = await game.generate_game_image()
    
    # Create keyboard with play button
    keyboard = [
        [InlineKeyboardButton("Играть", callback_data="play_game")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send initial game state
    with open(image_path, 'rb') as photo:
        message = await update.message.reply_photo(
            photo=photo,
            caption=f"Счёт: {game.score}",
            reply_markup=reply_markup
        )
    
    # Store message ID for future updates
    game.message_id = message.message_id
    game.chat_id = update.effective_chat.id
    
    # Clean up temporary image
    os.remove(image_path)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "play_game":
        if user_id in active_games:
            game = active_games[user_id]
            
            # Drop a pancake
            game_over = await game.drop_pancake()
            
            # Generate updated game image
            image_path = await game.generate_game_image()
            
            # Update keyboard based on game state
            keyboard = [
                [InlineKeyboardButton("Играть", callback_data="play_game")]
            ]
            
            if game_over:
                keyboard = [
                    [InlineKeyboardButton("Новая игра", callback_data="new_game")]
                ]
                caption = f"Игра окончена! Финальный счёт: {game.score}"
            else:
                caption = f"Счёт: {game.score}"
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Update the message with new game state
            with open(image_path, 'rb') as photo:
                await context.bot.edit_message_media(
                    chat_id=game.chat_id,
                    message_id=game.message_id,
                    media=InputMediaPhoto(
                        media=photo,
                        caption=caption
                    ),
                    reply_markup=reply_markup
                )
            
            # Clean up temporary image
            os.remove(image_path)
    
    elif query.data == "new_game":
        # Start a new game
        active_games[user_id] = PancakeGame()
        game = active_games[user_id]
        
        # Generate initial game image
        image_path = await game.generate_game_image()
        
        # Create keyboard with play button
        keyboard = [
            [InlineKeyboardButton("Играть", callback_data="play_game")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update the message with new game state
        with open(image_path, 'rb') as photo:
            await context.bot.edit_message_media(
                chat_id=update.effective_chat.id,
                message_id=query.message.message_id,
                media=InputMediaPhoto(
                    media=photo,
                    caption=f"Счёт: {game.score}"
                ),
                reply_markup=reply_markup
            )
        
        # Store message ID for future updates
        game.message_id = query.message.message_id
        game.chat_id = update.effective_chat.id
        
        # Clean up temporary image
        os.remove(image_path)

def main() -> None:
    """Start the bot."""
    # Create the Application
    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.error("No BOT_TOKEN found in environment variables!")
        return
    
    # Создаем приложение
    application = Application.builder().token(token).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("play", play_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 