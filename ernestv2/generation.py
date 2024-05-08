# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
import copy

VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = 1000000
DRAW = 0

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

def generate_pieces(
    curr: State,
    playerColor: bool
) -> list[PlaceAction]:
    pieces = set()
    legal_squares = generate_legal_squares(curr.board, playerColor)
    #print(legal_squares)
    for square in legal_squares:
        legal_pieces = generate_pieces_for_square(curr.board, square)
        pieces.update(legal_pieces)
    return list(pieces)

def generate_states(
    curr: State,
    playerColor: bool
) -> list[State]:
    """
    Given a State and the target coordinate, return all neighbour states that can be reached from the given one,
    accounting for any line deletion where possible, but not the lines that contain the target square.
    """
    new_boards = set()
    new_states = []
    legal_squares = generate_legal_squares(curr.board, playerColor)
    for square in legal_squares:
        legal_pieces = generate_pieces_for_square(curr.board, square)
        for piece in legal_pieces:
            new_state = create_state(curr, piece, playerColor)
            new_board = frozenset(new_state.board.items())
            if new_board not in new_boards:
                new_boards.add(new_board)
                new_states.append(new_state)
    return new_states

def generate_legal_squares(
    board: dict[Coord, PlayerColor],
    playerColor: bool
) -> set[Coord]:
    """
    Given a board state, return all the legal empty squares where PlaceActions are possible around squares
    with red blocks.
    """
    squares = []
    for key in board:
        if playerColor:
            if board[key] == PlayerColor.RED:
                squares.extend(empty_squares_around(board, key))
        else:
            if board[key] == PlayerColor.BLUE:
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
    

