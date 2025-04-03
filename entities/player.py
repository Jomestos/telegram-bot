class Player:
    def __init__(self, nickname: str, balance: int):
        self.nickname = nickname
        self.balance = balance
        self.totalLapBet = 0

    def __eq__(self, other):
        return self.nickname == other.nickname

    def __hash__(self):
        return hash(self.nickname) 
    
    def __str__(self):
        result = f"{self.nickname.capitalize()}\n"
        result += f"{self.balance}💰"
        return result