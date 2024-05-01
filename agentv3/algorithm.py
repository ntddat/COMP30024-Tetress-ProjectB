# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import copy
import time

VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = 1000000
DRAW = 0

MAX_MOVES = 150
TIME_PER_MOVE = 2

class Search:

    time_per_move: int
    temp_board: dict[Coord, PlayerColor]
    temp_row_filled: list[int]
    temp_col_filled: list[int]
    temp_moves: int
    temp_piece: PlaceAction
    best_move: PlaceAction

    def _init_(self):
        self.time_per_move = TIME_PER_MOVE
        self.temp_board = {}
        self.temp_row_filled = [0]*11
        self.temp_col_filled = [0]*11
        self.temp_moves = 0
        self.temp_piece = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

    def iterativeDeepening(
        self,
        curr: State,
        color: PlayerColor
    ) -> tuple[float, PlaceAction]:

        maxPlayer = True
        if color == PlayerColor.BLUE:
            maxPlayer = False

        remaining_moves = MAX_MOVES - curr.moves
        depth = 1
        start_time = time.process_time()
        x = 0
        while (depth < remaining_moves and time.process_time() - start_time < TIME_PER_MOVE):
            x = self.search(curr, depth, 0, VERY_SMALL_NUMBER, VERY_BIG_NUMBER, maxPlayer)
            print("time")
            depth += 1
            
        return x, self.best_move


    def noLegalMoves(
        self,
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
        self,
        curr: State,
        len_child: int,
        maxPlayer: bool
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
        eval = 100*(numRed - numBlue) + 0.1*len_child
        if not maxPlayer:
            eval = -eval
        return eval

    counter = 0

    def search(
        self, 
        curr: State,
        depth: int, 
        fromRoot: int,
        alpha: float,
        beta: float,
        maxPlayer: bool
    ) -> float:
        if curr.moves == 150 or self.noLegalMoves(curr, maxPlayer): 
            return self.evaluation(curr, 0, maxPlayer)
        child_pieces = generate_pieces(curr, maxPlayer)
        #print(child_pieces)
        len_child = len(child_pieces)
        # print(len_child)
        if not maxPlayer:
            len_child = -1*len_child
        if not child_pieces:
            if maxPlayer:
                return RED_WIN
            else:
                return BLUE_WIN
        if depth == 0:
            return self.evaluation(curr, len_child, maxPlayer)

        original_board = curr.board.copy()
        original_row_filled = curr.row_filled.copy()
        original_col_filled = curr.col_filled.copy()
        original_moves = curr.moves
        original_piece = curr.piece
        for piece in child_pieces:
            self.place_piece(curr, piece, maxPlayer)
            val = -self.search(curr, depth - 1, fromRoot + 1, -beta, -alpha, not maxPlayer)
            curr.board = original_board.copy()
            curr.row_filled = original_row_filled.copy()
            curr.col_filled = original_col_filled.copy()
            curr.moves = original_moves
            curr.piece = original_piece

            if val >= beta:
                return beta

            if val > alpha:
                alpha = val
                if fromRoot == 0:
                    self.best_move = piece

        return alpha
        """
        CONTINUE HERE
        """

    def reset_state(self, curr: State):
        curr.board =  self.temp_board.copy()
        curr.row_filled = self.temp_row_filled.copy()
        curr.col_filled = self.temp_col_filled.copy()
        curr.moves = self.temp_moves
        curr.piece = self.temp_piece

    def create_temp(self, curr: State):
        self.temp_board = curr.board.copy()
        self.temp_row_filled = curr.row_filled.copy()
        self.temp_col_filled = curr.col_filled.copy()
        self.temp_moves = curr.moves
        self.temp_piece = curr.piece

    def minimax(
        self,
        curr: State,
        depth: int,
        alpha: float,
        beta: float,
        maxPlayer: bool
    ) -> tuple[float, PlaceAction]:
        if curr.moves == 150 or self.noLegalMoves(curr, maxPlayer): 
            return self.evaluation(curr, 0), curr.piece
        # right now there are always 2 moves made before minimax is ran, but in the future might have to change because
        # first move of each side always generate 0 child states
        #child_states = generate_states(curr, maxPlayer)
        child_pieces = generate_pieces(curr, maxPlayer)
        #print(child_pieces)
        len_child = len(child_pieces)
        # print(len_child)
        if not maxPlayer:
            len_child = -1*len_child
        if not child_pieces:
            if maxPlayer:
                return BLUE_WIN, curr.piece
            else:
                return RED_WIN, curr.piece
        if depth == 0:
            return self.evaluation(curr, len_child), curr.piece
        
        original_board = curr.board.copy()
        original_row_filled = curr.row_filled.copy()
        original_col_filled = curr.col_filled.copy()
        original_moves = curr.moves
        original_piece = curr.piece
        if maxPlayer:
            value = VERY_SMALL_NUMBER
            returned_piece = None
            for piece in child_pieces:
                self.place_piece(curr, piece, maxPlayer)
                returned_val, returned_piece = self.minimax(curr, depth - 1, alpha, beta, False) 
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
                self.place_piece(curr, piece, maxPlayer)
                returned_val, returned_piece = self.minimax(curr, depth - 1, alpha, beta, True) 
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
        self,
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
        self.delete_lines(curr)
        curr.moves += 1
        curr.piece = piece
        

    def delete_lines(self, state: State):
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
        self,
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
        self.delete_lines(new_state)
        return new_state
    