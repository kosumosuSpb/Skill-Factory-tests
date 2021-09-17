"""

Игра Морской Бой

Пользователь расставляет корабли (есть возможность это сделать автоматически через рандомайзер)
затем рандомайзер расставляет корабли компьютера.

ИИ стреляет также через рандомайзер, однако был добавлен простой алгоритм
поиска остальной части подбитого корабля. Также ИИ не стреляет в поле вокруг подбитого корабля,
что делает игру с ним более интересной.

"""


from random import randint, choice
from time import sleep


class AddShipException(Exception):
    # класс исключения для ошибки установки кораблей
    pass


# основной класс игры
class Game:
    def __init__(self):
        self.gamer_board = None
        self.computer_board = None

    @staticmethod
    def welcome_message():
        print('Вас приветствует игра "Морской бой"! \n')
        print('Сначала игрок расставляет свои корабли (это можно сделать автоматически), затем \n'
              'генерируется доска компьютера. \n')
        print('Установка кораблей происходит следующим образом: \n'
              'Вводятся координаты носа корабля (сначала по вертикали, потом по горизонтали) \n'
              'через пробел, затем опционально можно указать через пробел его ориентация в пространстве: \n'
              '0 - горизонтально (по-умолчанию), 1 - вертикально \n'
              'сначала будет установлен 3-палубник, потом два 2х, потом 4 одинарных \n')

    @staticmethod
    def farewell_message():
        print('Конец игры')

    # запрос авторасстановки кораблей на доску игрока
    # возвращает True или False
    @staticmethod
    def auto_fill_request():
        while True:
            try:
                read_input = input('Хотите расставить корабли автоматически? \n'
                                   'y/n д/н >>> ')
                return read_input.lower() in ('y', 'д')
            except Exception:
                print('Неверный ввод!')

    # последовательность для ручной расстановки кораблей игрока
    # с возможностью пересоздать доску, если не получилось разместить корабли
    def manual_fill_board(self):
        while True:
            try:
                self.gamer_board = GameBoard()  # создаём доску для игрока
                self.gamer_board.print_board()  # вывод пустой доски пользователя
                self.gamer_board.fill_user_board()  # расстановка кораблей пользователя вручную
                return
            # если пользователь запросил пересоздание доски через ввод, то ловим исключение
            # и начинаем создание и расстановку снова
            except AddShipException:
                print('Пересоздаём доску...')

    # инициализация игрока: запрос на создание доски, расстановка кораблей
    def gamer_init(self):
        if self.auto_fill_request():  # спрашиваем игрока, не хочет ли он автоматически расставить корабли
            for i in range(10):
                try:
                    self.gamer_board = GameBoard()  # создаём доску для компа, передаём в неё объект игры
                    self.gamer_board.fill_random_board()  # генерация случайной расстановки кораблей
                    print('Ваша доска: ')
                    self.gamer_board.print_board()
                    break  # если всё ок и не выпал в исключение, то завершаем цикл
                except AddShipException:  # если выпал в исключение, то снова создаём доску и всё по новой
                    print("Не смогли заполнить доску, попробуем ещё раз")
            else:  # если цикл завершился, это значит, что доска не заполнена
                print("Даже за много попыток не смогли заполнить доску, вот облом. \n"
                      "Расставьте вручную")
                self.manual_fill_board()
        else:
            self.manual_fill_board()  # если хочет сам расставить корабли, то пусть ставит

    # инициализация компа: вызов генерации доски и расстановки кораблей
    def comp_init(self):
        # цикл для создания доски и расстановки кораблей компа
        for i in range(10):
            try:
                self.computer_board = GameBoard(ai=True)  # создаём доску для компа, передаём объект игры
                self.computer_board.fill_random_board()  # генерация случайной расстановки кораблей для компа
                return True  # если всё ок и не выпал в исключение, то выходим из цикла и возвращаем True
            except AddShipException:  # если выпал в исключение, то снова создаём доску и всё по новой
                print("Компьютер не смог заполнить доску, попробуем ещё раз")
        else:  # если цикл завершился, это значит, что доска не заполнена
            print("Даже за много попыток не смогли заполнить доску, вот облом")
            return False  # если не получилось сделать доску, то выходим с False и завершаем игру

    # запуск основного алгоритма ходов игры
    def play(self):
        user = Player(self.computer_board)
        ai = Player(self.gamer_board)
        while True:
            if user.user_move():  # ход игрока и проверки.
                return
            if ai.ai_move():  # выстрел компа и проверки
                return


