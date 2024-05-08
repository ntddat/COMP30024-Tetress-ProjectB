# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
from .transposition_table import Transposition_Table, LOOKUP_FAILED, TYPE_EXACT, TYPE_LOWER_BOUND, TYPE_UPPER_BOUND
from .zobrist import Zobrist
import copy
import time

VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = -1000000
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
    tt: Transposition_Table

    def __init__(self):
        self.time_per_move = TIME_PER_MOVE
        self.temp_board = {}
        self.temp_row_filled = [0]*11
        self.temp_col_filled = [0]*11
        self.temp_moves = 0
        self.temp_piece = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.tt = Transposition_Table(100000)

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
            x = self.search(curr, depth, 0, VERY_SMALL_NUMBER, VERY_BIG_NUMBER, maxPlayer, 0)
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
        return eval

    def search(
        self, 
        curr: State,
        depth: int, 
        from_root: int,
        alpha: float,
        beta: float,
        maxPlayer: bool,
        enemy_move_num: int
    ) -> float:
        color = 1
        if not maxPlayer:
            color = -1
        if curr.moves == 150 or self.noLegalMoves(curr, maxPlayer): 
            return color*self.evaluation(curr, 0, maxPlayer)

        # look up transposition table and check if there is already a value at
        # an at least equal depth
        tt_lookup = self.tt.lookup(curr.zobrist_key, depth, from_root, alpha, beta)
        if tt_lookup != LOOKUP_FAILED:
            if from_root == 0:
                self.best_move = self.tt.get_piece(curr.zobrist_key)
            return tt_lookup

        child_pieces = generate_pieces(curr, maxPlayer)
        #print(child_pieces)
        len_child = len(child_pieces)
        # print(len_child)
        if from_root == 1:
            enemy_move_num = len_child
            if not maxPlayer:
                enemy_move_num = -enemy_move_num
        if not child_pieces:
            eval = 0
            if maxPlayer:
                eval = BLUE_WIN
            else:
                eval = RED_WIN
            return color*eval
        if depth == 0:
            return color*self.evaluation(curr, enemy_move_num, maxPlayer)

        original_board = curr.board.copy()
        original_row_filled = curr.row_filled.copy()
        original_col_filled = curr.col_filled.copy()
        original_moves = curr.moves
        original_piece = curr.piece
        original_zobrist = curr.zobrist_key

        hashPiece = self.tt.get_piece(curr.zobrist_key)

        tt_type = TYPE_UPPER_BOUND
        val = VERY_SMALL_NUMBER
        for piece in child_pieces:
            self.place_piece(curr, piece, maxPlayer)

            if hashPiece != None:
                if piece == hashPiece:
                    print("check")
                    val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not maxPlayer, enemy_move_num)
                else:
                    val = -self.search(curr, depth - 1, from_root + 1, -alpha - 1, -alpha, not maxPlayer, enemy_move_num)
                    if val > alpha and val < beta:
                        val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not maxPlayer, enemy_move_num)
            else:
                val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not maxPlayer, enemy_move_num)

            curr.board = original_board.copy()
            curr.row_filled = original_row_filled.copy()
            curr.col_filled = original_col_filled.copy()
            curr.moves = original_moves
            curr.piece = original_piece
            curr.zobrist_key = original_zobrist

            if val >= beta:
                self.tt.store(curr.zobrist_key, beta, depth, TYPE_LOWER_BOUND, piece)
                return beta

            if val > alpha:
                tt_type = TYPE_EXACT
                alpha = val
                if from_root == 0:
                    self.best_move = piece

        self.tt.store(curr.zobrist_key, alpha, depth, tt_type, self.best_move)
        return alpha
        """
        CONTINUE HERE
        """

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
        curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c1, color)
        curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c2, color)
        curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c3, color)
        curr.zobrist_key ^= curr.zobrist.get_zobrist_value(piece.c4, color)
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
        

    def delete_lines(
        self, 
        state: State):
        delete_squares = [Coord]

        # ROWS
        for i in range(0, BOARD_N):
            if state.row_filled[i] == BOARD_N:
                for key in state.board:
                    if key.r == i:
                        delete_squares.append(key)
        
        # COLUMNS
        for i in range(0, BOARD_N):
            if state.col_filled[i] == BOARD_N:
                for key in state.board:
                    if key.c == i:
                        delete_squares.append(key)
        
        for key in delete_squares:
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
    