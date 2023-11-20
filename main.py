class Point: # класс точек кораблей , поля... выстрелов
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Point({self.x}, {self.y}"


class BoardExeption(Exception):
    pass


class BoardOutExeption(BoardExeption):  # выстрел за пределы доски
    def __str__(self):
        return "Летит в молоко, целься лучше!"


class BoardUsedExeption(BoardExeption):  # повторный выстрел в точку куда уже стрелял
    def __str__(self):
        return "Уже стрелял сюда!"


class BoardWrongShipLocationExeption(BoardExeption):  # неверное размещение корабля
    pass


class Ship:
    def __init__(self, hv, long, orient):  # координаты носа и палубы, длинна, ориентация
        self.hv = hv
        self.long = long
        self.orient = orient
        self.health = 1

    @property
    def points(self):
        ship_points = []
        for i in range(self.long):
            cur_x = self.hv.x
            cur_y = self.hv.y

            if self.orient == 0:
                cur_x += i
            elif self.orient == 1:
                cur_y += i
            ship_points.append(Point(cur_x, cur_y))
        return ship_points

    def damage(self, shot): # попадания в корабли
        return shot in self.points


class Board:
    def __init__(self, hiden=False, size=6):
        self.size = size
        self.hiden = hiden # видимость поля

        self.count = 0 # счетчик сбитых кораблей

        self.map = [["0"] * size for _ in range(size)] # размеры поля

        self.busy = [] # занятые чем либо поля
        self.ships = [] # список кораблей

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |" # рисуем поле (шапка, поля)
        for i, row in enumerate(self.map):
            res += f"\n{i+1} | " + " | ".join(row) + " |" # продолжаем рисовать поле
        if self.hiden:
            res = res.replace("■", "o")
        return res

    def out(self, d):
        return not ((0<=d.x < self.size) and (0<= d.y < self.size))

    def contour (self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.points:
            for dx, dy in near:
                cur = Point(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.map[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship (self, ship):
        for d in ship.points:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipLocationExeption()