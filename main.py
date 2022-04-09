import random
import sys
import math

import pygame
from pygame.locals import QUIT, KEYDOWN

from libs.map import Map
from libs.entity import Floor, Player, Wall

COMMAND_LIST = [
    "w",
    "a",
    "s",
    "d",
    "v",
    "up",
    "down",
    "right",
    "left",
    "left shift",
    "space",
    "return",
    "escape"
]
MENU_SECTIONS = [
    "skills",
    "items"
]

MAP_SIZE = (50, 50)
VISIBLE_RADIUS = 3
VISION_TILE_SIZE = 50
MINI_MAP_TILE_SIZE = 8

MINI_MAP_POSITION = (25, 25)
STATUS_POSITION = (-50, 50)
MENU_POSITION = (-50, 150)


class Game:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(300, 100)
        self.screen = pygame.display.set_mode((0, 0))
        self.screen.fill((255, 255, 255))

        self.walk_count = 0
        self.menu_index = 0
        self.opening_menu_section = None
        self.player = Player((0,0), "test", "")
        self.map_level = 0
        self.maps = []
        self.is_stopped = False

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
        player_str_list = ["^", ">", "v", "<"]
        player_text = sysfont.render(player_str_list[self.player.direction], True, (0, 0, 0))
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

        floor_render = sysfont.render(f"{self.map_level}F", True, (0, 0, 0))
        status_render = sysfont.render(
            f"HP: {self.player.hp}/{self.player.max_hp}  " + \
            f"Hunger: {self.player.hunger}/{self.player.max_hunger}  " + \
            f"atk: {self.player.attack}  " + \
            f"def: {self.player.defend}",
            True,
            (0, 0, 0)
        )
        status_div_width = status_render.get_size()[0]

        self.screen.blit(floor_render, (
            screen_size[0] - status_div_width + STATUS_POSITION[0],
            STATUS_POSITION[1]
        ))
        self.screen.blit(status_render, (
            screen_size[0] - status_div_width + STATUS_POSITION[0],
            STATUS_POSITION[1] + 25
        ))

    def print_top_menu(self):
        menu_font_size = 30
        sysfont = pygame.font.SysFont(None, menu_font_size)
        screen_size = pygame.display.get_surface().get_size()

        renders = []
        max_width = -1

        for index, menu_section in enumerate(MENU_SECTIONS):
            render_str = menu_section
            if index == self.menu_index:
                render_str += "  <"
            render = sysfont.render(render_str, True, (0, 0, 0))
            if max_width < render.get_size()[0]:
                max_width = render.get_size()[0]
            renders.append(render)

        for index, render in enumerate(renders):
            self.screen.blit(render, (
                screen_size[0] - max_width + MENU_POSITION[0],
                MENU_POSITION[1] + menu_font_size * index
            ))

    def print_items_menu(self):
        screen_size = pygame.display.get_surface().get_size()

        sysfont = pygame.font.SysFont(None, 40)
        render = sysfont.render("items", True, (0, 0, 0))
        self.screen.blit(render, (
            screen_size[0] - render.get_size()[0] + MENU_POSITION[0],
            MENU_POSITION[1]
        ))

        font_size = 25
        sysfont = pygame.font.SysFont(None, font_size)
        renders = []
        max_width = -1
        for index, item_key in enumerate(self.player.items.keys()):
            render_str = f"{item_key} x{self.player.items[item_key][1]}"
            if index == self.menu_index:
                render_str += "  <"
            render = sysfont.render(render_str, True, (0,0,0))
            if max_width < render.get_size()[0]:
                max_width = render.get_size()[0]
            renders.append(render)

        for index, render in enumerate(renders):
            self.screen.blit(render, (
                screen_size[0] - max_width + MENU_POSITION[0],
                MENU_POSITION[1] + (index+1) * font_size
            ))


    def print_menu(self):
        if self.opening_menu_section is None:
            self.print_top_menu()
        elif self.opening_menu_section == "skills":
            pass
        elif self.opening_menu_section == "items":
            self.print_items_menu()


    def print_screen(self):
        # 画面初期化
        self.screen.fill((255, 255, 255))

        # ミニマップ表示
        self.print_mini_map()

        # ステータス表示
        self.print_status()

        # メニュー表示
        self.print_menu()

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
        self.player.get_vision(current_map)

        # 画面更新
        self.print_screen()

    def play_turn(self, key):
        current_map = self.maps[self.map_level-1]
        is_end_turn = False

        old_position = self.player.position
        if key == "w":
            self.player.direction = 0
            if not self.is_stopped:
                if self.player.move(self.player.direction, self):
                    is_end_turn = True
        elif key == "a":
            self.player.direction = 3
            if not self.is_stopped:
                if self.player.move(self.player.direction, self):
                    is_end_turn = True
        elif key == "s":
            self.player.direction = 2
            if not self.is_stopped:
                if self.player.move(self.player.direction, self):
                    is_end_turn = True
        elif key == "d":
            self.player.direction = 1
            if not self.is_stopped:
                if self.player.move(self.player.direction, self):
                    is_end_turn = True
        elif key == "left shift":
            self.is_stopped = not self.is_stopped
        elif key == "v":
            self.player.direction
            is_end_turn = True
        elif key == "up":
            self.menu_index = max(self.menu_index-1, 0)
        elif key == "down":
            limit_index = 0
            if self.opening_menu_section is None:
                limit_index = len(MENU_SECTIONS)-1
            elif self.opening_menu_section == "items":
                limit_index = len(self.player.items.keys())-1
            elif self.opening_menu_section == "skills":
                limit_index = len(self.player.skills)-1
            self.menu_index = min(self.menu_index+1, limit_index)
        elif key == "right":
            if self.opening_menu_section is None:
                self.opening_menu_section = MENU_SECTIONS[self.menu_index]
                self.menu_index = 0
        elif key == "left":
            if self.opening_menu_section is not None:
                self.opening_menu_section = None
        elif key == "return":
            if self.opening_menu_section == "items":
                if len(self.player.items.keys()) <= 0:
                    return
                item_key = list(self.player.items.keys())[self.menu_index]
                is_end_turn = True
                if self.player.use_item(item_key, self):
                    self.menu_index = max(self.menu_index-1, 0)
            elif self.opening_menu_section == "skills":
                if len(self.player.skills) <= 0:
                    return
                is_end_turn = True
        elif key == "escape":
            pygame.quit()
            sys.exit()

        if is_end_turn:
            pass

        # ゲームオーバー
        if self.player.hp <= 0:
            pygame.quit()
            sys.exit()

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
                print(pressed_key)
                if pressed_key not in COMMAND_LIST:
                    continue
                self.play_turn(pressed_key)

            pygame.display.update()



def main():
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
