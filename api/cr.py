from typing import Union

State = dict[str, Union[int, list[list[list[int]]]]]

Move = Union[tuple[str, int, int, int, int], tuple[str, int, int, int, int, int, int, int]]


SET_STONE = 'set'
MOVE_STONE = 'move'
REMOVE_STONE = 'remove'

WHITE = 1
BLACK = -1

MOVE_TYPE = 0
MOVE_COLOR = 1
MOVE_X = 2
MOVE_Y = 3
MOVE_Z = 4


def is_end(state: State) -> bool:
    return state['white_remaining'] == 0 and state['black_remaining'] == 0 and (state['white_count'] <= 2 or state['black_count'] <= 2)


def evaluate(state: State) -> int:
    stones = state['stones']
    
    value = 0
    
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][line][spot]
            
            if abs(line_sum) > 1:
                value += line_sum * 10
                
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][spot][line]

            if abs(line_sum) > 1:
                value += line_sum * 10
    
    value += state['white_count'] * 5
    value -= state['black_count'] * 5
    return value


def get_neighboaring_empty_spots(state, x, y, z):
    stones = state['stones']
    
    # left
    if y != 1 and z - 1 >= 0 and stones[x][y][z - 1] == 0:
        yield x, y, z - 1
    
    # right
    if y != 1 and z + 1 <= 2 and stones[x][y][z + 1] == 0:
        yield x, y, z + 1
    
    # up
    if z != 1 and y - 1 >= 0 and stones[x][y - 1][z] == 0:
        yield x, y - 1, z
    
    # down
    if z != 1 and y + 1 <= 2 and stones[x][y + 1][z] == 0:
        yield x, y + 1, z
    
    # cross-square out
    if (y == 1 or z == 1) and x - 1 >= 0 and stones[x - 1][y][z] == 0:
        yield x - 1, y, z
    
    # cross-square in
    if (y == 1 or z == 1) and x + 1 <= 2 and stones[x + 1][y][z] == 0:
        yield x + 1, y, z


def get_moves(state: State, player: int, line_made: bool) -> list[Move]:
    # REMOVE_STATE moves
    if line_made:
        for s, square in enumerate(state['stones']):
            for i, row in enumerate(square):
                for j, element in enumerate(row):
                    if element == player * -1:
                        yield REMOVE_STONE, player, s, i, j
                        
        return
    
    # SET_STONE moves
    if state['white_remaining' if player == WHITE else 'black_remaining'] > 0:
        for s, square in enumerate(state['stones']):
            for i, row in enumerate(square):
                for j, element in enumerate(row):
                    if i == 1 and j == 1:
                        continue
                    if element == 0:
                        yield SET_STONE, player, s, i, j
                    
        return
    
    # MOVE_STONE moves
    for s, square in enumerate(state['stones']):
        for i, row in enumerate(square):
            for j, element in enumerate(row):
                if element == player:
                    for x, y, z in get_neighboaring_empty_spots(state, s, i, j):
                        yield MOVE_STONE, player, x, y, z, s, i, j


def is_making_line(state: State, move: Move) -> bool:
    stones = state['stones']
    _, _, x, y, z, *_ = move
    
    # check if this move makes new horizontal line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[x][y][i]
        
    if abs(stones_sum) == 3:
        return True
    
    # check if this move makes new vertical line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[x][i][z]
        
    if abs(stones_sum) == 3:
        return True
    
    # check if this move makes new cross-sqare top line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[i][0][1]
    
    if abs(stones_sum) == 3:
        return True
    
    # check if this move makes new cross-sqare bottom line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[i][2][1]
        
    if abs(stones_sum) == 3:
        return True
    
    # check if this move makes new cross-sqare left line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[i][1][0]

    if abs(stones_sum) == 3:
        return True

    # check if this move makes new cross-sqare right line
    stones_sum = 0
    for i in range(3):
        stones_sum += stones[i][1][2]

    if abs(stones_sum) == 3:
        return True
    
    return False


