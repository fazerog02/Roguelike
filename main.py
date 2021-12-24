import random
import sys

import readchar

from libs.map import Map
from libs.entity import Player


MAP_SIZE = (25, 25)
VISIBLE_RADIUS = 3


class Game:
    def __init__(self):
        self.player = Player((0,0), "test", "")
        self.map_level = 0
        self.maps = []

    def next_map(self):
        # マップ生成
        self.maps.append(Map(MAP_SIZE))
        self.map_level += 1
        current_map = self.maps[self.map_level-1]

        # プレイヤー座標ぎめ
        all_rooms = current_map.root_area.getAllRooms()
        room = random.choice(all_rooms)
        self.player.position = (
            room.position[0] + random.randint(0, room.size[0] - 1),
            room.position[1] + random.randint(0, room.size[1] - 1)
        )

        # 視界確保
        visible_begin = (
                max(self.player.position[0]-VISIBLE_RADIUS, 0),
                max(self.player.position[1]-VISIBLE_RADIUS, 0)
            )
        visible_end = (
            min(self.player.position[0]+VISIBLE_RADIUS+1, current_map.root_area.size[0]),
            min(self.player.position[1]+VISIBLE_RADIUS+1, current_map.root_area.size[1])
        )
        for row in range(visible_begin[1], visible_end[1]):
            for col in range(visible_begin[0], visible_end[0]):
                current_map.visible[row][col] = True

        # マップ表示
        current_map.printMap(self.player.position)

    def wait_turn(self):
        current_map = self.maps[self.map_level-1]

        while True:
            key = readchar.readchar()
            if key not in ["w", "a", "s", "d", "e"]:
                continue

            next_position = self.player.position
            if key == "w":
                next_position = (
                    next_position[0],
                    next_position[1] - 1
                )
            elif key == "a":
                next_position = (
                    next_position[0] - 1,
                    next_position[1]
                )
            elif key == "s":
                next_position = (
                    next_position[0],
                    next_position[1] + 1
                )
            elif key == "d":
                next_position = (
                    next_position[0] + 1,
                    next_position[1]
                )
            elif key == "e":
                sys.exit()

            # マップからはみ出さないようにする
            if next_position[0] < 0 or \
            next_position[1] < 0 or \
            next_position[0] >= current_map.root_area.size[0] or \
            next_position[1] >= current_map.root_area.size[1]:
                continue

            # 敵or壁の上には行けない
            stepped_entity = current_map.data[next_position[1]][next_position[0]]
            if stepped_entity.tag in ["wall", "enemy"]:
                continue

            # トラップor階段だったら関数実行
            if stepped_entity.tag == "trap":
                stepped_entity.on_stepped_on(self)
            elif stepped_entity.tag == "stair":
                # 階段だったらここで強制終了
                stepped_entity.on_stepped_on(self)
                return

            # アイテムだったら拾う
            if stepped_entity.tag == "item":
                stepped_entity.get_item(self.player)

            # 視界確保
            self.player.position = next_position
            visible_begin = (
                max(self.player.position[0]-VISIBLE_RADIUS, 0),
                max(self.player.position[1]-VISIBLE_RADIUS, 0)
            )
            visible_end = (
                min(self.player.position[0]+VISIBLE_RADIUS+1, current_map.root_area.size[0]),
                min(self.player.position[1]+VISIBLE_RADIUS+1, current_map.root_area.size[1])
            )
            for row in range(visible_begin[1], visible_end[1]):
                for col in range(visible_begin[0], visible_end[0]):
                    current_map.visible[row][col] = True

            break

        # 再描画
        current_map.printMap(self.player.position)


def main():
    game = Game()
    game.next_map()
    while True:
        game.wait_turn()

if __name__ == "__main__":
    main()
