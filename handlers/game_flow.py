from telebot import types
from entities.game_table import GameTable
from entities.player import Player
from utils import findPlayerByNickname
from config import bot, removeMarkup

def _chooseOption(message, gameTable: GameTable): 
    from handlers.player_management import editPlayersBalance
    from handlers.player_management import removePlayer
    from handlers.player_management import addPlayer

    match message.text:
        case "Add players":
            addPlayer(message, gameTable)
        case "Remove players":
            bot.send_message(message.chat.id, "Input player's nickname", reply_markup=removeMarkup)
            bot.register_next_step_handler(message, lambda msg: removePlayer(msg, gameTable))
        case "Edit player's balance":
            bot.send_message(message.chat.id, "Input player's nickname", reply_markup=removeMarkup)
            bot.register_next_step_handler(message, lambda msg: editPlayersBalance(msg, gameTable))
        case "Start the game":
            bot.send_message(message.chat.id, "<i>Note: if you want to bet another amount of 💰, you can write it manually</i> \nWhen preflop is over, press the appropriate button for the correct order of moves.", parse_mode='html', reply_markup=removeMarkup)
            startTheGame(message, gameTable)
        case _:
            bot.send_message(message.chat.id, "Unknown operation 😢")
            bot.register_next_step_handler(message, lambda msg: _chooseOption(msg, gameTable))

def startTheGame(message, gameTable: GameTable):
    gameTable.startNewLap()
    bot.send_message(message.chat.id, f"======Lap №{gameTable.currentLap} started======")
    bot.send_message(message.chat.id, "Players data:\n" + gameTable.getPrintedPlayers())
    gameTable.doBlinds(message)
    

def _getMarkupForGame(bigBlind: int) -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup()
    btnPass = types.KeyboardButton("Pass")
    btnCheck = types.KeyboardButton("Check")
    btnCall = types.KeyboardButton("Call")
    btnBetOneBB = types.KeyboardButton(f"1 BB ({bigBlind})")
    btnBetTwoBB = types.KeyboardButton(f"2 BB ({bigBlind*2})")
    btnBetThreeBB = types.KeyboardButton(f"3 BB ({bigBlind*3})")
    btnAllIn = types.KeyboardButton("All in")
    btnWinner = types.KeyboardButton("Give pot to this player")
    btnSplitPot = types.KeyboardButton("Split pot between players")
    btnEditUsers = types.KeyboardButton("Edit users")
    btnStartFLop = types.KeyboardButton("Preflop is ended")
    btnQuitGame = types.KeyboardButton("End the game")

    markup.row(btnPass, btnCheck, btnCall)
    markup.row(btnBetOneBB, btnBetTwoBB, btnBetThreeBB)
    markup.row(btnAllIn)
    markup.row(btnWinner, btnSplitPot)
    markup.row(btnEditUsers, btnStartFLop)
    markup.row(btnQuitGame)
    return markup

def makeActionForPlayer(message, gameTable: GameTable, player: Player):
    bot.send_message(message.chat.id, f"Action for player <b>{player.nickname}</b> with balance <b>{player.balance}</b>💰", parse_mode='html', reply_markup=_getMarkupForGame(gameTable.bigBlind))
    bot.register_next_step_handler(message, lambda msg: _handlePlayersAction(msg, player, gameTable))

