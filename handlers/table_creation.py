from config import bot, removeMarkup
from telebot import types
from entities.game_table import GameTable
from utils import _changeTableSettingsOrInputPlayers




def getBlinds(message):
    _askForSmallBlind(message)

def _askForSmallBlind(message): 
    bot.send_message(message.chat.id, "Input small blind:", reply_markup=removeMarkup)
    bot.register_next_step_handler(message, _setSmallBlind)

def _setSmallBlind(message):
    try:
        smallBlind = int(message.text.strip())        
        _askForBigBlind(message, smallBlind)
    except ValueError:
        bot.send_message(message.chat.id, "<b>Invalid number.</b> Try again.", parse_mode='html')
        _askForSmallBlind(message)

def _askForBigBlind(message, smallBlind: int):
    bot.send_message(message.chat.id, "Input big blind:")
    bot.register_next_step_handler(message, lambda msg: _setBigBlind(msg, smallBlind))

def _setBigBlind(message, smallBlind: int):
    try:
        bigBlind = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "<b>Invalid number.</b> Try again.", parse_mode='html')
        _askForBigBlind(message, smallBlind)
        return
    
    if smallBlind >= bigBlind:
        bot.send_message(message.chat.id, "BB has to be <b>greater</b> than SB", parse_mode='html')
        getBlinds(message)
    else:    
        _createTable(message, smallBlind, bigBlind) 

def _createTable(message, smallBlind: int, bigBlind: int):
    gameTable = GameTable(smallBlind, bigBlind, chatId=message.chat.id)
    bot.send_message(message.chat.id, f"Game table created.\nSB = {smallBlind}\nBB = {bigBlind}", parse_mode='html')
  
    markup = types.ReplyKeyboardMarkup()
    btnChange = types.KeyboardButton("Change table settings")
    btnContinue = types.KeyboardButton("Input players")
    markup.row(btnChange, btnContinue)
    
    bot.send_message(message.chat.id, "Change settings, or continue?", reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: _changeTableSettingsOrInputPlayers(msg, gameTable))