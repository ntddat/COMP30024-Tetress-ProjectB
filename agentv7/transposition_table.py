# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress
from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction

LOOKUP_FAILED = -1111111
TYPE_EXACT = 0
TYPE_LOWER_BOUND = 1
TYPE_UPPER_BOUND = 2

class Entry:
    key: int
    value: float
    depth: int
    type: int
    piece: PlaceAction

    def __init__(
        self, 
        key: int,
        value: int,
        depth: int,
        type: int,
        piece: PlaceAction
    ):
        self.key = key
        self.value = value
        self.depth = depth
        self.type = type
        self.piece = piece

class Transposition_Table:
    entries: list[Entry]
    size: int

    def __init__(self, size: int):
        self.entries = [None]*size
        self.size = size
    
    def lookup(
        self,
        zobrist_key: int,
        depth: int,
        from_root: int,
        alpha: float,
        beta: float
    ) -> float:
        entry = self.entries[zobrist_key % self.size]

        if entry == None:
            return LOOKUP_FAILED

        if entry.key == zobrist_key:
            if entry.depth >= depth:
                if entry.type == TYPE_EXACT:
                    return entry.value 
                if entry.type == TYPE_UPPER_BOUND and entry.value <= alpha:
                    return entry.value
                if entry.type == TYPE_LOWER_BOUND and entry.value >= beta:
                    return entry.value
        return LOOKUP_FAILED

    def store(
        self,
        zobrist_key: int,
        value: int,
        depth: int,
        type: int,
        piece: PlaceAction
    ):
        entry = Entry(zobrist_key, value, depth, type, piece)
        self.entries[zobrist_key % self.size] = entry
    
    def get_piece(self, zobrist_key: int):
        if self.entries[zobrist_key % self.size] != None:
            return self.entries[zobrist_key % self.size].piece
        return None

    """
    def clear(self):
        for i in range(0, len(self.entries)):
    """

            