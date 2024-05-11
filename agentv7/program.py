# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
from .state import State
from .generation import place_piece
from .algorithm import Search
from .utils import render_board
import random

VERY_BIG_NUMBER = 100000
VERY_SMALL_NUMBER = -100000

"""
Plan:
Minimax with Alpha-Beta Pruning
State representation: 
- As of now can just use Part A's, but can change later (especially stuff to do with move generation)
- Also can add an array to store number of squares filled in each row/column, to help with line deletion
- Can maybe use bitboards hmmm ?
Optimizations:
- Quiescence search for moves that delete lines
- Transposition table
- Move ordering (not sure how to do this yet tho)
- Iterative deepening maybe
- Neural networks
"""

"""
Maybe just do MCTS lmao
Make a random agent to fight
"""

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.

    Features of the Agent:
    - MINIMAX with ALPHA-BETA PRUNING
    - ITERATIVE DEEPENING
    - PRINCIPAL VARIATION
    - TRANSPOSITION TABLE using ZOBRIST KEY HASHING
    - BOARD REPRESENTATION using BITBOARDS

    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        max_player = True
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                max_player = False
                print("Testing: I am playing as BLUE")

        # Initialize the Agent
        self._color = color
        board: dict[Coord, PlayerColor] = {}
        self._state = State(board, None, [0]*BOARD_N, [0]*BOARD_N, 0, None, -1, max_player)
        self._search = Search()

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 

        """

        # If it is the first turn of the game (occurs when the Agent is RED)
        if self._state.moves == 0:
            # Find and place a random piece
            random.seed()
            square = random.randint(0, 120)
            index = random.randint(0, 163)
            return self._state.b_utils.pieces_on_square[square][index]

        # If it is the second turn of the game (occurs when the Agent is BLUE)
        if self._state.moves == 1:
            random.seed()
            while True:
                # Find a random piece
                square = random.randint(0, 120)
                index = random.randint(0, 163)
                # If the piece is legal (doesn't overlap with pre-existing piece)
                if self._state.b_utils.masks_on_square[square][index] & self._state.bitboard == 0:
                    # Check if the placement of this move will result in an immediate loss next turn
                    # This happens when 2 I pieces are placed right next to each other horizontally or vertically
                    for num in self._state.b_utils.turn_two_losses:
                        if self._state.b_utils.masks_on_square[square][index] & num != 0:
                            continue
                    # Place the piece if it is satisfactory
                    return self._state.b_utils.pieces_on_square[square][index]

        print("BOARD:")
        print(render_board(self._state.board, True))
        self._state.b_utils.print_bitboard(self._state.bitboard)
        print("ROW:")
        print(self._state.row_filled)
        print("COL:")
        print(self._state.col_filled)
        print("NUM_RED:")
        print(self._state.num_red)
        print("NUM_BLUE:")
        print(self._state.num_blue)

        # Begin the search algorithm to find a piece
        eval, move = self._search.iterativeDeepening(self._state, self._color)

        print("TIME REMAINING:")
        print(referee["time_remaining"])
        print("EVALUATION:")
        print(eval)
        # Place the piece
        return move
        
        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        match self._color:
            case PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
        max_player = True
        if color == PlayerColor.BLUE:
            max_player = False

        # Update the internal state representation after a piece is placed
        place_piece(self._state, place_action, max_player)