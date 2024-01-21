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


def is_end(state):
    return state['white_remaining'] == 0 and state['black_remaining'] == 0 and (state['white_count'] <= 2 or state['black_count'] <= 2)


def custom_easy_evaluate(state):
    stones = state['stones'] #predstavlja matricu trnutnog rasporeda kamena na tabli
    value = 0 #ukupnu vrednost heuristike za trenutno stanje igre

    # Weights for the heuristic components
    stone_weight = 5 #broj kamena
    potential_mill_weight = 3 #tizina mlinova
    mill_weight = 10 #kada se racuna vrednost postignutih mlinova, kada se u nekoj liniji nalze sva tri kamena
    mobility_weight = 2 #ova brednost (2) se koristi kao faktoe prilikom racunanja vrednosti na ossnovu slobodnih polja na tabli
    line_weight = 5 #tezina za linije sa tri kamena iste boje

    # Count the number of stones
    value += state['white_count'] * stone_weight #ovde se dodaje vrednost state['white_count'] trenutnoj vrednosti. ovo state predstavlja tezinu koja se pridruzuje svakom belom kamenu
    value -= state['black_count'] * stone_weight #ova linija oduzima vrednost state)black_coutn

    # Count the potential mills
    for square in range(3):#prolazimo kroz sva tri kvadrata
        for line in [0, 2]: #unutrasnja petlja se pokrece za svaki kvadrat i iteretira kroz odabrane linije u tom kvadratu
            line_sum = sum(stones[square][line]) #racuna se suma vrednosti kamenja u tenutnoj liniji kvadrata. 
            if abs(line_sum) == 2 and 0 in stones[square][line]: #proveravmo da li je apsolutna vrednost line_sum jednaka 2, sto znacci da ima tacno dva kamena u toj liniji i da li u toj liniji posstoji prazno mesto vrednosti 0
                value += potential_mill_weight if line_sum > 0 else -potential_mill_weight #ako su oba uslova zadovoljena to znaci da je ova linija potencijalni mlin. U tom 
                #slucaju dodaje se odgovrajuca tezina. Ako je suma pozitivna dodaje se tezina, ako je negativna oduzima se tezina. Ovo se uzima u obzir koja  je boja kamenja koja ce formirati potencijalni miln

    # odnosi se na prepoznavanje i ocenjivanje mliona na tabli igre
    for square in range(3): 
        for line in [0, 2]: #unutrasnja petlja se pokrece za svaki kvadrat i iteretira kroz odabrane linije u tom kvadratu
            line_sum = sum(stones[square][line]) #racuna se suma vrednosti kamenja u tenutnoj liniji kvadrata. 
            if abs(line_sum) == 3:  #ova linija proverava  da li je apsolutna vrednost jednaka 3, sto znaci da postoje tacno tri kamena
                value += mill_weight if line_sum > 0 else -mill_weight #ako je prethodni uslov zadovoljen to znaci da posotoji mlin

   
    value += stones.count(0) * mobility_weight #dodaje vrrednost vrednosti heuristike u skladu sa brojem praznih polja na tabli.
    value -= stones.count(1) * mobility_weight

    # Count the lines
    for square in range(3):
        for line in [0, 1, 2]: #unutrasnja petlja se pokrece za svaki kvadrat i iteretira korz sve tri linije u tom kvadratu
            line_sum = sum(stones[square][line]) #ova linija racuna sumu
            if abs(line_sum) == 3:
                value += line_weight if line_sum > 0 else -line_weight

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


def get_moves(state, player, line_made):
    # REMOVE_STONE moves
    if line_made:
        for s, square in enumerate(state['stones']):
            for i, row in enumerate(square):
                for j, element in enumerate(row):
                    # move = (REMOVE_STONE, player * -1, s, i, j)
                    # if element == player * -1 and not is_making_line(state, move):
                    #     yield move
                    if element == player * -1:
                        yield REMOVE_STONE, player, s, i, j
        return
    
    # SET_STONE moves
    if state['white_remaining' if player == 1 else 'black_remaining'] > 0:
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


