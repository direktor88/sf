from random import randint  # добавляем случайные числа


class Point:  # класс точек кораблей , поля... выстрелов
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y  # сверка одного значения с другим

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
    def points(self):  #
        ship_points = []  # точки корабля
        for i in range(self.long):  # проходим по длинне
            cur_x = self.hv.x
            cur_y = self.hv.y

            if self.orient == 0:  # размещаем корабль на поле в зависимости от ориентации
                cur_x += i
            elif self.orient == 1:
                cur_y += i
            ship_points.append(Point(cur_x, cur_y))
        return ship_points

    def damage(self, shot):  # попадания в корабли
        return shot in self.points


class Board:
    def __init__(self, hiden=False, size=6):
        self.size = size  # размер
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
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))  # проверка на попадание в габариты поля

    def contour(self, ship, verb=False):  # обводим по контуру корабля (для проверки можно ли поставить корабль
        # и не только)
        near = [
            (-1, -1), (-1, 0), (-1, 1),  # точки контура вокруг корабля
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.points:  # проверяем точки корабля
            for dx, dy in near:  # шарим вокруг да около...
                cur = Point(d.x + dx, d.y + dy)  # точки занятости
                if not (self.out(cur)) and cur not in self.busy:  # проверка на занятость и выстрелы в молоко
                    if verb:
                        self.map[cur.x][cur.y] = "."  # если мимо ставим точку
                    self.busy.append(cur)  # заполняем поле "занятости"

    def add_ship(self, ship):  # добавить корабль
        for d in ship.points:  # перебор (итерация) точек корабля
            if self.out(d) or d in self.busy:  # если точка за пределами поля или занята - исключение
                raise BoardWrongShipLocationExeption()
        for d in ship.points:  # исключения нет - добавляем на поле корабль из квадратов и в поле "занятости"
            self.map[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)  # добавляем в список коралей "корабль"
        self.contour(ship)  # обрисовываем контур корабля

    def shot(self, d):  # пиу пиу
        if self.out(d):  # проверка на выстрел за пределы поля
            raise BoardOutExeption()
        if d in self.busy:  # проверка на занятую клетку
            raise BoardUsedExeption()
        self.busy.append(d)  # заполняем (дополняем) поле занятости

        for ship in self.ships:  # перебор "корабля" в списке кораблей
            if ship.damage(d):  # если корабль повреждее (есть попадание)
                ship.health -= 1 # вычитаем 1 из уровня здоровья
                self.map[d.x][d.y] = "X" # отмечаем крестиком попадание
                if ship.health == 0: # если полностью подбит корабль
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Потопил")
                    return False
                else:
                    print("попал!") # если только попал
                    return True

        self.map[d.x][d.y] = "." # если не попал
        print("Мимо!!")
        return False

    def begin(self):
        self.busy = []  # поле в начале игры должно быть читсым


class Player:  # класс игрока (может быть как живым так и нет)
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self): # проверка, опрос
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
        d = Point(randint(0, 5), randint(0, 5)) # выстрелы робота в диапазоне от 0 до 5 (случайные числа)
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}') # добавляем 1 в связи с особенностью машинного счета
        return d # возвращаем координаты выстрела


class User(Player):  # обычный игрок
    def ask(self): # действия игрока (выстрелы)
        while True:
            cords = input("Делай ход: введи координаты   ").split()
            if len(cords) != 2:
                print("Нужно две цифры!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Введи только цифры!!")
                continue
            x, y = int(x), int(y)
            return Point(x - 1, y - 1) # убавляем 1 в связи с особенностью машинного счета, отправляем точки выстрела


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
        attempts = 0 # счетчик попыток
        for l in long: # перебор длинн кораблей
            while True:
                attempts += 1
                if attempts > 2000:  # количество попыток расставить корабли
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))  # генерация корабля
                # по трем аргументам - координата первой (начальной) точки, длинна корабля,
                # генерация - ориентации вертикаль или горизонталь
                try: # пробуй добавить корабль на поле
                    board.add_ship(ship)
                    break  # если получилось создать доску с кораблями выходим из попыток
                except BoardWrongShipLocationExeption:
                    pass  # возвращаемся к созданию карты и расставлению кораблей
        board.begin() # по завершению
        return board # вернуть заполненное поле

    def random_map(self): # генерация случайной карты
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
        num = 0  # счетчик ходов
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
                repeat = self.user.move()  # повтор хода
            else:
                print("Ход компьютера")
                repeat = self.comp.move()
            if repeat:
                num -= 1  # если попал - повторяешь попытку
            if self.comp.board.count == 7:  # если счетчик сбитых кораблей "исчерпан"
                print("Выиграл игрок!!!")
                break
            if self.user.board.count == 7:  # если счетчик сбитых кораблей "исчерпан"
                print("Выиграл COMPUTER!!!")
                break
            num += 1  # если промазал - переход хода

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

# g.size = 6
# print(g.random_map())