def apply_move(state: State, move: Move):
    stones = state['stones']
    if move[MOVE_TYPE] == SET_STONE:
        _, color, x, y, z = move
        stones[x][y][z] = color
        state['white_remaining' if color == WHITE else 'black_remaining'] -= 1
        state['white_count' if color == WHITE else 'black_count'] += 1
    elif move[MOVE_TYPE] == REMOVE_STONE:
        _, color, x, y, z = move
        stones[x][y][z] = 0
        state['white_count' if color == WHITE else 'black_count'] -= 1
    elif move[MOVE_TYPE] == MOVE_STONE:
        _, color, to_x, to_y, to_z, from_x, from_y, from_z = move
        stones[from_x][from_y][from_z] = 0
        stones[to_x][to_y][to_z] = color
        
    state['turn'] += 1


def undo_move(state: State, move: Move):
    stones = state['stones']
    if move[MOVE_TYPE] == SET_STONE:
        _, color, x, y, z = move
        stones[x][y][z] = 0
        state['white_remaining' if color == WHITE else 'black_remaining'] += 1
        state['white_count' if color == WHITE else 'black_count'] -= 1
    elif move[MOVE_TYPE] == REMOVE_STONE:
        _, color, x, y, z = move
        stones[x][y][z] = color * -1
        state['white_count' if color == WHITE else 'black_count'] += 1
    elif move[MOVE_TYPE] == MOVE_STONE:
        _, color, to_x, to_y, to_z, from_x, from_y, from_z = move
        stones[from_x][from_y][from_z] = color
        stones[to_x][to_y][to_z] = 0
    
    state['turn'] += 1


def minimax(state: State, depth: int, player: int, line_made: bool = False) -> tuple[int, Move | None]:
    if depth == 0 or is_end(state):
        return evaluate(state), None

    next_player = player * -1
    value = float('-inf') if player == BLACK else float('inf')  # Postavi inicijalnu vrijednost ovisno o igraču
    best_move = None

    for move in get_moves(state, player, line_made):
        apply_move(state, move)
        new_line_made = line_made or is_making_line(state, move)

        child_value, _ = minimax(state, depth - 1, next_player, new_line_made)
        value = max(value, child_value) if player == WHITE else min(value, child_value)

        print(f'{depth}:{player}:{value=}')
        best_move = move if value == child_value else best_move

        undo_move(state, move)

    return value, best_move

def alphabeta(state: State, depth: int, a: int, b: int, player: int, line_made: bool = False) -> tuple[int, Move | None]:
    if depth == 0 or is_end(state):
        return evaluate(state), None

    next_player = player * -1
    value = float('-inf') if player == BLACK else float('inf')  # Postavi inicijalnu vrijednost ovisno o igraču
    best_move = None

    for move in get_moves(state, player, line_made):
        apply_move(state, move)
        new_line_made = line_made or is_making_line(state, move)

        child_value, _ = alphabeta(state, depth - 1, a, b, next_player, new_line_made)
        value = max(value, child_value) if player == WHITE else min(value, child_value)

        print(f'{depth}:{player}:{value=}')
        best_move = move if value == child_value else best_move

        undo_move(state, move)

        if player == WHITE and value >= b:
            break
        elif player == BLACK and value <= a:
            break

        a = max(a, value) if player == WHITE else a
        b = min(b, value) if player == BLACK else b

    return value, best_move



def element_repr(el: int) -> str:
    return '○' if el == 1 else '●' if el == -1 else '·'


