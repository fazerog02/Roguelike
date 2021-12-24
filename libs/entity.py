class Entity:
    def __init__(self, img, tag):
        self.tag = tag
        self.img = img

    def __str__(self):
        return "D"


class Floor(Entity):
    def __init__(self, img, tag="floor"):
        super().__init__(img, tag)

    def __str__(self):
        return "."


class Wall(Entity):
    def __init__(self, img, tag="wall"):
        super().__init__(img, tag)

    def __str__(self):
        return "#"


class Trap(Entity):
    def __init__(self, on_stepped_on, img, tag="trap"):
        super().__init__(img, tag)
        self.on_stepped_on = on_stepped_on


class Item(Trap):
    def __init__(self, name, effect, img, tag="item"):
        super().__init__(self.get_item, img, tag)
        self.name = name
        self.effect = effect

    def get_item(self, player):
        player.add_item(self)


class Food(Item):
    def __init__(self, name, hunger, img, extra_effect=None):
        super().__init__(name, self.add_hunger, img)
        self.hunger = hunger
        self.extra_effect = extra_effect

    def add_hunger(self, game):
        game.player.hunger = min(
            game.player.hunger + self.hunger,
            game.player.max_hunger
        )
        if self.extra_effect is not None:
            self.extra_effect(game)


class Player(Entity):
    def __init__(self, position, name, img, tag="player"):
        super().__init__(img, tag)
        self.position = position
        self.name = name
        self.lv = 0
        self.exp = 0
        self.hp = 10
        self.max_hp = 10
        self.attack = 1
        self.defend = 1
        self.hunger = 100
        self.max_hunger = 100
        self.skills = []
        self.items = {}

    def on_lv_up():
        pass

    def on_get_exp(self, got_exp):
        self.exp += got_exp
        if self.exp >= self.lv * 10:
            self.exp -= self.lv * 10
            self.lv += 1
            self.on_lv_up()

    def add_item(self, item):
        if item.name in self.items.keys():
            self.items[item.name][1] += 1
        else:
            self.items[item.name] = [item, 1]

    def __str__(self):
        return "@"
