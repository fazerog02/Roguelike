from libs.entity import Food, Item
from objects.traps import Stair


class WarpMachine(Item):
    def __init__(self):
        super().__init__("warp machine", self.warp_to_stair, "")

    def warp_to_stair(self, game):
        current_map = game.maps[game.map_level-1]
        for row in range(len(current_map.data)):
            for col in range(len(current_map.data[row])):
                if current_map.data[row][col].__class__.__name__ == Stair.__name__:
                    game.player.position = (col, row)
                    game.player.get_vision(current_map)
                    game.print_screen()
                    return

    def __str__(self):
        return "W"


class Meat(Food):
    def __init__(self):
        super().__init__("meat", 0, "", self.max_hunger_heal)

    def max_hunger_heal(self, game):
        game.player.hunger = game.player.max_hunger

    def __str__(self):
        return "M"


class Carrot(Food):
    def __init__(self):
        super().__init__("carrot", 30, "")

    def __str__(self):
        return "C"


ITEMS = [
    WarpMachine,
    Meat,
    Carrot
]
