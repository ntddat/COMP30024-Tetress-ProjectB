# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, place_piece, piece_is_legal
from .transposition_table import Transposition_Table, LOOKUP_FAILED, TYPE_EXACT, TYPE_LOWER_BOUND, TYPE_UPPER_BOUND
from .zobrist import Zobrist
import time

# Constants
VERY_BIG_NUMBER = 10000000
VERY_SMALL_NUMBER = -10000000
RED_WIN = 1000000
BLUE_WIN = -1000000
DRAW = 0

MAX_MOVES = 150
TIME_PER_MOVE = 1

class Search:
    """
    A class containing all the logic of the search algorithm.
    """

    time_per_move: int
    temp_best_move: PlaceAction
    best_move: PlaceAction
    temp_best_eval: float
    best_eval: float
    cancelled: bool
    tt: Transposition_Table
    test_temp: PlaceAction

    def __init__(self):
        self.time_per_move = TIME_PER_MOVE
        self.temp_best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.temp_best_eval = 0
        self.best_eval = 0
        self.cancelled = False
        self.tt = Transposition_Table(100000)
        self.test_temp = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

    def iterativeDeepening(
        self,
        curr: State,
        color: PlayerColor
    ) -> tuple[float, PlaceAction]:
        """
        The starting point of the search algorithm. Uses iterative deepenening for the search, starting
        with depth 1, then 2, 3, so on.
        """

        # Resetting attributes used for the search
        self.cancelled = False
        self.best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))
        self.temp_best_move = PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0))

        max_player = True
        if color == PlayerColor.BLUE:
            max_player = False

        remaining_moves = MAX_MOVES - curr.moves
        depth = 1
        # The time that the search begins, used to limit the amount of time for searching per turn
        self.start_time = time.process_time()

        # Depending on the "density" of the board, set a different time limit per turn for the search
        # In most cases, the more squares occupied on the board, the fewer pieces are able to be placed,
        # meaning there is a higher chance the game can end due to one side having no legal moves. The
        # search time limit is extended to make sure the Agent doesn't end up in this situation.
        if len(curr.board) < 60:
            self.time_per_move = 1.5
        elif len(curr.board) < 90:
            self.time_per_move = 2
        else:
            self.time_per_move = 3

        # Begins the iterative deepening search
        while (depth < remaining_moves and time.process_time() - self.start_time < self.time_per_move):
            # Begins minimax search
            self.temp_best_eval = self.search(curr, depth, 0, VERY_SMALL_NUMBER, VERY_BIG_NUMBER, max_player)
            # If the current iteration wasn't cancelled prematurely because time ran out, update the best move
            # and evaluation to return after the search is completed
            if not self.cancelled:
                self.best_move = self.temp_best_move
                self.best_eval = self.temp_best_eval
            print("time")
            depth += 1

        if self.test_temp == self.best_move:
            print("DAMN.")
            
        return self.best_eval, self.best_move


    def noSquares(
        self,
        curr: State,
        max_player: bool
    ) -> bool:
        """
        Checks if the current player (max_player) has no squares of their color on the board.
        """
        # If it is the first move for either color, this doesn't matter 
        if curr.moves < 2:
            return False
        
        if max_player:
            if curr.num_red > 0:
                return False
        else:
            if curr.num_blue > 0:
                return False
        return True

    def evaluation(
        self,
        curr: State,
        len_child: int,
    ) -> float:
        """
        The evaluation function for the minimax search algorithm. If the current state has a
        definitive result, return the corresponding value (RED_WIN, BLUE_WIN, DRAW).
        Otherwise, evaluate the current state using the following 2 components:
        - The number of red squares - the number of blue squares, with high weightage
        - The number of moves that can be made from this position (a negative number if it is
        BLUE's turn, and positive if RED's turn), with low weightage
        """

        # If one color has no squares on the board
        if curr.num_red > 0 and curr.num_blue == 0:
            return RED_WIN
        if curr.num_red == 0 and curr.num_blue > 0:
            return BLUE_WIN
        # If 150 moves have passed with no winners
        if curr.moves == 150:
            if curr.num_red > curr.num_blue:
                return RED_WIN
            elif curr.num_red < curr.num_blue:
                return BLUE_WIN
            else:
                return DRAW

        # Evaluate current position
        eval = 100*(curr.num_red - curr.num_blue) + 0.1*len_child
        return eval

    def search(
        self, 
        curr: State,
        depth: int, 
        from_root: int,
        alpha: float,
        beta: float,
        max_player: bool,
    ) -> float:
        """
        The minimax search algorithm. Uses the following features:
        - Alpha-Beta pruning
        - Move Ordering
        - Principal Variation
        - A transposition table (with Zobrist Key hashing)
        If during a search, the time limit for the turn is reached. The search is terminated, and
        the result of the previous iteration of iterative deepening is used.
        (this might not be the correct way to do it)
        """

        color = 1
        if not max_player:
            color = -1

        # If 150 moves have passed without a winner or if one color has no squares on the
        # board, evaluate the current state
        if curr.moves == 150 or self.noSquares(curr, max_player): 
            return color*self.evaluation(curr, 0)

        # If time ran out for the current turn, and a best move has already been found from 
        # a previous iteration, terminate the search
        if time.process_time() - self.start_time > self.time_per_move and self.best_move != PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0)):
            self.cancelled = True
            return 0

        # Look up the transposition table and check if the current state has already been
        # evaluated at an at least equal depth
        tt_lookup = self.tt.lookup(curr.zobrist_key, depth, from_root, alpha, beta)
        if tt_lookup != LOOKUP_FAILED:
            move = self.tt.get_piece(curr.zobrist_key)
            # If the piece retrieved from the transposition table is legal (it is illegal
            # when the lookup returns a wrong move because of hash collision)
            if piece_is_legal(curr.board, move):
                if from_root == 0:
                    self.temp_best_move = move
                    self.test_temp = self.temp_best_move
                return tt_lookup

        child_pieces = list(generate_pieces(curr, max_player))
        # The number of moves that can be made from this position, negative if it is BLUE's turn.
        # Used in the evaluation function
        len_child = len(child_pieces)
        if not max_player:
            len_child = -len_child

        # If there are no moves that can be made from this position, that means the current player
        # has lost
        if not child_pieces:
            eval = 0
            if max_player:
                eval = BLUE_WIN
            else:
                eval = RED_WIN
            return color*eval

        # Evaluate the position if the depth of the search has ended
        if depth == 0:
            return color*self.evaluation(curr, len_child)

        # Storing the original state's attributes to revert back to after making a move
        original_board = curr.board.copy()
        original_row_filled = curr.row_filled.copy()
        original_col_filled = curr.col_filled.copy()
        original_num_red = curr.num_red
        original_num_blue = curr.num_blue
        original_moves = curr.moves
        original_piece = curr.piece
        original_zobrist = curr.zobrist_key
        original_bitboard = curr.bitboard

        # If the current position is stored in the transposition table, retrieve the move
        # that was considered best, so that it can be searched fully
        hash_piece = self.tt.get_piece(curr.zobrist_key)

        # Order moves to improve alpha-beta pruning
        self.order_moves(child_pieces, hash_piece)

        # If after the search, no best move is found (no evaluation is > alpha), the evaluation we
        # get (alpha) might not be accurate, and is simply an upper bound for the actual evaluation.
        # So, by default, TYPE_UPPER_BOUND is used for any storing in the transposition table
        tt_type = TYPE_UPPER_BOUND
        val = VERY_SMALL_NUMBER
        for piece in child_pieces:
            # Place the piece on the current board
            place_piece(curr, piece, max_player)

            # Principal Variation: The move retrieved from the transposition table and the best move
            # found from the previous iteration will be searched fully. All other moves will be searched
            # with a "null window" of 1 (difference between alpha and beta is 1) to speed up the search,
            # since it is unlikely that these other moves will be better. 
            # If neither of these moves are available, we perform a full search on every move
            if hash_piece == None and self.best_move == PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0)):
                val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not max_player)
            else:
                if piece == hash_piece or piece == self.best_move:
                    val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not max_player)
                else:
                    val = -self.search(curr, depth - 1, from_root + 1, -alpha - 1, -alpha, not max_player)
                    # If after the null window search, the move ended up being good, perform a full search
                    if val > alpha and val < beta:
                        val = -self.search(curr, depth - 1, from_root + 1, -beta, -alpha, not max_player)

            # Revert the board back to original
            curr.board = original_board.copy()
            curr.row_filled = original_row_filled.copy()
            curr.col_filled = original_col_filled.copy()
            curr.num_red = original_num_red
            curr.num_blue = original_num_blue
            curr.moves = original_moves
            curr.piece = original_piece
            curr.zobrist_key = original_zobrist
            curr.bitboard = original_bitboard

            # If time ran out, terminate the search
            if self.cancelled:
                return 0

            # Beta cutoff: Move is too good for the opponent to choose
            if val >= beta:
                # Store position in transposition table. Because of the beta cutoff, the
                # evaluation of the position might not be accurate, and is simply a lower
                # bound for the actual evaluation (TYPE_LOWER_BOUND)
                self.tt.store(curr.zobrist_key, beta, depth, TYPE_LOWER_BOUND, piece)
                return beta

            # Alpha: Best move so far in the current state is found
            if val > alpha:
                # A best move is found, so we can reasonably say that the evaluation is 
                # accurate (TYPE_EXACT)
                tt_type = TYPE_EXACT
                alpha = val
                if from_root == 0:
                    self.temp_best_move = piece

        # Store position in transposition table
        self.tt.store(curr.zobrist_key, alpha, depth, tt_type, self.temp_best_move)
        return alpha
        
    def order_moves(
        self,
        child_pieces: list[PlaceAction],
        hash_piece: PlaceAction
    ):
        """
        Move ordering for the move list of the current position. When possible, the best move from the previous
        iteration of iterative deepening and the move hashed from the transposition table will be moved to the front
        """

        # If both move types are not available to be ordered, end the function
        if hash_piece == None and self.best_move == PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0)):
            return

        # If there are only 2 moves to order, end the function
        if len(child_pieces) <= 2:
            return
        
        # By default, put the best move of the previous iteration at index 0, the hashed move at index 1
        best_piece_index = 0
        hash_piece_index = 1
        best_piece_done = False
        hash_piece_done = False
        # If the best move is not available, put the hashed move at index 0
        if self.best_move == PlaceAction(Coord(0, 0), Coord(0, 0), Coord(0, 0), Coord(0, 0)):
            hash_piece_index = 0
            best_piece_done = True
        if hash_piece == None:
            hash_piece_done = True

        for i in range(len(child_pieces)):
            if best_piece_done and hash_piece_done:
                break
            if not best_piece_done:
                if child_pieces[i] == self.best_move:
                    child_pieces[i], child_pieces[best_piece_index] = child_pieces[best_piece_index], child_pieces[i]
                    best_piece_done = True
            if not hash_piece_done:
                if child_pieces[i] == hash_piece:
                    child_pieces[i], child_pieces[hash_piece_index] = child_pieces[hash_piece_index], child_pieces[i]
                    hash_piece_done = True