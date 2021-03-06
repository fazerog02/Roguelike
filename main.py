import os
import random


WALL_CHAR = "."
ROOM_CHAR = "#"
ROAD_CHAR = "/"


class Area:
    # (x, y)の形式
    MAX_ROOM_SIZE = (15, 15)
    MIN_ROOM_SIZE = (3, 3)
    ROOM_OFFSET = (1, 1)  # 部屋の周りに必ず1マス空くようするため

    def __init__(self, position, size):
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.areas = None
        self.room = None

    def divide(self):
        # 横幅が縦幅以上のときは縦割りを優先する
        if self.size[0] >= self.size[1]:
            # 2分割しても部屋が最小サイズより小さくならないかチェック
            if self.size[0] < (self.MIN_ROOM_SIZE[0] + 2 + 1) * 2:
                return

            # 縦割り
            divide_width = random.randint(
                self.MIN_ROOM_SIZE[0] + self.ROOM_OFFSET[0]*2,
                self.size[0] - self.MIN_ROOM_SIZE[0] - self.ROOM_OFFSET[0]*2 - 1  # -1は境界線を部屋に含めないためのもの
            )
            new_rooms = [
                Area(
                    self.position,
                    (divide_width, self.size[1])
                ),
                Area(
                    (self.position[0] + divide_width + 1, self.position[1]),
                    (self.size[0] - divide_width - 1, self.size[1])
                )
            ]
            self.areas = new_rooms

        # 2分割しても部屋が最小サイズより小さくならないかチェック
        if self.size[1] < (self.MIN_ROOM_SIZE[1] + 2 + 1) * 2:
            return

        # 横割り
        divide_height = random.randint(
            self.MIN_ROOM_SIZE[1] + self.ROOM_OFFSET[1]*2,
            self.size[1] - self.MIN_ROOM_SIZE[1] - self.ROOM_OFFSET[1]*2 - 1  # -1は境界線を部屋に含めないためのもの
        )
        new_rooms = [
            Area(
                self.position,
                (self.size[0], divide_height)
            ),
            Area(
                (self.position[0], self.position[1] + divide_height + 1),
                (self.size[0], self.size[1] - divide_height - 1)
            )
        ]
        self.areas = new_rooms

    def createRoom(self):
        room_size = (
            random.randint(
                self.MIN_ROOM_SIZE[0],
                min(self.size[0] - 2, self.MAX_ROOM_SIZE[0])
            ),
            random.randint(
                self.MIN_ROOM_SIZE[1],
                min(self.size[1] - 2, self.MAX_ROOM_SIZE[1])
            )
        )
        room_position = (
            self.position[0] + random.randint(1, self.size[0] - room_size[0] - 1),
            self.position[1] + random.randint(1, self.size[1] - room_size[1] - 1)
        )
        self.room = Area(room_position, room_size)

    def printRoom(self, map_data):
        for row in range(0, self.size[1]):
            for col in range(0, self.size[0]):
                map_data[self.position[1] + row][self.position[0] + col] = ROOM_CHAR

    def getAllRooms(self):
        rooms = []
        queue = [self]
        while len(queue) > 0:
            new_queue = []
            for area in queue:
                if area.room is not None:
                    rooms.append(area.room)
                if area.areas is not None:
                    new_queue.extend(area.areas)
            queue = new_queue

        return rooms

    def createAllRoads(self, map_data):
        rooms = []
        if self.areas is not None:
            # 子エリアがあれば再帰する
            child_rooms1 = self.areas[0].createAllRoads(map_data)
            child_rooms2 = self.areas[1].createAllRoads(map_data)
        else:
            # 末端エリアだったら自分だけを返して終わり
            rooms.append(self.room)
            return rooms

        if self.size[1] == self.areas[0].size[1]:
            # エリアが縦割りされている場合
            nearest_room_l = None
            nearest_room_r = None
            boarder_x = self.position[0] + self.areas[0].size[0]

            # ボーダーの左側で一番ボーダーに近い部屋を探す
            for room in child_rooms1:
                # 必ずボーダーの左側(ボーダーより小さいx座標)なので、x+widthの大きさが大きい方がボーダーに近い
                if nearest_room_l is None or room.position[0] + room.size[0] > nearest_room_l.position[0] + nearest_room_l.size[0]:
                    nearest_room_l = room

            # ボーダーの右側で一番ボーダーに近い部屋を探す
            for room in child_rooms2:
                # 必ずボーダーの右側(ボーダーより大きいx座標)なので、x+widthの大きさが小さい方がボーダーに近い
                if nearest_room_r is None or room.position[0] + room.size[0] < nearest_room_r.position[0] + nearest_room_r.size[0]:
                    nearest_room_r = room

            # 左側から道を引く
            path_y_l = nearest_room_l.position[1] + random.randint(0, nearest_room_l.size[1]-1)
            for i in range(nearest_room_l.position[0] + nearest_room_l.size[0], boarder_x+1):
                map_data[path_y_l][i] = ROAD_CHAR

            # 右側から道を引く
            path_y_r = nearest_room_r.position[1] + random.randint(0, nearest_room_r.size[1]-1)
            for i in range(boarder_x, nearest_room_r.position[0]):
                map_data[path_y_r][i] = ROAD_CHAR

            # 左右の道をつなげる
            min_path_y = min(path_y_l, path_y_r)
            max_path_y = max(path_y_l, path_y_r)
            for i in range(min_path_y, max_path_y+1):
                map_data[i][boarder_x] = ROAD_CHAR
        else:
            # 横割り
            nearest_room_t = None
            nearest_room_b = None
            boarder_y = self.position[1] + self.areas[0].size[1]

            # ボーダーの上側で一番ボーダーに近い部屋を探す
            for room in child_rooms1:
                # 必ずボーダーの上側(ボーダーより小さいy座標)なので、y+heightの大きさが大きい方がボーダーに近い
                if nearest_room_t is None or room.position[1] + room.size[1] > nearest_room_t.position[1] + nearest_room_t.size[1]:
                    nearest_room_t = room

            # ボーダーの下側で一番ボーダーに近い部屋を探す
            for room in child_rooms2:
                # 必ずボーダーの下側(ボーダーより大きいy座標)なので、y+heightの大きさが小さい方がボーダーに近い
                if nearest_room_b is None or room.position[1] + room.size[1] < nearest_room_b.position[1] + nearest_room_b.size[1]:
                    nearest_room_b = room

            # 上側から道を引く
            path_x_t = nearest_room_t.position[0] + random.randint(0, nearest_room_t.size[0]-1)
            for i in range(nearest_room_t.position[1] + nearest_room_t.size[1], boarder_y+1):
                map_data[i][path_x_t] = ROAD_CHAR

            # 下側から道を引く
            path_x_b = nearest_room_b.position[0] + random.randint(0, nearest_room_b.size[0]-1)
            for i in range(boarder_y, nearest_room_b.position[1]):
                map_data[i][path_x_b] = ROAD_CHAR

            # 上下の道をつなげる
            min_path_x = min(path_x_t, path_x_b)
            max_path_x = max(path_x_t, path_x_b)
            for i in range(min_path_x, max_path_x+1):
                map_data[boarder_y][i] = ROAD_CHAR

        rooms.extend(child_rooms1)
        rooms.extend(child_rooms2)
        return rooms