def is_making_line(state, move):
    stones = state['stones']
    _, _, x, y, z, *_ = move
    
    # Provera horizontalne linije
    if abs(sum(stones[x][y])) == 3:
        return True
    
    # Provera vertikalne linije
    if abs(sum(stones[x][i][z] for i in range(3))) == 3:
        return True
    
    # Provera dijagonalne linije
    if x == 1 and y == 1 and z == 1:
        if abs(sum(stones[i][1][1] for i in range(3))) == 3:
            return True
    
    # Provera dijagonalne linije koja prolazi kroz sredinu tabele
    if abs(sum(stones[i][1][1] for i in range(3))) == 3:
        return True
    if abs(sum(stones[1][i][1] for i in range(3))) == 3:
        return True
    if abs(sum(stones[1][1][i] for i in range(3))) == 3:
        return True

    # Provera horizontalnih, vertikalnih i dijagonalnih linija za sve x, y, z
    for i in range(3):
        # Provera horizontalne linije za sve x
        if abs(sum(stones[i][y])) == 3:
            return True
        # Provera vertikalne linije za sve z
        if abs(sum(stones[x][j][z] for j in range(3))) == 3:
            return True

        # Provera dijagonalne linije za x, y, z
        if abs(sum(stones[j][i][j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[j][i][2 - j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[j][y][j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[x][j][j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[j][1][z] for j in range(3))) == 3:
            return True
        if abs(sum(stones[x][1][j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[1][y][j] for j in range(3))) == 3:
            return True
        if abs(sum(stones[j][y][2 - j] for j in range(3))) == 3:
            return True

    # Provera linija koje prolaze kroz susedne kvadrate
    if y == 0 or y == 2:
        if abs(sum(stones[x][0][1] for x in range(3))) == 3:
            return True
        if abs(sum(stones[x][2][1] for x in range(3))) == 3:
            return True
    if z == 0 or z == 2:
        if abs(sum(stones[x][1][0] for x in range(3))) == 3:
            return True
        if abs(sum(stones[x][1][2] for x in range(3))) == 3:
            return True

    # Dodatna provera za sve x, y, z
    for i in range(3):
        # Provera horizontalnih linija za sve y
        if abs(sum(stones[x][i][z] for x in range(3))) == 3:
            return True
        # Provera vertikalnih linija za sve x i z
        if abs(sum(stones[j][y][z] for j in range(3))) == 3:
            return True
        # Provera dijagonalnih linija za sve x i y
        if abs(sum(stones[z][i][j] for j in range(3))) == 3:
            return True

    # Provera linija koje prolaze kroz susedne kvadrate za z
    if x == 0 or x == 2:
        if abs(sum(stones[0][i][z] for i in range(3))) == 3:
            return True
        if abs(sum(stones[2][i][z] for i in range(3))) == 3:
            return True
    if y == 0 or y == 2:
        if abs(sum(stones[i][0][z] for i in range(3))) == 3:
            return True
        if abs(sum(stones[i][2][z] for i in range(3))) == 3:
            return True
    

    return False



def apply_move(state, move):
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

def undo_move(state, move):
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
    
    state['turn'] -= 1



COMPUTER_PLAYER = 1
PLAYER = -1

def minimax(state, depth, player, line_made=False, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or is_end(state):
        return custom_easy_evaluate(state), None

    next_player = PLAYER if player == COMPUTER_PLAYER else COMPUTER_PLAYER

    if player == COMPUTER_PLAYER:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = minimax(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value > value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            alpha = max(alpha, value)
            if value >= beta:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = minimax(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value < value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            beta = min(beta, value)
            if value <= alpha:
                break
        return value, best_move

import random  # Don't forget to import the 'random' module

def improved_heuristic(state):
    stones = state['stones']
    mills = state.get('mills', [])  
    
    value = 0
    
    # Count horizontal lines
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][line][spot]
            
            if abs(line_sum) == 3:
                value += line_sum * 100  

    # Count vertical lines            
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][spot][line]

            if abs(line_sum) == 3:
                value += line_sum * 100  
    
    # Count number of stones
    value -= state['white_count'] * 25
    value += state['black_count'] * 250
    
    # Initialization of the own_mill_bonus variable
    own_mill_bonus = 0
    
    # Create own mill and block opponent if both have two stones
    if state['turn'] == 1 and state['white_count'] == 2 and state['black_count'] == 2:
        own_mill_bonus = 100
        block_opponent_bonus = 50

        for square in range(3):
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][line][spot]
                
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * own_mill_bonus  
                elif abs(line_sum) == 2 and line_sum * state['turn'] < 0:
                    # Add a condition to block the opponent only if there are not 2 stones in a row
                    if abs(line_sum) != 2:
                        value += line_sum * block_opponent_bonus  

            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][spot][line]

                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * own_mill_bonus  
                elif abs(line_sum) == 2 and line_sum * state['turn'] < 0:
                    # Add a condition to block the opponent only if there are not 2 stones in a row
                    if abs(line_sum) != 2:
                        value += line_sum * block_opponent_bonus  

    # Building own mills before blocking opponents
    build_mill_bonus = 75
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][line][spot]
            
            if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                value += line_sum * build_mill_bonus
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][spot][line]

            if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                value += line_sum * build_mill_bonus
    
    # Strategies for attracting opponents towards mills
    opponent_near_mill_bonus = 40
    if state['turn'] == -1 and state['black_count'] == 2:
        for square in range(3):
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][line][spot]
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * opponent_near_mill_bonus
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][spot][line]
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * opponent_near_mill_bonus

    # Eat stones when a mill is formed
    eat_stones_bonus = 150
    for mill in mills:
        mill_count = 0
        for position in mill:
            x, y, z = position
            mill_count += stones[x][y][z]
        if abs(mill_count) == 3:
            value += mill_count * eat_stones_bonus

            # Remove opponent stones
            for position in mill:
                x, y, z = position
                if stones[x][y][z] == -1:  # Assuming -1 represents opponent's stones
                    stones[x][y][z] = 0

    # Eat opponent stones that move frequently
    move_frequency_bonus = 30
    for square in range(3):
        for line in [0, 2]:
            line_sum_horizontal = 0
            line_sum_vertical = 0
            for spot in range(3):
                line_sum_horizontal += stones[square][line][spot]
                line_sum_vertical += stones[square][spot][line]
            
            if abs(line_sum_horizontal) == 2 and line_sum_horizontal * state['turn'] < 0:
                value += line_sum_horizontal * move_frequency_bonus
            if abs(line_sum_vertical) == 2 and line_sum_vertical * state['turn'] < 0:
                value += line_sum_vertical * move_frequency_bonus

    # Improved blocking mechanism
    block_opponent_mill_bonus = 80
    if state['turn'] == COMPUTER_PLAYER:
        for mill in mills:
            mill_count = 0
            for position in mill:
                x, y, z = position
                mill_count += stones[x][y][z]
            if abs(mill_count) == 2 and mill_count * state['turn'] < 0:
                # Add a condition to always block the opponent when there are 2 stones in a row
                value += mill_count * block_opponent_mill_bonus

    # Add a random component
    random_bonus = random.randint(0, 10)
    value += random_bonus

    return value





