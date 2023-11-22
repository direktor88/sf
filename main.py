from random import randint


class Point:  # класс точек кораблей , поля... выстрелов
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
        self.hv = hv  # первая точка корабля
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

    def damage(self, shot):  # попадания в корабли
        return shot in self.points


class Board:
    def __init__(self, hiden=False, size=6):
        self.size = size
        self.hiden = hiden  # видимость поля

        self.count = 0  # счетчик сбитых кораблей

        self.map = [["0"] * size for _ in range(size)]  # размеры поля

        self.busy = []  # занятые чем либо поля
        self.ships = []  # список кораблей

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"  # рисуем поле (шапка, поля)
        for i, row in enumerate(self.map):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"  # продолжаем рисовать поле
        if self.hiden:
            res = res.replace("■", "o")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
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

    def add_ship(self, ship):
        for d in ship.points:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipLocationExeption()
        for d in ship.points:
            self.map[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):  # пиу пиу
        if self.out(d):
            raise BoardOutExeption()
        if d in self.busy:
            raise BoardUsedExeption()
        self.busy.append(d)

        for ship in self.ships:
            if ship.damage(d):
                ship.health -= 1
                self.map[d.x][d.y] = "X"
                if ship.health == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Потопил")
                    return False
                else:
                    print("попал!")
                    return True

        self.map[d.x][d.y] = "."
        print("Мимо!!")
        return False

    def begin(self):
        self.busy = []  # поле в начале игры должно быть читсым


class Player:  # класс игрока (может быть как живым так и нет)
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardExeption as e:
                print(e)


class AI(Player):  # "робот"
    def ask(self):
        d = Point(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):  # обычный игрок
    def ask(self):
        while True:
            cords = input("Делай ход:   ").split()
            if len(cords) != 2:
                print("Нужно две цифры!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введи только цифры!!")
                continue
            x, y = int(x), int(y)
            return Point(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        user_map = self.random_map()  # карта игрока
        comp_map = self.random_map()  # карта компьютера
        comp_map.hiden = True  # карта компьютера скрыта

        self.comp = AI(comp_map, user_map)
        self.user = User(user_map, comp_map)

    def try_map(self):
        long = [3, 2, 2, 1, 1, 1, 1]  # длинна кораблей
        board = Board(size=self.size)
        attempts = 0
        for l in long:
            while True:
                attempts += 1
                if attempts > 2000:  # количество попыток расставить корабли
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))  # генерация корабля
                # по трем аргументам - координата первой точки, длинна корабля, ориентация вертикаль или горизонталь
                try:
                    board.add_ship(ship)
                    break  # если получилось создать доску с кораблями выходим из попыток
                except BoardWrongShipLocationExeption:
                    pass  # возвращаемся к созданию карты и расставлению кораблей
        board.begin()
        return board

    def random_map(self):
        board = None
        while board is None:
            board = self.try_map()
        return board

    def greet(self):
        print()
        print("Привет")
        print("это игра")
        print("'Морской бой'")
        print()
        print("всё как обычно:")
        print("мир в опасности: 'и восстали машины из пепла ядерного огня'")
        print("для выстрела введи номер строки и столбца")
        print()

    def loop(self):
        num = 0 # счетчик ходов
        while True:
            print("-" * 20)
            print("Поле игрока")
            print(self.user.board)
            print("-" * 20)
            print("Поле противника")
            print(self.comp.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ход игрока")
                repeat = self.user.move() # повтор хода
            else:
                print("Ход компьютера")
                repeat = self.comp.move()
            if repeat:
                num -= 1 # если попал - повторяешь попытку
            if self.comp.board.count == 7:  # если счетчик сбитых кораблей "исчерпан"
                print("Выиграл игрок!!!")
                break
            if self.user.board.count == 7: # если счетчик сбитых кораблей "исчерпан"
                print("Выиграл COMPUTER!!!")
                break
            num += 1 # если промазал - переход хода

    def start(self):
        self.greet()
        self.loop()

g= Game()
g.start()

# g.size = 6
# print(g.random_map())
