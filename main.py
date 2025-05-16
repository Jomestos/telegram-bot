from config import bot
from handlers import table_creation

@bot.message_handler(commands=['create_table'])
def startChatting(message):
    table_creation.getBlinds(message)

if __name__ == "__main__":
    bot.infinity_polling()