# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress
from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
import random

SEED = 1370085

class Zobrist:

    """
    121*2 random numbers
    look at the seblague and the blunder bot
    """

    side_to_move: int
    rand_numbers: list[int]

    def __init__(self):
        random.seed(SEED)
        self.rand_numbers = [0]*242
        for i in range(0, 242):
            self.rand_numbers[i] = random.getrandbits(64)
        self.side_to_move = random.getrandbits(64)

    def calc_zobrist_key(
        self, 
        board: dict[Coord, PlayerColor],
        maxPlayer: bool
    ) -> int:
        zobrist_key = 0
        for key in board:
            color = 0
            if board[key] == PlayerColor.BLUE:
                color = 1
            zobrist_key ^= self.rand_numbers[BOARD_N*key.r + key.c + color*BOARD_N*BOARD_N]
        if not maxPlayer:
            zobrist_key ^= self.side_to_move
        
        return zobrist_key

    def get_zobrist_value(
        self,
        square: Coord,
        color: PlayerColor
    ) -> int:
        color_num = 0
        if color == PlayerColor.BLUE:
            color_num = 1
        return self.rand_numbers[BOARD_N*square.r + square.c + color_num*BOARD_N*BOARD_N]