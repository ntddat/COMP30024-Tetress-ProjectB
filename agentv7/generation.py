# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
import copy

# Constants
VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = 1000000
DRAW = 0

"""
File to store functions related to move generation and placement (used to have more functions
before the addition of bitboards)
"""

def place_piece(
    curr: State,
    piece: PlaceAction,
    max_player: bool
):
    """
    Update the current state, given a piece to be placed.
    """
    color = PlayerColor.BLUE
    if max_player:
        color = PlayerColor.RED
    # Update the dict board
    curr.board.update({piece.c1: color})
    curr.board.update({piece.c2: color})
    curr.board.update({piece.c3: color})
    curr.board.update({piece.c4: color})
    # Update the bitboard
    curr.bitboard = curr.b_utils.set_bit(curr.bitboard, piece.c1.r*BOARD_N + piece.c1.c)
    curr.bitboard = curr.b_utils.set_bit(curr.bitboard, piece.c2.r*BOARD_N + piece.c2.c)
    curr.bitboard = curr.b_utils.set_bit(curr.bitboard, piece.c3.r*BOARD_N + piece.c3.c)
    curr.bitboard = curr.b_utils.set_bit(curr.bitboard, piece.c4.r*BOARD_N + piece.c4.c)
    # Update the number of red or blue squares count
    if color == PlayerColor.RED:
        curr.num_red += 4
    else:
        curr.num_blue += 4
    # Update the zobrist key
    curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c1, color)
    curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c2, color)
    curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c3, color)
    curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c4, color)
    # Update the counter for how many squares are in each row/column
    curr.row_filled[piece.c1.r] += 1
    curr.col_filled[piece.c1.c] += 1
    curr.row_filled[piece.c2.r] += 1
    curr.col_filled[piece.c2.c] += 1
    curr.row_filled[piece.c3.r] += 1
    curr.col_filled[piece.c3.c] += 1
    curr.row_filled[piece.c4.r] += 1
    curr.col_filled[piece.c4.c] += 1
    # Check for any line deletions that happened, and update accordingly
    delete_lines(curr)
    curr.moves += 1
    curr.piece = piece

def delete_lines(state: State):
    """
    Given a state, check if there are any lines that need to be deleted, and update
    the state accordingly
    """
    # List of squares to be removed
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
            # Update the counter for how many squares are in each row/column
            state.row_filled[key.r] -= 1
            state.col_filled[key.c] -= 1
            # Update the number of red or blue squares count
            if state.board[key] == PlayerColor.RED:
                state.num_red -= 1
            else:
                state.num_blue -= 1
            # Update the dict board
            del state.board[key]
            # Update the bitboard
            state.bitboard = state.b_utils.pop_bit(state.bitboard, key.r*BOARD_N + key.c)

def create_state(
    curr: State,
    piece: PlaceAction,
    maxPlayer: bool
) -> State:
    new_state = State(curr.board.copy(), piece, curr.row_filled.copy(), curr.col_filled.copy(), curr.moves + 1, curr.zobrist, curr.zobrist_key, curr.max_player)
    color = PlayerColor.BLUE
    if maxPlayer:
        color = PlayerColor.RED
    new_state.board.update({piece.c1: color})
    new_state.board.update({piece.c2: color})
    new_state.board.update({piece.c3: color})
    new_state.board.update({piece.c4: color})
    new_state.zobrist_key ^= new_state.zobrist.get_zobrist_value(piece.c1, color)
    new_state.zobrist_key ^= new_state.zobrist.get_zobrist_value(piece.c2, color)
    new_state.zobrist_key ^= new_state.zobrist.get_zobrist_value(piece.c3, color)
    new_state.zobrist_key ^= new_state.zobrist.get_zobrist_value(piece.c4, color)
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

def generate_pieces(
    curr: State,
    max_player: bool
) -> list[PlaceAction]:
    """
    Given a state, generate all legal moves for the current player
    """
    color = PlayerColor.RED
    if not max_player:
        color = PlayerColor.BLUE
    pieces = set()
    # For every square of the current player's color, retrieve its corresponding bitboards
    # and check if each bitboard is a legal move. If so, add the corresponding move to the 
    # list of legal moves
    for key in curr.board:
        if curr.board[key] == color:
            mask_list = curr.b_utils.masks_on_square[key.r*11 + key.c]
            piece_list = curr.b_utils.pieces_on_square[key.r*11 + key.c]
            for i in range(len(mask_list)):
                result = curr.bitboard & mask_list[i]
                if result == 0:
                    pieces.add(piece_list[i])

    return pieces

    """
def generate_pieces(
    curr: State,
    maxPlayer: bool
) -> list[PlaceAction]:
    pieces = set()
    legal_squares = generate_legal_squares(curr.board, maxPlayer)
    #print(legal_squares)
    for square in legal_squares:
        legal_pieces = generate_pieces_for_square(curr.board, square)
        pieces.update(legal_pieces)
    return pieces
    """

    """
def generate_states(
    curr: State,
    maxPlayer: bool
) -> list[State]:
    """
    """
    Given a State and the target coordinate, return all neighbour states that can be reached from the given one,
    accounting for any line deletion where possible, but not the lines that contain the target square.
    """
    """
    new_boards = set()
    new_states = []
    legal_squares = generate_legal_squares(curr.board, maxPlayer)
    for square in legal_squares:
        legal_pieces = generate_pieces_for_square(curr.board, square)
        for piece in legal_pieces:
            new_state = create_state(curr, piece, maxPlayer)
            new_board = frozenset(new_state.board.items())
            if new_board not in new_boards:
                new_boards.add(new_board)
                new_states.append(new_state)
    return new_states
    """

def num_legal_squares(
    board: dict[Coord, PlayerColor],
    maxPlayer: bool
) -> int:
    """
    Given a board state, return all the legal empty squares where PlaceActions are possible around squares
    with red blocks.
    """
    color = PlayerColor.RED
    if not maxPlayer:
        color = PlayerColor.BLUE

    squares = []
    for key in board:
        if board[key] == color:
            squares.extend(empty_squares_around(board, key))
    
    squares = set(squares)

    return len(squares)

def generate_legal_squares(
    board: dict[Coord, PlayerColor],
    maxPlayer: bool
) -> set[Coord]:
    """
    Given a board state, return all the legal empty squares where PlaceActions are possible around squares
    with red blocks.
    """
    color = PlayerColor.RED
    if not maxPlayer:
        color = PlayerColor.BLUE

    squares = []
    for key in board:
        if board[key] == color:
            squares.extend(empty_squares_around(board, key))

    return set(squares)

def empty_squares_around(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[Coord]:
    """
    Given a square coordinate and a board state, return all the empty squares around the coordinate (only
    vertical and horizontal, not diagonal).
    """
    empties = []

    if square.up() not in board:
        empties.append(square.up())
    if square.right() not in board:
        empties.append(square.right())
    if square.down() not in board:
        empties.append(square.down())
    if square.left() not in board:
        empties.append(square.left())

    return empties
    
def piece_is_legal(
    board: dict[Coord, PlayerColor],
    piece: PlaceAction
) -> bool:
    """
    Given a PlaceAction with 4 coordinates and a board state, return true if none of the 4 coordinates already 
    exist in the board state dict, false otherwise. Essentially checking if the PlaceAction is a legal move.
    """
    if piece.c1 in board:
        return False
    if piece.c2 in board:
        return False
    if piece.c3 in board:
        return False
    if piece.c4 in board:
        return False

    return True;