# класс доски
class GameBoard:
    SHIP_SIZES = (3, 2, 2, 1, 1, 1, 1)  # кортеж для создания корабля нужного размера
    BRD_SIZE = 6  # размер доски

    # конструктор доски
    def __init__(self, ai=False):  # ai = True - если это доска компа
        # начальная доска с пустыми клетками, которым передаёт их координаты и доску, в которой они находятся
        self.board_cells = [[Cell(self, j, i) for i in range(self.BRD_SIZE)] for j in range(self.BRD_SIZE)]
        self.ships = []  # список с кораблями на доске
        self.ai = ai  # маркер доски с ИИ
        self.ai_shipseeker = None  # атрибут для хранения ячеек для поиска остальной части подбитого корабля

    # универсальный вывод одной доски в консоль
    def print_board(self):  # надо будет как то вывести две доски сразу, но потом
        print(' ', *[x_coord for x_coord in range(1, self.BRD_SIZE + 1)], sep=' ')  # координаты по X
        for i in range(self.BRD_SIZE):
            print(i + 1, end=' ')  # координаты по Y
            for j in range(self.BRD_SIZE):
                print(self.board_cells[i][j], end=' ')
            print()

    def fill_user_board(self):  # вызов метода установки кораблей пользователя нужное количество раз
        for _size in self.SHIP_SIZES:
            self.add_ship(_size)  # передаём в метод размер корабля
            self.print_board()  # показываем, что получилось

    def fill_random_board(self):  # вызов метода установки кораблей компа нужное количество раз
        for _size in self.SHIP_SIZES:
            self.add_random_ship(_size)  # передаём в метод размер корабля

    # функция определения занимаемых клеток будущим кораблём
    def ship_pos_cells(self, y, x, size, orientation):
        if orientation == 0:  # если горизонтальный
            return [self.board_cells[y][_x] for _x in range(x, x + size)]
        else:  # если вертикальный (1)
            return [self.board_cells[_y][x] for _y in range(y, y + size)]

    # метод установки корабля на доску вручную. Принимает размер корабля
    def add_ship(self, size):
        while True:
            try:
                read_input = input(f'Введите координаты для установки корабля размера {size} \n'
                                   'и (опционально) его ориентацию в пространстве через пробел. \n'
                                   'Если корабль поставить некуда - введите 0 (ноль) \n'
                                   '>>>').split()
                if len(read_input) == 3:
                    y, x, orientation = read_input
                    y, x, orientation = int(y) - 1, int(x) - 1, int(orientation)
                    # отнимаем единицу, чтобы по внутренним координатам без ошибок ориентировался
                elif len(read_input) == 2:
                    y, x = read_input
                    y, x = int(y) - 1, int(x) - 1
                    # отнимаем единицу, чтобы по внутренним координатам без ошибок ориентировался
                    orientation = 0  # по умолчанию даём горизонтальный корабль

                # даём возможность пересоздать доску
                elif read_input == ['0']:
                    raise AddShipException
                else:  # если что-то не уложилось в эти условия - кидаем исключение
                    raise Exception
            except AddShipException:  # ловим исключение AddShipException и передаём выше
                raise
            except Exception:  # если что-то пошло не так - начинаем по новой
                print('Неправильный ввод!')
                continue

            if x in range(self.BRD_SIZE) and y in range(self.BRD_SIZE) and orientation in (0, 1):  # если ввод верный
                # проверка того, что клетки корабля не выйдут за пределы доски
                if (orientation == 0 and x + size <= self.BRD_SIZE) or (orientation == 1 and y + size <= self.BRD_SIZE):
                    # собираем список клеток, занимаемых новым кораблём
                    _cell_list = self.ship_pos_cells(y, x, size, orientation)
                    if all(_cell.status not in ('AT', 'Alive') for _cell in _cell_list):  # если не занимает занятое, то
                        ship = Ship(y, x, size, self, orientation)  # создаём корабль (и передаём объект доски)
                        self.ships.append(ship)  # добавляем корабль в общий список кораблей на доске
                        break  # выходим из цикла установки корабля
                    else:
                        print('Поле занято!')
                else:
                    print('Корабль выходит за пределы доски!')
            else:
                print('Координаты вне поля или неверный ввод ориентации корабля! \n')

    # установка кораблей на доску через рандомайзер. Также принимает размер корабля
    def add_random_ship(self, size):
        cycle_count = 0
        while cycle_count < 100:  # условие выхода. Если не смог поставить корабль, то надо будет сбросить доску
            # генерируем координаты и ориентацию
            y, x, orientation = randint(0, self.BRD_SIZE - 1), randint(0, self.BRD_SIZE - 1), randint(0, 1)
            # если корабль не будет выходить за пределы доски,
            if (orientation == 0 and x + size <= self.BRD_SIZE) or (orientation == 1 and y + size <= self.BRD_SIZE):
                # список клеток, занимаемых новым кораблём
                _cell_list = self.ship_pos_cells(y, x, size, orientation)
                if all(_cell.status not in ('AT', 'Alive') for _cell in _cell_list):  # если не занимает занятое, то
                    ship = Ship(y, x, size, self, orientation)  # создаём экземпляр корабля
                    self.ships.append(ship)  # добавляем корабль в общий список кораблей на доске
                    return
            cycle_count += 1
        raise AddShipException()


