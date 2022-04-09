DIRECTION_LIST = [
    (0, -1),  # 上
    (1, 0),  # 右
    (0, 1),  # 下
    (-1, 0)  # 左
]
VISIBLE_RADIUS = 3


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


class Creature(Entity):
    def __init__(self, position, direction, name, lv, max_hp, attack, defend, img, skills, items, tag="creature"):
        super().__init__(img, tag)
        self.position = position
        self.direction = direction  # 上:0, 右:1, 下:2, 左:3
        self.name = name
        self.lv = lv
        self.hp = max_hp
        self.max_hp = max_hp
        self.attack = attack
        self.defend = defend
        self.skills = skills
        self.items = items

    def move(self, direction, game, is_player=False):
        map = game.maps[game.map_level-1]

        new_position = (
            self.position[0] + DIRECTION_LIST[direction][0],
            self.position[1] + DIRECTION_LIST[direction][1]
        )

        # マップからはみ出さないようにする
        if new_position[0] < 0 or \
        new_position[1] < 0 or \
        new_position[0] >= map.root_area.size[0] or \
        new_position[1] >= map.root_area.size[1]:
            return False

        # 敵or壁の上には行けない
        stepped_entity = map.data[new_position[1]][new_position[0]]
        if stepped_entity.tag in ["wall", "enemy"]:
            return False

        self.position = new_position

        # トラップor階段だったら関数実行
        if stepped_entity.tag == "trap":
            stepped_entity.on_stepped_on(self)
        elif stepped_entity.tag == "stair" and is_player:
            # 階段だったらここで強制終了
            stepped_entity.on_stepped_on(game)
            return True

        # アイテムだったら拾う
        if stepped_entity.tag == "item":
            stepped_entity.get_item(self)
            map.data[self.position[1]][self.position[0]] = Floor("")

        return True


class Enemy(Creature):
    def __init__(self, position, direction, name, lv, max_hp, attack, defend, skills=[], items={}, tag="creature"):
        super().__init__(position, direction, name, lv, max_hp, attack, defend, "", skills, items, tag)


class Player(Creature):
    def __init__(self, position, name, tag="player"):
        super().__init__(position, 2, name, 0, 10, 1, 1, "", [], {}, tag)
        self.exp = 0
        self.hunger = 100
        self.max_hunger = 100
        self.walk_count = 0

    def move(self, direction, game):
        result = super().move(direction, game, True)

        if result:
            # 空腹度の処理
            self.walk_count += 1
            if self.walk_count % 10 == 0:
                self.hunger = max(self.hunger-1, 0)
            if self.hunger <= 0:
                self.hp -= 1

            self.get_vision(game.maps[game.map_level-1])
        return result

    def get_vision(self, map):
        visible_begin = (
                max(self.position[0]-VISIBLE_RADIUS, 0),
                max(self.position[1]-VISIBLE_RADIUS, 0)
            )
        visible_end = (
            min(self.position[0]+VISIBLE_RADIUS+1, map.root_area.size[0]),
            min(self.position[1]+VISIBLE_RADIUS+1, map.root_area.size[1])
        )
        for row in range(visible_begin[1], visible_end[1]):
            for col in range(visible_begin[0], visible_end[0]):
                map.visible[row][col] = True

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

    def use_item(self, item_key, game):
        self.items[item_key][0].effect(game)
        self.items[item_key][1] -= 1
        if self.items[item_key][1] <= 0:
            del self.items[item_key]
            return True
        return False

    def __str__(self):
        return "@"
