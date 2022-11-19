from random import randint


# класс точки (Dot)
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"Dot({self.x}, {self.y})"


# классы исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Нельзя стрелять за границы доски"


class BoardUsedException(BoardException):
    def __str__(self):
        return "В эту клетку уже стреляли"


class BoardWrongShipException(BoardException):
    pass


# класс корабля (ship)
class Ship:
    def __init__(self, bow, len_, dir_):
        self.bow = bow
        self.len_ = len_
        self.dir_ = dir_
        self.live = len_

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.len_):
            start_x = self.bow.x
            start_y = self.bow.y

            if self.dir_ == 0:
                start_x += i
            elif self.dir_ == 1:
                start_y += i
            ship_dots.append(Dot(start_x, start_y))
        return ship_dots

    def shoot(self, shot):
        return shot in self.dots


# класс поля для игрока и компа
class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):
        res = ""
        res += "  1 2 3 4 5 6 "
        for i, row in enumerate(self.field):
            res += f"\n{i + 1}|" + "|".join(row) + "|"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.live -= 1
                self.field[d.x][d.y] = "X"
                if ship.live == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль взорван!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


# класс игрока
class Player:
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
            except BoardException as e:
                print(e)


# классы игрока-человека и игрока-AI
class User(Player):
    def ask(self):
        while True:
            cords = input("Ходите: ").split()
            if len(cords) != 2:
                print("Ошибка - введите 2 координаты")
                continue
            x, y, = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Ошибка - введите числа")
                continue
            x, y, = int(x), int(y)
            return Dot(x - 1, y - 1)


class AI(Player):
    def ask(self):
        a = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера  {a.x + 1} {a.y + 1}")
        return a


# класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True
        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 5000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("Морской бой. v1.0 ")
        print("формат ввода: x, y")
        print("x - номер строки  ")
        print("y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("Доска игрока")
            print(self.user.board)
            print("------------")
            print("Доска компьютера")
            print(self.ai.board)
            if num % 2 == 0:
                print("Ход игрока")
                repeat = self.user.move()
            else:
                print("Ход компьютера")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print(self.user.board)
                print(self.ai.board)
                print("Игрок победил!")
                break
            if self.user.board.count == 7:
                print(self.user.board)
                print(self.ai.board)
                print("Компьютер победил!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


game = Game()
game.start()
