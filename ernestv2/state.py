# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, PlaceAction, BOARD_N
VERY_BIG_NUM = 1000

class State:
    """
    A class representing a current state of the board, with additional information like the f value used
    for the A* algorithm (f = used_cost + heuristic), the piece the had just been placed and other things.
    """
    board: dict[Coord, PlayerColor]
    row_filled: list[int]
    col_filled: list[int]
    prev_pieces: list[PlaceAction]
    piece: PlaceAction
    moves: int

    def __init__(self,
        board: dict[Coord, PlayerColor],
        piece: PlaceAction | None,
        row: list[int],
        col: list[int],
        movesPlayed: int):
        self.board = board
        self.piece = piece
        self.children = []
        self.row_filled = row
        self.col_filled = col
        self.moves = movesPlayed
        self.prev_pieces = []

    # Comparison functions
    def __lt__(self, other: 'State') -> bool:
        return self.f_min < other.f_min

    def __le__(self, other: 'State') -> bool:
        return self.f_min <= other.f_min

    def __gt__(self, other: 'State') -> bool:
        return self.f_min > other.f_min

    def __ge__(self, other: 'State') -> bool:
        return self.f_min >= other.f_min


