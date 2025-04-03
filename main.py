from config import bot
from handlers.table_creation import register_handlers

if __name__ == "__main__":
    register_handlers()
    bot.infinity_polling()