def _handlePlayersAction(message, player: Player, gameTable: GameTable):
    isOperationExist = False
    nextPlayer = _getNextPlayer(gameTable, player)

    if message.text.strip().isnumeric():
        gameTable.makeBet(player, int(message.text.strip()))
        isOperationExist = True

    prefix = message.text[:4]
    if not isOperationExist and prefix in ["1 BB", "2 BB", "3 BB"]:
        gameTable.makeBet(player, int(message.text[6:-1].strip()))
        isOperationExist = True

    match message.text:
        case "Pass": 
            gameTable.makePass(player)
        case "Check":
            gameTable.makeBet(player, 0)
        case "Call":
            gameTable.makeCall(player)
        case "All in":
            gameTable.makeBet(player, player.balance)
        case "Give pot to this player":
            _setTheWinner(message, player, gameTable)
            startTheGame(message, gameTable)
            return
        case "Split pot between players":
            splitThePotAction(message, gameTable)
            return
        case "Edit users":
            editPlayersAction(message, player, gameTable)
            return 
        case "Preflop is ended":
            makeActionForPlayer(message, gameTable, gameTable.getSbPlayer())
            return
        case "End the game":
            from main import startChatting
            bot.send_message(message.chat.id, "Game was ended!\nThanks for playing😊")
            startChatting(message)
            return
        case _:
            if not isOperationExist:
                bot.send_message(message.chat.id, "Unknown operation, or invalid number 😢\nTry one more time.")
                bot.register_next_step_handler(message, lambda msg: _handlePlayersAction(msg, player, gameTable))
                return
    
    makeActionForPlayer(message, gameTable, nextPlayer)


def _setTheWinner(message, player: Player, gameTable: GameTable):
    player.balance += gameTable.pot
    gameTable.pot = 0
    bot.send_message(message.chat.id, f"Player {player.nickname} wins, and now his bank <b>{player.balance}</b>💰", parse_mode='html')


def _getNextPlayer(gameTable: GameTable, player) -> Player:
    index = gameTable.playersInGame.index(player)
    return gameTable.playersInGame[(index + 1) % len(gameTable.playersInGame)]

def splitThePotAction(message, gameTable: GameTable):
    bot.send_message(message.chat.id, "Write the players' names between whom the pot will be divided\n<i>e.g. \"User1, User2, ...\".</i>", parse_mode='html')
    bot.register_next_step_handler(message, lambda msg: _makeSplitPot(msg, gameTable))

def _makeSplitPot(message, gameTable: GameTable):
    winners = message.text.strip().lower().split(", ")
    if len(winners) < 2:
        bot.send_message(message.chat.id, "There must be at least 2 winners\nAlso usernames have to be entered in the next way: <i>\"User1, User2, ...\".</i>", parse_mode='html')
        bot.register_next_step_handler(message, lambda msg: _makeSplitPot(msg, gameTable))
        return

    prize = gameTable.pot // len(winners)
    players = []

    for winner in winners:
        pl = findPlayerByNickname(message, winner, gameTable)
        if pl is None:
            bot.register_next_step_handler(message, lambda msg: _makeSplitPot(msg, gameTable))
            return
        players.append(pl) 
    
    for player in players:
        player.balance += prize
        bot.send_message(message.chat.id, f"Player {player.nickname} wins, and now his bank <b>{player.balance}</b>💰", parse_mode='html')
        
    startTheGame(message, gameTable)

def editPlayersAction(message, player: Player, gameTable: GameTable): 
    markup = types.ReplyKeyboardMarkup()
    btnYes = types.KeyboardButton("Yes")
    btnNo = types.KeyboardButton("No")
    markup.row(btnYes, btnNo)
    bot.send_message(message.chat.id, "Note: if you want to change users data, this <b>lap will start again</b>.\nAre you sure you want to change the data?", parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(message, lambda msg: _editBalanceInGame(msg, player, gameTable))

def _editBalanceInGame(message, player: Player, gameTable: GameTable):
    if message.text == "Yes":
        gameTable.currentLap -= 1
        _resetBets(gameTable)
        from handlers.player_management import printAllPlayers
        printAllPlayers(message, gameTable)
    elif message.text == "No":
        makeActionForPlayer(message, gameTable, player)
    else: 
        bot.send_message(message.chat.id, "Unknown operation 😢\nTry one more time.")
        bot.register_next_step_handler(message, lambda msg: _handlePlayersAction(msg, player, gameTable))

def _resetBets(gameTable: GameTable):
    for player in gameTable.players:
        player.balance += player.totalLapBet
        player.totalLapBet = 0
    gameTable.pot = 0