# класс игрока
# при создании объекта класса в него передаётся доска противника
# т.е. при создании игрока ему передаётся доска компа
# а при создании компа - доска игрока
class Player:
    def __init__(self, board):
        self.board = board
        self.ai_shipseeker = None  # атрибут для хранения ячеек для поиска остальной части подбитого корабля

    # выстрел игрока
    # вызываться должен из доски компьютера, чтобы проверки проходили по ней
    def user_move(self):
        print('Что показывает радар: ')
        self.board.print_board()  # вывод доски компа
        while True:
            try:
                shot_coordinates = input('Введите координаты выстрела \n>>>').split()
                y, x = shot_coordinates
                y, x = int(y) - 1, int(x) - 1
            except Exception:
                print('Неправильный ввод!')
                continue
            if x in range(self.board.BRD_SIZE) and y in range(self.board.BRD_SIZE):  # если ввод верный,

                # не получилось вынести в отдельный метод проверок и действий из за различий
                shot_cell = self.board.board_cells[y][x]  # ищем соответствующую клетку
                if shot_cell.status == 'Alive':  # если там живой корабль,
                    shot_cell.status = 'Dead'  # помечаем его клетку, как подбитую

                    # проверки:
                    # жив ли корабль. Если нет, то вывести сообщение, что корабль потоплен
                    if all(_cell.status == 'Dead' for _cell in
                           shot_cell.ship.cells):  # если все клетки корабля мертвы,
                        shot_cell.ship.alive = False  # то сменить статус корабля на мёртв
                        print('Корабль потоплен!')
                    else:
                        print('Корабль подбит!')

                    # есть ли ещё живые корабли на доске? если нет, то конец игры
                    if all(not _ship.alive for _ship in self.board.ships):  # если на доске нет живых кораблей
                        print('Все корабли потоплены!')
                        self.board.print_board()
                        print('Игрок победил!')
                        return True

                    # выводим доску компа. Должна вывестись скрывая корабли, потому что ai = True
                    self.board.print_board()
                elif shot_cell.status == 'Dead' or shot_cell.status == 'Miss':  # если уже стреляли
                    print('Сюда уже стреляли!')
                else:  # если мимо,
                    shot_cell.status = 'Miss'  # помечаем клетку статусом "Мимо"
                    print('Мимо!')
                    self.board.print_board()
                    sleep(1)
                    return False
            else:
                print('Координаты за пределами доски!')

    # выстрел компа.
    # Вызывать из доски игрока, чтобы проверки проходили по ней
    def ai_move(self):
        print('Ход компьютера')
        sleep(1)  # чтобы не мелькало, и было понятно, что происходит
        while True:
            if self.ai_shipseeker:  # если на прошлом этапе был подбит корабль
                # рандом выбирает из 4 направлений где может быть остальная его часть
                shot_cell = choice(self.ai_shipseeker)
                # удаляем выбранную клетку из списка, чтобы снова не использовать
                # кроме того, это предохраняет от бага с тройным кораблём, если попасть ему в середину
                _index = self.ai_shipseeker.index(shot_cell)
                self.ai_shipseeker.pop(_index)
            else:
                # если нет такой инфы, то генерируем новые координаты
                # генерируем координаты для выстрела
                y, x = randint(0, self.board.BRD_SIZE - 1), randint(0, self.board.BRD_SIZE - 1)

                # не получилось вынести в отдельный метод проверок и действий из за различий
                shot_cell = self.board.board_cells[y][x]  # ищем соответствующую клетку

            # если там живой корабль,
            if shot_cell.status == 'Alive':
                shot_cell.status = 'Dead'  # помечаем его клетку, как подбитую

                # проверки:
                # жив ли корабль.
                if all(_cell.status == 'Dead' for _cell in shot_cell.ship.cells):  # если все клетки корабля мертвы,
                    shot_cell.ship.alive = False  # то сменить статус корабля на мёртв

                    for _cell in shot_cell.ship.at_field:  # пробегаем по влиянию убитого корабля
                        if _cell.status not in ('Miss', 'Dead'):  # если туда ещё не стреляли и нет корабля
                            _cell.status = 'DeadField'  # помечаем их, как поле корабля, куда нет смысла стрелять

                    print('Корабль игрока потоплен!')
                    self.ai_shipseeker = None  # сбросим ячейки поиска остатков корабля
                else:
                    print('Корабль игрока подбит!')
                    # если подбил, то ищем где остальные клетки корабля относительно последнего удачного выстрела
                    self.ai_shipseeker = self.ai_ship_finder(shot_cell)

                # есть ли ещё живые корабли на доске? если нет, то конец игры
                if all(not _ship.alive for _ship in self.board.ships):  # если на доске нет живых кораблей
                    print('Все корабли игрока потоплены!')
                    self.board.print_board()
                    print('Компьютер победил!')
                    return True

                # выводим доску пользователя.
                self.board.print_board()
                print('Наводка на новую цель...')
                sleep(2)  # Чтобы игрок что-то успел увидеть в процессе действий компа
                continue  # чтобы не проверял остальные условия, раз уж попал и отметил, что попал

            # если в эту клетку уже стреляли
            elif shot_cell.status == 'Dead' or shot_cell.status == 'Miss' or shot_cell.status == 'DeadField':
                continue  # просто молча запускаем цикл снова

            # если мимо
            else:
                shot_cell.status = 'Miss'  # помечаем клетку статусом "Мимо"
                print('Компьютер промазал!')
                self.board.print_board()
                return False

    # метод ИИ для поиска части подбитого корабля
    # выдаст список ячеек для выстрела.
    def ai_ship_finder(self, shot_cell):
        y, x = shot_cell.y - 1, shot_cell.x - 1
        # формируем список из ячеек, по которым будем искать остальную часть корабля
        # сразу убираем те, которые выходят за пределы доски
        return [self.board.board_cells[y + i][x + j]
                for j in range(3)
                for i in range(3)
                if abs(i - j) == 1
                and 0 <= y + i < self.board.BRD_SIZE
                and 0 <= x + j < self.board.BRD_SIZE]