def is_stone_in_mill(position, mills):
    # Provera da li se kamen nalazi u nekom mlinu
    return position in mills



def hard_heuristic(state):
    stones = state['stones']
    mills = state.get('mills', [])  # Dodajte liniju koja uzima mlinove iz stanja (ili koristite odgovarajući ključ)
    
    value = 0
    
    # count horizontal lines
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][line][spot]
            
            if abs(line_sum) == 3:
                value += line_sum * 100  # Povećajte vrednost za pravljenje mlinova

    # count vertical lines            
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][spot][line]

            if abs(line_sum) == 3:
                value += line_sum * 100  # Povećajte vrednost za pravljenje mlinova
    
    # count number of stones
    value -= state['white_count'] * 25
    value += state['black_count'] * 250
    
    # Inicijalizacija promenljive own_mill_bonus
    own_mill_bonus = 0
    
    # Create own mill and block opponent if both have two stones
    if state['turn'] == 1 and state['white_count'] == 2 and state['black_count'] == 2:
        own_mill_bonus = 100
        block_opponent_bonus = 50

        for square in range(3):
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][line][spot]
                
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * own_mill_bonus  # Increase value for creating own mill
                elif abs(line_sum) == 2 and line_sum * state['turn'] < 0:
                    value += line_sum * block_opponent_bonus  # Increase value for blocking opponent's mill

            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][spot][line]

                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * own_mill_bonus  # Increase value for creating own mill
                elif abs(line_sum) == 2 and line_sum * state['turn'] < 0:
                    value += line_sum * block_opponent_bonus  # Increase value for blocking opponent's mill
    # Building own mills before blocking opponents
    build_mill_bonus = 75
    for square in range(3):
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][line][spot]
            
            if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                value += line_sum * build_mill_bonus
        for line in [0, 2]:
            line_sum = 0
            for spot in range(3):
                line_sum += stones[square][spot][line]

            if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                value += line_sum * build_mill_bonus
    
    # Strategies for attracting opponents towards mills
    opponent_near_mill_bonus = 40
    if state['turn'] == -1 and state['black_count'] == 2:
        for square in range(3):
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][line][spot]
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * opponent_near_mill_bonus
            for line in [0, 2]:
                line_sum = 0
                for spot in range(3):
                    line_sum += stones[square][spot][line]
                if abs(line_sum) == 2 and line_sum * state['turn'] > 0:
                    value += line_sum * opponent_near_mill_bonus

    # Additional conditions for making the heuristic "hard"
    if state['turn'] == COMPUTER_PLAYER and state['black_count'] > 2:
        # Computer has made a mill, force a move that undoes the opponent's mill
        value += 500
    
    return value

