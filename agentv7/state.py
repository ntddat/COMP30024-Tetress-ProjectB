# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, PlaceAction, BOARD_N
from .zobrist import Zobrist
from .bitboards import Bitboard
VERY_BIG_NUM = 1000

class State:
    """
    A class representing a current state of the board, with additional information like the f value used
    for the A* algorithm (f = used_cost + heuristic), the piece the had just been placed and other things.
    """
    board: dict[Coord, PlayerColor]
    bitboard: int
    b_utils: Bitboard
    row_filled: list[int]
    col_filled: list[int]
    num_red: int
    num_blue: int
    piece: PlaceAction
    moves: int
    zobrist: Zobrist
    zobrist_key: int
    max_player: bool

    def __init__(self,
        board: dict[Coord, PlayerColor],
        piece: PlaceAction | None,
        row: list[int],
        col: list[int],
        moves_played: int,
        zobrist: Zobrist | None,
        zobrist_key: int,
        max_player: bool):
        self.board = board
        self.bitboard = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
        self.b_utils = Bitboard()
        self.piece = piece
        self.row_filled = row
        self.col_filled = col
        self.num_red = 0
        self.num_blue = 0
        self.moves = moves_played
        if zobrist_key == -1:
            self.zobrist = Zobrist()
            self.zobrist_key = self.zobrist.calc_zobrist_key(board, max_player)
        else:
            self.zobrist = zobrist
            self.zobrist_key = zobrist_key
        self.max_player = max_player
