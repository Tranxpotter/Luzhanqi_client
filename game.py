WAITING = 0
SETTING_UP = 1
PLAYING = 2
END = 4

#Player only states
READY = 3

STATES = {
    0 : "Waiting",
    1 : "Setting up",
    2 : "Playing",
    3 : "Ready"
}

class Game:
    def __init__(self, state:int, players:list[str], player_states:list[int], turn:int, board:list, *args, **kwargs) -> None:
        self.state = state
        self.players = players
        self.player_states = player_states
        self.turn = turn
        self._turn_changed = False
        self.board = board
        self.running = True
        self.restart = False

    def update(self, game_dict:dict):
        self.state = game_dict["state"] if game_dict.get("state") else self.state
        self.players = game_dict["players"] if game_dict.get("players") else self.players
        self.player_states = game_dict["player_states"] if game_dict.get("player_states") else self.player_states
        curr_turn = game_dict["turn"] if game_dict.get("turn") else self.turn
        if self.turn != curr_turn:
            self._turn_changed = True
        self.turn = curr_turn
        self.board = game_dict["board"] if game_dict.get("board") else self.board
    
    def check_turn_changed(self) -> bool:
        if self._turn_changed:
            self._turn_changed = False
            return True
        return False
    


    