# класс клетки
class Cell:
    # словарь для вывода клетки на доску в зависимости от состояния клетки
    print_status = {None: '•',          # пусто
                    'Alive': '□',       # клетка корабля
                    'Dead': '■',        # мёртвая клетка корабля
                    'AT': '•',          # поле влияния корабля
                    'DeadField': '•',   # поле влияния корабля, которое нашёл ИИ
                    'Miss': 'x'}        # промазал

    # дикт для вывода доски компа для пользователя
    enemy_status = {None: '•',
                    'Alive': '•',
                    'Dead': '■',
                    'AT': '•',
                    'DeadField': '•',
                    'Miss': 'x'}

    def __init__(self, board, y, x):
        self.board = board
        self.y = y
        self.x = x
        self.status = None  # состояние клетки: None, Alive, Dead, AT (поле вокруг корабля), Miss.
        self.ship = None  # тут ссылка на корабль, который стоит на этой клетке

    def __str__(self):  # определяем то, как клетка будет выводиться в консоль
        if self.board.ai:  # если это доска компа, то выводим не всё
            return self.enemy_status[self.status]
        else:  # если это своя доска - то выводим всё
            return self.print_status[self.status]


# класс корабля
# передаём координаты, размер, ориентацию и доску, на которой он стоит,
# чтобы иметь доступ к её клеткам
class Ship:
    def __init__(self, y, x, size, board, orientation=0):
        self.y = y
        self.x = x
        self.size = size
        self.orientation = orientation
        self.board = board
        self.alive = True
        self.cells = self.ship_himself()  # клетки, которые занимает корабль
        self.at_field = self.make_at_field()  # поле вокруг корабля
        for _cell in self.cells:  # пробегаем по клеткам корабля
            _cell.status = 'Alive'  # помечаем их, как занятые и живые
            _cell.ship = self  # передаём в них инфу о корабле (в сущности, сам корабль)
        for _cell in self.at_field:  # пробегаем по влиянию корабля
            if not _cell.status:  # если там не стоит корабль, то
                _cell.status = 'AT'  # помечаем их, как AT-поле корабля (куда нельзя ничего ставить)

    # ship метод, возвращающий клетки, которые занимает корабль
    def ship_himself(self):
        if self.orientation == 0:  # если горизонтальный
            return [self.board.board_cells[self.y][_x] for _x in range(self.x, self.x + self.size)]
        else:  # если вертикальный (1)
            return [self.board.board_cells[_y][self.x] for _y in range(self.y, self.y + self.size)]

    # at-field метод, вычисляющий занятое кораблём пространство (включая поле вокруг него)
    def make_at_field(self):
        # сначала формируем список кортежей координат, подходящих под поле вокруг корабля
        if self.orientation == 0:  # если горизонтальный
            coords = [
                (self.y + i - 1, self.x - 1 + j)
                for j in range(self.size + 2)
                for i in range(3)
            ]
        else:  # если вертикальный
            coords = [
                (self.y + i - 1, self.x - 1 + j)
                for j in range(3)
                for i in range(self.size + 2)
            ]
        # фильтруем результат:
        # убираем из списка координаты, которые за пределами доски
        # возвращаем список клеток, которые будут составлять поле корабля
        return [
            self.board.board_cells[y][x]
            for y, x in coords
            if 0 <= y < self.board.BRD_SIZE
            and 0 <= x < self.board.BRD_SIZE]


# основной алгоритм игры
def main():
    game = Game()  # давай сыграем с тобой в игру
    game.welcome_message()  # приветственное сообщение
    game.gamer_init()  # инициализация игрока (доски и кораблей)
    if game.comp_init():  # инициализация компа (доски и кораблей)
        game.play()  # если комп справился с расстановкой - начинаем игру
    game.farewell_message()  # сообщение о конце игры


# запуск игры
main()
