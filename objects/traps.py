from libs.entity import Trap


class Stair(Trap):
    def __init__(self):
        super().__init__(self.next_map, "", tag="stair")

    def next_map(self, game):
        game.next_map()

    def __str__(self):
        return "S"
