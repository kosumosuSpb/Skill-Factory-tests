"""
интерфейс для игры в крестики-нолики в терминале

Игроки по очереди вводят координаты,
программа сама определяет условие победы и конца игры.

"""


def print_board():  # выводит актуальное поле
    print(*x_coord)  # координаты по X
    for i in range(3):
        print(i, end=' ')  # координаты по Y
        for j in range(3):
            print(board[i][j], end=' ')
        print()


def move():
    # в начале по умолчанию ходит Х
    global current_player

    # запрос хода с координатами и проверки валидности (можно через декоратор, но так попроще)
    while True:
        # noinspection PyBroadException
        try:
            next_move = input(f'Введите координаты хода для {current_player} через пробел: '
                              f'\nсначала по вертикали, потом по горизонтали \n>>> ')
            x, y = next_move.split()
            x, y = int(x), int(y)
        except Exception:
            print('Неправильный ввод! Попробуйте ещё раз.')
            continue

        if 0 <= x < 3 and 0 <= y < 3:
            if board[x][y] == '-':
                board[x][y] = current_player
                break
            else:
                print('Поле уже занято, выберете другие координаты!')
        else:
            print('Координаты за пределами поля, выберете другие координаты!')


def end_check():
    global endgame

    # проверяем строки
    endgame = any(all(elem == current_player for elem in row) for row in board)

    # проверяем колонки
    if not endgame:
        endgame = any(all(board[j][i] == current_player for j in range(3)) for i in range(3))

    # проверяем диагонали
    #   главная:
    if not endgame:
        endgame = all(board[i][i] == current_player for i in range(3))
    #   побочная
    if not endgame:
        endgame = all(board[i][2 - i] == current_player for i in range(3))
    # если кто-то выиграл, то конец игры
    if endgame:
        print(f'Выиграл игрок {current_player}!')
        print_board()
    # если никто не выиграл, то проверяем, не заполнены ли все поля (что тоже означает конец)
    else:
        endgame = all(all(elem != '-' for elem in row) for row in board)
        if endgame:
            print('Ничья!')
            print_board()


# board:
x_coord = [' ', 0, 1, 2]
# координаты по Y выводятся при выводе доски
board = [['-' for i in range(3)] for j in range(3)]
endgame = False
current_player = 'X'

while not endgame:
    print_board()
    move()
    end_check()
    current_player = 'O' if current_player == 'X' else 'X'  # меняем игрока

print('Конец игры!')