def generate_pieces_for_square(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.

    Example for vertical I piece and square (3, 2):
     , , , , , ,
     , , , , , ,
     , , , , , ,
     ,r, , , , ,
     , , , , , ,
     , , , , , ,
     , , , , , ,
    The vertical I piece can be placed 4 different ways on the given square:
     , ,r, , , ,      , , , , , ,      , , , , , ,      , , , , , ,
     , ,r, , , ,      , ,r, , , ,      , , , , , ,      , , , , , ,
     , ,r, , , ,      , ,r, , , ,      , ,r, , , ,      , , , , , ,
     ,r,r, , , ,      ,r,r, , , ,      ,r,r, , , ,      ,r,r, , , ,
     , , , , , ,      , ,r, , , ,      , ,r, , , ,      , ,r, , , ,
     , , , , , ,      , , , , , ,      , ,r, , , ,      , ,r, , , ,
     , , , , , ,      , , , , , ,      , , , , , ,      , ,r, , , ,
    The same logic can be applied for other pieces, if the piece placement is legal
    """
    pieces = []
    pieces.extend(generate_I_pieces(board, square))
    pieces.extend(generate_L_pieces(board, square))
    pieces.extend(generate_J_pieces(board, square))
    pieces.extend(generate_T_pieces(board, square))
    pieces.extend(generate_Z_pieces(board, square))
    pieces.extend(generate_S_pieces(board, square))
    pieces.extend(generate_O_pieces(board, square))
    return pieces

def generate_I_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal I piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    I_pieces = []

    # Horizontal I piece
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(3)))):
        I_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(3)))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right(2)))):
        I_pieces.append(PlaceAction(square.left(), square, square.right(), square.right(2)))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.right()))):
        I_pieces.append(PlaceAction(square.left(2), square.left(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(3), square.left(2), square.left(), square))):
        I_pieces.append(PlaceAction(square.left(3), square.left(2), square.left(), square))
    # Vertical I piece
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(3)))):
        I_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(3)))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down(2)))):
        I_pieces.append(PlaceAction(square.up(), square, square.down(), square.down(2)))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.down()))):
        I_pieces.append(PlaceAction(square.up(2), square.up(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(3), square.up(2), square.up(), square))):
        I_pieces.append(PlaceAction(square.up(3), square.up(2), square.up(), square))

    return I_pieces

def generate_L_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal L piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    L_pieces = []

    # L piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(2).right()))):
        L_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(2).right()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down().right()))):
        L_pieces.append(PlaceAction(square.up(), square, square.down(), square.down().right()))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.right()))):
        L_pieces.append(PlaceAction(square.up(2), square.up(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left().up(2), square.left().up(), square.left(), square))):
        L_pieces.append(PlaceAction(square.left().up(2), square.left().up(), square.left(), square))
    # L piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left(2), square.left(2).down()))):
        L_pieces.append(PlaceAction(square, square.left(), square.left(2), square.left(2).down()))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.left(), square.left().down()))):
        L_pieces.append(PlaceAction(square.right(), square, square.left(), square.left().down()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square, square.down()))):
        L_pieces.append(PlaceAction(square.right(2), square.right(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().right(2), square.up().right(), square.up(), square))):
        L_pieces.append(PlaceAction(square.up().right(2), square.up().right(), square.up(), square))
    # L piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up(2), square.up(2).left()))):
        L_pieces.append(PlaceAction(square, square.up(), square.up(2), square.up(2).left()))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.up(), square.up().left()))):
        L_pieces.append(PlaceAction(square.down(), square, square.up(), square.up().left()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square, square.left()))):
        L_pieces.append(PlaceAction(square.down(2), square.down(), square, square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().down(2), square.right().down(), square.right(), square))):
        L_pieces.append(PlaceAction(square.right().down(2), square.right().down(), square.right(), square))
    # L piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(2).up()))):
        L_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(2).up()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right().up()))):
        L_pieces.append(PlaceAction(square.left(), square, square.right(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.up()))):
        L_pieces.append(PlaceAction(square.left(2), square.left(), square, square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().left(2), square.down().left(), square.down(), square))):
        L_pieces.append(PlaceAction(square.down().left(2), square.down().left(), square.down(), square))

    return L_pieces

def generate_J_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal J piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    J_pieces = []

    # J piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down(2), square.down(2).left()))):
        J_pieces.append(PlaceAction(square, square.down(), square.down(2), square.down(2).left()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.down(), square.down().left()))):
        J_pieces.append(PlaceAction(square.up(), square, square.down(), square.down().left()))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square, square.left()))):
        J_pieces.append(PlaceAction(square.up(2), square.up(), square, square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().up(2), square.right().up(), square.right(), square))):
        J_pieces.append(PlaceAction(square.right().up(2), square.right().up(), square.right(), square))
    # J piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left(2), square.left(2).up()))):
        J_pieces.append(PlaceAction(square, square.left(), square.left(2), square.left(2).up()))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.left(), square.left().up()))):
        J_pieces.append(PlaceAction(square.right(), square, square.left(), square.left().up()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square, square.up()))):
        J_pieces.append(PlaceAction(square.right(2), square.right(), square, square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().right(2), square.down().right(), square.down(), square))):
        J_pieces.append(PlaceAction(square.down().right(2), square.down().right(), square.down(), square))
    # J piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up(2), square.up(2).right()))):
        J_pieces.append(PlaceAction(square, square.up(), square.up(2), square.up(2).right()))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.up(), square.up().right()))):
        J_pieces.append(PlaceAction(square.down(), square, square.up(), square.up().right()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square, square.right()))):
        J_pieces.append(PlaceAction(square.down(2), square.down(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left().down(2), square.left().down(), square.left(), square))):
        J_pieces.append(PlaceAction(square.left().down(2), square.left().down(), square.left(), square))
    # J piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right(2), square.right(2).down()))):
        J_pieces.append(PlaceAction(square, square.right(), square.right(2), square.right(2).down()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.right(), square.right().down()))):
        J_pieces.append(PlaceAction(square.left(), square, square.right(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square, square.down()))):
        J_pieces.append(PlaceAction(square.left(2), square.left(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().left(2), square.up().left(), square.up(), square))):
        J_pieces.append(PlaceAction(square.up().left(2), square.up().left(), square.up(), square))

    return J_pieces

def generate_T_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal T piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    T_pieces = []

    # T piece rotated 0 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().down(), square.right(2)))):
        T_pieces.append(PlaceAction(square, square.right(), square.right().down(), square.right(2)))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.down(), square.right()))):
        T_pieces.append(PlaceAction(square.left(), square, square.down(), square.right()))
    if (piece_is_legal(board, PlaceAction(square.left().up(), square.up(), square, square.right().up()))):
        T_pieces.append(PlaceAction(square.left().up(), square.up(), square, square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left(2), square.left(), square.down().left(), square))):
        T_pieces.append(PlaceAction(square.left(2), square.left(), square.down().left(), square))
    # T piece rotated 90 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().left(), square.down(2)))):
        T_pieces.append(PlaceAction(square, square.down(), square.down().left(), square.down(2)))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.left(), square.down()))):
        T_pieces.append(PlaceAction(square.up(), square, square.left(), square.down()))
    if (piece_is_legal(board, PlaceAction(square.up().right(), square.right(), square, square.down().right()))):
        T_pieces.append(PlaceAction(square.up().right(), square.right(), square, square.down().right()))
    if (piece_is_legal(board, PlaceAction(square.up(2), square.up(), square.left().up(), square))):
        T_pieces.append(PlaceAction(square.up(2), square.up(), square.left().up(), square))
    # T piece rotated 180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.left().up(), square.left(2)))):
        T_pieces.append(PlaceAction(square, square.left(), square.left().up(), square.left(2)))
    if (piece_is_legal(board, PlaceAction(square.right(), square, square.up(), square.left()))):
        T_pieces.append(PlaceAction(square.right(), square, square.up(), square.left()))
    if (piece_is_legal(board, PlaceAction(square.right().down(), square.down(), square, square.left().down()))):
        T_pieces.append(PlaceAction(square.right().down(), square.down(), square, square.left().down()))
    if (piece_is_legal(board, PlaceAction(square.right(2), square.right(), square.up().right(), square))):
        T_pieces.append(PlaceAction(square.right(2), square.right(), square.up().right(), square))
    # T piece rotated 270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.up(), square.up().right(), square.up(2)))):
        T_pieces.append(PlaceAction(square, square.up(), square.up().right(), square.up(2)))
    if (piece_is_legal(board, PlaceAction(square.down(), square, square.right(), square.up()))):
        T_pieces.append(PlaceAction(square.down(), square, square.right(), square.up()))
    if (piece_is_legal(board, PlaceAction(square.down().left(), square.left(), square, square.up().left()))):
        T_pieces.append(PlaceAction(square.down().left(), square.left(), square, square.up().left()))
    if (piece_is_legal(board, PlaceAction(square.down(2), square.down(), square.right().down(), square))):
        T_pieces.append(PlaceAction(square.down(2), square.down(), square.right().down(), square))

    return T_pieces

def generate_Z_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal Z piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    Z_pieces = []

    # Z piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().down(), square.right(2).down()))):
        Z_pieces.append(PlaceAction(square, square.right(), square.right().down(), square.right(2).down()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.down(), square.right().down()))):
        Z_pieces.append(PlaceAction(square.left(), square, square.down(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square.left().up(), square.up(), square, square.right()))):
        Z_pieces.append(PlaceAction(square.left().up(), square.up(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(2).up(), square.left().up(), square.left(), square))):
        Z_pieces.append(PlaceAction(square.left(2).up(), square.left().up(), square.left(), square))
    # Z piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().left(), square.down(2).left()))):
        Z_pieces.append(PlaceAction(square, square.down(), square.down().left(), square.down(2).left()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.left(), square.down().left()))):
        Z_pieces.append(PlaceAction(square.up(), square, square.left(), square.down().left()))
    if (piece_is_legal(board, PlaceAction(square.up().right(), square.right(), square, square.down()))):
        Z_pieces.append(PlaceAction(square.up().right(), square.right(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(2).right(), square.up().right(), square.up(), square))):
        Z_pieces.append(PlaceAction(square.up(2).right(), square.up().right(), square.up(), square))

    return Z_pieces

def generate_S_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal S piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    S_pieces = []

    # S piece rotated 0/180 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.right().up(), square.right(2).up()))):
        S_pieces.append(PlaceAction(square, square.right(), square.right().up(), square.right(2).up()))
    if (piece_is_legal(board, PlaceAction(square.left(), square, square.up(), square.right().up()))):
        S_pieces.append(PlaceAction(square.left(), square, square.up(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square.left().down(), square.down(), square, square.right()))):
        S_pieces.append(PlaceAction(square.left().down(), square.down(), square, square.right()))
    if (piece_is_legal(board, PlaceAction(square.left(2).down(), square.left().down(), square.left(), square))):
        S_pieces.append(PlaceAction(square.left(2).down(), square.left().down(), square.left(), square))
    # S piece rotated 90/270 degrees to the right
    if (piece_is_legal(board, PlaceAction(square, square.down(), square.down().right(), square.down(2).right()))):
        S_pieces.append(PlaceAction(square, square.down(), square.down().right(), square.down(2).right()))
    if (piece_is_legal(board, PlaceAction(square.up(), square, square.right(), square.down().right()))):
        S_pieces.append(PlaceAction(square.up(), square, square.right(), square.down().right()))
    if (piece_is_legal(board, PlaceAction(square.up().left(), square.left(), square, square.down()))):
        S_pieces.append(PlaceAction(square.up().left(), square.left(), square, square.down()))
    if (piece_is_legal(board, PlaceAction(square.up(2).left(), square.up().left(), square.up(), square))):
        S_pieces.append(PlaceAction(square.up(2).left(), square.up().left(), square.up(), square))

    return S_pieces

def generate_O_pieces(
    board: dict[Coord, PlayerColor],
    square: Coord
) -> list[PlaceAction]:
    """
    Given a square coordinate and a board state, return all legal O piece (tetromino) arrangements for that 
    square in a list.
    Each piece will have an maximum of 4 arrangements, since there is a possibility that all 4 squares of
    the piece itself can be placed on the given square.
    """
    O_pieces = []

    if (piece_is_legal(board, PlaceAction(square, square.right(), square.down(), square.right().down()))):
        O_pieces.append(PlaceAction(square, square.right(), square.down(), square.right().down()))
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.down(), square.left().down()))):
        O_pieces.append(PlaceAction(square, square.left(), square.down(), square.left().down()))
    if (piece_is_legal(board, PlaceAction(square, square.right(), square.up(), square.right().up()))):
        O_pieces.append(PlaceAction(square, square.right(), square.up(), square.right().up()))
    if (piece_is_legal(board, PlaceAction(square, square.left(), square.up(), square.left().up()))):
        O_pieces.append(PlaceAction(square, square.left(), square.up(), square.left().up()))

    return O_pieces

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

    return True