# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import copy

VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = 1000000
DRAW = 0

def noLegalMoves(
    curr: State,
    maxPlayer: bool
) -> bool:
    if curr.moves <= 2:
        return False
    if maxPlayer:
        for key in curr.board:
            if curr.board[key] == PlayerColor.RED:
                return False
    else:
        for key in curr.board:
            if curr.board[key] == PlayerColor.BLUE:
                return False
    return True

def evaluation(
    curr: State,
    len_child: int
) -> float:
    numRed = 0
    for key in curr.board:
        if curr.board[key] == PlayerColor.RED:
            numRed += 1
    numBlue = 0
    for key in curr.board:
        if curr.board[key] == PlayerColor.BLUE:
            numBlue += 1
    if numRed > 0 and numBlue == 0:
        return RED_WIN
    if numRed == 0 and numBlue > 0:
        return BLUE_WIN
    if curr.moves == 150:
        if numRed > numBlue:
            return RED_WIN
        elif numRed < numBlue:
            return BLUE_WIN
        else:
            return DRAW
    return 100*(numRed - numBlue) + 0.1*len_child

counter = 0

def minimax(
    curr: State,
    depth: int,
    alpha: float,
    beta: float,
    maxPlayer: bool
) -> tuple[float, PlaceAction]:
    if curr.moves == 150 or noLegalMoves(curr, maxPlayer): 
        return evaluation(curr, 0), curr.piece
    # right now there are always 2 moves made before minimax is ran, but in the future might have to change because
    # first move of each side always generate 0 child states
    #child_states = generate_states(curr, maxPlayer)
    child_pieces = generate_pieces(curr, maxPlayer)
    #print(child_pieces)
    len_child = len(child_pieces)
    # print(len_child)
    if not maxPlayer:
        len_child = -1*len_child
    if depth == 0:
        return evaluation(curr, len_child), curr.piece
    if not child_pieces:
        return evaluation(curr, len_child), curr.piece
    
    original_board = curr.board.copy()
    original_row_filled = curr.row_filled.copy()
    original_col_filled = curr.col_filled.copy()
    original_moves = curr.moves
    original_piece = curr.piece
    if maxPlayer:
        value = VERY_SMALL_NUMBER
        returned_piece = None
        for piece in child_pieces:
            place_piece(curr, piece, maxPlayer)
            returned_val, returned_piece = minimax(curr, depth - 1, alpha, beta, False) 
            value = max(value, returned_val)
            curr.board = original_board.copy()
            curr.row_filled = original_row_filled.copy()
            curr.col_filled = original_col_filled.copy()
            curr.moves = original_moves
            curr.piece = original_piece
            returned_piece = piece
            if value > beta:
                #print("pruned")
                break
            alpha = max(alpha, value)
        return value, returned_piece
    else: 
        value = VERY_BIG_NUMBER
        returned_piece = None
        for piece in child_pieces:
            place_piece(curr, piece, maxPlayer)
            returned_val, returned_piece = minimax(curr, depth - 1, alpha, beta, True) 
            value = min(value, returned_val)
            curr.board = original_board.copy()
            curr.row_filled = original_row_filled.copy()
            curr.col_filled = original_col_filled.copy()
            curr.moves = original_moves
            curr.piece = original_piece
            returned_piece = piece
            if value < alpha:
                #print("pruned")
                break
            beta = min(beta, value)

        return value, returned_piece

def place_piece(
    curr: State,
    piece: PlaceAction,
    maxPlayer: bool
):
    color = PlayerColor.BLUE
    if maxPlayer:
        color = PlayerColor.RED
    curr.board.update({piece.c1: color})
    curr.board.update({piece.c2: color})
    curr.board.update({piece.c3: color})
    curr.board.update({piece.c4: color})
    curr.row_filled[piece.c1.r] += 1
    curr.col_filled[piece.c1.c] += 1
    curr.row_filled[piece.c2.r] += 1
    curr.col_filled[piece.c2.c] += 1
    curr.row_filled[piece.c3.r] += 1
    curr.col_filled[piece.c3.c] += 1
    curr.row_filled[piece.c4.r] += 1
    curr.col_filled[piece.c4.c] += 1
    delete_lines(curr)
    curr.moves += 1
    curr.piece = piece
    

def delete_lines(state: State):
    delete_entries = []

    # ROWS
    for i in range(0, BOARD_N):
        if state.row_filled[i] == BOARD_N:
            for key in state.board:
                if key.r == i:
                    delete_entries.append(key)
    
    # COLUMNS
    for i in range(0, BOARD_N):
        if state.col_filled[i] == BOARD_N:
            for key in state.board:
                if key.c == i:
                    delete_entries.append(key)
    
    for key in delete_entries:
        if key in state.board:
            state.row_filled[key.r] -= 1
            state.col_filled[key.c] -= 1
            del state.board[key]

def create_state(
    curr: State,
    piece: PlaceAction,
    maxPlayer: bool
) -> State:
    new_state = State(curr.board.copy(), piece, curr.row_filled.copy(), curr.col_filled.copy(), curr.moves + 1)
    color = PlayerColor.BLUE
    if maxPlayer:
        color = PlayerColor.RED
    new_state.board.update({piece.c1: color})
    new_state.board.update({piece.c2: color})
    new_state.board.update({piece.c3: color})
    new_state.board.update({piece.c4: color})
    new_state.row_filled[piece.c1.r] += 1
    new_state.col_filled[piece.c1.c] += 1
    new_state.row_filled[piece.c2.r] += 1
    new_state.col_filled[piece.c2.c] += 1
    new_state.row_filled[piece.c3.r] += 1
    new_state.col_filled[piece.c3.c] += 1
    new_state.row_filled[piece.c4.r] += 1
    new_state.col_filled[piece.c4.c] += 1
    delete_lines(new_state)
    return new_state