WAITING = 0
SETTING_UP = 1
PLAYING = 2

#Player only states
READY = 3

class Game:
    def __init__(self, state:int, players:list[str], turn:int, board:list, *args, **kwargs) -> None:
        self.state = state
        self.players = players
        self.turn = turn
        self.board = board

    def update(self, game_dict:dict):
        self.state = game_dict["state"] if game_dict.get("state") else self.state
        self.players = game_dict["players"] if game_dict.get("players") else self.players
        self.turn = game_dict["turn"] if game_dict.get("turn") else self.turn
        self.board = game_dict["board"] if game_dict.get("board") else self.board
    
    


    