from config import bot, removeMarkup
from telebot import types
from entities.player import Player
from entities.game_table import GameTable
from utils import findPlayerByNickname


def _setPlayers(message, gameTable: GameTable):
    bot.send_message(message.chat.id, f"Input players in the next way:\n<i>nickname</i>\n<i>initial balance</i>\n\n<i>Note: send</i> <b>\"stop\"</b> <i>when all players have been added</i>", parse_mode='html', reply_markup=removeMarkup)
    _askForPlayer(message, gameTable)

def _askForPlayer(message, gameTable: GameTable):
    bot.send_message(message.chat.id, f"Set data for player №{len(gameTable.players)+1}")
    bot.register_next_step_handler(message, lambda msg: inputPlayers(msg, gameTable))

def inputPlayers(message, gameTable: GameTable):
    if message.text.strip().lower() == "stop":
        if len(gameTable.players) < 2:
            bot.send_message(message.chat.id, "There must be at least 2 players.", parse_mode='html')
            _askForPlayer(message, gameTable)
            return
        else:    
            printAllPlayers(message, gameTable)
    else:
        try:
            data = message.text.split("\n")
            nickname = data[0].strip().capitalize()
            balance = int(data[1].strip())
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "<b>Invalid format or number.</b> Try again.", parse_mode='html')
            _askForPlayer(message, gameTable)
            return

        player = Player(nickname, balance)
        gameTable.addPlayer(player) 
        _askForPlayer(message, gameTable)

def printAllPlayers(message, gameTable: GameTable):
    markup = types.ReplyKeyboardMarkup()
    btnAddPlayer = types.KeyboardButton("Add players")
    btnRemovePlayer = types.KeyboardButton("Remove players")
    btnEditPlayer = types.KeyboardButton("Edit player's balance")
    btnStartTheGame = types.KeyboardButton("Start the game")
    markup.row(btnAddPlayer, btnRemovePlayer)
    markup.row(btnEditPlayer)
    markup.row(btnStartTheGame)

    bot.send_message(message.chat.id, "Players data:\n" + gameTable.getPrintedPlayers(), reply_markup=markup) 

    from handlers.game_flow import _chooseOption
    bot.register_next_step_handler(message, lambda msg: _chooseOption(msg, gameTable))

def addPlayer(message, gameTable: GameTable): 
    _setPlayers(message, gameTable)

def removePlayer(message, gameTable: GameTable):
    nickname = message.text.strip().lower()
    gameTable.removePlayer(nickname)
    printAllPlayers(message, gameTable)

def editPlayersBalance(message, gameTable: GameTable):
    nickname = message.text.strip().lower()
    player = findPlayerByNickname(message, nickname, gameTable)
    if player is None: 
        bot.register_next_step_handler(message, lambda msg: editPlayersBalance(msg, gameTable))
        return
    
    bot.send_message(message.chat.id, "Enter the new amount of balance")
    bot.register_next_step_handler(message, lambda msg: _editBalance(msg, player, gameTable))

def _editBalance(message, player: Player, gameTable: GameTable):
    if message.text.isnumeric():
        amount = int(message.text)
        player.balance = amount
        printAllPlayers(message, gameTable)
    else: 
        bot.send_message(message.chat.id, "<b>Invalid number for balance.</b> Try again.", parse_mode='html')
        bot.register_next_step_handler(message, lambda msg: _editBalance(msg, player, gameTable))