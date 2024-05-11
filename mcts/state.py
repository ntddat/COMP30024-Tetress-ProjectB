# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, PlaceAction, BOARD_N


VERY_BIG_NUM = 1000
MAX_MOVES = 150
WIN = 1
LOSE = -1
DRAW = 0

class State:
    """
    A class representing a current state of the board, with additional information like the f value used
    for the A* algorithm (f = used_cost + heuristic), the piece the had just been placed and other things.
    """
    board: dict[Coord, PlayerColor]
    row_filled: list[int]
    col_filled: list[int]
    wins: int
    parent = None
    piece: PlaceAction
    visits: int
    moves: int
    color: PlayerColor

    def __init__(self,
        board: dict[Coord, PlayerColor],
        piece: PlaceAction | None,
        row: list[int],
        col: list[int],
        color: PlayerColor,
        movesPlayed: int,
        parent=None,
        ):

        self.board = board
        self.piece = piece
        self.row_filled = row
        self.col_filled = col
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.parent = parent
        self.color = color
        self.moves = movesPlayed

    # Comparison functions
    def __lt__(self, other: 'State') -> bool:
        return self.f_min < other.f_min

    def __le__(self, other: 'State') -> bool:
        return self.f_min <= other.f_min

    def __gt__(self, other: 'State') -> bool:
        return self.f_min > other.f_min

    def __ge__(self, other: 'State') -> bool:
        return self.f_min >= other.f_min
    