class Map:
    def __init__(self, size, seed=None):
        self.seed = int.from_bytes(os.urandom(16), byteorder="big") if seed is None else seed
        self.root_area = Area((0, 0), size)  # 2分木でエリア分割を管理する
        self.data = self.generateMap(size, self.seed)

    def generateMap(self, size, seed=None):
        random.seed(seed)
        map_data = [[WALL_CHAR for _j in range(size[0])] for _i in range(size[1])]

        # エリア分割
        now_areas = [self.root_area]
        for _i in range(random.randint(2, 4)):  # 2~4分割->部屋が4~16個生成される
            tmp_areas = []
            for area in now_areas:
                area.divide()
                if area.areas is not None:
                    tmp_areas.extend(area.areas)
                else:
                    # 分割に失敗したら末端エリアとして処理する
                    area.createRoom()
            now_areas = tmp_areas

        # すべての末端エリアに部屋を追加
        for area in now_areas:
            area.createRoom()

        # 部屋を表示
        all_rooms = self.root_area.getAllRooms()
        for room in all_rooms:
            room.printRoom(map_data)

        # 道生成&表示
        self.root_area.createAllRoads(map_data)

        return map_data

    def printMap(self):
        for col in self.data:
            for char in col:
                print(char, end="")
            print()


map = Map((50, 50))
map.printMap()