def alphabeta(state, depth, a, b, player, line_made=False):
    if depth == 0 or is_end(state):
        return improved_heuristic(state), None

    next_player = PLAYER if player == COMPUTER_PLAYER else COMPUTER_PLAYER

    if player == COMPUTER_PLAYER:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = alphabeta(state, depth - 1, a, b, next_player, line_made)
            if new_value > value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            a = max(a, value)
            if value >= b:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = alphabeta(state, depth - 1, a, b, next_player, line_made)
            if new_value < value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            b = min(b, value)
            if value <= a:
                break
        return value, best_move









def allfabeta(state, depth, player, line_made=False, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or is_end(state):
        return improved_heuristic(state), None

    next_player = PLAYER if player == COMPUTER_PLAYER else COMPUTER_PLAYER

    if player == COMPUTER_PLAYER:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = allfabeta(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value > value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            alpha = max(alpha, value)
            if value >= beta:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = allfabeta(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value < value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            beta = min(beta, value)
            if value <= alpha:
                break
        return value, best_move


import random



def allfabetaa(state, depth, player, line_made=False, alpha=float('-inf'), beta=float('inf')):
    if depth == 0 or is_end(state):
        return hard_heuristic(state), None

    next_player = PLAYER if player == COMPUTER_PLAYER else COMPUTER_PLAYER

    if player == COMPUTER_PLAYER:
        value = float('-inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = allfabetaa(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value > value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            alpha = max(alpha, value)
            if value >= beta:
                break
        return value, best_move
    else:
        value = float('inf')
        best_move = None
        for move in get_moves(state, player, line_made):
            apply_move(state, move)
            if is_making_line(state, move):
                next_player *= -1
                line_made = True
            if move[MOVE_TYPE] == REMOVE_STONE:
                line_made = False
            new_value, _ = allfabetaa(state, depth - 1, next_player, line_made, alpha, beta)
            if new_value < value:
                best_move = move
                value = new_value
            line_made = False
            undo_move(state, move)
            beta = min(beta, value)
            if value <= alpha:
                break
        return value, best_move