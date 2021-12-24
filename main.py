import random
import sys
import math

import pygame
from pygame.locals import QUIT, KEYDOWN

from libs.map import Map
from libs.entity import Floor, Player


MAP_SIZE = (25, 25)
VISIBLE_RADIUS = 3
VISION_TILE_SIZE = 50

MINI_MAP_POSITION = (50, 50)
STATUS_POSITION = (50, 50)
MENU_POSITION = (50, 50)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0))
        self.screen.fill((255, 255, 255))

        self.player = Player((0,0), "test", "")
        self.map_level = 0
        self.maps = []

    def get_vision(self):
        current_map = self.maps[self.map_level-1]

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

    def print_vision(self):
        current_map = self.maps[self.map_level-1]
        sysfont = pygame.font.SysFont(None, VISION_TILE_SIZE)
        screen_size = pygame.display.get_surface().get_size()
        base_position = (
            math.floor(screen_size[0]/2 - VISION_TILE_SIZE*3.5),
            math.floor(screen_size[1]/2 - VISION_TILE_SIZE*3.5)
        )

        # マップGUI描画
        tile_position_offset = [0, 0]
        visible_begin = (
            self.player.position[0]-VISIBLE_RADIUS,
            self.player.position[1]-VISIBLE_RADIUS
        )
        visible_end = (
            self.player.position[0]+VISIBLE_RADIUS+1,
            self.player.position[1]+VISIBLE_RADIUS+1,
        )
        for row in range(visible_begin[1], visible_end[1]):
            for col in range(visible_begin[0], visible_end[0]):
                if row < 0 or \
                row >= current_map.root_area.size[0] or \
                col < 0 or \
                col >= current_map.root_area.size[0]:
                    word = " "
                else:
                    word = str(current_map.data[row][col])

                text = sysfont.render(word, True, (0, 0, 0))
                self.screen.blit(
                    text,
                    (
                        base_position[0] + tile_position_offset[0],
                        base_position[1] + tile_position_offset[1]
                    )
                )
                tile_position_offset[0] += VISION_TILE_SIZE
            tile_position_offset[0] = 0
            tile_position_offset[1] += VISION_TILE_SIZE

        # プレイヤーGUI描画
        player_text = sysfont.render("@", True, (0, 0, 0))
        self.screen.blit(player_text, (
            base_position[0] + VISION_TILE_SIZE*VISIBLE_RADIUS,
            base_position[1] + VISION_TILE_SIZE*VISIBLE_RADIUS
        ))

    def print_screen(self):
        # 画面初期化
        self.screen.fill((255, 255, 255))

        # ミニマップ表示

        # ステータス表示

        # メニュー表示

        # マップ表示
        self.print_vision()

    def next_map(self):
        # マップ生成
        self.maps.append(Map(MAP_SIZE))
        self.map_level += 1
        current_map = self.maps[self.map_level-1]

        # プレイヤー座標ぎめ
        all_rooms = current_map.root_area.getAllRooms()
        while True:
            room = random.choice(all_rooms)
            self.player.position = (
                room.position[0] + random.randint(0, room.size[0] - 1),
                room.position[1] + random.randint(0, room.size[1] - 1)
            )
            if current_map.data[self.player.position[1]][self.player.position[0]].__class__.__name__ == Floor.__name__:
                break

        # 視界確保
        self.get_vision()

        # 画面更新
        self.print_screen()

    def play_turn(self, key):
        current_map = self.maps[self.map_level-1]

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
            pygame.quit()
            sys.exit()

        # マップからはみ出さないようにする
        if next_position[0] < 0 or \
        next_position[1] < 0 or \
        next_position[0] >= current_map.root_area.size[0] or \
        next_position[1] >= current_map.root_area.size[1]:
            return

        # 敵or壁の上には行けない
        stepped_entity = current_map.data[next_position[1]][next_position[0]]
        if stepped_entity.tag in ["wall", "enemy"]:
            return

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
            current_map.data[next_position[1]][next_position[0]] = Floor("")

        # 視界確保
        self.player.position = next_position
        self.get_vision()

        # 画面更新
        self.print_screen()

    def play(self):
        self.next_map()

        while True:
            event = pygame.event.wait()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                pressed_key = pygame.key.name(event.key)
                if pressed_key not in ["w", "a", "s", "d", "e"]:
                    continue
                self.play_turn(pressed_key)

            pygame.display.update()



def main():
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
