import random
import sys
import math

import pygame
from pygame.locals import QUIT, KEYDOWN

from libs.map import Map
from libs.entity import Floor, Player, Wall


MAP_SIZE = (50, 50)
VISIBLE_RADIUS = 3
VISION_TILE_SIZE = 50
MINI_MAP_TILE_SIZE = 8

MINI_MAP_POSITION = (25, 25)
STATUS_POSITION = (-400, 50)
MENU_POSITION = (50, 50)


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(300, 100)
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

    def print_mini_map(self):
        current_map = self.maps[self.map_level-1]
        sysfont = pygame.font.SysFont(None, MINI_MAP_TILE_SIZE)
        directions = [
            (0, -1),  # 上
            (1, 0),  # 右
            (0, 1),  # 下
            (-1, 0),  # 左
            (1, -1),  # 右上
            (1, 1),  # 右下
            (-1, 1),  # 左下
            (-1, -1),  # 左上
        ]

        for row in range(len(current_map.data)):
            for col in range(len(current_map.data[0])):
                if row == self.player.position[1] and col == self.player.position[0]:
                    text = "@"
                else:
                    if current_map.visible[row][col]:
                        # 輪郭だけ表示したいので、周りが全て壁だったら表示しない
                        is_inside_wall = True
                        for direction in directions:
                            # out of range防止
                            if row + direction[1] < 0 or \
                            row + direction[1] >= len(current_map.data) or \
                            col + direction[0] < 0 or \
                            col + direction[0] >= len(current_map.data[0]):
                                continue

                            if current_map.data[row + direction[1]][col + direction[0]].__class__.__name__ != Wall.__name__:
                                is_inside_wall = False
                                break

                        text = str(current_map.data[row][col]) if not is_inside_wall else " "
                    else:
                        text = " "

                render = sysfont.render(text, True, (0, 0, 0))
                self.screen.blit(render, (
                    col*MINI_MAP_TILE_SIZE + MINI_MAP_POSITION[0],
                    row*MINI_MAP_TILE_SIZE + MINI_MAP_POSITION[1]
                ))

    def print_status(self):
        sysfont = pygame.font.SysFont(None, 25)
        screen_size = pygame.display.get_surface().get_size()

        render = sysfont.render(f"{self.map_level}F", True, (0, 0, 0))
        self.screen.blit(render, (
            screen_size[0] + STATUS_POSITION[0],
            STATUS_POSITION[1]
        ))

        render = sysfont.render(
            f"HP: {self.player.hp}/{self.player.max_hp}  " + \
            f"Hunger: {self.player.hunger}/{self.player.max_hunger}  " + \
            f"atk: {self.player.attack}  " + \
            f"def: {self.player.defend}",
            True,
            (0, 0, 0)
        )
        self.screen.blit(render, (
            screen_size[0] + STATUS_POSITION[0],
            STATUS_POSITION[1] + 25
        ))

    def print_screen(self):
        # 画面初期化
        self.screen.fill((255, 255, 255))

        # ミニマップ表示
        self.print_mini_map()

        # ステータス表示
        self.print_status()

        # メニュー表示

        # マップ表示
        self.print_vision()

    def next_map(self):
        print("-------------------")
        print("generating map...")
        # マップ生成
        self.maps.append(Map(MAP_SIZE))
        self.map_level += 1
        current_map = self.maps[self.map_level-1]

        # プレイヤー座標ぎめ
        print("computing player position...")
        all_rooms = current_map.root_area.getAllRooms()
        while True:
            room = random.choice(all_rooms)
            self.player.position = (
                room.position[0] + random.randint(0, room.size[0] - 1),
                room.position[1] + random.randint(0, room.size[1] - 1)
            )
            if current_map.data[self.player.position[1]][self.player.position[0]].__class__.__name__ == Floor.__name__:
                break

        print("finished to generate first map")
        print("-------------------\n")

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
