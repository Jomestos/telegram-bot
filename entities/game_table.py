from entities.player import Player
from config import bot

class GameTable:
    def __init__(self, smallBlind: int, bigBlind: int, chatId):
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        self.players: list[Player] = []
        self.playersInGame: list[Player]
        self.chatId = chatId
        self.pot = 0
        self.currentLap = 0
    
    def addPlayer(self, player: Player) -> None:
        if player not in self.players:
            self.players.append(player)

    def getPrintedPlayers(self) -> str:
        if len(self.players) == 0:
            return "There's no players" 

        result = ""
        for player in self.players:
            result += str(player) + "\n\n"
        return result
            
    def removePlayer(self, nickname) -> None:
        player = self.getPlayerByNickname(nickname)
        try:
            self.players.remove(player)
        except Exception:
            return

    def getPlayerByNickname(self, nickname: str) -> Player:
        return next((player for player in self.players if player.nickname == nickname), None)

    def removePlayerFromLap(self, player: Player):
        try:
            self.playersInGame.remove(player)
        except ValueError:
            return
        
    def startNewLap(self):
        self.currentLap += 1

        for player in self.players:
            player.totalLapBet = 0 

        self.resetPlayersInGame()

    def resetPlayersInGame(self):
        self.playersInGame = [player for player in self.players.copy() if player.balance > 0]


    def doBlinds(self, message):
        playersAmount = len(self.playersInGame)
        if playersAmount < 2:
            bot.send_message(self.chatId, f"One player has stayed with balance > 0.\n{self.playersInGame[0].nickname} win!")
            
            from handlers.table_creation import _createTable
            _createTable(message, smallBlind=self.smallBlind, bigBlind=self.bigBlind)
            return


        if self.currentLap >= playersAmount + 1:
            self.currentLap = 1
        self._makeSB(self.getSbPlayer())
        self._makeBB(self.getBbPlayer())

        from handlers.game_flow import makeActionForPlayer
        makeActionForPlayer(message, self, self.getLeftPlayerFromBB())

    def getLeftPlayerFromBB(self) -> Player:
        playerSB = self.getSbPlayer()
        indexSB = self.playersInGame.index(playerSB)
        return self.playersInGame[(indexSB + 2) % len(self.playersInGame)]

    def getBbPlayer(self) -> Player:
        playerSB = self.getSbPlayer()
        indexSB = self.playersInGame.index(playerSB)
        return self.playersInGame[(indexSB + 1) % len(self.playersInGame)]

    def getSbPlayer(self) -> Player:
        if self.currentLap == len(self.playersInGame):
            return self.playersInGame[0]
        return self.playersInGame[self.currentLap]
    
    def _makeSB(self, player: Player):
        self.makeBet(player, self.smallBlind, showMessage=False)
        bot.send_message(self.chatId, f"{player.nickname} bet the <u>SB</u> ({self.smallBlind})\nHis balance now - <b>{player.balance}</b>💰", parse_mode='html')

    def _makeBB(self, player: Player):
        self.makeBet(player, self.bigBlind, showMessage=False)
        bot.send_message(self.chatId, f"{player.nickname} bet the <u>BB</u> ({self.bigBlind})\nHis balance now - <b>{player.balance}</b>💰", parse_mode='html')
    
    def makePass(self, player: Player):
        if len(self.playersInGame) == 1:
            bot.send_message(self.chatId, "Choose the winner, only one player stayed", parse_mode='html')
            return 
        self.removePlayerFromLap(player)
        bot.send_message(self.chatId, f"Player {player.nickname} decided to make pass and lost <b>{player.totalLapBet}</b>💰", parse_mode='html')

    def makeCall(self, player: Player):
        maxBet = max(p.totalLapBet for p in self.players)
        dif = maxBet - player.totalLapBet
        self.makeBet(player, dif)

    def makeBet(self, player: Player, bet: int, showMessage: bool = True):
        if player.balance <= bet:
            bet = player.balance
        
        self.pot += bet
        player.balance -= bet
        player.totalLapBet += bet

        if showMessage:
            bot.send_message(self.chatId, f"Player {player.nickname} made a bet <i>{bet}</i>.\nHis balance now: {player.balance}💰\nPlayer's total lap bet: <b>{player.totalLapBet}</b>\nPot: <b>{self.pot}</b>", parse_mode='html')