def state_repr(state: State) -> str:
    stones = state['stones']
    board = ''
    board += element_repr(stones[0][0][0]) + '⎯⎯⎯⎯⎯' + element_repr(stones[0][0][1]) + '⎯⎯⎯⎯⎯' + element_repr(stones[0][0][2]) + '\n'
    board += '|     |     |\n'
    board += '| ' + element_repr(stones[1][0][0]) + '⎯⎯⎯' + element_repr(stones[1][0][1]) + '⎯⎯⎯' + element_repr(stones[1][0][2]) + ' |\n'
    board += '| |   |   | |\n'
    board += '| | ' + element_repr(stones[2][0][0]) + '⎯' + element_repr(stones[2][0][1]) + '⎯' + element_repr(stones[2][0][2]) + ' | |\n'
    board += '| | |   | | |\n'
    board += element_repr(stones[0][1][0]) + '⎯' + element_repr(stones[1][1][0]) + '⎯' + element_repr(stones[2][1][0])
    board += '   '
    board += element_repr(stones[2][1][2]) + '⎯' + element_repr(stones[1][1][2]) + '⎯' + element_repr(stones[0][1][2]) + '\n'
    board += '| | |   | | |\n'
    board += '| | ' + element_repr(stones[2][2][0]) + '⎯' + element_repr(stones[2][2][1]) + '⎯' + element_repr(stones[2][2][2]) + ' | |\n'
    board += '| |   |   | |\n'
    board += '| ' + element_repr(stones[1][2][0]) + '⎯⎯⎯' + element_repr(stones[1][2][1]) + '⎯⎯⎯' + element_repr(stones[1][2][2]) + ' |\n'
    board += '|     |     |\n'
    board += element_repr(stones[0][2][0]) + '⎯⎯⎯⎯⎯' + element_repr(stones[0][2][1]) + '⎯⎯⎯⎯⎯' + element_repr(stones[0][2][2]) + '\n'
    return board


start_state: State = {
    'turn': 0,
    'white_remaining': 9,
    'black_remaining': 9,
    'white_count': 0,
    'black_count': 0,
    'line_made': False,
    'stones': [
        # square 0
        [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
        # square 1
        [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
        # square 2
        [[0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]],
    ]
}
def human_vs_computer():
    state = start_state
    while not is_end(state):
        print(state_repr(state))
        player_move = get_human_move(state)
        apply_move(state, player_move)

        if is_end(state):
            print(state_repr(state))
            print("Game over!")
            break

        print(state_repr(state))
        print("Computer's turn...")
        computer_move = get_computer_move(state)
        apply_move(state, computer_move)


def get_human_move(state: State) -> Move:
    while True:
        try:
            move_type = input("Enter move type (set, move, remove): ")
            if move_type not in [SET_STONE, MOVE_STONE, REMOVE_STONE]:
                raise ValueError("Invalid move type. Please enter set, move, or remove.")

            color = WHITE if state['turn'] % 2 == 0 else BLACK
            x, y, z = map(int, input("Enter coordinates (x y z): ").split())

            if move_type == SET_STONE:
                return SET_STONE, color, x, y, z
            elif move_type == REMOVE_STONE:
                return REMOVE_STONE, color, x, y, z
            elif move_type == MOVE_STONE:
                to_x, to_y, to_z = map(int, input("Enter target coordinates (to_x to_y to_z): ").split())
                return MOVE_STONE, color, to_x, to_y, to_z, x, y, z

        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")


def get_computer_move(state: State) -> Move:
    depth = 3  
    _, best_move = alphabeta(state, depth, -1000000, 1000000, WHITE)
    return best_move



# Dodaj ovu funkciju ako želiš omogućiti igraču da izabere da li želi da igra prvi ili drugi
def choose_starting_player():
    while True:
        try:
            choice = input("Do you want to play first? (yes/no): ").lower()
            if choice == "yes":
                return WHITE
            elif choice == "no":
                return BLACK
            else:
                raise ValueError("Invalid choice. Please enter yes or no.")
        except ValueError as e:
            print(f"Invalid input: {e}. Please try again.")


# Dodaj ovu liniju da biraš ko prvi igra
start_state['turn'] = 0 if choose_starting_player() == WHITE else 1

# Pokreni igru
human_vs_computer()
