from config import bot
from entities.game_table import GameTable
from entities.player import  Player 

def findPlayerByNickname(message, nickname: str, gameTable: GameTable) -> Player:
    player = gameTable.getPlayerByNickname(nickname)
    if player is None:
        bot.send_message(message.chat.id, f"Player {nickname} is not found. Try again.")
    return player

def _changeTableSettingsOrInputPlayers(message, gameTable):
    if message.text == "Change table settings":
        from handlers.table_creation import getBlinds
        getBlinds(message)
    elif message.text == "Input players":
        from handlers.player_management import _setPlayers
        _setPlayers(message, gameTable)
    else:
        bot.send_message(message.chat.id, "Unknown operation 😢")
        bot.register_next_step_handler(message, lambda msg: _changeTableSettingsOrInputPlayers(msg, gameTable))

        